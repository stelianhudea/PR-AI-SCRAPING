#!/bin/bash

echo "==============================================="
echo "🚀 SISTEM AUTOMAT DE CONFIGURARE ULB AI"
echo "==============================================="

# 1. Verificăm dacă Ollama este instalat
if ! command -v ollama &> /dev/null
then
    echo "⚠️ Ollama nu este instalat. Îl instalăm acum..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama este deja instalat."
fi

# 2. Pornim serviciul Ollama și descărcăm Llama3
echo "⏳ Ne asigurăm că modelul Llama3 este descărcat..."
ollama pull llama3

# 3. Instalăm dependențele de sistem (necesită parolă sudo)
echo "🔐 Instalăm suportul pentru grafice (Tkinter)..."
sudo apt update && sudo apt install -y python3-tk python3-venv

# 4. Creăm și activăm mediul virtual (VENV)
if [ ! -d "venv" ]; then
    echo "📦 Creăm mediul virtual Python..."
    python3 -m venv venv
fi
source venv/bin/activate

# 5. Instalăm librăriile din requirements.txt
if [ -f "requirements2.txt" ]; then
    echo "📥 Instalăm librăriile Python (poate dura puțin)..."
    pip install --upgrade pip
    pip install -r requirements2.txt
else
    echo "❌ Eroare: Fișierul requirements.txt nu a fost găsit!"
    exit 1
fi

echo "==============================================="
echo "✅ CONFIGURARE FINALIZATĂ!"
echo "🚀 Pornim interfața principală..."
echo "==============================================="

# 6. Rulăm programul principal
python3 main.py