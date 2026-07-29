export const translations = {
  en: {
    // Navigation & Layout
    overview: "Overview Dashboard",
    realtimeLogs: "Realtime Logs",
    topology: "Topology Map",
    errors: "Error Monitoring",
    slowRequests: "Slow Requests",
    alerts: "Alert Rules & Center",
    users: "User Management",
    logout: "Log Out",
    welcome: "Welcome",
    language: "Language",
    
    // Overview Dashboard
    totalRequests: "Total Requests",
    errorRate: "Error Rate",
    avgLatency: "Avg Latency",
    activeAlerts: "Active Alerts",
    reqTrend: "Request Status Trend",
    statusDist: "HTTP Status Distribution",
    topErrors: "Top Error Paths (4xx/5xx)",
    topSlow: "Top Slow Request Paths",
    path: "Path",
    count: "Count",
    
    // Table Columns
    time: "Time",
    clientIp: "Client IP",
    method: "Method",
    host: "Host",
    uri: "URI",
    status: "Status",
    duration: "Time(s)",
    upstream: "Upstream",
    actions: "Actions",
    
    // Realtime Logs
    realtimeStream: "Realtime Nginx Log Stream",
    play: "Play",
    pause: "Pause",
    clear: "Clear Logs",
    pausedState: "Stream Paused",
    liveState: "Live Stream",
    
    // Topology
    topologyTitle: "Service Topology Map",
    topologyDesc: "Visualizes the flow of HTTP requests from Nginx servers to downstream upstreams in real-time.",
    
    // Error Monitoring
    errorTitle: "Nginx Error Request Monitoring",
    errorDesc: "List of all HTTP 4xx and 5xx client and server errors.",
    
    // Slow Request Monitoring
    slowTitle: "Nginx Slow Request Monitoring",
    slowDesc: "List of all requests exceeding the configured response time threshold.",
    
    // Alerts Page
    alertsTitle: "Alert Rules & Monitoring Center",
    createRule: "Create Alert Rule",
    activeEvents: "Active & History Events",
    alertRules: "Alert Rules",
    ruleName: "Rule Name",
    condition: "Condition",
    threshold: "Threshold",
    durationMinutes: "Duration (Minutes)",
    state: "Status",
    firing: "Firing",
    resolved: "Resolved",
    active: "Active",
    disabled: "Disabled",
    details: "Details",
    resolve: "Resolve",
    errCreateRule: "Failed to create alert rule",
    succCreateRule: "Alert rule created successfully",
    succResolve: "Alert resolved successfully",
    errResolve: "Failed to resolve alert",
    
    // Create Alert Form
    condErrorRate: "Error Rate (%)",
    cond5xxCount: "5xx Count",
    condSlowCount: "Slow Request Count",
    condDdos: "DDoS Threat (Req/IP)",
    condScan: "Vulnerability Scanning (Errors/IP)",
    notificationChannel: "Notification Channel",
    console: "Console Log",
    webhook: "Webhook Endpoint",
    submit: "Submit",
    cancel: "Cancel",
    
    // User Page
    userTitle: "User & Role Management",
    createUser: "Create New User",
    username: "Username",
    email: "Email",
    fullName: "Full Name",
    role: "Role",
    statusCol: "Status",
    delete: "Delete",
    roleAdmin: "Admin",
    roleOperator: "Operator",
    roleViewer: "Viewer",
    
    // Create User Form
    password: "Password",
    
    // Login Page
    loginTitle: "Nginx Monitor Sign In",
    loginSub: "State-of-the-art Realtime Monitoring",
    usernameReq: "Please input your username!",
    passwordReq: "Please input your password!",
  },
  vi: {
    // Navigation & Layout
    overview: "Bảng Điều Khiển",
    realtimeLogs: "Log Thời Gian Thực",
    topology: "Sơ Đồ Topology",
    errors: "Giám Sát Lỗi",
    slowRequests: "Yêu Cầu Chậm",
    alerts: "Quy Tắc Cảnh Báo",
    users: "Quản Lý Người Dùng",
    logout: "Đăng Xuất",
    welcome: "Chào mừng",
    language: "Ngôn ngữ",
    
    // Overview Dashboard
    totalRequests: "Tổng Số Request",
    errorRate: "Tỷ Lệ Lỗi",
    avgLatency: "Độ Trễ Trung Bình",
    activeAlerts: "Cảnh Báo Kích Hoạt",
    reqTrend: "Xu Hướng Mã Trạng Thái",
    statusDist: "Phân Phối HTTP Status",
    topErrors: "Đường Dẫn Lỗi Nhiều Nhất (4xx/5xx)",
    topSlow: "Đường Dẫn Yêu Cầu Chậm Nhất",
    path: "Đường dẫn",
    count: "Số lượng",
    
    // Table Columns
    time: "Thời gian",
    clientIp: "IP Khách",
    method: "Phương thức",
    host: "Host",
    uri: "URI",
    status: "Trạng thái",
    duration: "Thời gian (s)",
    upstream: "Upstream",
    actions: "Hành động",
    
    // Realtime Logs
    realtimeStream: "Dòng Log Nginx Thời Gian Thực",
    play: "Tiếp tục",
    pause: "Tạm dừng",
    clear: "Xóa log",
    pausedState: "Đã tạm dừng dòng log",
    liveState: "Dòng log trực tiếp",
    
    // Topology
    topologyTitle: "Sơ Đồ Phân Phối Luồng Topology",
    topologyDesc: "Trực quan hóa luồng yêu cầu HTTP từ máy chủ Nginx đến các máy chủ Upstream thời gian thực.",
    
    // Error Monitoring
    errorTitle: "Giám Sát Lỗi Nginx Access Logs",
    errorDesc: "Danh sách tất cả các lỗi Client (4xx) và Server (5xx).",
    
    // Slow Request Monitoring
    slowTitle: "Giám Sát Yêu Cầu Chậm Nginx",
    slowDesc: "Danh sách tất cả các yêu cầu vượt quá ngưỡng thời gian phản hồi quy định.",
    
    // Alerts Page
    alertsTitle: "Trung Tâm Quản Lý & Quy Tắc Cảnh Báo",
    createRule: "Tạo Quy Tắc Cảnh Báo",
    activeEvents: "Sự Cố Đang Hoạt Động & Lịch Sử",
    alertRules: "Quy Tắc Cảnh Báo",
    ruleName: "Tên Quy Tắc",
    condition: "Điều kiện",
    threshold: "Ngưỡng",
    durationMinutes: "Thời gian (Phút)",
    state: "Trạng thái",
    firing: "Kích hoạt",
    resolved: "Đã xử lý",
    active: "Hoạt động",
    disabled: "Vô hiệu hóa",
    details: "Chi tiết",
    resolve: "Xử lý",
    errCreateRule: "Không thể tạo quy tắc cảnh báo",
    succCreateRule: "Tạo quy tắc cảnh báo thành công",
    succResolve: "Đã đánh dấu xử lý sự cố thành công",
    errResolve: "Không thể xử lý cảnh báo",
    
    // Create Alert Form
    condErrorRate: "Tỷ Lệ Lỗi (%)",
    cond5xxCount: "Số lượng lỗi 5xx",
    condSlowCount: "Số lượng yêu cầu chậm",
    condDdos: "Mối đe dọa DDoS (Yêu cầu/IP)",
    condScan: "Quét cổng/Dò lỗ hổng (Lỗi/IP)",
    notificationChannel: "Kênh thông báo",
    console: "Console Log",
    webhook: "Webhook Endpoint",
    submit: "Xác nhận",
    cancel: "Hủy bỏ",
    
    // User Page
    userTitle: "Quản Lý Thành Viên & Phân Quyền",
    createUser: "Tạo Người Dùng Mới",
    username: "Tên đăng nhập",
    email: "Email",
    fullName: "Họ và Tên",
    role: "Vai trò",
    statusCol: "Trạng thái",
    delete: "Xóa",
    roleAdmin: "Quản trị viên",
    roleOperator: "Vận hành",
    roleViewer: "Người xem",
    
    // Create User Form
    password: "Mật khẩu",
    
    // Login Page
    loginTitle: "Đăng Nhập Nginx Monitor",
    loginSub: "Hệ Thống Giám Sát Thời Gian Thực Cao Cấp",
    usernameReq: "Vui lòng nhập tên đăng nhập!",
    passwordReq: "Vui lòng nhập mật khẩu!",
  },
  ja: {
    // Navigation & Layout
    overview: "ダッシュボード",
    realtimeLogs: "リアルタイムログ",
    topology: "トポロジーマップ",
    errors: "エラー監視",
    slowRequests: "遅延要求監視",
    alerts: "アラートルール",
    users: "ユーザー管理",
    logout: "ログアウト",
    welcome: "ようこそ",
    language: "言語",
    
    // Overview Dashboard
    totalRequests: "総リクエスト数",
    errorRate: "エラー率",
    avgLatency: "平均レイテンシ",
    activeAlerts: "検知アラート",
    reqTrend: "ステータストレンド",
    statusDist: "HTTPステータス分布",
    topErrors: "エラー頻発パス (4xx/5xx)",
    topSlow: "遅延リクエストパス",
    path: "パス",
    count: "回数",
    
    // Table Columns
    time: "時刻",
    clientIp: "クライアントIP",
    method: "メソッド",
    address: "アドレス",
    uri: "URI",
    status: "ステータス",
    duration: "時間 (秒)",
    upstream: "アップストリーム",
    actions: "操作",
    
    // Realtime Logs
    realtimeStream: "リアルタイムNginxログストリーム",
    play: "再開",
    pause: "一時停止",
    clear: "ログクリア",
    pausedState: "ストリーム一時停止中",
    liveState: "ライブストリーム",
    
    // Topology
    topologyTitle: "サービストポロジーマップ",
    topologyDesc: "NginxサーバーからアップストリームサーバーへのHTTPリクエストフローをリアルタイムで可視化します。",
    
    // Error Monitoring
    errorTitle: "Nginxエラーリクエスト監視",
    errorDesc: "すべてのHTTP 4xxおよび5xxクライアントおよびサーバーエラーのリスト。",
    
    // Slow Request Monitoring
    slowTitle: "Nginx遅延リクエスト監視",
    slowDesc: "設定された応答時間しきい値を超えるすべての要求のリスト。",
    
    // Alerts Page
    alertsTitle: "アラートルール＆モニタリングセンター",
    createRule: "アラートルール作成",
    activeEvents: "現在のアラート＆履歴",
    alertRules: "アラートルール設定",
    ruleName: "ルール名",
    condition: "条件",
    threshold: "しきい値",
    durationMinutes: "期間 (分)",
    state: "ステータス",
    firing: "発生中",
    resolved: "解決済み",
    active: "有効",
    disabled: "無効",
    details: "詳細",
    resolve: "解決にする",
    errCreateRule: "アラートルールの作成に失敗しました",
    succCreateRule: "アラートルールを作成しました",
    succResolve: "アラートを解決にしました",
    errResolve: "アラートの解決に失敗しました",
    
    // Create Alert Form
    condErrorRate: "エラー率 (%)",
    cond5xxCount: "5xx エラー数",
    condSlowCount: "遅延要求数",
    condDdos: "DDoS攻撃脅威 (リクエスト/IP)",
    condScan: "脆弱性スキャン (エラー数/IP)",
    notificationChannel: "通知チャネル",
    console: "コンソールログ",
    webhook: "Webhook エンドポイント",
    submit: "送信",
    cancel: "キャンセル",
    
    // User Page
    userTitle: "ユーザー＆ロール管理",
    createUser: "ユーザー作成",
    username: "ユーザー名",
    email: "メールアドレス",
    fullName: "氏名",
    role: "ロール",
    statusCol: "ステータス",
    delete: "削除",
    roleAdmin: "管理者",
    roleOperator: "運用者",
    roleViewer: "閲覧者",
    
    // Create User Form
    password: "パスワード",
    
    // Login Page
    loginTitle: "Nginxモニター ログイン",
    loginSub: "最先端のリアルタイム監視システム",
    usernameReq: "ユーザー名を入力してください！",
    passwordReq: "パスワードを入力してください！",
  }
};

export type Language = 'en' | 'vi' | 'ja';
export type TranslationKey = keyof typeof translations.en;
