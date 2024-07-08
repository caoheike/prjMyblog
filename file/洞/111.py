import re
import requests
from bs4 import BeautifulSoup

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
        response = requests.get(target, headers=headers, timeout=10)
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

# 将nonce值写入文件
def write_nonce_to_file(nonce, file_path):
    with open(file_path, 'a') as file:
        file.write(f"{nonce}\n")

def main():
    hosts_file = 'host.txt'
    output_file = 'nonce.txt'
    
    hosts = read_hosts(hosts_file)
    for host in hosts:
        nonce = fetch_nonce(f"http://{host}")
        if nonce:
            write_nonce_to_file(nonce, output_file)
            print(f"Nonce for {host}: {nonce}")
        else:
            print(f"No nonce found for {host}")

if __name__ == "__main__":
    main()
