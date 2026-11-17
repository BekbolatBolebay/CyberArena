#!/usr/bin/env python3
"""
CyberArena Hardware-Adaptive Profiler & Compose Generator.

Inspects host CPU cores, total/available RAM, free disk space, and container
runtime availability, then selects an optimal profile (light, balanced, full)
and generates `docker-compose.adaptive.yml` so laptops never overheat or OOM.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HostSpecs:
    cpu_cores: int
    total_ram_mb: int
    avail_ram_mb: int
    free_disk_gb: float
    has_compose: bool
    runtime_name: str


PROFILE_CONFIGS: dict[str, dict[str, Any]] = {
    "light": {
        "label": "LIGHT (Үнемді режим — ~60 MB RAM)",
        "description": "Әлсіз немесе бос жады аз ноутбуктерге арналған. Docker-сіз таза Python-да іске қосылады.",
        "mode": "native",
        "services": ["portal", "ip-camera"],
        "estimated_ram_mb": 64,
    },
    "balanced": {
        "label": "BALANCED (Орташа режим — ~768 MB RAM)",
        "description": "4–11 GB RAM ноутбуктерге оңтайлы. Portal + IP Camera + OWASP Juice Shop қосылады.",
        "mode": "docker",
        "services": ["portal", "juice-shop", "ip-camera"],
        "limits": {
            "portal": {"cpus": "0.35", "memory": "192M"},
            "juice-shop": {"cpus": "0.45", "memory": "448M"},
            "ip-camera": {"cpus": "0.20", "memory": "128M"},
        },
        "estimated_ram_mb": 768,
    },
    "full": {
        "label": "FULL (Толық полигон — ~1.5 GB RAM)",
        "description": "12+ GB RAM және көп ядролы жүйелерге арналған. Барлық 4 зертхана толық қуатта қосылады.",
        "mode": "docker",
        "services": ["portal", "juice-shop", "dvwa", "ip-camera"],
        "limits": {
            "portal": {"cpus": "0.50", "memory": "256M"},
            "juice-shop": {"cpus": "0.75", "memory": "640M"},
            "dvwa": {"cpus": "0.75", "memory": "512M"},
            "ip-camera": {"cpus": "0.25", "memory": "128M"},
        },
        "estimated_ram_mb": 1536,
    },
}


def read_meminfo_mb() -> tuple[int, int]:
    """Return (total_ram_mb, available_ram_mb) on Linux; safe fallback otherwise."""
    meminfo = Path("/proc/meminfo")
    if meminfo.is_file():
        values: dict[str, int] = {}
        for line in meminfo.read_text(encoding="utf-8", errors="ignore").splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                key = parts[0].rstrip(":")
                values[key] = int(parts[1])  # kB
        total_kb = values.get("MemTotal", 0)
        avail_kb = values.get("MemAvailable", values.get("MemFree", 0))
        if total_kb > 0:
            return total_kb // 1024, max(avail_kb // 1024, 256)

    # Fallback for macOS / non-Linux
    try:
        out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True, timeout=2)
        total_mb = int(out.strip()) // (1024 * 1024)
        return total_mb, total_mb // 2
    except Exception:
        return 4096, 2048


def detect_container_runtime() -> tuple[bool, str]:
    """Detect whether docker-compose / docker compose / podman is available and usable."""
    has_compose_bin = bool(shutil.which("docker-compose"))
    has_docker_bin = bool(shutil.which("docker"))
    if not has_compose_bin and not has_docker_bin:
        return False, "none"

    if has_docker_bin:
        try:
            ver = subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=3,
                check=False,
            )
            out = (ver.stdout or "").lower()
            is_podman = "podman" in out or bool(shutil.which("podman"))
            if has_compose_bin:
                return True, f"{'podman' if is_podman else 'docker'} (docker-compose)"
            comp = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
                check=False,
            )
            if comp.returncode == 0:
                return True, f"{'podman' if is_podman else 'docker'} compose"
        except OSError:
            pass

    if has_compose_bin:
        return True, "docker-compose"
    return False, "none"


def detect_host_specs(base_dir: Path) -> HostSpecs:
    """Gather host CPU, memory, disk, and container runtime info."""
    cpu_cores = os.cpu_count() or 2
    total_ram_mb, avail_ram_mb = read_meminfo_mb()
    disk = shutil.disk_usage(str(base_dir))
    free_disk_gb = round(disk.free / (1024 ** 3), 1)
    has_compose, runtime_name = detect_container_runtime()
    return HostSpecs(
        cpu_cores=cpu_cores,
        total_ram_mb=total_ram_mb,
        avail_ram_mb=avail_ram_mb,
        free_disk_gb=free_disk_gb,
        has_compose=has_compose,
        runtime_name=runtime_name,
    )


def choose_profile(specs: HostSpecs, forced: str | None = None) -> tuple[str, str]:
    """Select the optimal adaptive profile and return (profile_name, reason)."""
    if forced:
        name = forced.lower()
        if name not in PROFILE_CONFIGS:
            raise ValueError(f"Белгісіз профиль: {forced}. Қолжетімді: light, balanced, full")
        if PROFILE_CONFIGS[name]["mode"] == "docker" and not specs.has_compose:
            return "light", f"'{name}' таңдалды, бірақ Docker табылмады -> 'light' режиміне ауысты."
        return name, f"Қолмен таңдалды: {name.upper()}"

    if not specs.has_compose:
        return "light", "Docker/Compose табылмады -> жеңіл Python режимі таңдалды."
    if specs.total_ram_mb < 4500 or specs.avail_ram_mb < 1400 or specs.cpu_cores <= 2:
        return "light", "Жедел жады немесе CPU қоры шектеулі -> қызуды болдырмау үшін LIGHT режимі таңдалды."
    if specs.free_disk_gb < 3.0:
        return "light", "Бос диск орны < 3 GB -> LIGHT режимі таңдалды."
    if specs.total_ram_mb < 11500 or specs.avail_ram_mb < 3000 or specs.cpu_cores < 6 or specs.free_disk_gb < 6.0:
        return "balanced", "Орташа қуатты жүйе -> BALANCED режимі таңдалды (Juice Shop + Portal + Камера)."
    return "full", "Қуатты жүйе анықталды -> FULL режимі таңдалды (барлық 4 жүйе)."


def render_adaptive_compose(profile: str) -> str:
    """Build docker-compose YAML tailored to the selected profile limits."""
    cfg = PROFILE_CONFIGS[profile]
    if cfg["mode"] != "docker":
        return ""

    limits = cfg["limits"]
    services_yaml: list[str] = [
        "# Автоматты түрде scripts/hardware_profile.py арқылы жасалған адаптивті конфигурация",
        "services:",
    ]

    if "portal" in cfg["services"]:
        lim = limits["portal"]
        services_yaml.append(
            f"""  portal:
    build:
      context: ./portal
      dockerfile: Dockerfile
    container_name: arena_portal
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - arena_portal_data:/app/data
    networks:
      - cyber_net
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          cpus: '{lim["cpus"]}'
          memory: {lim["memory"]}"""
        )

    if "juice-shop" in cfg["services"]:
        lim = limits["juice-shop"]
        services_yaml.append(
            f"""  juice-shop:
    image: docker.io/bkimminich/juice-shop:latest
    container_name: arena_juice_shop
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    networks:
      - cyber_net
    deploy:
      resources:
        limits:
          cpus: '{lim["cpus"]}'
          memory: {lim["memory"]}"""
        )

    if "dvwa" in cfg["services"]:
        lim = limits["dvwa"]
        services_yaml.append(
            f"""  dvwa:
    image: docker.io/vulnerables/web-dvwa:latest
    container_name: arena_dvwa
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:80"
    networks:
      - cyber_net
    deploy:
      resources:
        limits:
          cpus: '{lim["cpus"]}'
          memory: {lim["memory"]}"""
        )

    if "ip-camera" in cfg["services"]:
        lim = limits["ip-camera"]
        services_yaml.append(
            f"""  ip-camera:
    build:
      context: ./targets/ip_camera
      dockerfile: Dockerfile
    container_name: arena_ip_camera
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"
    networks:
      - cyber_net
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          cpus: '{lim["cpus"]}'
          memory: {lim["memory"]}"""
        )

    services_yaml.append(
        """
