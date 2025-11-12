#!/usr/bin/env python3
"""
Model Manager for Local LLM Setup
Manages Ollama models, monitors performance, and provides utilities
"""

import subprocess
import json
import time
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    name: str
    size: str
    quantization: str
    description: str
    use_case: str


class ModelManager:
    """Manages Ollama models and operations"""

    MODELS = {
        "primary": ModelInfo(
            name="qwen2.5-coder:7b-instruct-q8_0",
            size="7B",
            quantization="Q8",
            description="Primary coding model - highest quality",
            use_case="Production code, critical bugs, complex algorithms"
        ),
        "fast": ModelInfo(
            name="qwen2.5-coder:7b-instruct-q4_K_M",
            size="7B",
            quantization="Q4",
            description="Fast model for quick iterations",
            use_case="Prototypes, simple scripts, testing"
        ),
        "extended": ModelInfo(
            name="qwen2.5-coder:7b-instruct-q6_K",
            size="7B",
            quantization="Q6",
            description="Extended context variant",
            use_case="Multi-file refactoring, large files"
        ),
        "complex": ModelInfo(
            name="qwen2.5-coder:14b-instruct-q4_K_M",
            size="14B",
            quantization="Q4",
            description="Complex reasoning model",
            use_case="Architecture, design patterns, complex tasks"
        ),
    }

    def __init__(self):
        self.check_ollama()

    def check_ollama(self):
        """Check if Ollama is installed and running"""
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Ollama is not installed or not in PATH")
            print("Please run ./setup.sh first")
            sys.exit(1)

    def list_models(self) -> List[Dict]:
        """List all installed Ollama models"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error listing models: {e}")
            return []

    def is_model_installed(self, model_name: str) -> bool:
        """Check if a model is installed"""
        output = self.list_models()
        return model_name in output

    def pull_model(self, model_name: str):
        """Pull a model from Ollama registry"""
        print(f"Pulling model: {model_name}")
        print("This may take a while depending on your internet connection...")
        try:
            subprocess.run(["ollama", "pull", model_name], check=True)
            print(f"✓ Successfully pulled {model_name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error pulling model: {e}")

    def test_model(self, model_name: str, prompt: str = "def fibonacci(n):") -> Dict:
        """Test a model and measure performance"""
        print(f"\nTesting {model_name}...")
        print(f"Prompt: {prompt}")
        print("-" * 50)

        start_time = time.time()

        try:
            result = subprocess.run(
                ["ollama", "run", model_name, f"Complete this code:\n{prompt}"],
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )

            end_time = time.time()
            duration = end_time - start_time

            print(result.stdout)
            print("-" * 50)
            print(f"Time taken: {duration:.2f} seconds")

            # Estimate tokens (rough approximation)
            output_length = len(result.stdout.split())
            tok_per_sec = output_length / duration if duration > 0 else 0
            print(f"Estimated speed: {tok_per_sec:.1f} tok/s")

            return {
                "success": True,
                "duration": duration,
                "output": result.stdout,
                "tokens_per_sec": tok_per_sec
            }

        except subprocess.TimeoutExpired:
            print("✗ Test timed out (>60s)")
            return {"success": False, "error": "timeout"}
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running model: {e}")
            return {"success": False, "error": str(e)}

    def show_model_info(self):
        """Display information about available models"""
        print("\n" + "=" * 60)
        print("Available Model Configurations")
        print("=" * 60 + "\n")

        for key, model in self.MODELS.items():
            installed = "✓" if self.is_model_installed(model.name) else "✗"
            print(f"{installed} {key.upper()}: {model.name}")
            print(f"   Size: {model.size} | Quantization: {model.quantization}")
            print(f"   {model.description}")
            print(f"   Use case: {model.use_case}")
            print()

    def setup_all_models(self):
        """Pull all recommended models"""
        print("Setting up all recommended models...")
        print("This will download several GB of data.\n")

        for key, model in self.MODELS.items():
            if not self.is_model_installed(model.name):
                response = input(f"Pull {key} model ({model.name})? [Y/n]: ")
                if response.lower() != 'n':
                    self.pull_model(model.name)
            else:
                print(f"✓ {key} model already installed")

    def benchmark_all(self):
        """Run benchmarks on all installed models"""
        print("\n" + "=" * 60)
        print("Benchmarking Installed Models")
        print("=" * 60)

        test_prompt = "def quicksort(arr):"
        results = {}

        for key, model in self.MODELS.items():
            if self.is_model_installed(model.name):
                result = self.test_model(model.name, test_prompt)
                results[key] = result
            else:
                print(f"\nSkipping {key} - not installed")

        print("\n" + "=" * 60)
        print("Benchmark Summary")
        print("=" * 60 + "\n")

        for key, result in results.items():
            if result.get("success"):
                print(f"{key.upper():12} - {result['tokens_per_sec']:.1f} tok/s "
                      f"({result['duration']:.1f}s)")
            else:
                print(f"{key.upper():12} - Failed: {result.get('error', 'unknown')}")


def main():
    manager = ModelManager()

    if len(sys.argv) < 2:
        print("Model Manager for Local LLM")
        print("\nUsage: python model_manager.py <command>")
        print("\nCommands:")
        print("  list       - List installed models")
        print("  info       - Show model information")
        print("  setup      - Pull all recommended models")
        print("  test       - Test a specific model")
        print("  benchmark  - Benchmark all installed models")
        print("\nExamples:")
        print("  python model_manager.py info")
        print("  python model_manager.py test primary")
        print("  python model_manager.py benchmark")
        sys.exit(0)

    command = sys.argv[1]

    if command == "list":
        print(manager.list_models())

    elif command == "info":
        manager.show_model_info()

    elif command == "setup":
        manager.setup_all_models()

    elif command == "test":
        if len(sys.argv) < 3:
            print("Usage: python model_manager.py test <model_key>")
            print("Available keys: primary, fast, extended, complex")
            sys.exit(1)

        model_key = sys.argv[2]
        if model_key not in manager.MODELS:
            print(f"Unknown model key: {model_key}")
            sys.exit(1)

        model = manager.MODELS[model_key]
        if not manager.is_model_installed(model.name):
            print(f"Model {model.name} is not installed")
            print(f"Run: ollama pull {model.name}")
            sys.exit(1)

        manager.test_model(model.name)

    elif command == "benchmark":
        manager.benchmark_all()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
