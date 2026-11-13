import urllib.request
import socket

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

urls = [
    'http://127.0.0.1:5000',
    'http://localhost:5000',
    f'http://{local_ip}:5000'
]

for url in urls:
    try:
        response = urllib.request.urlopen(url, timeout=3)
        print(f"ACTIVE: {url} (HTTP {response.getcode()})")
    except Exception as e:
        print(f"FAILED: {url} ({e})")
