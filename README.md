# AI GitHub Code Review Platform 🤖🚀

AI GitHub Code Review Platform là một hệ thống tự động nhận diện và phân tích các Pull Request (PR) từ GitHub bằng Trí tuệ Nhân tạo (OpenAI GPT), đưa ra khuyến nghị kiểm thử, tự động nhận xét (comment) trực tiếp vào PR và hiển thị thống kê chi tiết trên một Dashboard trực quan.

Hệ thống được thiết kế theo dạng monorepo, sẵn sàng cho môi trường production, tích hợp hàng đợi công việc Celery/Redis bất đồng bộ, hệ quản trị cơ sở dữ liệu PostgreSQL và được đóng gói hoàn toàn bằng Docker Compose.

---

## 1. Kiến Trúc Tổng Thể

Hệ thống bao gồm các thành phần cốt lõi:
- **FastAPI Web Server:** Nhận Webhook từ GitHub, kiểm tra tính hợp lệ của chữ ký bảo mật, quản lý metadata của Repository, PR và phân phối các API cho Dashboard.
- **Celery Worker & Redis Queue:** Nhận nhiệm vụ phân tích bất đồng bộ để tránh nghẽn luồng HTTP Webhook.
- **AI Review Service:** Chịu trách nhiệm chia tách mã nguồn khác biệt (diff) thành các phần nhỏ nếu quá giới hạn ký tự (`MAX_DIFF_CHARS`), gửi phân tích tới OpenAI và tổng hợp kết quả thành một DTO có cấu trúc.
- **React Dashboard (Ant Design & TypeScript):** Hiển thị trực quan trạng thái, thống kê các review lỗi bảo mật, bug tiềm ẩn, code smell và hiệu năng.
- **Nginx Reverse Proxy:** Định tuyến phân luồng lưu lượng truy cập frontend và backend thông qua cổng 80 chuẩn.

---

## 2. Luồng Hoạt Động (Flow)

```
Developer tạo/cập nhật PR 
   ↓
GitHub gửi Webhook chứa mã SHA256 về Backend thông qua Nginx
   ↓
Backend xác thực chữ ký (GitHub Webhook Secret) & Lưu PR info vào PostgreSQL
   ↓
Backend tạo Review Job ở trạng thái 'pending' & Đẩy Job ID vào Redis Queue
   ↓
Celery Worker đón Job ID -> Chuyển trạng thái sang 'running'
   ↓
Worker gọi GitHub API lấy Diff -> Gửi Diff sang OpenAI GPT
   ↓
OpenAI trả về JSON (Bug, Security, Smells, Perf, Test cases, Recommendation)
   ↓
Worker định dạng thành Markdown tuyệt đẹp -> Post Comment trực tiếp lên PR
   ↓
Worker lưu kết quả chi tiết vào PostgreSQL -> Chuyển trạng thái sang 'success'
   ↓
Dashboard cập nhật hiển thị kết quả review trực quan theo thời gian thực
```

---

## 3. Cách Chạy Local Bằng Docker Compose

### Bước 1: Thiết lập file môi trường `.env`
Tạo file `.env` tại thư mục root hoặc thư mục `backend/` dựa trên `.env.example`:

```bash
# Nhân bản và chỉnh sửa file
cp backend/.env.example .env
```

Điền các thông số cấu hình tối thiểu:
```env
APP_ENV=development
OPENAI_API_KEY=sk-proj-yourOpenAiKeyHere...
GITHUB_TOKEN=ghp_yourGitHubTokenHere...
GITHUB_WEBHOOK_SECRET=your_super_secret_webhook_key
```
> **Lưu ý:** Nếu không có `OPENAI_API_KEY`, hệ thống sẽ tự động chạy ở chế độ **MOCK** (tự tạo dữ liệu review giả lập đẹp mắt để bạn thử nghiệm đầy đủ tính năng).

### Bước 2: Khởi động hệ thống
Khởi chạy toàn bộ container stack bằng Docker Compose:

```bash
docker compose up --build
```

