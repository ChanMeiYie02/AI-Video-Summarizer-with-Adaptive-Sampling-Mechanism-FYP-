#!/bin/bash
export PATH=/usr/local/cuda/bin:$PATH
cd ~/llama-cpp-turboquant
rm -rf build
mkdir -p build
cd build
cmake -DGGML_CUDA=ON ..
cmake --build . --config Release -- -j$(nproc)
