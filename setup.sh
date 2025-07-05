#!/usr/bin/env bash

# 检查 choco 是否可用
if ! command -v choco &> /dev/null; then
  echo "错误：未检测到 Chocolatey，请先以管理员身份安装并配置好 choco。"
  exit 1
fi

echo "开始安装依赖（请确保在管理员权限下运行）..."

# 安装 Node.js LTS
choco install nodejs-lts -y

# 安装 Python
choco install python -y

# 安装 MySQL
choco install mysql -y

# 安装 Redis
choco install redis -y

# 安装 RabbitMQ 并启用管理插件
choco install rabbitmq -y
rabbitmq-plugins enable rabbitmq_management

# （可选）安装 Docker Desktop
choco install docker-desktop -y

echo "依赖安装完成！"
