# 第一阶段：构建阶段
FROM maven:3.9.6-eclipse-temurin-17 AS builder

# 设置工作目录
WORKDIR /app

# 复制Maven配置文件
COPY pom.xml .
COPY .mvn .mvn

# 复制 Maven settings.xml
COPY .mvn/settings/settings.xml /root/.m2/settings.xml

# 下载所有依赖项，但不构建应用程序
# 这一步骤依赖将被缓存，除非pom.xml文件发生变化
RUN mvn dependency:go-offline -B

# 复制源代码
COPY src src

# 编译并打包应用程序
RUN mvn package -DskipTests

# 第二阶段：运行阶段
FROM eclipse-temurin:17-jre-jammy

# 设置工作目录
WORKDIR /app

# 从构建阶段复制JAR文件
COPY --from=builder /app/target/*.jar app.jar

# 暴露数据库相关环境变量（根据application.properties中的配置）
ENV DB_URL=jdbc:mysql://localhost:3306/short-url
ENV DB_USERNAME=root
ENV DB_PASSWORD=123456
ENV JPA_DDL_AUTO=update
ENV JPA_SHOW_SQL=true
ENV SERVER_PORT=8080

# 暴露 Kafka 相关环境变量
ENV SPRING_KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV SPRING_KAFKA_CONSUMER_GROUP_ID=short-url-group
# 暴露 Redis 相关环境变量
ENV SPRING_REDIS_HOST=redis
ENV SPRING_REDIS_PORT=6379
ENV SPRING_REDIS_DB=0

# 暴露端口
EXPOSE ${SERVER_PORT}

# 启动应用程序
ENTRYPOINT ["java", \
    "-Dspring.datasource.url=${DB_URL}", \
    "-Dspring.datasource.username=${DB_USERNAME}", \
    "-Dspring.datasource.password=${DB_PASSWORD}", \
    "-Dspring.jpa.hibernate.ddl-auto=${JPA_DDL_AUTO}", \
    "-Dspring.jpa.show-sql=${JPA_SHOW_SQL}", \
    "-Dserver.port=${SERVER_PORT}", \
    "-Dspring.kafka.bootstrap-servers=${SPRING_KAFKA_BOOTSTRAP_SERVERS}", \
    "-Dspring.kafka.consumer.group-id=${SPRING_KAFKA_CONSUMER_GROUP_ID}", \
    "-Dspring.data.redis.host=${SPRING_REDIS_HOST}", \
    "-Dspring.data.redis.port=${SPRING_REDIS_PORT}", \
    "-Dspring.data.redis.database=${SPRING_REDIS_DB}", \
    "-jar", "app.jar"]