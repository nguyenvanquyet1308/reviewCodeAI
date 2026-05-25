# HƯỚNG DẪN TRIỂN KHAI HỆ THỐNG LÊN PRODUCTION VPS (TỪ A -> Z) 🚀🤖

Tài liệu này hướng dẫn chi tiết cách triển khai hệ thống **AI GitHub Code Review Platform** lên một máy chủ ảo (VPS) mới mua chạy hệ điều hành **Ubuntu 22.04 LTS** hoặc **Ubuntu 24.04 LTS**.

---

## MỤC LỤC
1. [Yêu cầu hệ thống tối thiểu](#1-yêu-cầu-hệ-thống-tối-thiểu)
2. [Bước 1: Kết nối VPS & Cập nhật hệ thống](#bước-1-kết-nối-vps--cập-nhật-hệ-thống)
3. [Bước 2: Cài đặt Docker & Docker Compose](#bước-2-cài-đặt-docker--docker-compose)
4. [Bước 3: Tải mã nguồn lên VPS](#bước-3-tải-mã-nguồn-lên-vps)
5. [Bước 4: Cấu hình biến môi trường (`.env`)](#bước-4-cấu-hình-biến-môi-trường-env)
6. [Bước 5: Cấu hình Nginx & SSL (HTTPS) trên Host (Khuyên dùng)](#bước-5-cấu-hình-nginx--ssl-https-trên-host-khuyên-dùng)
7. [Bước 6: Khởi chạy hệ thống bằng Docker Compose](#bước-6-khởi-chạy-hệ-thống-bằng-docker-compose)
8. [Bước 7: Tạo Webhook trên GitHub Repository](#bước-7-tạo-webhook-trên-github-repository)
9. [Bước 8: Quản lý & Giám sát hệ thống (Troubleshooting)](#bước-8-quản-lý--giám-sát-hệ-thống-troubleshooting)
10. [Bước 9: Thiết lập Tự Động Triển Khai (CI/CD) Qua GitHub Actions](#bước-9-thiết-lập-tự-động-triển-khai-cicd-qua-github-actions)

---

## 1. Yêu cầu hệ thống tối thiểu
*   **Hệ điều hành:** Ubuntu 20.04 / 22.04 / 24.04 LTS (x86_64)
*   **Cấu hình phần cứng:**
    *   *Tối thiểu (Demo):* 1 vCPU, 2 GB RAM, 25 GB SSD.
    *   *Khuyên dùng (Production):* 2 vCPU, 4 GB RAM (hoặc tạo thêm phân vùng SWAP nếu RAM 2GB để tránh tràn RAM khi build React).
*   **Tên miền (Domain Name):** Bạn cần chuẩn bị 1 tên miền (ví dụ: `review.yourdomain.com`) và trỏ bản ghi **A** về địa chỉ IP Public của VPS.
    > [!IMPORTANT]
    > **Tại sao cần tên miền & SSL?** GitHub yêu cầu endpoint nhận Webhook phải sử dụng giao thức bảo mật HTTPS công khai. Nếu chỉ dùng IP hoặc HTTP, webhook sẽ không hoạt động hoặc không an toàn.

---

## Bước 1: Kết nối VPS & Cập nhật hệ thống

Mở Terminal trên máy tính cá nhân của bạn (macOS/Linux) hoặc PowerShell/Git Bash (Windows) và chạy lệnh:

```bash
# Thay thế root và địa chỉ IP bằng thông tin VPS của bạn
ssh root@your_vps_ip
```

Sau khi đăng nhập thành công, hãy cập nhật tất cả gói phần mềm hệ thống lên phiên bản mới nhất:

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Bước 2: Cài đặt Docker & Docker Compose

Chạy chuỗi lệnh sau để cài đặt Docker Engine và Docker Compose plugin chính thức từ Docker Repository:

```bash
# 1. Cài đặt các gói phụ thuộc cần thiết
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 2. Thêm khóa GPG chính thức của Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. Thiết lập Docker Repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Cài đặt Docker & Docker Compose
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. Kiểm tra cài đặt thành công
docker --version
docker compose version
```

Đảm bảo Docker tự động khởi động cùng hệ thống:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## Bước 3: Tải mã nguồn lên VPS

Bạn có hai cách để đưa mã nguồn lên VPS:

### Cách A: Nhân bản qua Git (Khuyên dùng)
Nếu code của bạn đã được đẩy lên GitHub/GitLab ở dạng Private hoặc Public:
```bash
# Cài đặt git nếu chưa có
sudo apt install git -y

# Clone repo về thư mục /var/www hoặc thư mục home
cd /var/www
git clone <URL_KHO_MÃ_NGUỒN_CỦA_BẠN> review-app
cd review-app
```

### Cách B: Upload thủ công bằng SCP/SFTP
Sử dụng công cụ như MobaXterm, FileZilla hoặc câu lệnh Terminal để nén và gửi thư mục dự án lên VPS.

---

## Bước 4: Cấu hình biến môi trường (`.env`)

Sao chép file cấu hình mẫu `.env.example` thành file `.env` chính thức ở thư mục gốc của dự án:

```bash
cp .env.example .env
```

Sử dụng trình soạn thảo `nano` để chỉnh sửa cấu hình:

```bash
nano .env
```

Hãy thay đổi và điền đầy đủ các thông tin quan trọng dưới đây:

```env
# 1. Môi trường chạy
APP_ENV=production
APP_NAME="AI GitHub Code Review Platform"

# 2. CẤU HÌNH DATABASE POSTGRESQL (Thay đổi để bảo mật)
# BẮT BUỘC thay đổi user và mật khẩu mặc định thành chuỗi phức tạp
POSTGRES_USER=app_db_admin
POSTGRES_PASSWORD=MatKhauBaoMatCuaBan123_#@!
POSTGRES_DB=ai_review

# 3. REDIS CONNECTION (Để mặc định khi chạy Docker Compose)
REDIS_URL=redis://redis:6379/0

# 4. CẤU HÌNH OPENAI API KEY (Bắt buộc)
# Tạo khoá tại: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxx...
OPENAI_MODEL=gpt-4o-mini

# 5. CẤU HÌNH GITHUB (Bắt buộc để Bot phản hồi lên PR)
# Token classic có quyền 'repo' để tạo comment
GITHUB_TOKEN=ghp_xxxxxxxx... 
# Secret webhook để kiểm tra tính toàn vẹn (ví dụ: chuỗi ký tự ngẫu nhiên)
GITHUB_WEBHOOK_SECRET=your_super_secret_string_here

# 6. THÔNG SỐ CODE REVIEW
REVIEW_DRAFT_PR=false
MAX_DIFF_CHARS=50000
```

> **Mẹo sử dụng Nano:** Nhấn `Ctrl + O` -> `Enter` để lưu file, và `Ctrl + X` để thoát trình soạn thảo.

---

## Bước 5: Cấu hình Nginx & SSL (HTTPS) trên Host (Khuyên dùng)

Để bảo vệ đường truyền dữ liệu và tuân thủ yêu cầu Webhook của GitHub, chúng ta sẽ cấu hình một Web Server Nginx trực tiếp trên hệ điều hành VPS để quản lý chứng chỉ SSL của Let's Encrypt và chuyển hướng request vào hệ thống Docker Compose.

### 5.1. Cài đặt Nginx và Certbot trên VPS
Chạy lệnh sau trên VPS:

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

### 5.2. Tạo File Cấu hình Host Nginx
Tạo một file cấu hình ảo (Virtual Host) cho tên miền của bạn:

```bash
sudo nano /etc/nginx/sites-available/codereview
```

Dán nội dung cấu hình sau (thay đổi `review.yourdomain.com` thành tên miền thực tế của bạn):

```nginx
server {
    listen 80;
    server_name review.yourdomain.com;

    # Tăng kích thước payload cho phép upload nếu cần
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8080; # Chuyển tiếp tới cổng 8080 của Docker Compose
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Hỗ trợ Websocket nếu có
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Lưu và kích hoạt cấu hình:

```bash
# Tạo liên kết tượng trưng (symlink)
sudo ln -s /etc/nginx/sites-available/codereview /etc/nginx/sites-enabled/

# Xóa cấu hình mặc định của Nginx nếu không dùng tới
sudo rm -f /etc/nginx/sites-enabled/default

# Kiểm tra cú pháp cấu hình Nginx
sudo nginx -t

# Khởi động lại Nginx
sudo systemctl restart nginx
```

### 5.3. Yêu cầu chứng chỉ SSL (HTTPS) từ Let's Encrypt
Chạy công cụ Certbot để tự động lấy chứng chỉ và cấu hình tự chuyển hướng HTTP sang HTTPS:

```bash
# Thay thế bằng tên miền của bạn
sudo certbot --nginx -d review.yourdomain.com
```

Trong quá trình cài đặt, Certbot sẽ hỏi Email của bạn và yêu cầu đồng ý với các điều khoản. Hãy làm theo hướng dẫn trên màn hình.
Sau khi chạy xong, Certbot sẽ cấu hình tự động gia hạn chứng chỉ (mỗi 90 ngày) thông qua một systemd timer. Bạn có thể kiểm tra gia hạn tự động bằng:
```bash
sudo certbot renew --dry-run
```

---

## Bước 6: Khởi chạy hệ thống bằng Docker Compose

Bởi vì chúng ta đã dùng Nginx trên Host VPS để nhận cổng `80/443` công khai, chúng ta cần cấu hình để Docker Nginx chạy ở cổng nội bộ `8080` của VPS nhằm tránh xung đột cổng.

### 6.1. Kiểm tra cấu hình `docker-compose.prod.yml`
File `docker-compose.prod.yml` ở thư mục gốc **đã được cấu hình sẵn** để chỉ lắng nghe cục bộ trên VPS ở cổng `8080` (được bảo mật đằng sau Nginx Host), tránh xung đột cổng `80` và `443` công khai.

Bạn có thể kiểm tra nội dung file bằng lệnh:

```bash
cat docker-compose.prod.yml
```

Nội dung phần cấu hình cổng của dịch vụ `nginx` đã được thiết lập như sau:

```yaml
  nginx:
    restart: unless-stopped
    # Bind to localhost:8080 to proxy requests from the host Nginx with SSL
    ports:
      - "127.0.0.1:8080:80"
```

### 6.2. Khởi chạy Docker Container Stack
Build và khởi chạy toàn bộ dịch vụ ở chế độ chạy ngầm (detached mode):

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 6.3. Kiểm tra các dịch vụ
Kiểm tra trạng thái các container đang chạy:

```bash
docker compose ps
```

Nếu tất cả container đều hiển thị trạng thái `Up`, hệ thống đã chạy thành công!
Bạn có thể truy cập tên miền `https://review.yourdomain.com` trên trình duyệt để kiểm tra giao diện React Dashboard.

---

## Bước 7: Tạo Webhook trên GitHub Repository

Để hệ thống tự động nhận diện và gửi phân tích PR, bạn cần tạo webhook trên repository của mình:

1.  Vào trang GitHub Repository của bạn -> Chọn **Settings** (Cài đặt) ở thanh menu trên cùng.
2.  Chọn **Webhooks** ở menu bên trái -> Nhấn nút **Add webhook** (Thêm webhook).
3.  Cấu hình chi tiết các trường như sau:
    *   **Payload URL:** Địa chỉ API Webhook của bạn. Ví dụ: `https://review.yourdomain.com/api/webhooks/github` (lưu ý có `/api/webhooks/github` ở cuối).
    *   **Content type:** Chọn `application/json` (Bắt buộc).
    *   **Secret:** Nhập chính xác chuỗi ký tự bạn đã cấu hình tại biến `GITHUB_WEBHOOK_SECRET` trong file `.env`.
    *   **Which events would you like to trigger this webhook?:**
        *   Chọn **Let me select individual events** (Để tôi tự chọn sự kiện).
        *   Tích chọn duy nhất **Pull requests**.
        *   Bỏ chọn tất cả các mục khác bao gồm cả `Pushes`.
    *   **Active:** Tích chọn (để kích hoạt webhook).
4.  Nhấn nút **Add webhook** để hoàn tất.

GitHub sẽ gửi thử một request `ping` đến VPS của bạn. Hãy tải lại trang để kiểm tra xem webhook có dấu tích xanh (Success - Mã HTTP 200 hoặc 202) hay không.

---

## Bước 8: Quản lý & Giám sát hệ thống (Troubleshooting)

### 8.1. Kiểm tra logs ứng dụng
Khi xảy ra lỗi hoặc bạn muốn kiểm tra xem Bot có đang phân tích code hay không, hãy xem logs của các container:

```bash
# Xem logs của toàn bộ hệ thống theo thời gian thực
docker compose logs -f

# Xem logs của riêng Backend FastAPI
docker compose logs -f backend

# Xem logs của riêng Celery Worker (nơi gọi OpenAI API và comment lên GitHub)
docker compose logs -f celery_worker
```

### 8.2. Cập nhật mã nguồn mới (CI/CD thủ công)
Khi bạn thực hiện thay đổi code ở local và đẩy lên GitHub, muốn cập nhật code mới trên VPS:

```bash
# 1. Kéo code mới về
git pull origin main

# 2. Build lại và restart container stack mà không làm gián đoạn database volume
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 8.3. Khởi động lại hệ thống
```bash
# Dừng hệ thống
docker compose down

# Khởi chạy lại hệ thống
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 8.4. Sao lưu và khôi phục cơ sở dữ liệu PostgreSQL
Để sao lưu dữ liệu trong container Postgres:

```bash
# Sao lưu dữ liệu ra file backup.sql trên VPS
docker exec -t review_postgres pg_dumpall -c -U app_db_admin > backup.sql
```

Để khôi phục dữ liệu từ file backup:

```bash
# Khôi phục dữ liệu từ file backup.sql vào database
cat backup.sql | docker exec -i review_postgres psql -U app_db_admin -d ai_review
```

---

## Bước 9: Thiết lập Tự Động Triển Khai (CI/CD) Qua GitHub Actions

File cấu hình `.github/workflows/ci.yml` đã được nâng cấp thành **CI/CD Pipeline**. Mỗi khi bạn push mã nguồn mới lên nhánh `main` hoặc `master`, GitHub Actions sẽ tự động kiểm thử, kiểm tra khả năng build Docker và tự động SSH vào VPS để kéo code mới và restart hệ thống.

Để kích hoạt tính năng này, bạn cần cấu hình SSH Key kết nối giữa GitHub và VPS theo các bước sau:

### 9.1. Tạo SSH Key trên VPS
Truy cập vào VPS thông qua SSH và chạy lệnh:

```bash
# Tạo cặp khóa SSH mới (ấn Enter liên tiếp khi được hỏi để bỏ qua mật khẩu khóa)
ssh-keygen -t ed25519 -C "github-actions"

# Thêm khóa công khai (Public Key) vào danh sách truy cập được phép của VPS
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# Phân quyền chuẩn cho thư mục SSH
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 9.2. Lấy Khóa Bí Mật (Private Key)
Hiển thị khóa bí mật để copy:

```bash
cat ~/.ssh/id_ed25519
```
Sao chép toàn bộ nội dung xuất hiện (bao gồm cả dòng `-----BEGIN OPENSSH PRIVATE KEY-----` và `-----END OPENSSH PRIVATE KEY-----`).

### 9.3. Cấu hình Secrets trên GitHub Repository
1. Trên kho mã nguồn GitHub của bạn, chọn **Settings** (Cài đặt) -> **Secrets and variables** -> **Actions**.
2. Nhấn nút **New repository secret** để thêm các biến sau:
   *   `VPS_HOST`: Điền địa chỉ IP Public của VPS của bạn (ví dụ: `123.45.67.89`).
   *   `VPS_USER`: Điền user đăng nhập (thường là `root`).
   *   `VPS_SSH_KEY`: Dán toàn bộ nội dung **Private Key** đã copy ở bước 9.2.
   *   `VPS_PORT` *(Tùy chọn)*: Điền cổng SSH của VPS nếu bạn thay đổi cổng mặc định (mặc định là `22` nếu không điền).

Từ bây giờ, quy trình deploy của bạn sẽ hoàn toàn tự động! Mỗi khi bạn chạy `git push origin main`, chỉ cần đợi khoảng 2-3 phút, phiên bản mới nhất sẽ tự động cập nhật lên VPS.

---
Chúc bạn triển khai thành công! Nếu gặp bất kỳ khó khăn nào trong quá trình cài đặt, hãy kiểm tra logs của `celery_worker` để xem thông báo lỗi chi tiết từ OpenAI API hoặc GitHub API.

Chúc bạn triển khai thành công! Nếu gặp bất kỳ khó khăn nào trong quá trình cài đặt, hãy kiểm tra logs của `celery_worker` để xem thông báo lỗi chi tiết từ OpenAI API hoặc GitHub API.
