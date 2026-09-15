# 🎬 Meiyie Migration Guide: Moving to Another PC

This guide walks you through transferring the **Meiyie Multimodal Video Summarizer** stack to a new machine. Because this project relies on a hybrid Windows/WSL2 setup, CUDA acceleration, and large local models, direct copying of the entire folder (especially virtual environments) will not work. Follow these steps to ensure a smooth transition.

---

## 📋 System & Hardware Requirements

Ensure the new PC meets these specifications:
*   **OS:** Windows 10/11 (with WSL2 enabled).
*   **GPU:** NVIDIA GPU with ≥16 GB VRAM recommended (to run Gemma 4 models smoothly).
*   **RAM:** ≥32 GB system RAM recommended.
*   **Storage:** ~10-15 GB of free space for virtual environments, compiling C++ repositories, and model weights.

---

## 🧰 Step 1: Install System Prerequisites (New PC)

Install the following software on the new host Windows PC:

1.  **Python 3.11:** Download and install [Python 3.11.x](https://www.python.org/downloads/release/python-3110/).
    > [!IMPORTANT]
    > Ensure you check **"Add Python 3.11 to PATH"** during installation.
2.  **Git for Windows:** Download and install [Git](https://git-scm.com/downloads).
3.  **FFmpeg:**
    *   Download the Windows build from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
    *   Extract the folder and add its `bin/` directory to your Windows System environment variable `PATH`.
    *   Verify by running `ffmpeg -version` in a command prompt.
4.  **NVIDIA CUDA Toolkit:**
    *   Install the NVIDIA CUDA Toolkit (version 12.1+ recommended) on Windows to allow GPU acceleration for PyTorch.
5.  **WSL2 (Windows Subsystem for Linux):**
    *   Open PowerShell as Administrator and run:
        ```powershell
        wsl --install
        ```
    *   Install Ubuntu from the Microsoft Store if not installed automatically.
    *   Configure CUDA support inside WSL2 by following the [NVIDIA WSL CUDA Guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html).

---

## 🚚 Step 2: Transfer Project Files

When copying files from your current PC to the new PC:

1.  **Copy the project workspace** (`Meiyie/`) but **DO NOT** copy these directories:
    *   ❌ `vts/` (Windows virtual environment - must be rebuilt)
    *   ❌ `vts_linux/` (Linux virtual environment - must be rebuilt)
    *   ❌ `data/frames/*` or `data/audio/*` (Temporary caches, unless you want to preserve past runs)
2.  **Model Weights Cache (Optional but recommended to avoid huge downloads):**
    *   On your current PC, Hugging Face models are cached under:
        `C:\Users\admin_mtds\.cache\huggingface\`
    *   Copy the `huggingface/` directory from your old PC and paste it on the new PC under:
        `C:\Users\<YOUR_NEW_WINDOWS_USERNAME>\.cache\huggingface\`
    *   This copies both the Hugging Face Transformers model (`google/gemma-4-E2B-it`) and the GGUF model file (`unsloth/gemma-4-E2B-it-GGUF`).

---

## 🐍 Step 3: Rebuild the Python Environment (Windows)

On the new PC, navigate to the `Meiyie/` workspace in PowerShell and run:

```powershell
# 1. Create a fresh virtual environment
python -m venv vts

# 2. Activate the environment
.\vts\Scripts\activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Install additional external packages not in requirements.txt
pip install transnetv2-pytorch
pip install yt-dlp
```

---

## 🐧 Step 4: Compile `llama-server` in WSL2

The summarization backend runs a custom `llama-server` compiled with CUDA support inside your WSL2 environment.

1.  Open your WSL2 terminal (Ubuntu).
2.  Copy the `llama-cpp-turboquant` repository directory into your WSL environment, or clone/retrieve it inside WSL. Alternatively, copy the folder from Windows:
    ```bash
    cp -r /mnt/c/Users/<YOUR_NEW_WINDOWS_USERNAME>/Desktop/Meiyie/models/llama-cpp-turboquant ~/llama-cpp-turboquant
    ```
3.  Compile `llama-server` with CUDA enabled:
    ```bash
    cd ~/llama-cpp-turboquant
    mkdir build
    cd build
    # Configure with CUDA support (GGML_CUDA=ON or LLAMA_CUDA=1 depending on cmake configuration)
    cmake -DGGML_CUDA=ON ..
    # Compile
    cmake --build . --config Release -- -j$(nproc)
    ```
    *This creates the executable at `~/llama-cpp-turboquant/build/bin/llama-server`.*

---

## ⚙️ Step 5: Update Configuration & Startup Scripts

Since file paths contain your Windows and WSL usernames, you **MUST** update [run.bat](file:///c:/Users/admin_mtds/OneDrive/Desktop/Meiyie/run.bat) to match your new system names.

### Modifying [run.bat](file:///c:/Users/admin_mtds/OneDrive/Desktop/Meiyie/run.bat):

Open `run.bat` in a text editor and replace the usernames.

#### Example modification:
```diff
- start /min wsl /home/admin_mtds/llama-cpp-turboquant/build/bin/llama-server -m /mnt/c/Users/admin_mtds/.cache/huggingface/hub/models--unsloth--gemma-4-E2B-it-GGUF/snapshots/f064409f340b34190993560b2168133e5dbae558/gemma-4-E2B-it-Q4_K_M.gguf --cache-type-k turbo3 --cache-type-v turbo3 --host 0.0.0.0 --port 8080 -c 32768 -ngl 99 -fa on
+ start /min wsl /home/<NEW_WSL_USERNAME>/llama-cpp-turboquant/build/bin/llama-server -m /mnt/c/Users/<NEW_WINDOWS_USERNAME>/.cache/huggingface/hub/models--unsloth--gemma-4-E2B-it-GGUF/snapshots/f064409f340b34190993560b2168133e5dbae558/gemma-4-E2B-it-Q4_K_M.gguf --cache-type-k turbo3 --cache-type-v turbo3 --host 0.0.0.0 --port 8080 -c 32768 -ngl 99 -fa on
```

> [!TIP]
> If you prefer not to rely on the Hugging Face cache directory on Windows, you can move the GGUF file `gemma-4-E2B-it-Q4_K_M.gguf` directly into the `models/` directory in your workspace and update `run.bat` to refer to `/mnt/c/Users/<NEW_WINDOWS_USERNAME>/Desktop/Meiyie/models/gemma-4-E2B-it-Q4_K_M.gguf`.

---

## 🚀 Step 6: Launch on the New PC

Once all configurations are updated:

1.  Run the startup batch script in Windows CMD/PowerShell:
    ```powershell
    .\run.bat
    ```
2.  This script will automatically:
    *   Spawn the `llama-server` in the background inside WSL.
    *   Wait 5 seconds for initialization.
    *   Launch the Streamlit dashboard on `http://localhost:8501`.
