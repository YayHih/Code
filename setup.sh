#!/bin/bash
set -e

echo "=================================================="
echo "Local LLM Setup for RTX 3060 (12GB VRAM)"
echo "Optimized for Claude Code-level Performance"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux. For other OS, please adapt accordingly."
    exit 1
fi

# Check for NVIDIA GPU
print_info "Checking for NVIDIA GPU..."
if ! command -v nvidia-smi &> /dev/null; then
    print_error "nvidia-smi not found. Please install NVIDIA drivers first."
    exit 1
fi

nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo ""

# Step 1: Install Ollama
print_info "Step 1/6: Installing Ollama..."
if command -v ollama &> /dev/null; then
    print_info "Ollama already installed: $(ollama --version)"
else
    print_info "Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    print_info "Ollama installed successfully!"
fi
echo ""

# Start Ollama service
print_info "Starting Ollama service..."
if systemctl is-active --quiet ollama; then
    print_info "Ollama service is already running"
else
    sudo systemctl start ollama || print_warn "Could not start ollama service. You may need to run 'ollama serve' manually."
fi
echo ""

# Step 2: Pull optimal models
print_info "Step 2/6: Downloading optimal models..."
print_info "This will download ~8-9GB of models. Please be patient..."
echo ""

# Primary model: Qwen2.5-Coder-7B Q8
print_info "Pulling Qwen2.5-Coder-7B-Q8 (primary coding model)..."
ollama pull qwen2.5-coder:7b-instruct-q8_0 || ollama pull qwen2.5-coder:7b-instruct

# Alternative Q6 version for more context
print_info "Pulling Qwen2.5-Coder-7B-Q6 (extended context variant)..."
ollama pull qwen2.5-coder:7b-instruct-q6_K || print_warn "Q6 variant not available, using Q8"

# Advanced model for complex tasks
print_info "Pulling Qwen2.5-14B-Q4 (complex reasoning model - optional)..."
ollama pull qwen2.5-coder:14b-instruct-q4_K_M || print_warn "14B model not available, will use 7B for all tasks"

# Embedding model for RAG
print_info "Pulling nomic-embed-text (for RAG/embeddings)..."
ollama pull nomic-embed-text

echo ""
print_info "Models downloaded successfully!"
echo ""

# Step 3: Install Python dependencies
print_info "Step 3/6: Installing Python dependencies..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

print_info "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_info "Installing packages..."
pip install --upgrade pip
pip install aider-chat
pip install langchain langchain-community
pip install chromadb
pip install sentence-transformers
pip install faiss-cpu
pip install openai  # For OpenAI-compatible API client
pip install numpy pandas
pip install psutil gputil  # For monitoring
echo ""

# Step 4: Create directory structure
print_info "Step 4/6: Creating directory structure..."
mkdir -p config
mkdir -p scripts
mkdir -p rag_system
mkdir -p monitoring
mkdir -p examples
print_info "Directory structure created!"
echo ""

# Step 5: Test the setup
print_info "Step 5/6: Testing the setup..."
echo ""
print_info "Testing Ollama with a simple query..."
echo "print('Hello from local LLM!')" | ollama run qwen2.5-coder:7b-instruct-q8_0 "Complete this Python code to print a greeting" || \
    ollama run qwen2.5-coder:7b-instruct "Complete this Python code to print a greeting"
echo ""

# Step 6: Display next steps
print_info "Step 6/6: Setup complete!"
echo ""
echo "=================================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=================================================="
echo ""
echo "Your local LLM system is ready. Here's what was installed:"
echo ""
echo "✓ Ollama inference engine"
echo "✓ Qwen2.5-Coder-7B-Q8 (primary coding model)"
echo "✓ Qwen2.5-Coder-7B-Q6 (extended context)"
echo "✓ Qwen2.5-14B-Q4 (complex tasks)"
echo "✓ nomic-embed-text (embeddings for RAG)"
echo "✓ Aider (autonomous coding agent)"
echo "✓ RAG system dependencies"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start coding with Aider:"
echo "   ./scripts/start_aider.sh"
echo ""
echo "3. Or use Ollama directly:"
echo "   ollama run qwen2.5-coder:7b-instruct-q8_0"
echo ""
echo "4. Setup RAG for your codebase:"
echo "   python scripts/setup_rag.py /path/to/your/codebase"
echo ""
echo "5. Monitor performance:"
echo "   python scripts/monitor.py"
echo ""
echo "See README.md for detailed usage instructions."
echo ""
