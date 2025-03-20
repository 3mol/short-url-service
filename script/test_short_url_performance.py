#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import string
import concurrent.futures
from tqdm import tqdm

# 配置
BASE_URL = "http://localhost:8080/short-url"
CREATE_URL_ENDPOINT = BASE_URL
GET_URL_ENDPOINT = BASE_URL
NUM_REQUESTS = 10000  # 总请求数
MAX_WORKERS = 50  # 并发数

def generate_random_url(length=10):
    """生成随机URL用于测试"""
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return f"https://example.com/{random_string}"

def create_short_url(url):
    """创建短链接"""
    try:
        response = requests.post(f"{CREATE_URL_ENDPOINT}", params={"url": url})
        if response.status_code == 201:
            return response.text
        else:
            print(f"创建短链接失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"创建短链接请求异常: {e}")
        return None

def get_original_url(short_url):
    """根据短链接获取原始URL"""
    try:
        response = requests.get(f"{GET_URL_ENDPOINT}", params={"shortUrl": short_url})
        if response.status_code == 200:
            return response.text
        else:
            print(f"获取原始URL失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"获取原始URL请求异常: {e}")
        return None

def test_create_performance():
    """测试创建短链接的性能"""
    print(f"\n开始测试创建短链接性能 ({NUM_REQUESTS} 请求)...")
    urls = [generate_random_url() for _ in range(NUM_REQUESTS)]
    start_time = time.time()
    
    short_urls = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 使用tqdm显示进度条
        for short_url in tqdm(executor.map(create_short_url, urls), total=NUM_REQUESTS, desc="创建短链接"):
            if short_url:
                short_urls.append(short_url)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"创建短链接测试完成:")
    print(f"总请求数: {NUM_REQUESTS}")
    print(f"成功请求数: {len(short_urls)}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每秒处理: {NUM_REQUESTS / elapsed_time:.2f} 请求")
    print(f"平均响应时间: {elapsed_time * 1000 / NUM_REQUESTS:.2f} 毫秒")
    
    return short_urls

def test_get_performance(short_urls):
    """测试获取原始URL的性能"""
    print(f"\n开始测试获取原始URL性能 ({len(short_urls)} 请求)...")
    start_time = time.time()
    
    successful_gets = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 使用tqdm显示进度条
        for original_url in tqdm(executor.map(get_original_url, short_urls), total=len(short_urls), desc="获取原始URL"):
            if original_url:
                successful_gets += 1
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"获取原始URL测试完成:")
    print(f"总请求数: {len(short_urls)}")
    print(f"成功请求数: {successful_gets}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每秒处理: {len(short_urls) / elapsed_time:.2f} 请求")
    print(f"平均响应时间: {elapsed_time * 1000 / len(short_urls):.2f} 毫秒")

def run_end_to_end_test():
    """运行端到端测试：先创建短链接，再获取原始URL"""
    print("=" * 50)
    print("开始短链接服务性能测试")
    print("=" * 50)
    
    # 测试创建短链接性能
    short_urls = test_create_performance()
    
    if short_urls:
        # 测试获取原始URL性能
        test_get_performance(short_urls)
    
    print("=" * 50)
    print("性能测试完成")
    print("=" * 50)

if __name__ == "__main__":
    run_end_to_end_test() 