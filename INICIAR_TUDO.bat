@echo off
cd /d %~dp0
start "FitControl Backend" cmd /k "cd backend && npm install && npm run dev"
start "FitControl Frontend" cmd /k "cd frontend && npm install && npm run dev"
