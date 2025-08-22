import os, mimetypes, math, shutil, asyncio, logging, aiohttp, time, subprocess, tempfile
from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from notion_client import AsyncClient
from threading import Timer

# ── ENV ───────────────────────────────
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB    = os.getenv("NOTION_DATABASE_ID")
WATCH_DIR    = Path(os.getenv("WATCH_DIR", "/downloads"))
STABLE_DELAY = 60.0  # 文件夹稳定检测延时（秒）
PART_SIZE    = 19 * 1024 * 1024  # 使用原来工作的大小
SINGLE_LIMIT = 20 * 1024 * 1024  # 使用原来工作的大小
NOTION_VER   = "2022-06-28"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("uploader")

notion = AsyncClient(auth=NOTION_TOKEN)

# 目录处理队列和锁机制
pending_dirs = {}
processing_dirs = set()  # 记录正在处理的目录

# ── Notion Helper ─────────────────────
async def _create(sess,name,mime,multi,parts=1):
    p={"filename":name,"content_type":mime}
    if multi: p|={"mode":"multi_part","number_of_parts":parts}
    h={"Authorization":f"Bearer {NOTION_TOKEN}","Notion-Version":NOTION_VER,"Content-Type":"application/json"}
    async with sess.post("https://api.notion.com/v1/file_uploads",json=p,headers=h) as r: r.raise_for_status(); return await r.json()

async def _send(sess,url,idx,chunk,mime):
    f=aiohttp.FormData();f.add_field("part_number",str(idx));f.add_field("file",BytesIO(chunk),filename=f"part{idx}",content_type=mime)
    h={"Authorization":f"Bearer {NOTION_TOKEN}","Notion-Version":NOTION_VER}
    async with sess.post(url,data=f,headers=h) as r: r.raise_for_status()

async def _complete(sess,fid):
    h={"Authorization":f"Bearer {NOTION_TOKEN}","Notion-Version":NOTION_VER,"accept":"application/json"}
    async with sess.post(f"https://api.notion.com/v1/file_uploads/{fid}/complete",headers=h) as r: r.raise_for_status()

def f_block(tp,fid): return {"object":"block","type":tp,tp:{"type":"file_upload","file_upload":{"id":fid}}}

async def _create_page(title: str, blocks: list, cover_image_id: str = None):
    props = {"名称": {"title": [{"text": {"content": title}}]}}
    if cover_image_id:
        props["文件和媒体"] = {"files": [{"type": "file_upload", "file_upload": {"id": cover_image_id}}]}
    return await notion.pages.create(parent={"database_id": NOTION_DB}, properties=props, children=blocks)

