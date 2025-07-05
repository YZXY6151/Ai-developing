# frontend/Dockerfile
# 使用较新的 Node 18 Alpine 版，体积小且官方长期支持
FROM node:18-alpine

WORKDIR /app

# 复制依赖清单并安装（锁文件可以是 package-lock.json 或 pnpm-lock.yaml）
COPY package.json package-lock.json* ./
RUN npm ci

# 复制前端源代码（此时上下文根 == frontend 目录）
COPY . .

# Vite dev server 监听所有网络接口
ENV HOST=0.0.0.0
ENV PORT=5173

EXPOSE 5173

# 启动开发服务器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
