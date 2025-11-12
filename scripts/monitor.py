#!/usr/bin/env python3
"""
Performance Monitoring Tool for Local LLM
Monitors VRAM usage, token generation speed, and system resources

Critical for preventing VRAM overflow (30-50x slowdown) and ensuring
optimal performance.
"""

import subprocess
import time
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GPUMetrics:
    timestamp: str
    vram_used_mb: float
    vram_total_mb: float
    vram_percent: float
    gpu_utilization: float
    temperature: Optional[float] = None


@dataclass
class SystemMetrics:
    timestamp: str
    cpu_percent: float
    ram_used_gb: float
    ram_total_gb: float
    ram_percent: float


class PerformanceMonitor:
    """Monitor system and GPU performance"""

    # VRAM thresholds (for 12GB card)
    VRAM_WARNING_MB = 10500  # 10.5 GB
    VRAM_CRITICAL_MB = 11500  # 11.5 GB

    def __init__(self):
        self.check_nvidia()
        self.metrics_history: List[GPUMetrics] = []

    def check_nvidia(self):
        """Check if nvidia-smi is available"""
        try:
            subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: nvidia-smi not found")
            print("Please ensure NVIDIA drivers are installed")
            sys.exit(1)

    def get_gpu_metrics(self) -> Optional[GPUMetrics]:
        """Get current GPU metrics"""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu",
                    "--format=csv,noheader,nounits"
                ],
                capture_output=True,
                text=True,
                check=True
            )

            values = result.stdout.strip().split(',')
            vram_used = float(values[0])
            vram_total = float(values[1])
            gpu_util = float(values[2])
            temp = float(values[3]) if len(values) > 3 else None

            return GPUMetrics(
                timestamp=datetime.now().isoformat(),
                vram_used_mb=vram_used,
                vram_total_mb=vram_total,
                vram_percent=(vram_used / vram_total) * 100,
                gpu_utilization=gpu_util,
                temperature=temp
            )

        except Exception as e:
            print(f"Error getting GPU metrics: {e}")
            return None

    def get_system_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics"""
        try:
            # Get CPU usage
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
                cpu_times = [int(x) for x in cpu_line.split()[1:]]
                cpu_total = sum(cpu_times)
                cpu_idle = cpu_times[3]
                cpu_percent = 100 * (1 - cpu_idle / cpu_total)

            # Get memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = int(parts[1].strip().split()[0])  # KB
                        meminfo[key] = value

            mem_total_gb = meminfo['MemTotal'] / (1024 * 1024)
            mem_available_gb = meminfo['MemAvailable'] / (1024 * 1024)
            mem_used_gb = mem_total_gb - mem_available_gb
            mem_percent = (mem_used_gb / mem_total_gb) * 100

            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                ram_used_gb=mem_used_gb,
                ram_total_gb=mem_total_gb,
                ram_percent=mem_percent
            )

        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return None

    def check_vram_status(self, metrics: GPUMetrics) -> str:
        """Check VRAM status and return warning level"""
        if metrics.vram_used_mb >= self.VRAM_CRITICAL_MB:
            return "CRITICAL"
        elif metrics.vram_used_mb >= self.VRAM_WARNING_MB:
            return "WARNING"
        else:
            return "OK"

    def print_metrics(self, gpu: GPUMetrics, system: Optional[SystemMetrics] = None):
        """Print metrics in a nice format"""
        status = self.check_vram_status(gpu)

        # Color codes
        RED = '\033[91m'
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        BLUE = '\033[94m'
        RESET = '\033[0m'

        # Choose color based on status
        if status == "CRITICAL":
            color = RED
        elif status == "WARNING":
            color = YELLOW
        else:
            color = GREEN

        print("\n" + "=" * 60)
        print(f"GPU Metrics - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        print(f"{color}VRAM Status: {status}{RESET}")
        print(f"VRAM Used:   {gpu.vram_used_mb:.0f} MB / {gpu.vram_total_mb:.0f} MB "
              f"({gpu.vram_percent:.1f}%)")
        print(f"GPU Util:    {gpu.gpu_utilization:.0f}%")

        if gpu.temperature:
            print(f"Temperature: {gpu.temperature:.0f}°C")

        # Calculate remaining VRAM
        remaining = gpu.vram_total_mb - gpu.vram_used_mb
        print(f"Remaining:   {remaining:.0f} MB")

        # Estimate context capacity
        context_capacity_16k = remaining / 3.2  # ~3.2GB per 16K context for 7B
        print(f"Estimated additional context capacity: ~{context_capacity_16k * 16:.0f}K tokens")

        if system:
            print("\n" + "-" * 60)
            print("System Metrics")
            print("-" * 60)
            print(f"CPU Usage:   {system.cpu_percent:.1f}%")
            print(f"RAM Used:    {system.ram_used_gb:.1f} GB / {system.ram_total_gb:.1f} GB "
                  f"({system.ram_percent:.1f}%)")

        # Warnings
        if status == "CRITICAL":
            print(f"\n{RED}⚠ CRITICAL: VRAM usage is dangerously high!{RESET}")
            print("Risk of overflow to system RAM (30-50x slowdown)")
            print("Actions:")
            print("  - Reduce context window size")
            print("  - Switch to smaller model or lower quantization")
            print("  - Enable KV cache quantization")

        elif status == "WARNING":
            print(f"\n{YELLOW}⚠ WARNING: VRAM usage is high{RESET}")
            print("Consider:")
            print("  - Monitoring closely during generation")
            print("  - Reducing context if possible")

    def monitor_continuous(self, interval: float = 2.0):
        """Continuously monitor and display metrics"""
        print("Starting continuous monitoring...")
        print(f"Update interval: {interval}s")
        print("Press Ctrl+C to stop")

        try:
            while True:
                gpu = self.get_gpu_metrics()
                system = self.get_system_metrics()

                if gpu:
                    self.metrics_history.append(gpu)
                    self.print_metrics(gpu, system)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")
            self.print_summary()

    def print_summary(self):
        """Print summary statistics"""
        if not self.metrics_history:
            return

        print("\n" + "=" * 60)
        print("Monitoring Summary")
        print("=" * 60)

        vram_values = [m.vram_used_mb for m in self.metrics_history]
        gpu_util_values = [m.gpu_utilization for m in self.metrics_history]

        print(f"Duration:     {len(self.metrics_history) * 2:.0f} seconds")
        print(f"Samples:      {len(self.metrics_history)}")
        print()
        print("VRAM Usage:")
        print(f"  Average:    {sum(vram_values) / len(vram_values):.0f} MB")
        print(f"  Peak:       {max(vram_values):.0f} MB")
        print(f"  Minimum:    {min(vram_values):.0f} MB")
        print()
        print("GPU Utilization:")
        print(f"  Average:    {sum(gpu_util_values) / len(gpu_util_values):.1f}%")
        print(f"  Peak:       {max(gpu_util_values):.0f}%")

        # Check if we hit critical levels
        critical_count = sum(1 for v in vram_values if v >= self.VRAM_CRITICAL_MB)
        warning_count = sum(1 for v in vram_values if v >= self.VRAM_WARNING_MB)

        if critical_count > 0:
            print(f"\n⚠ Hit critical VRAM levels {critical_count} times!")
        elif warning_count > 0:
            print(f"\n⚠ Hit warning VRAM levels {warning_count} times")

    def save_metrics(self, filename: str = "metrics.json"):
        """Save metrics history to file"""
        with open(filename, 'w') as f:
            data = [asdict(m) for m in self.metrics_history]
            json.dump(data, f, indent=2)
        print(f"Metrics saved to: {filename}")

    def show_recommendations(self):
        """Show optimization recommendations based on current state"""
        gpu = self.get_gpu_metrics()
        if not gpu:
            return

        print("\n" + "=" * 60)
        print("Optimization Recommendations")
        print("=" * 60)

        vram_free = gpu.vram_total_mb - gpu.vram_used_mb

        # Model recommendations
        print("\nModel Selection:")
        if vram_free > 8000:
            print("  ✓ Can run 7B Q8 + 32K context")
            print("  ✓ Can run 14B Q4 + 16K context with hybrid")
        elif vram_free > 6000:
            print("  ✓ Can run 7B Q6 + 32K context")
            print("  ⚠ 14B models may be tight")
        elif vram_free > 4000:
            print("  ⚠ Consider 7B Q4 or smaller models")
        else:
            print("  ⚠ VRAM heavily utilized")

        # Context recommendations
        print("\nContext Window:")
        max_context_16k_units = vram_free / 3.2
        print(f"  Safe context: ~{max_context_16k_units * 16:.0f}K tokens")

        # Optimization suggestions
        print("\nOptimizations to consider:")
        if vram_free < 2000:
            print("  • Enable KV cache quantization (40-50% memory reduction)")
            print("  • Reduce context window size")
            print("  • Switch to Q6 or Q4 quantization")
        print("  • Use Flash Attention (already enabled in llama.cpp)")
        print("  • Monitor with: python monitor.py watch")


def main():
    monitor = PerformanceMonitor()

    if len(sys.argv) < 2:
        print("Performance Monitoring Tool")
        print("\nUsage: python monitor.py <command>")
        print("\nCommands:")
        print("  status  - Show current status")
        print("  watch   - Continuously monitor (update every 2s)")
        print("  info    - Show optimization recommendations")
        print("\nExamples:")
        print("  python monitor.py status")
        print("  python monitor.py watch")
        sys.exit(0)

    command = sys.argv[1]

    if command == "status":
        gpu = monitor.get_gpu_metrics()
        system = monitor.get_system_metrics()
        if gpu:
            monitor.print_metrics(gpu, system)

    elif command == "watch":
        monitor.monitor_continuous()

    elif command == "info":
        monitor.show_recommendations()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
