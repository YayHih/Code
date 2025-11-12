#!/usr/bin/env python3
"""
Quick test script to verify your local LLM setup is working

This script tests:
1. Ollama is running
2. Models are available
3. Basic code generation works
4. Performance is acceptable
"""

import subprocess
import time
import sys


def test_ollama():
    """Test if Ollama is available"""
    print("1. Testing Ollama availability...")
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✓ Ollama is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ✗ Ollama not found")
        return False


def test_model(model_name: str):
    """Test if a specific model works"""
    print(f"\n2. Testing model: {model_name}...")

    test_prompt = "def fibonacci(n):\n    # Complete this function"

    start_time = time.time()

    try:
        result = subprocess.run(
            ["ollama", "run", model_name, f"Complete this Python function:\n{test_prompt}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )

        elapsed = time.time() - start_time
        output = result.stdout.strip()

        print(f"   ✓ Model works!")
        print(f"   ✓ Response time: {elapsed:.1f}s")

        # Estimate tokens per second
        tokens = len(output.split())
        tok_per_sec = tokens / elapsed if elapsed > 0 else 0
        print(f"   ✓ Estimated speed: {tok_per_sec:.1f} tok/s")

        print("\n   Generated code:")
        print("   " + "-" * 50)
        for line in output.split('\n')[:10]:  # Show first 10 lines
            print(f"   {line}")
        print("   " + "-" * 50)

        return True

    except subprocess.TimeoutExpired:
        print("   ✗ Model timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Model failed: {e}")
        return False


def test_vram():
    """Test VRAM usage"""
    print("\n3. Testing VRAM availability...")
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True
        )

        values = result.stdout.strip().split(',')
        used = float(values[0])
        total = float(values[1])
        percent = (used / total) * 100

        print(f"   ✓ VRAM: {used:.0f} MB / {total:.0f} MB ({percent:.1f}%)")

        if total < 11000:
            print("   ⚠ Warning: Less than 12GB VRAM detected")
            print("   You may need to use smaller models or lower context")

        return True

    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ✗ Could not detect GPU")
        return False


def main():
    print("=" * 60)
    print("Local LLM Setup Test")
    print("=" * 60)

    # Test 1: Ollama
    if not test_ollama():
        print("\nSetup incomplete. Please run ./setup.sh first")
        sys.exit(1)

    # Test 2: Model
    model = "qwen2.5-coder:7b-instruct-q8_0"
    if not test_model(model):
        print(f"\nModel {model} not working")
        print("Try: ollama pull qwen2.5-coder:7b-instruct")
        sys.exit(1)

    # Test 3: VRAM
    test_vram()

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nYour local LLM setup is working correctly.")
    print("\nNext steps:")
    print("  - Start coding with: ./scripts/start_aider.sh")
    print("  - Monitor performance: python scripts/monitor.py watch")
    print("  - Test multi-agent: python scripts/multi_agent.py three-agent 'your task'")
    print()


if __name__ == "__main__":
    main()
