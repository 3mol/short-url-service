# 短链接服务性能测试工具

这个项目包含了几个用于测试短链接服务性能的Python脚本，可以测试创建短链接和获取原始URL的性能。

## 环境要求

- Python 3.6+
- 依赖包：requests, tqdm, matplotlib, numpy

安装依赖：
```bash
pip install requests tqdm matplotlib numpy
```

### Linux中文字体支持

在Linux系统（特别是Arch Linux）上，如果测试图表中的中文显示为方块，需要安装中文字体：

```bash
# Arch Linux/Manjaro
sudo pacman -S noto-fonts-cjk wqy-microhei

# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk fonts-wqy-microhei

# CentOS/RHEL
sudo yum install google-noto-sans-cjk-fonts wqy-microhei-fonts
```

安装完成后，重新运行脚本即可正确显示中文。

## 脚本说明

项目包含三个测试脚本，从简单到复杂，功能逐渐增强：

### 1. 基础版测试脚本 (test_short_url_performance.py)

最简单的测试脚本，使用固定配置测试创建和获取短链接的性能。

使用方法：
```bash
python test_short_url_performance.py
```

### 2. 高级版测试脚本 (advanced_test_short_url.py)

支持命令行参数配置的高级测试脚本，可以选择测试类型、设置请求数量、并发数等。

使用方法：
```bash
# 测试创建短链接 (5000请求，100并发)
python advanced_test_short_url.py --type create --requests 5000 --concurrency 100

# 测试获取原始URL (从文件加载短链接)
python advanced_test_short_url.py --type get --url-file urls.json

# 完整端到端测试
python advanced_test_short_url.py --type both --requests 10000 --output results.json
```

命令行参数：
- `--type, -t`: 测试类型：创建短链接(create)、获取原始URL(get)或两者都测试(both)
- `--requests, -r`: 请求数量
- `--concurrency, -c`: 并发数
- `--base-url, -u`: API基础URL
- `--output, -o`: 输出结果保存文件名
- `--url-file, -f`: 包含短链接的JSON文件(用于get测试)
- `--verbose, -v`: 显示详细信息

### 3. 可视化测试脚本 (visual_test_short_url.py)

使用环境变量配置的测试脚本，可以生成性能图表，全面分析性能数据。

使用方法：
```bash
# 使用默认配置
python visual_test_short_url.py

# 使用环境变量配置
SHORT_URL_API=http://localhost:8080/short-url TEST_REQUESTS=5000 TEST_CONCURRENCY=100 python visual_test_short_url.py
```

环境变量说明：
- `SHORT_URL_API`: API基础URL，默认为http://localhost:8080/short-url
- `TEST_REQUESTS`: 请求数量，默认为10000
- `TEST_CONCURRENCY`: 并发数，默认为50
- `SAVE_RESULTS`: 是否保存结果，默认为true
- `GENERATE_CHART`: 是否生成图表，默认为true

## 测试结果说明

脚本会输出以下性能指标：

1. **创建短链接**和**获取原始URL**的性能数据：
   - 总请求数
   - 成功请求数
   - 总耗时
   - 平均每秒处理请求数（吞吐量）
   - 平均响应时间
   - 各百分位响应时间（P50, P90, P95, P99）

2. **visual_test_short_url.py**额外生成的图表：
   - 响应时间分布直方图
   - 响应时间百分位数柱状图
   - 平均响应时间和吞吐量比较图

## 使用场景

- 测试短链接服务在高并发下的性能表现
- 评估系统的响应时间和吞吐量
- 分析系统性能瓶颈
- 比较不同配置下的性能差异 