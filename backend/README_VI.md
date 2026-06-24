# Nginx Monitor - Backend API Server (Tiếng Việt)

API Server hiệu năng cao được xây dựng bằng FastAPI để quản lý xác thực, điều phối Agent và tiếp nhận xử lý luồng log thời gian thực.

## 🛠️ Công Nghệ Sử Dụng
* **Web Framework**: FastAPI (Python Không đồng bộ)
* **Cơ sở dữ liệu**:
  * **PostgreSQL**: Lưu trữ dữ liệu cấu trúc (User, Agent token, Alert rules) thông qua SQLAlchemy & Alembic.
  * **ClickHouse**: Lưu trữ log truy cập Nginx khối lượng lớn thông qua Driver HTTP `clickhouse-connect`.
  * **Redis**: Cầu nối Pub/Sub để đẩy sự kiện log thời gian thực qua kênh WebSocket.
* **Bảo mật**: Xác thực dựa trên JWT Token và mã hóa mật khẩu bằng `bcrypt`.

---

## 🚀 Hướng Dẫn Cài Đặt Cục Bộ

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên
* Các Database đang chạy (khởi động từ thư mục gốc qua `docker compose up -d`)

### 2. Thiết lập Môi trường ảo (Virtual Env) & Thư viện
Tạo môi trường ảo python và cài đặt các thư viện cần thiết:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Sao chép file `.env.example` và tùy chỉnh nếu cần:
```bash
cp .env.example .env
```
Các thông số mặc định trong `.env`:
* `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgrespassword`, `POSTGRES_DB=net_monitoring`
* `CLICKHOUSE_USER=default`, `CLICKHOUSE_PASSWORD=clickhousepassword`, `CLICKHOUSE_DB=net_monitoring`
* `REDIS_HOST=localhost`, `REDIS_PORT=6379`
* `JWT_SECRET_KEY` (Tự động tạo hoặc điền mã bí mật của anh)

### 4. Khởi chạy Database Migrations (PostgreSQL)
Chạy Alembic để khởi tạo toàn bộ cấu trúc bảng trong PostgreSQL:
```bash
source venv/bin/activate
alembic upgrade head
```

### 5. Khởi động Backend Server
Chạy trực tiếp file startup:
```bash
source venv/bin/activate
python app/main.py
```
Hoặc khởi chạy thông qua Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Khi server khởi động thành công:
* **Tài liệu API tương tác (Swagger UI)**: `http://localhost:8000/docs`
* **Tài liệu Redoc**: `http://localhost:8000/redoc`

---

## 🔑 Tài Khoản Quản Trị Mặc Định
Khi khởi động lần đầu, nếu hệ thống chưa có người dùng nào, Backend sẽ tự động đăng ký tài khoản Administrator mặc định:
* **Email**: `admin@admin.com`
* **Mật khẩu**: `adminpassword`

Anh hãy dùng tài khoản này để đăng nhập vào trang quản trị Dashboard.

---

## 📡 Các Nhóm API Chính

### Module Xác thực (`/api/auth`)
* `POST /api/auth/login`: Xác thực tài khoản và cấp JWT Token.
* `GET /api/auth/me`: Lấy thông tin cá nhân của tài khoản đang đăng nhập.

### Ghi nhận & Truy vấn Log (`/api/ingest`, `/api/logs`)
* `POST /api/ingest/nginx`: Nhận gói logs định kỳ đẩy lên từ Agent (yêu cầu header `X-Agent-Id` và `X-Agent-Token`).
* `GET /api/logs`: Truy vấn logs phân trang từ ClickHouse.
* `GET /api/logs/errors`: Truy vấn logs bị lỗi (HTTP Status >= 400) từ ClickHouse.
* `GET /api/logs/slow-requests`: Truy vấn logs bị xử lý chậm.

### Phân tích số liệu Dashboard (`/api/dashboard`)
* `GET /api/dashboard/overview`: Lấy các chỉ số tổng hợp (Tổng request, tỉ lệ lỗi, số lượng request bị chậm).
* `GET /api/dashboard/request-timeseries`: Lấy số lượng request theo mốc thời gian để vẽ biểu đồ.
* `GET /api/dashboard/status-timeseries`: Lấy thống kê phân phối mã trạng thái HTTP.

### Kênh WebSocket (`/api/ws`)
* `WS /api/ws/realtime`: Kết nối WebSocket liên tục để nhận luồng log thời gian thực được đẩy ra từ Redis Pub/Sub.
