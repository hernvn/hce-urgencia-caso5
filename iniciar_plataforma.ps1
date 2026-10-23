# Script de inicio automático (Backend FastAPI + Frontend React Vite)
Write-Host "Iniciando Plataforma HCE Interoperable y Telemedicina de Urgencia (Caso 5)..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'E:\Proyectos\arquitectura de software\backend'; python -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'E:\Proyectos\arquitectura de software\frontend'; npm run dev"

Write-Host "Servidores lanzados:" -ForegroundColor Green
Write-Host " -> Frontend React MVVM PWA: http://localhost:5173" -ForegroundColor Yellow
Write-Host " -> Backend FastAPI Swagger: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