# ── 视频缩略图生成功能 ─────────────────────
async def generate_video_thumbnail(video_path: Path) -> Path:
    """为视频生成缩略图，返回缩略图文件路径"""
    try:
        # 创建临时文件用于保存缩略图
        temp_dir = Path(tempfile.gettempdir())
        thumbnail_path = temp_dir / f"{video_path.stem}_thumbnail.jpg"
        
        # 使用ffmpeg生成第一帧缩略图
        cmd = [
            'ffmpeg', 
            '-i', str(video_path),
            '-vframes', '1',  # 只取第一帧
            '-y',  # 覆盖输出文件
            str(thumbnail_path)
        ]
        
        log.info(f"正在为视频 {video_path.name} 生成缩略图...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and thumbnail_path.exists():
            log.info(f"缩略图生成成功: {thumbnail_path.name}")
            return thumbnail_path
        else:
            log.error(f"ffmpeg生成缩略图失败: {result.stderr}")
            return None
            
    except Exception as e:
        log.error(f"生成缩略图时出错: {e}")
        return None

async def upload_thumbnail_for_media(media_files: list) -> str:
    """为媒体文件生成并上传缩略图到Notion，返回缩略图文件ID"""
    try:
        # 查找第一个视频文件
        first_video = None
        for fp in media_files:
            mime, _ = mimetypes.guess_type(fp)
            if mime and "video" in mime:
                first_video = fp
                break
        
        if not first_video:
            log.info("没有找到视频文件，跳过缩略图生成")
            return None
        
        # 生成缩略图
        thumbnail_path = await generate_video_thumbnail(first_video)
        if not thumbnail_path:
            log.warning("缩略图生成失败")
            return None
        
        try:
            # 使用独立的会话上传缩略图到Notion
            async with aiohttp.ClientSession() as thumb_sess:
                mime = "image/jpeg"
                sz = thumbnail_path.stat().st_size
                multi = sz > SINGLE_LIMIT
                parts = math.ceil(sz / PART_SIZE) if multi else 1
                
                up = await _create(thumb_sess, thumbnail_path.name, mime, multi, parts)
                fid, url = up["id"], up["upload_url"]
                
                if multi:
                    with open(thumbnail_path, "rb") as f:
                        for i in range(1, parts + 1):
                            await _send(thumb_sess, url, i, f.read(PART_SIZE), mime)
                    await _complete(thumb_sess, fid)
                else:
                    await _send(thumb_sess, url, 1, thumbnail_path.read_bytes(), mime)
                
                log.info(f"缩略图上传成功，文件ID: {fid}")
                return fid
            
        finally:
            # 删除临时缩略图文件
            if thumbnail_path.exists():
                thumbnail_path.unlink()
                log.info(f"已删除临时缩略图文件: {thumbnail_path.name}")
                
    except Exception as e:
        log.error(f"处理缩略图时出错: {e}")
        return None

# ── 核心上传逻辑 ─────────────────────

async def upload_single_file(fp: Path):
    log.info(f"处理单个文件: {fp.name}")
    try:
        mime,_=mimetypes.guess_type(fp); mime=mime or "application/octet-stream"
        sz=fp.stat().st_size; multi=sz>SINGLE_LIMIT
        parts=math.ceil(sz/PART_SIZE) if multi else 1
        
        async with aiohttp.ClientSession() as sess:
            up=await _create(sess,fp.name,mime,multi,parts); fid,url=up["id"],up["upload_url"]
            if multi:
                with open(fp,"rb") as f:
                    for i in range(1,parts+1): await _send(sess,url,i,f.read(PART_SIZE),mime)
                await _complete(sess,fid)
            else: await _send(sess,url,1,fp.read_bytes(),mime)
            
            kind="video" if "video" in mime else "image" if "image" in mime else "file"
            
            # 如果是视频文件，生成缩略图
            thumbnail_id = None
            if "video" in mime:
                thumbnail_id = await upload_thumbnail_for_media([fp])
            
            page = await _create_page(fp.stem, [f_block(kind,fid)], thumbnail_id)
            log.info("✅ 单文件上传成功！ %s", page['url'])
        
        fp.unlink()
        log.info("已删除本地文件 %s", fp.name)
    except Exception as e:
        log.error(f"处理文件 {fp.name} 时出错: {e}", exc_info=True)

async def upload_dir(dirp: Path):
    log.info(f"开始处理文件夹: {dirp.name}")
    try:
        if not dirp.exists():
            log.warning(f"文件夹 {dirp.name} 已不存在，跳过处理")
            return
            
        media = sorted([p for p in dirp.iterdir() if p.is_file()])
        if not media: 
            log.info(f"文件夹 {dirp.name} 为空，删除")
            shutil.rmtree(dirp, ignore_errors=True)
            return
        
        log.info(f"文件夹 {dirp.name} 包含 {len(media)} 个文件: {[f.name for f in media]}")
        
        blocks = []
        first_image_id = None
        async with aiohttp.ClientSession() as sess:
            for fp in media:
                # 添加文件存在性检查
                if not fp.exists():
                    log.warning(f"文件 {fp.name} 不存在，跳过")
                    continue
                    
                log.info(f"处理文件: {fp.name}")
                mime,_=mimetypes.guess_type(fp); mime=mime or "application/octet-stream"
                sz=fp.stat().st_size; multi=sz>SINGLE_LIMIT
                parts=math.ceil(sz/PART_SIZE) if multi else 1
                up=await _create(sess,fp.name,mime,multi,parts); fid,url=up["id"],up["upload_url"]
                if multi:
                    with open(fp,"rb") as f:
                        for i in range(1,parts+1): await _send(sess,url,i,f.read(PART_SIZE),mime)
                    await _complete(sess,fid)
                else: await _send(sess,url,1,fp.read_bytes(),mime)
                
                kind="video" if "video" in mime else "image" if "image" in mime else "file"
                blocks.append(f_block(kind,fid))
                
                # 记录第一张图片的ID用于封面
                if first_image_id is None and "image" in mime:
                    first_image_id = fid
        
        # 如果没有处理任何文件，直接删除目录
        if not blocks:
            log.warning(f"文件夹 {dirp.name} 中没有有效文件，删除目录")
            shutil.rmtree(dirp, ignore_errors=True)
            return
        
        # 如果没有图片作为封面，生成视频缩略图
        if first_image_id is None:
            # 重新获取存在的媒体文件用于生成缩略图
            existing_media = [p for p in media if p.exists()]
            if existing_media:
                thumbnail_id = await upload_thumbnail_for_media(existing_media)
                if thumbnail_id:
                    first_image_id = thumbnail_id
        
        # 使用第一个文件的文件名作为页面标题
        title = media[0].stem if media else dirp.name
        page = await _create_page(title, blocks, first_image_id)
        log.info("✅ 相册上传成功！包含 %d 个文件，页面：%s", len(blocks), page['url'])
        
        shutil.rmtree(dirp, ignore_errors=True)
        log.info("已删除目录及所有文件: %s", dirp.name)
    except Exception as e:
        log.error(f"处理目录 {dirp.name} 时出错: {e}", exc_info=True)
        raise  # 重新抛出异常供重试机制处理

async def upload_dir_with_retry(dirp: Path, max_retries=2):
    """带重试机制的目录上传函数"""
    dir_name = str(dirp)
    
    for attempt in range(max_retries + 1):
        try:
            await upload_dir(dirp)
            return  # 成功则返回
        except Exception as e:
            if attempt < max_retries:
                log.warning(f"处理目录 {dirp.name} 失败，第 {attempt + 1} 次重试... 错误: {e}")
                await asyncio.sleep(5)  # 等待5秒后重试
            else:
                log.error(f"处理目录 {dirp.name} 失败，已达到最大重试次数，跳过。错误: {e}")
                # 即使失败也要清理目录和处理锁
                if dirp.exists():
                    shutil.rmtree(dirp, ignore_errors=True)
                    log.info(f"已删除目录: {dirp.name}")
        finally:
            # 无论成功失败都要移除处理锁
            if dir_name in processing_dirs:
                processing_dirs.remove(dir_name)
                log.debug(f"已移除目录 {dirp.name} 的处理锁")

def schedule_dir_processing(dirp: Path, loop):
    """延时处理目录，确保所有文件都下载完成"""
    dir_name = str(dirp)
    
    # 检查目录是否已经在处理中
    if dir_name in processing_dirs:
        log.debug(f"目录 {dirp.name} 已在处理中，跳过")
        return
    
    # 取消之前的计时器（如果有的话）
    if dir_name in pending_dirs:
        pending_dirs[dir_name].cancel()
        log.debug(f"取消之前的处理计划: {dirp.name}")
    
    # 创建新的计时器
    def process_dir():
        if dirp.exists():
            # 添加到处理中的目录集合
            processing_dirs.add(dir_name)
            log.info(f"文件夹 {dirp.name} 稳定 {STABLE_DELAY} 秒，开始处理")
            loop.call_soon_threadsafe(asyncio.create_task, upload_dir_with_retry(dirp))
        if dir_name in pending_dirs:
            del pending_dirs[dir_name]
    
    timer = Timer(STABLE_DELAY, process_dir)
    pending_dirs[dir_name] = timer
    timer.start()
    log.info(f"文件夹 {dirp.name} 计划在 {STABLE_DELAY} 秒后处理")

# ── Watchdog (优化版本) ──────────────────────────
class StableWatcher(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop
    
    def on_created(self, ev):
        path = Path(ev.src_path)
        if path.name.startswith('.'): 
            return  # 忽略隐藏文件
            
        if ev.is_directory:
            # 目录创建 - 安排延时处理
            log.info("检测到新目录 %s", path.name)
            schedule_dir_processing(path, self.loop)
        else:
            # 检查是根目录文件还是子目录文件
            if path.parent == WATCH_DIR:
                log.info("检测到根目录单文件 %s，将单独处理", path.name)
                Timer(1.0, lambda: self.loop.call_soon_threadsafe(asyncio.create_task, upload_single_file(path))).start()
            else:
                # 子目录中的文件 - 重新安排该目录的处理
                parent_dir = path.parent
                if parent_dir.parent == WATCH_DIR:  # 确保是我们监控的直接子目录
                    log.info("检测到目录 %s 中新文件 %s，重新安排处理", parent_dir.name, path.name)
                    schedule_dir_processing(parent_dir, self.loop)
    
    def on_modified(self, ev):
        """文件修改（写入完成）时也触发重新调度"""
        if ev.is_directory:
            return
            
        path = Path(ev.src_path)
        if path.name.startswith('.'):
            return
            
        # 如果是子目录中的文件被修改，重新调度
        if path.parent != WATCH_DIR and path.parent.parent == WATCH_DIR:
            log.debug("文件 %s 修改，重新安排目录 %s 处理", path.name, path.parent.name)
            schedule_dir_processing(path.parent, self.loop)

async def main():
    WATCH_DIR.mkdir(exist_ok=True)
    log.info("启动稳定检测上传器，监视: %s", WATCH_DIR)
    log.info("逻辑：根目录单文件→单页面，根目录文件夹→等待稳定后合并页面")
    log.info("稳定延时: %s 秒", STABLE_DELAY)
    
    loop = asyncio.get_running_loop()
    event_handler = StableWatcher(loop)
    
    obs = Observer()
    # 使用递归监控来检测子目录中的文件变化
    obs.schedule(event_handler, str(WATCH_DIR), recursive=True)
    obs.start()
    
    try: 
        await asyncio.Event().wait()
    finally: 
        obs.stop(); obs.join()
        # 清理待处理的计时器
        for timer in pending_dirs.values():
            timer.cancel()
        # 清理处理锁
        processing_dirs.clear()

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt: 
        log.info("程序被手动中断")