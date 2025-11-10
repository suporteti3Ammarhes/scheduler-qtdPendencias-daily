#!/bin/bash

echo "===================================="
echo " Construindo Scheduler Executável"
echo "===================================="
echo ""

# Verificar se PyInstaller está instalado
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller não encontrado. Instalando..."
    pip3 install pyinstaller
fi

echo ""
echo "Limpando builds anteriores..."
rm -rf build dist *.spec

echo ""
echo "Construindo executável..."
pyinstaller --name=PendenciasScheduler \
    --onefile \
    --console \
    --add-data ".env:." \
    --hidden-import=pyodbc \
    --hidden-import=schedule \
    --hidden-import=pandas \
    --hidden-import=dotenv \
    --hidden-import=app.services.pendencias \
    --hidden-import=app.services.database \
    --hidden-import=app.models \
    --hidden-import=app.core \
    --hidden-import=app.utils \
    --collect-all schedule \
    --collect-all pyodbc \
    --collect-all pandas \
    app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================="
    echo " Build concluído com sucesso!"
    echo "===================================="
    echo ""
    echo "O executável está em: dist/PendenciasScheduler"
    echo ""
    echo "Para executar:"
    echo "  1. Copie o arquivo .env para a pasta do executável"
    echo "  2. Execute: ./dist/PendenciasScheduler"
    echo ""
else
    echo ""
    echo "===================================="
    echo " Erro durante o build!"
    echo "===================================="
    echo ""
fi
