from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from urllib.parse import urlparse
import yt_dlp, tempfile, os, re, shutil, zipfile, json

BASE = Path(__file__).resolve().parent
app = FastAPI(title="TÀI LÊ MMO - Facebook Downloader V4")
allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=["*"] if "*" in allowed_origins else allowed_origins,
                   allow_credentials=False, allow_methods=["GET","POST","OPTIONS"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE/"static"), name="static")
ALLOWED = {"facebook.com","www.facebook.com","m.facebook.com","fb.watch","web.facebook.com"}

def validate_url(url):
    try:
        p=urlparse(url.strip()); host=(p.hostname or "").lower()
        if p.scheme not in {"http","https"} or (host not in ALLOWED and not host.endswith(".facebook.com")): raise ValueError()
        return url.strip()
    except: raise HTTPException(400,"Liên kết Facebook không hợp lệ.")

def info_extract(url, flat=False, playlistend=None):
    opts={"quiet":True,"no_warnings":True,"skip_download":True,"noplaylist":not flat,"socket_timeout":30}
    if flat:
        opts.update({"extract_flat":"in_playlist","yes_playlist":True})
        if playlistend: opts["playlistend"]=playlistend
    with yt_dlp.YoutubeDL(opts) as y: return y.extract_info(url,download=False)

@app.get("/")
def home(): return FileResponse(BASE/"static"/"index.html")

@app.get("/api/health")
def health(): return {"ok":True,"version":"4.0"}

@app.get("/api/info")
def info(url:str=Query(...,min_length=8,max_length=2000)):
    url=validate_url(url)
    try: d=info_extract(url)
    except Exception as e:
        if "login" in str(e).lower() or "cookies" in str(e).lower():
            raise HTTPException(422,"Video yêu cầu đăng nhập/quyền truy cập. Chỉ hỗ trợ nội dung công khai.")
        raise HTTPException(422,"Không thể phân tích video công khai này.")
    fs=[]; seen=set()
    for f in d.get("formats") or []:
        if f.get("vcodec") in (None,"none") or not f.get("height"): continue
        k=(f.get("height"),f.get("ext"))
        if k in seen: continue
        seen.add(k); fs.append({"format_id":f.get("format_id"),"height":f["height"],"quality":f'{f["height"]}p',
          "ext":f.get("ext") or "mp4","has_audio":f.get("acodec") not in (None,"none"),
          "filesize":f.get("filesize") or f.get("filesize_approx")})
    fs.sort(key=lambda x:x["height"],reverse=True)
    return {"id":d.get("id"),"title":d.get("title") or "Facebook Video","thumbnail":d.get("thumbnail"),
            "duration":d.get("duration"),"uploader":d.get("uploader") or d.get("channel"),"formats":fs[:12]}

def download_one(url,height,tmp):
    selector=f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
    opts={"format":selector,"outtmpl":str(tmp/"%(title).70s-%(id)s.%(ext)s"),"merge_output_format":"mp4",
          "noplaylist":True,"quiet":True,"no_warnings":True,"restrictfilenames":True}
    before=set(tmp.glob("*"))
    with yt_dlp.YoutubeDL(opts) as y:
        y.extract_info(url,download=True)
    after=[p for p in tmp.glob("*") if p not in before and p.is_file()]
    if not after: raise RuntimeError("Không tạo được file")
    return max(after,key=lambda p:p.stat().st_mtime)

@app.get("/api/download")
def download(url:str,height:int=1080):
    url=validate_url(url)
    if height<144 or height>4320: raise HTTPException(400,"Chất lượng không hợp lệ.")
    tmp=Path(tempfile.mkdtemp(prefix="fbdown_"))
    try: path=download_one(url,height,tmp)
    except Exception:
        shutil.rmtree(tmp,ignore_errors=True); raise HTTPException(422,"Tải video thất bại.")
    safe=re.sub(r'[^A-Za-z0-9._-]+','_',path.name)[:140]
    def stream():
        try:
            with open(path,"rb") as f:
                while True:
                    c=f.read(1024*1024)
                    if not c: break
                    yield c
        finally: shutil.rmtree(tmp,ignore_errors=True)
    return StreamingResponse(stream(),media_type="application/octet-stream",
        headers={"Content-Disposition":f'attachment; filename="{safe}"'})

@app.get("/api/channel")
def channel(url:str=Query(...,min_length=8,max_length=2000),limit:int=20):
    url=validate_url(url); limit=max(1,min(limit,100))
    try: d=info_extract(url,flat=True,playlistend=limit)
    except Exception:
        raise HTTPException(422,"Không thể quét Page/kênh này. Hãy dùng URL trang Video/Reels công khai của Page.")
    entries=d.get("entries") or []
    out=[]
    for e in entries:
        if not e: continue
        webpage=e.get("webpage_url") or e.get("url")
        if webpage and not str(webpage).startswith("http"):
            vid=e.get("id"); webpage=f"https://www.facebook.com/watch/?v={vid}" if vid else None
        if not webpage: continue
        out.append({"id":e.get("id"),"title":e.get("title") or "Facebook Video",
                    "url":webpage,"thumbnail":e.get("thumbnail"),"duration":e.get("duration")})
    return {"title":d.get("title") or "Facebook Page","count":len(out),"videos":out[:limit]}

@app.post("/api/batch-download")
async def batch_download(payload:dict):
    urls=payload.get("urls") or []; height=int(payload.get("height") or 720)
    # Conservative server-side cap for free hosting.
    urls=[validate_url(str(x)) for x in urls[:20]]
    if not urls: raise HTTPException(400,"Chưa chọn video.")
    if height<144 or height>2160: raise HTTPException(400,"Chất lượng không hợp lệ.")
    tmp=Path(tempfile.mkdtemp(prefix="fbbatch_")); successes=[]
    try:
        for i,u in enumerate(urls,1):
            try:
                p=download_one(u,height,tmp)
                target=tmp/f"{i:03d}_{p.name}"
                if p!=target: p.rename(target)
                successes.append(target)
            except Exception: pass
        if not successes: raise RuntimeError()
        zp=tmp/"TAI_LE_MMO_FACEBOOK_BATCH.zip"
        with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED,allowZip64=True) as z:
            for p in successes: z.write(p,p.name)
            z.writestr("README.txt",f"Tải thành công {len(successes)}/{len(urls)} video. TAI LE MMO - CHO DI LA CON MAI.")
        def stream():
            try:
                with open(zp,"rb") as f:
                    while True:
                        c=f.read(1024*1024)
                        if not c: break
                        yield c
            finally: shutil.rmtree(tmp,ignore_errors=True)
        return StreamingResponse(stream(),media_type="application/zip",
            headers={"Content-Disposition":'attachment; filename="TAI_LE_MMO_FACEBOOK_BATCH.zip"',
                     "X-Downloaded-Count":str(len(successes))})
    except Exception:
        shutil.rmtree(tmp,ignore_errors=True)
        raise HTTPException(422,"Không tải được danh sách đã chọn. Hãy giảm số lượng hoặc thử lại.")
