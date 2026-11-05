#!/bin/bash

# Go to project root
cd "$(dirname "$0")/.." || exit 1

echo "====================================================="
echo "  Scientific English Agents (v3.0.0) Setup           "
echo "====================================================="
echo ""
echo "Select AI Provider:"
echo "A: Claude Code (Recommended for Mac/Win, needs Node.js)"
echo "B: Mistral (EU-hosted, needs Python 3.8 - 3.12)"
read -p "Choice (A/B): " choice

if [[ "$choice" == "A" || "$choice" == "a" ]]; then
    echo -e "\n[+] Setting up Claude Code..."
    npm install -g @anthropic-ai/claude-code
    cp providers/anthropic/CLAUDE.md.template CLAUDE.md

    read -p "Enter Anthropic API key (sk-ant-...): " apikey
    echo "ANTHROPIC_API_KEY=$apikey" > .env
    echo "PROVIDER=anthropic" >> .env

    echo -e "\nDone! ✅ Configure CLAUDE.md and run 'claude'."

elif [[ "$choice" == "B" || "$choice" == "b" ]]; then
    echo -e "\n[+] Checking Python version..."

    # Check if python or python3 command exists
    if command -v python &>/dev/null; then
        PY_CMD="python"
    elif command -v python3 &>/dev/null; then
        PY_CMD="python3"
    else
        echo "WARNING: Python not found. Please install Python."
        exit 1
    fi

    PY_VER=$($PY_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
    PY_MAJOR=$($PY_CMD -c 'import sys; print(sys.version_info.major)' 2>/dev/null)
    PY_MINOR=$($PY_CMD -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)

    if [ "$PY_MAJOR" -ne 3 ] || [ "$PY_MINOR" -lt 8 ] || [ "$PY_MINOR" -gt 12 ]; then
        echo -e "\033[0;31mWARNING: Python version must be between 3.8 and 3.12. You have $PY_VER.\033[0m"
        echo "Dependencies (like opentelemetry) may fail on Python 3.13+."
        read -p "Continue anyway? (Y/N): " py_cont
        if [[ ! "$py_cont" =~ ^[Yy]$ ]]; then
            echo "Exiting."
            exit 1
        fi
    else
        echo -e "\033[0;32mPython $PY_VER detected. Perfect!\033[0m"
    fi

    echo -e "\n[+] Setting up Mistral..."
    pip install mistralai python-dotenv
    cp providers/mistral/MISTRAL.md.template MISTRAL.md

    read -p "Enter Mistral API key: " apikey
    echo "MISTRAL_API_KEY=$apikey" > .env
    echo "MISTRAL_MODEL=mistral-large-latest" >> .env
    echo "PROVIDER=mistral" >> .env

    echo -e "\nDone! ✅ Configure MISTRAL.md and run 'python providers/mistral/session.py'."
else
    echo "Invalid choice. Exiting."
    exit 1
fi
