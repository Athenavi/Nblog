# 使用官方 Python 基础镜像
FROM python:3.13-slim-bullseye

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG=False \
    DJANGO_SETTINGS_MODULE=Nblog.settings \
    PYTHONPATH=/app

# 创建工作目录并设置为工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 设置入口点脚本
RUN chmod +x docker-entrypoint.sh

# 暴露端口
EXPOSE 8000

# 运行应用
ENTRYPOINT ["./docker-entrypoint.sh"]