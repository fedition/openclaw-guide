#!/usr/bin/env python3
"""虾逛 Analytics Server - 轻量级 PV/UV 统计后台"""

import json
import sqlite3
import os
import base64
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
try:
    import geoip2.database
    GEOIP_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeoLite2-City.mmdb')
    geo_reader = geoip2.database.Reader(GEOIP_DB) if os.path.exists(GEOIP_DB) else None
except ImportError:
    geo_reader = None

# === 配置 ===
PORT = 8790
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analytics.db')
ADMIN_USER = 'admin'
ADMIN_PASS = 'xiaguang2026'  # 修改为你的密码
ALLOWED_ORIGINS = ['https://zdypro.com', 'http://zdypro.com', 'http://139.180.152.53', 'http://localhost:8080']

# === IP 地区解析 ===
def lookup_geo(ip):
    if not geo_reader or not ip:
        return '', '', ''
    try:
        r = geo_reader.city(ip)
        country = r.country.names.get('zh-CN', r.country.names.get('en', ''))
        province = r.subdivisions.most_specific.names.get('zh-CN', r.subdivisions.most_specific.names.get('en', '')) if r.subdivisions else ''
        city = r.city.names.get('zh-CN', r.city.names.get('en', '')) if r.city else ''
        return country, province, city
    except Exception:
        return '', '', ''

# === 数据库 ===
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS pageviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            referrer TEXT,
            visitor_id TEXT NOT NULL,
            screen TEXT,
            lang TEXT,
            ip TEXT,
            user_agent TEXT,
            country TEXT DEFAULT '',
            province TEXT DEFAULT '',
            city TEXT DEFAULT '',
            created_at DATETIME DEFAULT (datetime('now', 'localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_pv_created ON pageviews(created_at);
        CREATE INDEX IF NOT EXISTS idx_pv_url ON pageviews(url);
        CREATE INDEX IF NOT EXISTS idx_pv_vid ON pageviews(visitor_id);
        CREATE INDEX IF NOT EXISTS idx_pv_ip ON pageviews(ip);
    ''')
    # 兼容旧表：添加新列（如果不存在）
    try:
        conn.execute('ALTER TABLE pageviews ADD COLUMN country TEXT DEFAULT ""')
    except Exception:
        pass
    try:
        conn.execute('ALTER TABLE pageviews ADD COLUMN province TEXT DEFAULT ""')
    except Exception:
        pass
    try:
        conn.execute('ALTER TABLE pageviews ADD COLUMN city TEXT DEFAULT ""')
    except Exception:
        pass
    conn.close()

# === 认证 ===
def check_auth(headers):
    auth = headers.get('Authorization', '')
    if not auth.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode('utf-8')
        user, passwd = decoded.split(':', 1)
        return user == ADMIN_USER and passwd == ADMIN_PASS
    except Exception:
        return False

# === Handler ===
class AnalyticsHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # 静默日志

    def send_cors(self):
        origin = self.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS or not origin:
            self.send_header('Access-Control-Allow-Origin', origin or '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/track':
            self.handle_track()
        else:
            self.send_error(404)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/admin' or path == '/admin/':
            self.serve_admin()
        elif path.startswith('/api/stats'):
            self.handle_stats()
        else:
            self.send_error(404)

    def handle_track(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
            country, province, city = lookup_geo(ip)

            conn = get_db()
            conn.execute('''
                INSERT INTO pageviews (url, title, referrer, visitor_id, screen, lang, ip, user_agent, country, province, city)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url', ''),
                data.get('title', ''),
                data.get('referrer', ''),
                data.get('vid', ''),
                data.get('screen', ''),
                data.get('lang', ''),
                ip,
                self.headers.get('User-Agent', ''),
                country, province, city,
            ))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as e:
            self.send_response(400)
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_stats(self):
        if not check_auth(self.headers):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Analytics"')
            self.end_headers()
            return

        query = parse_qs(urlparse(self.path).query)
        # 支持自定义日期范围: ?from=2026-01-01&to=2026-03-27 或 ?days=7
        date_from = query.get('from', [None])[0]
        date_to = query.get('to', [None])[0]
        if date_from:
            since = date_from
            until = date_to or datetime.now().strftime('%Y-%m-%d')
        else:
            days = int(query.get('days', ['7'])[0])
            since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')

        conn = get_db()

        # 每日 PV/UV
        daily = conn.execute('''
            SELECT date(created_at) as day,
                   COUNT(*) as pv,
                   COUNT(DISTINCT ip) as uv
            FROM pageviews
            WHERE date(created_at) >= ? AND date(created_at) <= ?
            GROUP BY day ORDER BY day
        ''', (since, until)).fetchall()

        # 页面排行
        pages = conn.execute('''
            SELECT url,
                   COUNT(*) as pv,
                   COUNT(DISTINCT ip) as uv
            FROM pageviews
            WHERE date(created_at) >= ? AND date(created_at) <= ?
            GROUP BY url ORDER BY pv DESC LIMIT 20
        ''', (since, until)).fetchall()

        # 今日实时
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = conn.execute('''
            SELECT COUNT(*) as pv, COUNT(DISTINCT ip) as uv
            FROM pageviews WHERE date(created_at) = ?
        ''', (today,)).fetchone()

        # 总计
        total = conn.execute('''
            SELECT COUNT(*) as pv, COUNT(DISTINCT ip) as uv
            FROM pageviews
        ''').fetchone()

        # 来源统计
        referrers = conn.execute('''
            SELECT CASE
                WHEN referrer = '' THEN '直接访问'
                ELSE referrer
            END as source,
            COUNT(*) as cnt
            FROM pageviews
            WHERE date(created_at) >= ? AND date(created_at) <= ?
            GROUP BY source ORDER BY cnt DESC LIMIT 10
        ''', (since, until)).fetchall()

        # 每小时分布（今天）
        hourly = conn.execute('''
            SELECT strftime('%H', created_at) as hour, COUNT(*) as pv
            FROM pageviews
            WHERE date(created_at) = ?
            GROUP BY hour ORDER BY hour
        ''', (today,)).fetchall()

        # 地区统计
        regions = conn.execute('''
            SELECT CASE
                WHEN country = '' THEN '未知'
                WHEN province = '' THEN country
                ELSE country || ' · ' || province || CASE WHEN city != '' AND city != province THEN ' · ' || city ELSE '' END
            END as region,
            COUNT(*) as pv,
            COUNT(DISTINCT ip) as uv
            FROM pageviews
            WHERE date(created_at) >= ? AND date(created_at) <= ?
            GROUP BY region ORDER BY pv DESC LIMIT 20
        ''', (since, until)).fetchall()

        conn.close()

        result = {
            'daily': [dict(r) for r in daily],
            'pages': [dict(r) for r in pages],
            'today': dict(today_stats) if today_stats else {'pv': 0, 'uv': 0},
            'total': dict(total) if total else {'pv': 0, 'uv': 0},
            'referrers': [dict(r) for r in referrers],
            'hourly': [dict(r) for r in hourly],
            'regions': [dict(r) for r in regions],
        }

        self.send_response(200)
        self.send_cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

    def serve_admin(self):
        if not check_auth(self.headers):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Analytics Admin"')
            self.end_headers()
            return

        admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin.html')
        with open(admin_path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content)

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', PORT), AnalyticsHandler)
    print(f'Analytics server running on port {PORT}')
    print(f'Admin: http://localhost:{PORT}/admin')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping...')
        server.server_close()