networks:
  cyber_net:
    driver: bridge

volumes:
  arena_portal_data:"""
    )
    return "\n\n".join(services_yaml) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="CyberArena Hardware-Adaptive Profiler")
    parser.add_argument("--profile", choices=["light", "balanced", "full"], default=None)
    parser.add_argument("--write-compose", type=Path, default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    specs = detect_host_specs(repo_root)
    profile, reason = choose_profile(specs, forced=args.profile)
    cfg = PROFILE_CONFIGS[profile]

    if args.write_compose and cfg["mode"] == "docker":
        content = render_adaptive_compose(profile)
        args.write_compose.write_text(content, encoding="utf-8")

    result = {
        "specs": asdict(specs),
        "profile": profile,
        "label": cfg["label"],
        "mode": cfg["mode"],
        "services": cfg["services"],
        "estimated_ram_mb": cfg["estimated_ram_mb"],
        "reason": reason,
    }

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("=== CYBER ARENA HARDWARE PROFILER ===")
    print(f"CPU Cores       : {specs.cpu_cores}")
    print(f"RAM (Total/Free): {specs.total_ram_mb} MB / {specs.avail_ram_mb} MB")
    print(f"Disk Free       : {specs.free_disk_gb} GB")
    print(f"Container Engine: {specs.runtime_name}")
    print(f"Selected Profile: {cfg['label']}")
    print(f"Reason          : {reason}")
    print(f"Active Targets  : {', '.join(cfg['services'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
