#!/usr/bin/env python3
"""
Simulated IoT IP Surveillance Camera Web Portal
Port: 8081
Target Credentials:
  Username: admin
  Password: camera123
"""

import os
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8081
VALID_USER = "admin"
VALID_PASS = "camera123"

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IP Camera Web Portal - Model IPC-HD4000</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #c9d1d9;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
            width: 400px;
            padding: 30px;
            position: relative;
        }
        .header {
            text-align: center;
            margin-bottom: 25px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 15px;
        }
        .cam-icon {
            font-size: 40px;
            margin-bottom: 10px;
            display: block;
        }
        h2 { font-size: 20px; color: #58a6ff; letter-spacing: 1px; }
        .subtitle { font-size: 12px; color: #8b949e; margin-top: 5px; }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 13px; margin-bottom: 6px; color: #8b949e; }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px 12px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #f0f6fc;
            font-size: 14px;
        }
        input:focus { border-color: #58a6ff; outline: none; }
        button {
            width: 100%;
            padding: 12px;
            background: #238636;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            font-size: 15px;
            transition: 0.2s;
        }
        button:hover { background: #2ea043; }
        .alert {
            background: rgba(248, 81, 73, 0.15);
            border: 1px solid #f85149;
            color: #ff7b72;
            padding: 10px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 15px;
            text-align: center;
        }
        .footer {
            margin-top: 20px;
            font-size: 11px;
            color: #484f58;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="header">
            <span class="cam-icon">📹</span>
            <h2>SECURE-VIEW™ IP CAMERA</h2>
            <div class="subtitle">Firmware: v4.8.2-Build2026 | Port: 8081</div>
        </div>
        {ERROR_MSG}
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username (Логин):</label>
                <input type="text" id="username" name="username" placeholder="admin" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password (Құпия сөз):</label>
                <input type="password" id="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit">LOGIN TO SURVEILLANCE FEED</button>
        </form>
        <div class="footer">
            Device ID: CAM-04-SERVER-ROOM | Status: ONLINE
        </div>
    </div>
</body>
</html>
"""

LIVE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CAM-04 [LIVE] - Surveillance Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #090d13;
            color: #00ff66;
            font-family: 'Courier New', Courier, monospace;
            padding: 20px;
            min-height: 100vh;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #00ff66;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .rec-dot {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: red;
            border-radius: 50%;
            margin-right: 8px;
            animation: blink 1s infinite;
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        .main-view {
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 20px;
        }
        .screen-container {
            background: #000;
            border: 2px solid #30363d;
            border-radius: 8px;
            position: relative;
            height: 520px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.2);
        }
        .overlay {
            position: absolute;
            top: 15px;
            left: 20px;
            font-size: 16px;
            color: #00ff66;
            text-shadow: 0 0 8px #00ff66;
            z-index: 10;
        }
        .overlay-right {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 16px;
            color: #ff3333;
            text-shadow: 0 0 8px #ff3333;
            z-index: 10;
        }
        .grid-cross {
            position: absolute;
            width: 60px;
            height: 60px;
            border: 1px dashed rgba(0, 255, 102, 0.4);
            border-radius: 50%;
        }
        .hacked-banner {
            position: absolute;
            bottom: 20px;
            background: rgba(0, 255, 102, 0.15);
            border: 2px solid #00ff66;
            padding: 12px 25px;
            border-radius: 6px;
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            z-index: 20;
            box-shadow: 0 0 15px #00ff66;
        }
        .controls {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            color: #c9d1d9;
        }
        .controls h3 { color: #58a6ff; margin-bottom: 15px; font-size: 16px; }
        .ptz-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 20px;
        }
        .ptz-btn {
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 12px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            text-align: center;
        }
        .ptz-btn:hover { background: #30363d; color: #58a6ff; }
        .logout-btn {
            display: block;
            margin-top: 30px;
            padding: 10px;
            background: #da3633;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
        }
        canvas { width: 100%; height: 100%; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2><span class="rec-dot"></span>CAM-04: СЕРВЕРЛІК БӨЛМЕ (SERVER ROOM)</h2>
            <div style="color: #8b949e; font-size: 12px; margin-top: 5px;">IP: 127.0.0.1:8081 | FPS: 30.0 | Bitrate: 4096 kbps</div>
        </div>
        <div id="clock" style="font-size: 18px; color: #00ff66;"></div>
    </div>

    <div class="main-view">
        <div class="screen-container">
            <div class="overlay">
                <div>[LIVE FEED] 1080P FHD</div>
                <div>PRESET: MAIN-ENTRANCE</div>
            </div>
            <div class="overlay-right">
                <div>● REC [SECURE]</div>
                <div>IR-NIGHT: ON</div>
            </div>
            <canvas id="cctvCanvas"></canvas>
            <div class="grid-cross"></div>
            <div class="hacked-banner">
                🎉 ҚҰТТЫҚТАЙМЫН! СІЗ КАМЕРАҒА КІРДІҢІЗ!<br>
                <span style="font-size: 14px; color: #00ff66;">Пароль бұзылды: admin / camera123</span>
            </div>
        </div>

        <div class="controls">
            <h3>🎮 PTZ КАМЕРА БАСҚАРУ</h3>
            <div class="ptz-grid">
                <div></div><div class="ptz-btn" onclick="alert('Камера жоғары бұрылды')">▲</div><div></div>
                <div class="ptz-btn" onclick="alert('Камера солға бұрылды')">◀</div>
                <div class="ptz-btn" onclick="alert('Ортаға бағытталды')">●</div>
                <div class="ptz-btn" onclick="alert('Камера оңға бұрылды')">▶</div>
                <div></div><div class="ptz-btn" onclick="alert('Камера төмен бұрылды')">▼</div><div></div>
            </div>

            <div style="margin-top: 20px; font-size: 13px; line-height: 1.6; color: #8b949e;">
                <p><strong>Орнатылған жері:</strong> 1-қабат, Бас серверлік қойма</p>
                <p><strong>Датчиктер:</strong> Қозғалыс белсенді</p>
                <p><strong>Батарея / Тоқ:</strong> 100% PoE Online</p>
            </div>

            <a href="/logout" class="logout-btn">ШЫҒУ (LOGOUT)</a>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toISOString().replace('T', ' ').substr(0, 19);
        }
        setInterval(updateClock, 1000);
        updateClock();

        // CCTV Noise simulation
        const canvas = document.getElementById('cctvCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 640;
        canvas.height = 360;

        function drawNoise() {
            const imgData = ctx.createImageData(canvas.width, canvas.height);
            const data = imgData.data;
            for (let i = 0; i < data.length; i += 4) {
                const val = Math.random() * 40 + 10;
                data[i] = val * 0.4;
                data[i+1] = val;
                data[i+2] = val * 0.5;
                data[i+3] = 255;
            }
            ctx.putImageData(imgData, 0, 0);

            // Draw rack silhouette
            ctx.fillStyle = "rgba(0, 50, 20, 0.5)";
            ctx.fillRect(80, 80, 160, 250);
            ctx.fillRect(380, 60, 180, 270);

            // Server blinking lights
            for(let y = 100; y < 320; y += 25) {
                ctx.fillStyle = Math.random() > 0.3 ? "#00ff66" : "#ffcc00";
                ctx.fillRect(90, y, 6, 6);
                ctx.fillRect(105, y, 6, 6);
                ctx.fillStyle = Math.random() > 0.5 ? "#00ffff" : "#00ff66";
                ctx.fillRect(395, y, 6, 6);
            }
            requestAnimationFrame(drawNoise);
        }
        drawNoise();
    </script>
</body>
</html>
"""

class CameraHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        cookie = self.headers.get('Cookie', '')
        if self.path == '/live':
            if 'session=authenticated' in cookie:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(LIVE_HTML.encode('utf-8'))
                return
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return

        if self.path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/')
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # Default login
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = LOGIN_HTML.replace('{ERROR_MSG}', '')
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)

        user = params.get('username', [''])[0]
        passwd = params.get('password', [''])[0]

        if user == VALID_USER and passwd == VALID_PASS:
            self.send_response(302)
            self.send_header('Set-Cookie', 'session=authenticated; Path=/')
            self.send_header('Location', '/live')
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            err_box = '<div class="alert">⚠️ Қате: Логин немесе пароль дұрыс емес!</div>'
            html = LOGIN_HTML.replace('{ERROR_MSG}', err_box)
            self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        # Write to arena console
        sys.stderr.write(f"[CAMERA ACCESS] {self.address_string()} - {format % args}\n")

if __name__ == '__main__':
    host = os.environ.get('CAMERA_HOST', '127.0.0.1')
    server = HTTPServer((host, PORT), CameraHandler)
    print(f"[✔] IP Camera Web Portal started on http://{host}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
