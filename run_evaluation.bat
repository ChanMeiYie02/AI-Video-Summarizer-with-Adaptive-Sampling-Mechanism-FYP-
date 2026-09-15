@echo off
title Meiyie Batch Evaluation Runner
echo ==========================================================
echo           STARTING BATCH EVALUATION SUITE
echo ==========================================================
echo.


echo 🚀 Starting local llama-server inside WSL (minimized)...
start "Llama-Server" /min wsl /home/wissam/llama-cpp-turboquant/build/bin/llama-server -m /mnt/c/Users/admin/.cache/huggingface/hub/models--unsloth--gemma-4-E2B-it-GGUF/snapshots/f064409f340b34190993560b2168133e5dbae558/gemma-4-E2B-it-Q4_K_M.gguf --cache-type-k turbo3 --cache-type-v turbo3 --host 0.0.0.0 --port 8080 -c 32768 -ngl 99 -fa on

echo ⏳ Waiting 10 seconds for the model weights to load on GPU...
timeout /t 10 /nobreak > nul
echo.

echo 🔬 Starting sequential batch experiment suite on 6 videos...
echo.
vts\Scripts\python.exe evaluation\run_batch.py

echo.
echo ==========================================================
echo 🎉 BATCH SUITE RUN COMPLETED SUCCESSFULLY!
echo ==========================================================
pause
