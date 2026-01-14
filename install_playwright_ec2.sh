#!/bin/bash
# Script per installare Playwright e i browser sulla EC2

echo "================================================================"
echo "  INSTALLAZIONE PLAYWRIGHT SU EC2"
echo "================================================================"
echo ""

# Attiva il virtual environment
cd /home/ubuntu/offermanager
source venv/bin/activate

echo "✓ Virtual environment attivato"
echo ""

# Installa Playwright se non già installato
echo "📦 Verifica installazione Playwright..."
if ! python -c "import playwright" 2>/dev/null; then
    echo "  Installazione Playwright..."
    pip install playwright
    echo "✓ Playwright installato"
else
    echo "✓ Playwright già installato"
fi
echo ""

# Installa i browser di Playwright
echo "🌐 Installazione browser Playwright..."
python -m playwright install chromium
python -m playwright install-deps chromium
echo "✓ Browser Chromium installato"
echo ""

# Verifica installazione
echo "🔍 Verifica installazione..."
python -c "from playwright.sync_api import sync_playwright; print('✓ Playwright funzionante')" 2>&1
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo "  ✅ INSTALLAZIONE COMPLETATA!"
    echo "================================================================"
else
    echo ""
    echo "================================================================"
    echo "  ⚠ ERRORE DURANTE INSTALLAZIONE"
    echo "================================================================"
    exit 1
fi

