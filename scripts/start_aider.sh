#!/bin/bash
# Aider Integration Script for Local LLM
# Provides easy access to different model configurations

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default settings
MODEL="qwen2.5-coder:7b-instruct-q8_0"
MODE="primary"

# Help function
show_help() {
    echo "Aider Integration for Local LLM"
    echo ""
    echo "Usage: $0 [mode] [options]"
    echo ""
    echo "Modes:"
    echo "  primary    - Primary 7B Q8 model (default, highest quality)"
    echo "  fast       - Fast 7B Q4 model (quick iterations)"
    echo "  extended   - 7B Q6 model (more context)"
    echo "  complex    - 14B Q4 model (complex reasoning)"
    echo ""
    echo "Options:"
    echo "  --architect - Architect mode (planning and design)"
    echo "  --help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start with primary model"
    echo "  $0 fast              # Start with fast model"
    echo "  $0 complex --architect # Use 14B model in architect mode"
    echo ""
}

# Parse arguments
MODE=${1:-primary}

case "$MODE" in
    "primary")
        MODEL="qwen2.5-coder:7b-instruct-q8_0"
        DESC="Primary Q8 (highest quality, 30-40 tok/s)"
        ;;
    "fast")
        MODEL="qwen2.5-coder:7b-instruct-q4_K_M"
        DESC="Fast Q4 (quick drafts, 40-50 tok/s)"
        ;;
    "extended")
        MODEL="qwen2.5-coder:7b-instruct-q6_K"
        DESC="Extended Q6 (more context, 35-45 tok/s)"
        ;;
    "complex")
        MODEL="qwen2.5-coder:14b-instruct-q4_K_M"
        DESC="Complex 14B (deep reasoning, 15-20 tok/s)"
        ;;
    "--help"|"-h"|"help")
        show_help
        exit 0
        ;;
    *)
        echo "Unknown mode: $MODE"
        show_help
        exit 1
        ;;
esac

# Architect mode
ARCHITECT_FLAG=""
if [[ "$2" == "--architect" ]]; then
    ARCHITECT_FLAG="--architect"
    DESC="$DESC (Architect mode)"
fi

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Ollama is not running. Starting it...${NC}"
    ollama serve &
    sleep 3
fi

# Display startup info
echo "=========================================="
echo -e "${GREEN}Starting Aider with Local LLM${NC}"
echo "=========================================="
echo ""
echo "Model: $MODEL"
echo "Mode:  $DESC"
echo ""
echo "Aider will use your local LLM for all operations."
echo "No API calls, completely private and free."
echo ""
echo "Tips:"
echo "  - Use /model to switch models mid-session"
echo "  - Use /architect for planning mode"
echo "  - Use /help for Aider commands"
echo "  - Press Ctrl+D or type /exit to quit"
echo ""
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Aider with optimal settings
aider \
    --model "ollama_chat/$MODEL" \
    --no-auto-commits \
    --dark-mode \
    $ARCHITECT_FLAG \
    "$@"
