# Nginx Monitor - React Dashboard (Tiếng Việt)

Giao diện giám sát và phân tích đồ thị thời gian thực, thiết kế full màn hình sang trọng, giúp trực quan hóa tình trạng tải của Nginx server, theo dõi logs lỗi, request chậm và quản lý các cảnh báo.

## 🛠️ Công Nghệ Sử Dụng
* **Build System & Runtime**: Vite + React + TypeScript
* **UI Component Library**: Ant Design (AntD)
* **Icons**: `@ant-design/icons`
* **Realtime Topology**: `reactflow` (Vẽ sơ đồ tương tác các dòng lưu lượng thực tế)
* **Biểu đồ trực quan**: `@ant-design/plots` (Các biểu đồ Area & Column trực quan hiệu năng cao)
* **HTTP Client**: Axios (Cấu hình Interceptor tự động đính kèm JWT Token)
* **Routing**: React Router DOM

---

## 🚀 Hướng Dẫn Cài Đặt Cục Bộ

### 1. Yêu cầu hệ thống
* Node.js 18 trở lên
* npm hoặc yarn
* Backend server đang chạy (tại `http://localhost:8000`)

### 2. Cài đặt các thư viện
```bash
cd frontend
npm install
```

### 3. Khởi động môi trường Dev (Hot Reload)
Chạy server Vite phát triển:
```bash
npm run dev
```
Sau khi chạy thành công, mở trình duyệt truy cập:
`http://localhost:5173`

---

## 📂 Các Trang Chính & Tính Năng

### 1. Tổng quan Dashboard (`/`)
* Hiển thị các ô chỉ số tổng quát: Tổng số request, số lượng lỗi phát sinh, request bị chậm và thời gian trễ trung bình (Avg Latency).
* **Biểu đồ Area Requests Over Time**: Theo dõi lưu lượng truy cập biến động theo thời gian thực.
* **Biểu đồ Column Status Distribution**: Thống kê phân chia nhóm mã HTTP (2xx, 3xx, 4xx, 5xx).

### 2. Dòng Log Thời Gian Thực (`/realtime`)
* Thiết lập **kết nối WebSocket** (`ws://localhost:8000/api/ws/realtime`) để cập nhật logs tức thì ngay khi Nginx nhận request.
* Hỗ trợ nút **Pause/Resume** để tạm dừng dòng log phục vụ việc đọc/sao chép thông tin log chi tiết, và nút **Clear** để dọn sạch bộ nhớ đệm hiển thị.
* Thứ tự các cột đã được tinh chỉnh tối ưu cho việc quan sát:
  `Time` ➔ `Client IP` ➔ `Method` ➔ `Address` ➔ `URI` ➔ `Status` ➔ `Time (s)` ➔ `Upstream`.

### 3. Sơ đồ kết nối Topology (`/topology`)
* Vẽ sơ đồ tương tác hiển thị cách các Client truy cập vào các cụm Nginx và định tuyến về các Upstream (microservices) phía dưới.
* Visual hóa đường đi bằng hoạt ảnh chuyển động màu sắc (Xanh = Bình thường, Đỏ = Có lỗi phát sinh) với tốc độ nhanh, mượt mà.

### 4. Giám sát Bất Thường (`/errors`, `/slow-requests`)
* **Errors**: Liệt kê nhanh các request lỗi 4xx/5xx để khoanh vùng và xử lý sự cố.
* **Slow Requests**: Liệt kê danh sách các request phản hồi chậm quá ngưỡng cấu hình (ví dụ > 1.0s) kèm chi tiết thời gian phản hồi của upstream.

---

## 📦 Đóng Gói Production (Build)
Để biên dịch và tối ưu hóa dự án để deploy lên môi trường Production:
```bash
npm run build
```
Thư mục `dist/` được tạo ra chứa toàn bộ mã nguồn tĩnh đã được nén tối ưu, sẵn sàng để deploy lên Nginx, Apache hoặc các host tĩnh khác.
