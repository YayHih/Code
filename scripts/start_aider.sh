#!/bin/bash
# Improved Aider Integration with better local LLM compatibility

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default settings
MODEL="qwen2.5-coder:7b-instruct-q8_0"
MODE="primary"
EDIT_FORMAT="diff"  # More forgiving format for local models

# Help function
show_help() {
    echo "Aider Integration for Local LLM (Optimized for Local Models)"
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
    echo "  --architect     - Architect mode (planning, more reliable with local models)"
    echo "  --whole         - Use whole file editing (most reliable for local models)"
    echo "  --diff          - Use diff format (default, good balance)"
    echo "  --udiff         - Use unified diff format"
    echo "  --auto-commits  - Enable auto-commits"
    echo "  --help          - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                        # Start with primary model"
    echo "  $0 fast --whole          # Fast model with whole file editing"
    echo "  $0 primary --architect   # Architect mode (recommended for local models)"
    echo ""
    echo "Recommended for local models:"
    echo "  $0 --whole               # Most reliable"
    echo "  $0 --architect           # Best for planning/complex tasks"
    echo ""
}

# Parse arguments
MODE="primary"
ARCHITECT_FLAG=""
AUTO_COMMITS="--no-auto-commits"
ADDITIONAL_FLAGS=""

# First, check if first arg is a mode or a flag
if [[ $# -gt 0 ]]; then
    case "$1" in
        primary|fast|extended|complex)
            MODE="$1"
            shift
            ;;
        --help|-h|help)
            show_help
            exit 0
            ;;
        # If it starts with --, it's a flag, keep MODE as primary
        --*)
            : # Do nothing, MODE stays as primary
            ;;
        *)
            # Unknown mode
            echo "Unknown mode: $1"
            echo "Valid modes: primary, fast, extended, complex"
            echo "Or use flags: --whole, --architect, etc."
            show_help
            exit 1
            ;;
    esac
fi

# Now parse all flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --architect)
            ARCHITECT_FLAG="--architect"
            shift
            ;;
        --whole)
            EDIT_FORMAT="whole"
            shift
            ;;
        --diff)
            EDIT_FORMAT="diff"
            shift
            ;;
        --udiff)
            EDIT_FORMAT="udiff"
            shift
            ;;
        --auto-commits)
            AUTO_COMMITS="--auto-commits"
            shift
            ;;
        --help|-h|help)
            show_help
            exit 0
            ;;
        *)
            ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS $1"
            shift
            ;;
    esac
done

# Set model based on MODE
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
esac

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
echo "Model:       $MODEL"
echo "Mode:        $DESC"
echo "Edit Format: $EDIT_FORMAT"
if [[ -n "$ARCHITECT_FLAG" ]]; then
    echo "Architect:   Enabled (recommended for local models)"
fi
echo ""
echo "Aider will use your local LLM for all operations."
echo "No API calls, completely private and free."
echo ""
echo "Tips for Local Models:"
echo "  - Use /architect for better reliability"
echo "  - Use --whole flag for most reliable edits"
echo "  - Be specific in your requests"
echo "  - Break complex tasks into smaller steps"
echo "  - Use /model to switch models mid-session"
echo "  - Use /help for all Aider commands"
echo "  - Press Ctrl+D or type /exit to quit"
echo ""
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Aider with optimal settings for local models
aider \
    --model "ollama_chat/$MODEL" \
    --edit-format "$EDIT_FORMAT" \
    $AUTO_COMMITS \
    --dark-mode \
    --no-suggest-shell-commands \
    --stream \
    $ARCHITECT_FLAG \
    $ADDITIONAL_FLAGS
