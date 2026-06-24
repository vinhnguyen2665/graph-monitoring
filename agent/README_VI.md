# Nginx Monitor - Python Stateful Ingestion Agent (Tiếng Việt)

Agent thu thập log siêu nhẹ, tin cậy và không đồng bộ viết bằng Python. Phân hệ này có nhiệm vụ "đọc đuôi" (tail) file log JSON của Nginx và định kỳ đóng gói đẩy về FastAPI backend.

## 🛠️ Tính Năng Nổi Bật
* **Stateful Tailing (Lưu Offset Bằng Byte)**: Tự động ghi nhớ vị trí byte cuối cùng đã đọc vào file `agent.offset`. Nếu agent bị tắt hoặc mất mạng, khi khởi động lại nó sẽ nhảy thẳng đến vị trí chưa đọc để tiếp tục đẩy log, **cam kết không đẩy trùng lặp** và **không làm mất mát dữ liệu**.
* **Phát hiện Log Rotation**: Tự động phát hiện khi Nginx xoay vòng file log (dung lượng file bị thu nhỏ hoặc thay mới) để tự động reset vị trí đọc về `0`.
* **Cơ chế Batching thông minh**: Gom log lại và đẩy theo lô (ví dụ mỗi lô 100 dòng) hoặc tự động đẩy sau mỗi 3 giây nếu không đủ lô, giúp tối ưu hóa băng thông mạng.
* **Xử lý ngoại lệ mạnh mẽ**: Tự động phát hiện và bỏ qua các dòng JSON bị lỗi cấu trúc, ghi cảnh báo debug chi tiết và tự động thử lại khi backend mất kết nối.

---

## 🚀 Hướng Dẫn Cài Đặt & Vận Hành

### 1. Cài đặt các thư viện phụ thuộc
Đảm bảo đã kích hoạt virtual environment và cài đặt thư viện:
```bash
cd agent
pip install -r requirements.txt
```

### 2. Cấu hình Agent (`config.yml`)
Agent sử dụng file `config.yml` nằm cùng thư mục để kết nối.
File cấu hình mẫu (`config.yml.example`):
```yaml
agent_id: "agent-uuid-lay-tu-postgres"
agent_token: "token-mat-khau-agent"
server_url: "http://localhost:8000"
log_path: "/var/log/nginx/access_json.log"
batch_size: 100
flush_interval_seconds: 3
offset_file: "./agent.offset"
debug: true
```

### 3. Khởi chạy Agent
Để chạy Agent chế độ đọc file log thực tế và đẩy về Backend:
```bash
python agent.py run --config config.yml
```

Để kiểm tra nhanh đường truyền tới health check của Backend:
```bash
python agent.py test --config config.yml
```

Để kiểm định chất lượng file log Nginx có đúng định dạng JSON chuẩn không:
```bash
python agent.py validate-log --file /var/log/nginx/access_json.log
```

---

## 🧪 Hệ Thống Giả Lập Dữ Liệu (`generate_dummy_logs.py`)

Để hỗ trợ kiểm thử hệ thống nhanh chóng mà không cần cài đặt Nginx server thật, em đã trang bị sẵn một script sinh log giả lập cực kỳ thông minh trong thư mục `agent/`.

Cách khởi chạy:
```bash
python generate_dummy_logs.py
```

### Các Chế Độ Chạy:
Script cung cấp 3 lựa chọn linh hoạt:
1. **Lựa chọn 1 (Ghi log ra file ảo)**: Ghi liên tục dòng logs giả lập (80% OK, 10% Lỗi, 10% Chậm) vào file `agent/dummy_access.log`. Anh có thể mở Terminal khác chạy `agent.py` để tail file này.
2. **Lựa chọn 2 (Đẩy trực tiếp qua HTTP API)**: Đóng gói 100 logs giả lập đẩy thẳng lên API `/api/ingest/nginx`. Biểu đồ trên Dashboard sẽ sáng dữ liệu ngay lập tức!
3. **Lựa chọn 3 (Cả hai)**: Đẩy trực tiếp 100 logs ban đầu và duy trì ghi logs mới vào file `dummy_access.log`.

### Khởi chạy nhanh bằng dòng lệnh (Không cần chọn menu)
Phù hợp để tự động hóa hoặc chạy ngầm dưới nền:
```bash
# Đẩy 100 logs ảo trực tiếp để xem kết quả ngay
python generate_dummy_logs.py 2

# Chạy ngầm tiến trình sinh log ảo liên tục dưới nền
python generate_dummy_logs.py 1 > /dev/null 2>&1 &
```
