#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import string
import concurrent.futures
import os
import json
import sys
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# 配置matplotlib支持中文
def setup_chinese_font():
    """配置matplotlib支持中文显示"""
    # 尝试使用系统中文字体
    font_paths = [
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',  # Arch Linux常见路径
        '/usr/share/fonts/wenquanyi/wqy-microhei.ttc',        # WenQuanYi微米黑
        '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',     # 另一种路径
        '/usr/share/fonts/TTF/SourceHanSansCN-Regular.ttf',   # 思源黑体
        '/usr/share/fonts/noto/NotoSansCJK-Regular.ttc',      # Noto Sans CJK
        '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc'  # Google Noto CJK
    ]
    
    font_found = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            plt.rcParams['font.family'] = ['sans-serif']
            if 'wqy-microhei' in font_path:
                plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
            elif 'SourceHanSansCN' in font_path:
                plt.rcParams['font.sans-serif'] = ['Source Han Sans CN']
            else:
                plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            print(f"使用中文字体: {font_path}")
            font_found = True
            break
    
    if not font_found:
        # 使用matplotlib自带的DejaVu字体
        print("警告: 未找到合适的中文字体，图表中的中文可能无法正确显示")
        print("尝试安装中文字体: sudo pacman -S noto-fonts-cjk wqy-microhei")
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

# 从环境变量获取配置，如果不存在则使用默认值
BASE_URL = os.environ.get('SHORT_URL_API', 'http://localhost/short-url')
NUM_REQUESTS = int(os.environ.get('TEST_REQUESTS', '10000'))
MAX_WORKERS = int(os.environ.get('TEST_CONCURRENCY', '50'))
SAVE_RESULTS = os.environ.get('SAVE_RESULTS', 'true').lower() == 'true'
GENERATE_CHART = os.environ.get('GENERATE_CHART', 'true').lower() == 'true'

def generate_random_url(length=10):
    """生成随机URL用于测试"""
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return f"https://example.com/{random_string}"

def create_short_url(url):
    """创建短链接"""
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}", params={"url": url})
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 201:
            return {
                "status": "success", 
                "short_url": response.text, 
                "original_url": url,
                "response_time": response_time * 1000  # 转换为毫秒
            }
        else:
            return {
                "status": "error", 
                "code": response.status_code, 
                "message": response.text, 
                "original_url": url,
                "response_time": response_time * 1000
            }
    except Exception as e:
        return {
            "status": "exception", 
            "message": str(e), 
            "original_url": url,
            "response_time": 0
        }

def get_original_url(short_url):
    """根据短链接获取原始URL"""
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}", params={"shortUrl": short_url})
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            return {
                "status": "success", 
                "short_url": short_url, 
                "original_url": response.text,
                "response_time": response_time * 1000
            }
        else:
            return {
                "status": "error", 
                "code": response.status_code, 
                "message": response.text, 
                "short_url": short_url,
                "response_time": response_time * 1000
            }
    except Exception as e:
        return {
            "status": "exception", 
            "message": str(e), 
            "short_url": short_url,
            "response_time": 0
        }

def generate_performance_chart(create_times, get_times, output_file='performance_chart.png'):
    """生成性能测试图表"""
    # 设置中文字体
    setup_chinese_font()
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18))
    
    # 响应时间分布直方图
    bins = np.linspace(0, max(max(create_times), max(get_times)) * 1.1, 50)
    
    ax1.hist(create_times, bins=bins, alpha=0.7, label='创建短链接')
    ax1.hist(get_times, bins=bins, alpha=0.7, label='获取原始URL')
    ax1.set_title('响应时间分布')
    ax1.set_xlabel('响应时间 (毫秒)')
    ax1.set_ylabel('请求数量')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # 响应时间百分位数
    percentiles = [50, 75, 90, 95, 99]
    create_percentiles = [np.percentile(create_times, p) for p in percentiles]
    get_percentiles = [np.percentile(get_times, p) for p in percentiles]
    
    ax2.bar(
        [f"P{p}创建" for p in percentiles], 
        create_percentiles, 
        width=0.4, 
        label='创建短链接'
    )
    ax2.bar(
        [f"P{p}获取" for p in percentiles], 
        get_percentiles, 
        width=0.4, 
        label='获取原始URL'
    )
    ax2.set_title('响应时间百分位数')
    ax2.set_ylabel('响应时间 (毫秒)')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # 平均响应时间和吞吐量比较
    metrics = ['平均响应时间 (毫秒)', '吞吐量 (请求/秒)']
    create_metrics = [np.mean(create_times), NUM_REQUESTS / (np.sum(create_times) / 1000)]
    get_metrics = [np.mean(get_times), NUM_REQUESTS / (np.sum(get_times) / 1000)]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ax3.bar(x - width/2, create_metrics, width, label='创建短链接')
    ax3.bar(x + width/2, get_metrics, width, label='获取原始URL')
    
    ax3.set_title('性能指标比较')
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics)
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"性能图表已保存到: {output_file}")

