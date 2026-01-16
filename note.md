1. frontend/vite.config.ts 安裝react套件
```
npm i -D @vitejs/plugin-react
```
2. 需裝 docker/docker desktop 用於mysql image
3. frontend:
Step 1
```
npm create vite@latest frontend
cd frontend
npm install
```
Step 2
- 用我给你的 App.tsx → 覆盖 frontend/src/App.tsx
- 用我给你的 main.tsx → 覆盖 frontend/src/main.tsx
- 新建 frontend/src/api.ts → 粘贴我给你的代码


# 20260115
docker-compose.yml
使用方式：
启动：docker compose up -d
Adminer（看 DB）：浏览器打开 http://localhost:8080
服务器填：mysql_dev 或 mysql_test
用户：oms
密码：oms
数据库：oms_dev / oms_test

# 20260116
```
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt


$env:ENV="test"; uvicorn app.main:app --reload --port 8000

$env:ENV="test"; python -m scripts.seed
```