Sau khi khởi chạy hoàn tất:
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000) (hoặc trực tiếp qua [http://localhost](http://localhost) nhờ Nginx)
- **Backend API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs) (hoặc [http://localhost/docs](http://localhost/docs))
- **PostgreSQL Database:** cổng `5432` trên localhost
- **Redis Queue:** cổng `6379` trên localhost

---

## 4. Hướng Dẫn Tạo Token & Cấu Hình Webhook

### 4.1. Cách tạo OpenAI API Key
1. Truy cập [OpenAI Platform](https://platform.openai.com/).
2. Đăng nhập và đi tới mục **API Keys**.
3. Chọn **Create new secret key**, đặt tên và lưu lại khoá (dạng `sk-...`).
4. Dán khoá này vào biến `OPENAI_API_KEY` trong `.env`.

### 4.2. Cách tạo GitHub Token (Personal Access Token - PAT)
Token này cho phép bot có thể comment trực tiếp kết quả review vào Pull Request của bạn.
1. Truy cập tài khoản GitHub cá nhân -> **Settings** -> **Developer settings** -> **Personal Access Tokens** -> **Tokens (classic)**.
2. Nhấn **Generate new token (classic)**.
3. Tích chọn các quyền sau:
   - `repo` (Toàn bộ quyền truy cập repository riêng tư và công khai).
   - `write:discussion` hoặc `pull_requests` (để đăng bình luận).
4. Nhấn **Generate token** và sao chép mã token.
5. Dán mã này vào biến `GITHUB_TOKEN` trong `.env`.

### 4.3. Cách cấu hình GitHub Webhook trên Repository
Để GitHub gửi dữ liệu PR về hệ thống của bạn mỗi khi có sự kiện:
1. Vào trang GitHub Repository của bạn.
2. Chọn **Settings** -> **Webhooks** -> **Add webhook**.
3. Nhập các thông số sau:
   - **Payload URL:** Địa chỉ API Webhook của bạn. Ví dụ: `https://your-domain.com/api/webhooks/github` (Nếu test local, bạn cần dùng công cụ như **ngrok** hoặc **Localtunnel** để forward cổng 80 ra internet công khai).
   - **Content type:** `application/json`
   - **Secret:** Nhập một chuỗi ký tự tự chọn (Ví dụ: `my_webhook_secret_123`). Chuỗi này phải khớp chính xác với `GITHUB_WEBHOOK_SECRET` trong `.env`.
   - **Which events would you like to trigger this webhook?:** Chọn **Let me select individual events**, tích chọn **Pull requests** và bỏ chọn các mục khác.
   - Tích chọn **Active**.
4. Nhấn **Add webhook**.

---

## 5. Cách Test Hệ Thống Bằng Pull Request Thật

1. Khởi động hệ thống local và chạy ngrok để phơi bày cổng 80:
   ```bash
   ngrok http 80
   ```
2. Lấy URL công khai ngrok cấp (ví dụ `https://a1b2-34-56-78.ngrok-free.app`) và cấu hình webhook GitHub thành:
   `https://a1b2-34-56-78.ngrok-free.app/api/webhooks/github`
3. Trên GitHub Repository, tạo một nhánh mới, chỉnh sửa một đoạn code (ví dụ viết thiếu xử lý lỗi hoặc hardcode mật khẩu để AI có thể phát hiện).
4. Tạo Pull Request từ nhánh đó vào `main`.
5. GitHub sẽ lập tức kích hoạt Webhook. Bạn có thể theo dõi logs của container `review_backend` và `review_celery_worker` để xem tiến trình xử lý.
6. Sau khoảng vài giây, hãy kiểm tra phần **Conversation** của Pull Request trên GitHub. Bạn sẽ thấy một comment chi tiết dạng bảng từ Bot của bạn.
7. Mở Dashboard tại `http://localhost:3000` để xem bản phân tích chi tiết bằng đồ hoạ.

---

## 6. Hướng Dẫn Triển Khai Lên VPS (Production-Ready)

1. Sao chép toàn bộ mã nguồn của dự án lên VPS (thông qua Git).
2. Tạo file `.env` tại root và điền đầy đủ các khoá bí mật thực tế.
3. Chạy lệnh Docker Compose với file cấu hình production để ẩn các cổng debug:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```
4. Đảm bảo cấu hình một chứng chỉ SSL (Let's Encrypt) trên VPS để bảo vệ webhook và dữ liệu truyền tải qua HTTPS.

---

## 7. Các Lỗi Thường Gặp & Cách Khắc Phục (Troubleshooting)

- **Lỗi `ModuleNotFoundError: No module named 'app'` khi chạy test:**
  - *Khắc phục:* Chạy test bằng lệnh `python -m pytest tests/` từ thư mục `backend/` thay vì chạy `pytest` trực tiếp.
- **Không nhận được Webhook trên Local:**
  - *Khắc phục:* Kiểm tra xem URL Webhook trên GitHub đã được cập nhật đúng địa chỉ ngrok chưa. Đảm bảo trạng thái Webhook trên GitHub hiển thị tích xanh (Success 200).
- **Lỗi `Signature verification failed`:**
  - *Khắc phục:* Đảm bảo chuỗi `GITHUB_WEBHOOK_SECRET` trong file `.env` khớp 100% với ô **Secret** đã cấu hình trên Webhook settings của GitHub.
- **Celery Worker không nhận Task:**
  - *Khắc phục:* Đảm bảo container Redis đang chạy tốt. Kiểm tra logs bằng lệnh `docker compose logs celery_worker`.

---

## 8. Hướng Phát Triển Tiếp Theo

- Tích hợp thêm các mô hình LLM nội bộ (Local Models) thông qua Ollama để bảo mật tuyệt đối mã nguồn doanh nghiệp.
- Hỗ trợ review chuyên sâu đa file (Multi-file Contextual Review) thay vì chỉ phân tích diff đơn lẻ.
- Tích hợp hệ thống phân tích bảo mật chuyên sâu (SAST/DAST) dạng Docker-in-Docker.