def run_performance_test():
    """运行性能测试"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"performance_results_{timestamp}.json"
    chart_file = f"performance_chart_{timestamp}.png"
    
    print("=" * 50)
    print(f"短链接服务性能测试 - {NUM_REQUESTS} 请求, {MAX_WORKERS} 并发")
    print(f"API URL: {BASE_URL}")
    print("=" * 50)
    
    # 第一步：创建短链接
    print("\n[1/2] 测试创建短链接性能...")
    urls = [generate_random_url() for _ in range(NUM_REQUESTS)]
    
    start_time = time.time()
    create_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(create_short_url, url): url for url in urls}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=NUM_REQUESTS, desc="创建短链接"):
            result = future.result()
            create_results.append(result)
    
    create_end_time = time.time()
    create_elapsed_time = create_end_time - start_time
    
    # 从结果中提取成功的短链接和响应时间
    successful_creates = [r for r in create_results if r["status"] == "success"]
    create_times = [r["response_time"] for r in create_results if r["status"] == "success"]
    
    print(f"\n创建短链接测试完成:")
    print(f"  总请求数: {NUM_REQUESTS}")
    print(f"  成功请求数: {len(successful_creates)}")
    print(f"  总耗时: {create_elapsed_time:.2f} 秒")
    print(f"  平均每秒处理: {NUM_REQUESTS / create_elapsed_time:.2f} 请求")
    print(f"  平均响应时间: {np.mean(create_times):.2f} 毫秒")
    print(f"  99%响应时间: {np.percentile(create_times, 99):.2f} 毫秒")
    
    # 第二步：获取原始URL
    print("\n[2/2] 测试获取原始URL性能...")
    short_urls = [r["short_url"] for r in successful_creates]
    
    start_time = time.time()
    get_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(get_original_url, url): url for url in short_urls}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(short_urls), desc="获取原始URL"):
            result = future.result()
            get_results.append(result)
    
    get_end_time = time.time()
    get_elapsed_time = get_end_time - start_time
    
    # 从结果中提取成功的获取操作和响应时间
    successful_gets = [r for r in get_results if r["status"] == "success"]
    get_times = [r["response_time"] for r in get_results if r["status"] == "success"]
    
    print(f"\n获取原始URL测试完成:")
    print(f"  总请求数: {len(short_urls)}")
    print(f"  成功请求数: {len(successful_gets)}")
    print(f"  总耗时: {get_elapsed_time:.2f} 秒")
    print(f"  平均每秒处理: {len(short_urls) / get_elapsed_time:.2f} 请求")
    print(f"  平均响应时间: {np.mean(get_times):.2f} 毫秒")
    print(f"  99%响应时间: {np.percentile(get_times, 99):.2f} 毫秒")
    
    # 保存结果
    if SAVE_RESULTS:
        results = {
            "test_config": {
                "base_url": BASE_URL,
                "num_requests": NUM_REQUESTS,
                "max_workers": MAX_WORKERS,
                "timestamp": timestamp
            },
            "create_test": {
                "total_requests": NUM_REQUESTS,
                "successful_requests": len(successful_creates),
                "total_time": create_elapsed_time,
                "requests_per_second": NUM_REQUESTS / create_elapsed_time,
                "avg_response_time": np.mean(create_times),
                "p50_response_time": np.percentile(create_times, 50),
                "p90_response_time": np.percentile(create_times, 90),
                "p95_response_time": np.percentile(create_times, 95),
                "p99_response_time": np.percentile(create_times, 99)
            },
            "get_test": {
                "total_requests": len(short_urls),
                "successful_requests": len(successful_gets),
                "total_time": get_elapsed_time,
                "requests_per_second": len(short_urls) / get_elapsed_time,
                "avg_response_time": np.mean(get_times),
                "p50_response_time": np.percentile(get_times, 50),
                "p90_response_time": np.percentile(get_times, 90),
                "p95_response_time": np.percentile(get_times, 95),
                "p99_response_time": np.percentile(get_times, 99)
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n性能测试结果已保存到: {results_file}")
    
    # 生成图表
    if GENERATE_CHART and len(create_times) > 0 and len(get_times) > 0:
        generate_performance_chart(create_times, get_times, chart_file)
    
    print("=" * 50)
    print("性能测试完成")
    print("=" * 50)

if __name__ == "__main__":
    run_performance_test() 