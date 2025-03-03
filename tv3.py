import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置参数
TIMEOUT = 2  # 单次请求超时时间（秒）
DOWNLOAD_DURATION = 6  # 下载测试时长（秒）
MIN_SPEED = 1.0  # 最小有效速度（KB/s）
THREADS = 10  # 并发线程数
INPUT_URL = "https://raw.githubusercontent.com/l19270149853/ZBY/refs/heads/main/tv2.txt"
OUTPUT_FILE = "tv3.txt"

def test_speed(url):
    """
    测试 URL 的下载速度
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        start_time = time.time()
        response = requests.get(url, stream=True, timeout=TIMEOUT, headers=headers)
        response.raise_for_status()

        downloaded_size = 0
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                downloaded_size += len(chunk)
                if time.time() - start_time >= DOWNLOAD_DURATION:
                    break

        elapsed_time = time.time() - start_time
        if elapsed_time == 0:
            return None

        speed = (downloaded_size / 1024) / elapsed_time  # 计算速度（KB/s）
        if speed >= MIN_SPEED:
            return url, speed
        else:
            return None
    except requests.RequestException as e:
        return None

def process_file():
    """
    处理输入文件并生成有效地址列表
    """
    valid_urls = []

    try:
        # 从指定的URL获取数据
        response = requests.get(INPUT_URL)
        response.raise_for_status()
        lines = response.text.splitlines()

        urls = [line.strip().split(",")[1] for line in lines if line.strip()]

        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = {executor.submit(test_speed, url): url for url in urls}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    url, speed = result
                    valid_urls.append(url)
                    print(f"有效地址: {url} (速度: {speed:.2f} KB/s)")

        # 保存有效地址到文件
        with open(OUTPUT_FILE, "w") as outfile:
            for url in valid_urls:
                outfile.write(url + "\n")

        print(f"测试完成，有效地址已保存到 {OUTPUT_FILE}")
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    process_file()
