# Nginx Monitor - React Dashboard

An elegant, fully-responsive full-screen analytics dashboard designed to visualize Nginx server health, live traffic flow, error tracking, and anomaly alerts.

## 🛠️ Technology Stack
* **Build System & Runtime**: Vite + React + TypeScript
* **UI Component Library**: Ant Design (AntD)
* **Icons**: `@ant-design/icons`
* **Realtime Topology**: `reactflow` (Visualization of traffic streams from client to upstreams)
* **Data Visualizations**: `@ant-design/plots` (G2Plot wrappers for Area & Column charts)
* **HTTP Client**: Axios with interceptors for JWT token handling
* **Routing**: React Router DOM

---

## 🚀 Local Development Setup

### 1. Requirements
* Node.js 18 or higher
* npm or yarn
* Backend server running (on `http://localhost:8000`)

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Run Development Server
Start Vite dev server with Hot Module Replacement (HMR):
```bash
npm run dev
```
Once started, open your browser at:
`http://localhost:5173`

---

## 📂 Key Pages & Features

### 1. Overview Dashboard (`/`)
* Displays summary cards for total requests, error count, slow requests count, and average latency.
* **Requests Over Time Area Chart**: Visualizes query speed and spikes.
* **Status Distribution Column Chart**: Displays a breakdown of HTTP response code classes (2xx, 3xx, 4xx, 5xx).

### 2. Realtime Logs (`/realtime`)
* Establishes a persistent **WebSocket connection** (`ws://localhost:8000/api/ws/realtime`) to display logs as they stream in.
* Supports **Pause/Resume** streaming controls to freeze logs for immediate investigation, and a **Clear** buffer tool.
* Column order optimized for readability:
  `Time` ➔ `Client IP` ➔ `Method` ➔ `Address` ➔ `URI` ➔ `Status` ➔ `Latency (s)` ➔ `Upstream`.

### 3. Topology Map (`/topology`)
* Renders a real-time reactive grid showcasing how clients connect to Nginx instances and route back to downstream microservices/upstreams.
* Visualizes request status as color-coded flows (Green = Normal, Red = Erroneous) running at rapid animation speeds.

### 4. Anomaly Monitors (`/errors`, `/slow-requests`)
* **Errors**: Instant querying of 4xx/5xx responses to pinpoint system issues.
* **Slow Requests**: Lists any requests exceeding the threshold (e.g. 1.0s) with detailed breakdown of latency versus upstream response time.

---

## 📦 Production Build
To build and optimize the application for production deployment:
```bash
npm run build
```
This generates a highly optimized static bundle inside the `dist/` directory, ready to be served by Nginx, Apache, or any static file hosting service.
