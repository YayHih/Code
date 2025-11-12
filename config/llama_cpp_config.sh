#!/bin/bash
# llama.cpp server configuration for optimal performance
# Use this if you want more control than Ollama provides

# Model paths (adjust as needed)
MODEL_7B_Q8="/path/to/qwen2.5-coder-7b-instruct-q8_0.gguf"
MODEL_7B_Q6="/path/to/qwen2.5-coder-7b-instruct-q6_K.gguf"
MODEL_14B_Q4="/path/to/qwen2.5-coder-14b-instruct-q4_K_M.gguf"

# Configuration for 7B Q8 - Primary coding model (Full GPU)
start_7b_q8() {
    echo "Starting Qwen2.5-Coder-7B-Q8 (Primary - Full GPU)"
    ./llama-server \
        --model "$MODEL_7B_Q8" \
        --host 0.0.0.0 \
        --port 8080 \
        --ctx-size 32768 \
        --n-gpu-layers 999 \
        --threads 4 \
        --batch-size 512 \
        --cache-type-k q8_0 \
        --cache-type-v q4_0 \
        --flash-attn \
        --mlock \
        --temp 0.15 \
        --top-p 0.95 \
        --top-k 40 \
        --repeat-penalty 1.1 \
        --rope-freq-base 1000000

    # Expected: 30-40 tok/s, 8.5GB VRAM, 24-32K safe context
}

# Configuration for 7B Q6 - Extended context (Full GPU)
start_7b_q6() {
    echo "Starting Qwen2.5-Coder-7B-Q6 (Extended Context - Full GPU)"
    ./llama-server \
        --model "$MODEL_7B_Q6" \
        --host 0.0.0.0 \
        --port 8081 \
        --ctx-size 32768 \
        --n-gpu-layers 999 \
        --threads 4 \
        --batch-size 512 \
        --cache-type-k q8_0 \
        --cache-type-v q4_0 \
        --flash-attn \
        --mlock \
        --temp 0.15 \
        --top-p 0.95 \
        --rope-freq-base 1000000

    # Expected: 35-45 tok/s, 6.5GB VRAM, 32K safe context
}

# Configuration for 14B Q4 - Complex reasoning (Hybrid GPU/CPU)
start_14b_q4() {
    echo "Starting Qwen2.5-Coder-14B-Q4 (Complex Tasks - Hybrid)"
    ./llama-server \
        --model "$MODEL_14B_Q4" \
        --host 0.0.0.0 \
        --port 8082 \
        --ctx-size 16384 \
        --n-gpu-layers 22 \
        --threads 12 \
        --batch-size 512 \
        --cache-type-k q8_0 \
        --cache-type-v q4_0 \
        --flash-attn \
        --mlock \
        --temp 0.15 \
        --top-p 0.95 \
        --rope-freq-base 1000000

    # Expected: 15-20 tok/s, 11.5GB VRAM, 16K context
    # Note: 22 GPU layers gives optimal hybrid performance
}

# VRAM monitoring function
monitor_vram() {
    echo "Monitoring VRAM usage..."
    watch -n 1 'nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits'
}

# Test function to find optimal GPU layer count for hybrid mode
test_gpu_layers() {
    MODEL=$1
    START_LAYERS=${2:-10}
    END_LAYERS=${3:-30}
    STEP=${4:-2}

    echo "Testing GPU layer configurations for $MODEL"
    echo "This will help find the optimal GPU/CPU split"
    echo ""

    for layers in $(seq $START_LAYERS $STEP $END_LAYERS); do
        echo "Testing with $layers GPU layers..."

        # Run test prompt and measure speed
        result=$(./llama-cli \
            --model "$MODEL" \
            --n-gpu-layers $layers \
            --threads 12 \
            --prompt "def fibonacci(n):" \
            --n-predict 100 \
            2>&1 | grep "tok/s")

        echo "  Layers: $layers - $result"
    done

    echo ""
    echo "Use the configuration with highest tok/s for your model"
}

# Main menu
case "${1:-help}" in
    "7b-q8")
        start_7b_q8
        ;;
    "7b-q6")
        start_7b_q6
        ;;
    "14b-q4")
        start_14b_q4
        ;;
    "monitor")
        monitor_vram
        ;;
    "test")
        test_gpu_layers "$2" "${3:-10}" "${4:-30}" "${5:-2}"
        ;;
    "help"|*)
        echo "llama.cpp Configuration Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  7b-q8     - Start primary 7B Q8 model (full GPU)"
        echo "  7b-q6     - Start 7B Q6 model (extended context)"
        echo "  14b-q4    - Start 14B Q4 model (hybrid GPU/CPU)"
        echo "  monitor   - Monitor VRAM usage"
        echo "  test      - Test optimal GPU layer count"
        echo "  help      - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 7b-q8                    # Start primary model"
        echo "  $0 test /path/to/model.gguf # Test layer configurations"
        echo ""
        ;;
esac
