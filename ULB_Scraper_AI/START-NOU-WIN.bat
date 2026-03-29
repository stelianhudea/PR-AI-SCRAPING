@echo off
title ULB AI - Setup & Run (Windows)
echo ===============================================
echo 🚀 SISTEM AUTOMAT DE CONFIGURARE ULB AI - WINDOWS
echo ===============================================

:: 1. Verificăm dacă Python este instalat
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Eroare: Python nu este instalat sau nu este in PATH!
    echo Te rog instaleaza Python de pe python.org si bifeaza 'Add to PATH'.
    pause
    exit /b
)

:: 2. Creăm mediul virtual (VENV) dacă nu există
if not exist "venv" (
    echo 📦 Creăm mediul virtual Python...
    python -m venv venv
)

:: 3. Activăm mediul virtual și instalăm librăriile
echo 📥 Activăm mediul și instalăm librăriile...
call venv\Scripts\activate
python -m pip install --upgrade pip
if exist "requirements2.txt" (
    pip install -r requirements.txt
) else (
    echo ⚠️ Atentie: requirements2.txt nu a fost gasit. 
    echo Instalam manual pachetele de baza...
    pip install pandas requests beautifulsoup4 langchain ollama matplotlib
)

:: 4. Verificăm Ollama (trebuie instalat manual pe Windows de pe ollama.com)
echo ⏳ Verificăm conexiunea cu Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ollama nu pare sa fie instalat. 
    echo Te rog descarca-l de pe https://ollama.com/download/windows
    pause
) else (
    echo ✅ Ollama detectat. Ne asiguram ca avem modelul Llama3...
    ollama pull llama3
)

echo ===============================================
echo ✅ CONFIGURARE FINALIZATĂ!
echo 🚀 Pornim interfața principală...
echo ===============================================

:: 5. Rulăm programul
python main.py

pause