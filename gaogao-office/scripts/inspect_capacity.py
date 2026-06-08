#!/usr/bin/env python3
"""Inspect local capacity for GaoGao Office employee dispatch.

This script is read-only. It gives the project manager a conservative
recommendation for how many employee conversations to dispatch at once.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class CapacityReport:
    platform: str
    logical_cpus: int | None
    memory_gb: float | None
    load_1m: float | None
    load_ratio: float | None
    tier: str
    max_parallel_employee_tasks: int
    policy_mode: str
    reason: str
    confidence: str


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def windows_memory_gb() -> float | None:
    try:
        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
            return None
        return round(status.ullTotalPhys / (1024**3), 2)
    except Exception:
        return None


def posix_memory_gb() -> float | None:
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return round((pages * page_size) / (1024**3), 2)
    except (AttributeError, OSError, ValueError):
        return None


def total_memory_gb() -> float | None:
    if platform.system().lower() == "windows":
        return windows_memory_gb()
    return posix_memory_gb()


def load_average(logical_cpus: int | None) -> tuple[float | None, float | None]:
    try:
        load_1m = os.getloadavg()[0]
    except (AttributeError, OSError):
        return None, None
    if not logical_cpus:
        return round(load_1m, 2), None
    return round(load_1m, 2), round(load_1m / max(logical_cpus, 1), 2)


def classify(logical_cpus: int | None, memory_gb: float | None, load_ratio: float | None) -> tuple[str, int, str, str]:
    if logical_cpus is None and memory_gb is None:
        return "unknown", 1, "adaptive-serial", "无法可靠读取本机配置，采用保守串行派工。"

    if (logical_cpus is not None and logical_cpus <= 4) or (memory_gb is not None and memory_gb < 8):
        tier, max_parallel, reason = "low", 1, "本机 CPU 或内存偏紧，员工可以全部入职，但正式任务一次只派一个。"
    elif (logical_cpus is not None and logical_cpus <= 8) or (memory_gb is not None and memory_gb < 16):
        tier, max_parallel, reason = "medium", 2, "本机配置中等，建议最多同时派两个员工，避免多个窗口一起重负载。"
    else:
        tier, max_parallel, reason = "high", 3, "本机配置较充足，默认最多同时派三个员工；除非 BOSS 明确要求，不全员并发。"

    if load_ratio is not None and load_ratio >= 0.75:
        return "busy", 1, "adaptive-serial", "当前系统负载较高，临时降级为一次只派一个员工。"
    if load_ratio is not None and load_ratio >= 0.5 and max_parallel > 1:
        max_parallel = max(1, max_parallel - 1)
        reason += " 当前负载略高，临时下调一个并发档位。"

    mode = "adaptive-serial" if max_parallel == 1 else "adaptive-limited"
    return tier, max_parallel, mode, reason


def inspect_capacity() -> CapacityReport:
    logical_cpus = os.cpu_count()
    memory_gb = total_memory_gb()
    load_1m, load_ratio = load_average(logical_cpus)
    tier, max_parallel, mode, reason = classify(logical_cpus, memory_gb, load_ratio)
    confidence = "medium" if logical_cpus is not None or memory_gb is not None else "low"
    return CapacityReport(
        platform=platform.platform(),
        logical_cpus=logical_cpus,
        memory_gb=memory_gb,
        load_1m=load_1m,
        load_ratio=load_ratio,
        tier=tier,
        max_parallel_employee_tasks=max_parallel,
        policy_mode=mode,
        reason=reason,
        confidence=confidence,
    )


def policy_payload(report: CapacityReport) -> dict[str, Any]:
    return {
        "mode": report.policy_mode,
        "max_parallel_employee_tasks": report.max_parallel_employee_tasks,
        "reason": report.reason,
        "source": "inspect_capacity.py",
        "capacity_tier": report.tier,
        "confidence": report.confidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect local capacity and recommend GaoGao Office dispatch concurrency.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    report = inspect_capacity()
    payload = asdict(report)
    payload["dispatch_policy"] = policy_payload(report)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"tier: {report.tier}")
        print(f"logical_cpus: {report.logical_cpus}")
        print(f"memory_gb: {report.memory_gb}")
        print(f"max_parallel_employee_tasks: {report.max_parallel_employee_tasks}")
        print(f"reason: {report.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
