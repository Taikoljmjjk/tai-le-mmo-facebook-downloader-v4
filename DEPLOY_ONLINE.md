# DEPLOY ONLINE — V3

## Cách đơn giản nhất: Render (frontend + backend cùng một dịch vụ)
Source đã được cấu hình để Render chạy Docker, cài FFmpeg và phục vụ luôn giao diện web.

### 1. Đưa source lên GitHub
- Tạo repository mới, ví dụ: `tai-le-mmo-facebook-downloader`
- Upload TOÀN BỘ file trong thư mục project này lên repository.

### 2. Deploy Render
- Đăng nhập Render.
- New > Blueprint (nếu Render nhận `render.yaml`) hoặc New > Web Service.
- Kết nối repository GitHub.
- Nếu tạo Web Service thủ công:
  - Runtime: Docker
  - Plan: Free (để thử nghiệm)
  - Health Check Path: `/api/health`
- Deploy.

Render sẽ cấp địa chỉ dạng:
`https://tai-le-mmo-facebook-downloader.onrender.com`

Không cần Cloudflare Pages ở V3 vì FastAPI phục vụ luôn giao diện. Cách này tránh CORS/API URL và dễ chạy nhất.

### 3. Kiểm tra
Mở:
- `/api/health` -> phải thấy `{"ok":true}`
- Trang chủ -> dán một URL video Facebook công khai và bấm TẢI VIDEO.

### 4. Cloudflare / tên miền riêng (tùy chọn)
Khi app chạy ổn, có thể gắn custom domain vào Render và quản lý DNS qua Cloudflare.
Không cần mua domain để test vì Render đã cấp subdomain `onrender.com`.

## Lưu ý về gói miễn phí
Gói Render Free phù hợp để thử nghiệm. Nó có thể ngủ sau thời gian không có truy cập, lần mở tiếp theo có thể mất thời gian khởi động. Video lớn/ghép FFmpeg có thể vượt tài nguyên của free tier.

## Bảo mật / vận hành
- Chỉ chấp nhận hostname Facebook trong backend.
- Không hỗ trợ vượt đăng nhập, nội dung riêng tư hoặc DRM.
- File tải được tạo trong thư mục tạm và xóa sau khi stream.
- Trước khi dùng công khai quy mô lớn, nên bổ sung reverse-proxy rate limiting và giới hạn kích thước/thời lượng video.
