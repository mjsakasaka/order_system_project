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