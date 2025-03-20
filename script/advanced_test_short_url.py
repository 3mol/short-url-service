#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import string
import concurrent.futures
import argparse
import json
import sys
import csv
from tqdm import tqdm
from datetime import datetime

# 默认配置
DEFAULT_CONFIG = {
    "base_url": "http://localhost:8080/short-url",
    "requests": 10000,
    "concurrency": 50,
    "output_file": None,
    "save_urls": False,
    "url_file": None,
    "verbose": False
}

def generate_random_url(length=10):
    """生成随机URL用于测试"""
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return f"https://example.com/{random_string}"

def create_short_url(url, base_url, verbose=False):
    """创建短链接"""
    try:
        response = requests.post(f"{base_url}", params={"url": url})
        if response.status_code == 201:
            if verbose:
                print(f"创建成功: {url} -> {response.text}")
            return {"status": "success", "short_url": response.text, "original_url": url}
        else:
            if verbose:
                print(f"创建失败: {response.status_code} - {response.text}")
            return {"status": "error", "code": response.status_code, "message": response.text, "original_url": url}
    except Exception as e:
        if verbose:
            print(f"请求异常: {e}")
        return {"status": "exception", "message": str(e), "original_url": url}

def get_original_url(short_url, base_url, verbose=False):
    """根据短链接获取原始URL"""
    try:
        response = requests.get(f"{base_url}", params={"shortUrl": short_url})
        if response.status_code == 200:
            if verbose:
                print(f"获取成功: {short_url} -> {response.text}")
            return {"status": "success", "short_url": short_url, "original_url": response.text}
        else:
            if verbose:
                print(f"获取失败: {response.status_code} - {response.text}")
            return {"status": "error", "code": response.status_code, "message": response.text, "short_url": short_url}
    except Exception as e:
        if verbose:
            print(f"请求异常: {e}")
        return {"status": "exception", "message": str(e), "short_url": short_url}

def test_create_performance(config):
    """测试创建短链接的性能"""
    num_requests = config["requests"]
    concurrency = config["concurrency"]
    base_url = config["base_url"]
    verbose = config["verbose"]
    
    print(f"\n开始测试创建短链接性能 ({num_requests} 请求, {concurrency} 并发)...")
    urls = [generate_random_url() for _ in range(num_requests)]
    start_time = time.time()
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # 使用tqdm显示进度条
        futures = {executor.submit(create_short_url, url, base_url, verbose): url for url in urls}
        for future in tqdm(concurrent.futures.as_completed(futures), total=num_requests, desc="创建短链接"):
            results.append(future.result())
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 分析结果
    successful = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    exceptions = [r for r in results if r["status"] == "exception"]
    
    print(f"\n创建短链接测试完成:")
    print(f"总请求数: {num_requests}")
    print(f"成功请求数: {len(successful)}")
    print(f"错误请求数: {len(errors)}")
    print(f"异常请求数: {len(exceptions)}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每秒处理: {num_requests / elapsed_time:.2f} 请求")
    print(f"平均响应时间: {elapsed_time * 1000 / num_requests:.2f} 毫秒")
    
    # 保存成功的短链接以供后续测试
    if config["save_urls"] and config["output_file"]:
        save_results_to_file(successful, config["output_file"])
        print(f"已保存 {len(successful)} 个短链接到 {config['output_file']}")
    
    return successful

def test_get_performance(config):
    """测试获取原始URL的性能"""
    if not config["url_file"]:
        print("错误: 获取原始URL测试需要提供url文件 (--url-file)")
        return []
    
    short_urls = load_urls_from_file(config["url_file"])
    if not short_urls:
        print("错误: 无法从文件加载短链接")
        return []
    
    num_requests = min(config["requests"], len(short_urls))
    concurrency = config["concurrency"]
    base_url = config["base_url"]
    verbose = config["verbose"]
    
    print(f"\n开始测试获取原始URL性能 ({num_requests} 请求, {concurrency} 并发)...")
    selected_urls = short_urls[:num_requests]
    start_time = time.time()
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # 使用tqdm显示进度条
        futures = {executor.submit(get_original_url, url["short_url"], base_url, verbose): url for url in selected_urls}
        for future in tqdm(concurrent.futures.as_completed(futures), total=num_requests, desc="获取原始URL"):
            results.append(future.result())
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 分析结果
    successful = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    exceptions = [r for r in results if r["status"] == "exception"]
    
    print(f"\n获取原始URL测试完成:")
    print(f"总请求数: {num_requests}")
    print(f"成功请求数: {len(successful)}")
    print(f"错误请求数: {len(errors)}")
    print(f"异常请求数: {len(exceptions)}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每秒处理: {num_requests / elapsed_time:.2f} 请求")
    print(f"平均响应时间: {elapsed_time * 1000 / num_requests:.2f} 毫秒")
    
    return successful

def run_end_to_end_test(config):
    """运行端到端测试：先创建短链接，再获取原始URL"""
    print("=" * 50)
    print("开始短链接服务端到端性能测试")
    print("=" * 50)
    
    # 测试创建短链接性能
    temp_file = f"temp_urls_{int(time.time())}.json"
    create_config = config.copy()
    create_config["save_urls"] = True
    create_config["output_file"] = temp_file
    
    test_create_performance(create_config)
    
    # 测试获取原始URL性能
    get_config = config.copy()
    get_config["url_file"] = temp_file
    test_get_performance(get_config)
    
    print("=" * 50)
    print("端到端性能测试完成")
    print("=" * 50)

def save_results_to_file(results, filename):
    """保存测试结果到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存结果失败: {e}")

def load_urls_from_file(filename):
    """从文件加载URL"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载URL失败: {e}")
        return []

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='短链接服务性能测试工具')
    parser.add_argument('--type', '-t', choices=['create', 'get', 'both'], default='both',
                        help='测试类型: 创建短链接(create), 获取原始URL(get), 或两者都测试(both)')
    parser.add_argument('--requests', '-r', type=int, default=DEFAULT_CONFIG["requests"],
                        help=f'请求数量 (默认: {DEFAULT_CONFIG["requests"]})')
    parser.add_argument('--concurrency', '-c', type=int, default=DEFAULT_CONFIG["concurrency"],
                        help=f'并发数 (默认: {DEFAULT_CONFIG["concurrency"]})')
    parser.add_argument('--base-url', '-u', default=DEFAULT_CONFIG["base_url"],
                        help=f'API基础URL (默认: {DEFAULT_CONFIG["base_url"]})')
    parser.add_argument('--output', '-o', default=DEFAULT_CONFIG["output_file"],
                        help='输出结果保存文件名')
    parser.add_argument('--url-file', '-f', default=DEFAULT_CONFIG["url_file"],
                        help='包含短链接的JSON文件 (用于get测试)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细信息')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    config = {
        "base_url": args.base_url,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "output_file": args.output,
        "url_file": args.url_file,
        "verbose": args.verbose,
        "save_urls": False
    }
    
    print(f"配置信息:")
    for key, value in config.items():
        if value is not None:
            print(f"  {key}: {value}")
    
    if args.type == 'create':
        test_create_performance(config)
    elif args.type == 'get':
        test_get_performance(config)
    else:  # 'both'
        run_end_to_end_test(config)

if __name__ == "__main__":
    main() 