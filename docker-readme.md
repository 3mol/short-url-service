# Short-URL 项目的Docker部署指南

## Docker 部署说明

本项目使用了多阶段构建的Dockerfile和docker-compose来简化部署。下面是相关的使用说明。

### Dockerfile

Dockerfile采用了多阶段构建（builder模式）：
- 第一阶段使用Maven镜像构建Java应用
- 第二阶段使用轻量级JRE镜像运行应用

主要环境变量配置：
- `DB_URL`: 数据库连接URL
- `DB_USERNAME`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `JPA_DDL_AUTO`: JPA自动建表策略
- `JPA_SHOW_SQL`: 是否显示SQL语句
- `SERVER_PORT`: 应用服务端口

### Docker Compose

docker-compose.yml 文件定义了两个服务：
1. `app`: 短URL应用服务
2. `db`: MySQL数据库服务

## 部署步骤

### 使用Docker Compose（推荐）

1. 克隆项目到本地
   ```bash
   git clone <项目仓库地址>
   cd short-url
   ```

2. 启动服务
   ```bash
   docker-compose up -d
   ```

3. 查看日志
   ```bash
   docker-compose logs -f app
   ```

4. 停止服务
   ```bash
   docker-compose down
   ```

### 仅使用Dockerfile构建（不推荐）

如果您已经有了MySQL服务，可以仅使用Dockerfile构建应用：

1. 构建Docker镜像
   ```bash
   docker build -t short-url-app .
   ```

2. 运行Docker容器
   ```bash
   docker run -d -p 8080:8080 \
     -e DB_URL=jdbc:mysql://<MySQL主机地址>:3306/short-url \
     -e DB_USERNAME=<用户名> \
     -e DB_PASSWORD=<密码> \
     -e JPA_DDL_AUTO=update \
     -e JPA_SHOW_SQL=true \
     -e SERVER_PORT=8080 \
     --name short-url-app \
     short-url-app
   ```

## 环境变量自定义

您可以通过修改docker-compose.yml文件中的environment部分来自定义环境变量：

```yaml
environment:
  - DB_URL=jdbc:mysql://db:3306/short-url?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=UTC
  - DB_USERNAME=short_url_user
  - DB_PASSWORD=short_url_pass
  - JPA_DDL_AUTO=update
  - JPA_SHOW_SQL=true
  - SERVER_PORT=8080
```

## 数据持久化

MySQL数据使用命名卷进行持久化存储：
```yaml
volumes:
  mysql-data:
```

这确保了容器重启后数据仍然保留。 