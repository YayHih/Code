# Troubleshooting Guide for Local LLM Setup

## Common Issues and Solutions

### 1. Aider Edit Format Errors

**Error**: "The LLM did not conform to the edit format" or "No filename provided before ``` in file listing"

**Cause**: Local models sometimes struggle with Aider's strict edit format requirements.

**Solutions** (in order of reliability):

#### Option A: Use Whole File Editing (Most Reliable)
```bash
./scripts/start_aider.sh --whole
```
This tells Aider to work with entire files instead of diffs. It's slower but much more reliable with local models.

#### Option B: Use Architect Mode (Best for Planning)
```bash
./scripts/start_aider.sh --architect
```
Architect mode is more conversational and doesn't require strict edit formatting. Great for:
- Planning and design discussions
- Understanding code
- Breaking down complex tasks
- Getting explanations

#### Option C: Use Diff Format (Default)
```bash
./scripts/start_aider.sh --diff
```
This is now the default. It's more forgiving than the original format.

#### Option D: Use Unified Diff Format
```bash
./scripts/start_aider.sh --udiff
```
Another alternative format that sometimes works better.

### 2. Best Practices for Local Models with Aider

**Be More Specific**
Instead of:
```
Make this code better
```

Use:
```
Add error handling to the parse_config function to check if the file exists before reading it
```

**Break Tasks Down**
Instead of:
```
Build a complete user authentication system
```

Use:
```
First, let's create a User class with username and password fields
```
Then after that works:
```
Now add a hash_password method using bcrypt
```

**Use Architect Mode for Planning**
1. Start with: `./scripts/start_aider.sh --architect`
2. Discuss the plan with the model
3. Once you have a plan, exit and restart without --architect
4. Implement step by step

### 3. Model-Specific Recommendations

**For Complex Tasks (Architecture, Design)**
```bash
./scripts/start_aider.sh complex --architect
```
Uses the 14B model in architect mode for better reasoning.

**For Quick Edits**
```bash
./scripts/start_aider.sh fast --whole
```
Uses Q4 model with whole file editing for speed.

**For Production Code (Recommended)**
```bash
./scripts/start_aider.sh primary --whole
```
Uses Q8 model with whole file editing for quality.

### 4. Alternative: Use Aider Commands Inside Session

If you're already in an Aider session and getting errors:

```
/architect          # Switch to architect mode
/clear             # Clear the conversation history
/help              # See all available commands
/model             # Switch to a different model
```

### 5. Aider Configuration File

Create `.aider.conf.yml` in your project directory:

```yaml
# Aider configuration optimized for local models
model: ollama_chat/qwen2.5-coder:7b-instruct-q8_0
edit-format: whole
dark-mode: true
auto-commits: false
stream: true
```

Then just run:
```bash
aider
```

### 6. If Edits Still Fail

Try this workflow:

1. **Get the suggestion**:
   ```bash
   ./scripts/start_aider.sh --architect
   ```
   Ask the model what changes to make, but don't let it edit files.

2. **Make changes manually**: Copy the suggested code and edit files yourself

3. **Have it review**: Use `/ask` command to have it review your changes without editing

### 7. VRAM Overflow During Aider Session

**Symptoms**: Suddenly very slow (< 1 tok/s), system feels sluggish

**Check VRAM**:
```bash
# In another terminal
python scripts/monitor.py status
```

**Solutions**:
- Exit Aider and restart with smaller model: `./scripts/start_aider.sh fast`
- Reduce context by using `/drop` command to remove files
- Use `/clear` to clear conversation history

### 8. Ollama Not Responding

**Check if running**:
```bash
pgrep ollama
```

**Restart Ollama**:
```bash
# Kill existing
pkill ollama

# Start fresh
ollama serve &
sleep 3

# Test
ollama run qwen2.5-coder:7b-instruct "def hello():"
```

### 9. Model Not Found

**Error**: "model not found: qwen2.5-coder:7b-instruct-q8_0"

