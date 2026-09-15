@echo off
title Meiyie Multimodal Video Summarizer Startup
echo ==========================================================
echo           STARTING MEIYIE SUMMARIZATION STACK
echo ==========================================================
echo.

echo 🚀 Starting local CUDA-accelerated llama-server in WSL...
start /min wsl /home/wissam/llama-cpp-turboquant/build/bin/llama-server -m /mnt/c/Users/admin/.cache/huggingface/hub/models--unsloth--gemma-4-E2B-it-GGUF/snapshots/f064409f340b34190993560b2168133e5dbae558/gemma-4-E2B-it-Q4_K_M.gguf --cache-type-k turbo3 --cache-type-v turbo3 --host 0.0.0.0 --port 8080 -c 32768 -ngl 99 -fa on

echo ⏳ Waiting 5 seconds for llama-server initialization...
timeout /t 5 /nobreak > nul

echo 💻 Starting Streamlit Dashboard...
vts\Scripts\streamlit run src\ui\app.py
