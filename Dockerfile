# 使用基础镜像
FROM python:3.8

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . .

# 安装项目所需的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器的端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py

# 运行 Flask 应用
CMD ["flask", "run", "--host", "0.0.0.0"]