**Solution**:
```bash
# List installed models
ollama list

# Pull missing model
ollama pull qwen2.5-coder:7b-instruct

# If specific quantization not available, try without suffix
# Ollama will use the default quantization
```

### 10. Slow Performance

**Expected speeds** (for reference):
- 7B Q8: 30-40 tok/s
- 7B Q6: 35-45 tok/s
- 7B Q4: 40-50 tok/s
- 14B Q4: 15-20 tok/s

**If slower than expected**:

1. **Check VRAM overflow**:
   ```bash
   nvidia-smi
   ```
   If using >11.5GB, you're likely overflowing.

2. **Reduce context**:
   In Aider, use `/drop` to remove files you don't need.

3. **Switch to smaller model**:
   ```bash
   /model ollama_chat/qwen2.5-coder:7b-instruct-q4_K_M
   ```

4. **Check other processes**:
   ```bash
   nvidia-smi
   ```
   Make sure no other processes are using GPU.

### 11. Python Virtual Environment Issues

**Error**: "aider: command not found"

**Solution**:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Verify
which aider
which python

# If still not found, reinstall
pip install aider-chat
```

### 12. Getting Best Results

**Do's**:
- ✅ Use `--whole` for most reliable editing
- ✅ Use `--architect` for planning and discussions
- ✅ Be specific in your requests
- ✅ Add files to context with `/add`
- ✅ Review changes before accepting
- ✅ Break complex tasks into steps
- ✅ Monitor VRAM usage

**Don'ts**:
- ❌ Don't ask very vague questions
- ❌ Don't add too many files at once (VRAM overflow)
- ❌ Don't expect it to work exactly like Claude/GPT-4
- ❌ Don't use architect mode for actual code edits
- ❌ Don't ignore VRAM warnings

## Quick Reference Commands

### Starting Aider
```bash
# Most reliable for local models
./scripts/start_aider.sh --whole

# Best for planning/architecture
./scripts/start_aider.sh --architect

# Fast iterations
./scripts/start_aider.sh fast --whole

# Complex reasoning
./scripts/start_aider.sh complex --architect
```

### Inside Aider Session
```bash
/add file.py          # Add file to chat
/drop file.py         # Remove file from chat
/architect            # Enter architect mode
/code                 # Exit architect mode
/ask question         # Ask without editing
/clear                # Clear chat history
/model                # Switch models
/help                 # Show all commands
/exit                 # Quit
```

### Monitoring
```bash
# Check VRAM
python scripts/monitor.py status

# Continuous monitoring
python scripts/monitor.py watch

# In another terminal while Aider runs
watch -n 2 nvidia-smi
```

## When to Use Alternative Workflows

If Aider continues to give edit format errors even with `--whole`:

### Alternative 1: Direct Ollama Usage
```bash
ollama run qwen2.5-coder:7b-instruct-q8_0
```
Then paste your code and ask questions directly.

### Alternative 2: Multi-Agent Scripts
```bash
# For code generation
python scripts/multi_agent.py three-agent "your task"

# For iterative refinement
python scripts/multi_agent.py iterative "your task"
```

### Alternative 3: RAG-Enhanced Generation
```bash
# After setting up RAG
python examples/rag_example.py interactive
```

### Alternative 4: Custom Integration
Build your own integration using Ollama's API:
```python
import subprocess

def ask_llm(prompt, model="qwen2.5-coder:7b-instruct-q8_0"):
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Still Having Issues?

1. **Check the logs**: Look at Aider's output for specific error messages
2. **Try different model**: Some tasks work better with different models
3. **Simplify the task**: Break it down into smaller pieces
4. **Use architect mode**: For understanding and planning
5. **Make edits manually**: Use the model for suggestions, you do the editing

## Getting Help

- Aider documentation: https://aider.chat/docs/
- Aider troubleshooting: https://aider.chat/docs/troubleshooting/edit-errors.html
- Ollama documentation: https://ollama.com/docs
- Check `README.md` for basic setup
- Monitor with `python scripts/monitor.py watch`
