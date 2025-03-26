#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始清理 Kafka...${NC}"

# 列出所有 topics
echo -e "${GREEN}当前存在的 topics:${NC}"
docker exec short-url-kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# 删除 short-url-topic
echo -e "${GREEN}正在删除 short-url-topic...${NC}"
docker exec short-url-kafka kafka-topics.sh --delete --topic short-url-topic --bootstrap-server localhost:9092

# 重新创建 topic
echo -e "${GREEN}正在重新创建 short-url-topic...${NC}"
docker exec short-url-kafka kafka-topics.sh --create --topic short-url-topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# 验证 topic 是否创建成功
echo -e "${GREEN}验证 topics:${NC}"
docker exec short-url-kafka kafka-topics.sh --list --bootstrap-server localhost:9092

echo -e "${GREEN}Kafka 清理完成！${NC}" 