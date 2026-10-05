# TÀI LÊ MMO — Facebook Video Downloader

Website tải video/Reels Facebook công khai theo chất lượng khả dụng.

## Chạy nhanh trên Windows
1. Cài Python 3.11+ và FFmpeg (thêm FFmpeg vào PATH).
2. Giải nén source.
3. Bấm `start_windows.bat`.
4. Trình duyệt mở `http://127.0.0.1:8000`.

## Chạy bằng Docker / VPS
```bash
docker compose up -d --build
```
Mở `http://IP-VPS:8000`.

## Production
Đặt Nginx/Caddy + HTTPS phía trước cổng 8000. Nên bổ sung rate-limit ở reverse proxy.
Cập nhật yt-dlp định kỳ:
```bash
pip install -U yt-dlp
```

## API
- `GET /api/info?url=...` — phân tích metadata/chất lượng.
- `GET /api/download?url=...&height=1080` — tải và tự ghép audio/video bằng FFmpeg khi cần.
- `GET /api/health` — health check.

## Lưu ý
Chỉ dùng với nội dung công khai mà người dùng có quyền tải/lưu. Không có cơ chế vượt đăng nhập, video riêng tư hay DRM.
Facebook có thể thay đổi cấu trúc phân phối bất kỳ lúc nào; khi extractor lỗi, cập nhật yt-dlp trước.


## V2 branding
- Logo/avatar: ảnh người dùng cung cấp.
- Hotline: 0394 342 601 (`tel:` clickable).
- Giao diện landing page công nghệ xanh navy/neon, responsive.
