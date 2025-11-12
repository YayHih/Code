# Local LLM Setup for RTX 3060

**Claude Code-level performance on your own hardware - completely free and private**

This repository contains a production-ready local LLM system optimized for RTX 3060 (12GB VRAM) with 160GB RAM. Based on extensive research, this setup achieves GPT-4o-competitive coding performance using Qwen2.5-Coder models running locally via Ollama.

## Key Features

✅ **Completely Free** - No API costs, runs entirely on your hardware
✅ **Private** - All processing happens locally, no data leaves your machine
✅ **Production Ready** - Research-driven configuration for maximum code quality
✅ **Claude Code Comparable** - 88.2% HumanEval score with proper setup
✅ **Multi-Agent Workflows** - 40-60% bug reduction through validation
✅ **RAG Integration** - Codebase-aware development with semantic search

## Hardware Requirements

- **GPU**: NVIDIA RTX 3060 (12GB VRAM) or equivalent
- **RAM**: 32GB minimum, 160GB+ recommended for multi-model workflows
- **Storage**: 50GB for models and indices
- **OS**: Linux (Ubuntu/Debian recommended)

## Quick Start (30 Minutes)

### 1. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install Ollama inference engine
- Download Qwen2.5-Coder models (7B Q8, Q6, 14B Q4)
- Install Python dependencies (Aider, LangChain, etc.)
- Set up directory structure

### 2. Activate the environment

```bash
source venv/bin/activate
```

### 3. Start coding with Aider

**⚠️ Important for Local Models**: If you get edit format errors, use:

```bash
./scripts/start_aider.sh --whole      # Most reliable for local models
./scripts/start_aider.sh --architect  # Best for planning/discussions
```

Or use different model configurations:

```bash
./scripts/start_aider.sh fast --whole      # Fast Q4 model (40-50 tok/s)
./scripts/start_aider.sh primary --whole   # High quality Q8 (30-40 tok/s)
./scripts/start_aider.sh complex --architect # 14B for complex tasks
```

**See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter any issues.**

### 4. Test your setup

```bash
# Check model status
python scripts/model_manager.py info

# Test a model
python scripts/model_manager.py test primary

# Monitor VRAM usage
python scripts/monitor.py status
```

## System Architecture

### Models

The system includes four model configurations optimized for different use cases:

| Model | VRAM | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **Primary (7B Q8)** | 8.5GB | 30-40 tok/s | ★★★★★ | Production code, critical bugs |
| **Extended (7B Q6)** | 6.5GB | 35-45 tok/s | ★★★★☆ | Multi-file refactoring, large files |
| **Complex (14B Q4)** | 8.5GB | 15-20 tok/s | ★★★★★ | Architecture, design patterns |
| **Fast (7B Q4)** | 4.5GB | 40-50 tok/s | ★★★☆☆ | Prototypes, simple scripts |

### Key Design Decisions

**Why Q8/Q6 over Q4?**
Research shows Q4 quantization degrades code quality by 8-15%. A 7B model at Q8 produces more reliable, debuggable code than a 13B model at Q4.

**Why these specific models?**
Qwen2.5-Coder achieves 88.2% on HumanEval, matching GPT-4o performance while running on consumer hardware.

**Why Ollama?**
Simplest setup with excellent defaults, built on llama.cpp so you get CPU offloading and model caching automatically.

## Usage Guide

### Aider Integration

Aider provides autonomous coding with Git integration:

```bash
# Start with primary model (highest quality)
./scripts/start_aider.sh

# In Aider:
/add file.py              # Add file to context
/architect               # Switch to planning mode
/model                   # Switch models
/commit                  # Commit changes
```

### Multi-Agent Workflows

Run the three-agent quality workflow for 40-60% bug reduction:

```bash
python scripts/multi_agent.py three-agent "Create a binary search tree with insert, delete, and search"
```

This runs:
1. **Planning Agent (14B Q4)** - Creates implementation strategy
2. **Code Agent (7B Q8)** - Implements high-quality code
3. **Testing Agent (7B Q6)** - Generates tests and validates

Or use iterative refinement (23.79% improvement):

```bash
python scripts/multi_agent.py iterative "Implement quicksort algorithm"
```

### RAG System for Codebase Awareness

Index your codebase for semantic search and context-aware development:

```bash
# Index your codebase
python scripts/setup_rag.py /path/to/your/codebase

# This creates a vector database with:
# - Semantic search across all code files
# - Sub-100ms retrieval speed
# - 25-35% reduction in API/library errors
# - 40-60% improvement in style consistency
```

Expected memory usage: ~4GB per 100K lines of code.

### Performance Monitoring

Monitor VRAM and prevent overflow (which causes 30-50x slowdown):

```bash
# Check current status
python scripts/monitor.py status

# Continuous monitoring
python scripts/monitor.py watch

# Get optimization recommendations
python scripts/monitor.py info
```

**Critical Thresholds:**
- **Warning**: >10.5 GB VRAM used
- **Critical**: >11.5 GB VRAM used (risk of overflow)

### Model Management

```bash
# Show model information
python scripts/model_manager.py info

# Test specific model
python scripts/model_manager.py test primary

# Benchmark all models
python scripts/model_manager.py benchmark

# Pull additional models
python scripts/model_manager.py setup
```

## Configuration Files

### `config/models.yaml`

Model configurations, selection strategies, and optimization settings.

### `config/Modelfile.qwen-optimized`

Ollama Modelfile with optimal parameters for code generation:
- Temperature: 0.15 (deterministic)
- Context: 32K tokens
- Optimized system prompt for coding

### `config/llama_cpp_config.sh`

Advanced configuration for llama.cpp users who want more control:
- Custom GPU/CPU layer distribution
- KV cache quantization
- Performance tuning utilities

## Advanced Features

### KV Cache Quantization

Enable for 40-50% memory reduction with minimal quality loss:

```bash
# In llama.cpp config
--cache-type-k q8_0  # 8-bit keys
--cache-type-v q4_0  # 4-bit values

# Result: 16K → 27K context in same VRAM budget
```

### Model Caching in RAM

With 160GB RAM, you can cache 3-5 models simultaneously for 2-4 second model switching:

```bash
# Models are automatically cached in RAM by Ollama
# Just pull multiple models and they stay resident

ollama pull qwen2.5-coder:7b-instruct-q8_0
ollama pull qwen2.5-coder:14b-instruct-q4_K_M

# Switching is nearly instant
```

### Hybrid GPU/CPU Inference

For 14B models that don't fit entirely in VRAM:

```bash
# Optimal: 60-75% GPU, rest CPU
--n-gpu-layers 22  # For 14B model on 12GB VRAM
--threads 12       # Use ~50% of CPU threads

# This gives 15-20 tok/s vs 0.69 tok/s with overflow
```

## Expected Performance

### Token Generation Speed

| Model | Speed | Notes |
|-------|-------|-------|
| 7B Q8 | 30-40 tok/s | Full GPU |
| 7B Q6 | 35-45 tok/s | Full GPU |
| 14B Q4 | 15-20 tok/s | Hybrid GPU/CPU |
| 7B Q4 | 40-50 tok/s | Full GPU, fast iteration |

### Time to Working Code

| Task Complexity | Generation | Debug | Total | Success Rate |
|----------------|-----------|-------|-------|--------------|
| Simple (50 LOC) | 30-60s | 2-5 min | 3-6 min | 85-90% |
| Medium (200 LOC) | 2-4 min | 10-20 min | 12-24 min | 70-80% |
| Complex (500+ LOC) | 5-10 min | 20-45 min | 25-55 min | 55-70% |

**Key Insight**: Debugging takes 2-5x generation time, which is why code quality (Q6+ quantization) matters more than raw speed.

## Critical Pitfalls to Avoid

### ❌ VRAM Overflow (30-50x slowdown)

**Problem**: GPU using system RAM as virtual VRAM
**Solution**: Monitor with `python scripts/monitor.py watch`, reduce context or model size

### ❌ Wrong Quantization

**Problem**: Using Q4 for primary coding
**Solution**: Use Q6 minimum, Q8 for maximum quality

### ❌ Context Budget Errors

**Problem**: Setting context too high, OOM crashes
**Solution**: Use 60-70% of theoretical maximum, enable KV cache quantization

### ❌ Over-Threading

**Problem**: Using all 28 threads
**Solution**: Use 50-75% (12-16 threads max) due to DDR3 bandwidth limits

## Optimization Checklist

### ✅ DO:

- Use Q6 or Q8 for production coding
- Monitor VRAM during generation
- Enable KV cache quantization
- Test GPU/CPU split ratios for hybrid models
- Implement RAG for codebases >10K LOC
- Use multi-agent validation for production code

### ❌ DON'T:

- Let VRAM overflow (catastrophic slowdown)
- Use Q3 or Q2 quantization for coding
- Assume Q4 is "good enough" without testing
- Use more than 14-16 CPU threads
- Skip validation of generated code

## Project Structure

```
.
├── setup.sh                    # Main setup script
├── config/
│   ├── models.yaml            # Model configurations
│   ├── Modelfile.qwen-optimized  # Ollama Modelfile
│   └── llama_cpp_config.sh    # Advanced llama.cpp config
├── scripts/
│   ├── start_aider.sh         # Launch Aider with model selection
│   ├── model_manager.py       # Model management utilities
│   ├── setup_rag.py           # RAG system setup
│   ├── multi_agent.py         # Multi-agent orchestration
│   └── monitor.py             # Performance monitoring
├── LLM_Research.txt           # Detailed research and benchmarks
└── README.md                  # This file
```

## Deployment Roadmap

### Phase 1: Quick Start (Week 1)

**Day 1**: Foundation Setup
- Run `./setup.sh`
- Test models with `model_manager.py`
- Verify VRAM usage

**Day 2-3**: Agentic Framework
- Practice with Aider
- Test multi-file edits
- Measure time-to-working-code

**Day 4-7**: Optimization
- Test different models and quantizations
- Establish baseline metrics
- Find optimal configuration for your workflow

### Phase 2: Advanced Integration (Week 2)

- Set up RAG for large codebases
- Configure multi-model workflows
- Test three-agent validation system
- Measure quality improvements

### Phase 3: Production Optimization (Week 3-4)

- Implement model caching in RAM
- Fine-tune temperature and sampling
- Build custom tools and integrations
- Document your configuration

## Troubleshooting

**📖 For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

### Aider Edit Format Errors

**Error**: "The LLM did not conform to the edit format"

**Quick Fixes**:
```bash
# Most reliable - use whole file editing
./scripts/start_aider.sh --whole

# For planning and discussions
./scripts/start_aider.sh --architect

# Fast model with whole file editing
./scripts/start_aider.sh fast --whole
```

**Why this happens**: Local models sometimes struggle with Aider's strict formatting. The `--whole` flag makes Aider work with complete files instead of diffs, which is much more reliable.

**See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions and best practices.**

### Ollama not starting

```bash
# Check status
systemctl status ollama

# Start manually
ollama serve
```

### Model pull fails

```bash
# Try with specific tag
ollama pull qwen2.5-coder:7b-instruct

# List available tags
ollama search qwen2.5-coder
```

### VRAM issues

```bash
# Monitor current usage
python scripts/monitor.py status

# Reduce context window or switch to smaller model
```

### Slow generation

```bash
# Check if in VRAM overflow
nvidia-smi

# If using hybrid mode, test different GPU layer counts
bash config/llama_cpp_config.sh test model.gguf
```

## Performance Benchmarks

Based on the research in `LLM_Research.txt`:

| Metric | Value |
|--------|-------|
| **HumanEval Score** | 88.2% (Qwen2.5-Coder-7B) |
| **MBPP Score** | 83.5% |
| **Context Window** | 128K (32K safe for 12GB VRAM) |
| **Bug Reduction** | 40-60% (multi-agent) |
| **Style Consistency** | 40-60% improvement (with RAG) |

## Resources

- [Ollama Documentation](https://ollama.com/docs)
- [Aider Documentation](https://aider.chat/docs)
- [Qwen2.5-Coder](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [LangChain](https://python.langchain.com/docs/get_started/introduction)

## Contributing

This is a public repository. Feel free to:
- Open issues for bugs or questions
- Submit PRs for improvements
- Share your optimization findings
- Add support for new models

## License

MIT License - See LICENSE file

## Acknowledgments

Based on extensive research into local LLM optimization, with insights from:
- Qwen2.5-Coder team for the excellent models
- llama.cpp for efficient inference
- Aider for autonomous coding framework
- Community benchmarks and real-world testing

---

**Built with ❤️ for developers who value privacy, control, and zero API costs**
