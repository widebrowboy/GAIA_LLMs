"""Utility functions to manage Ollama model processes.

This module centralises low-level interaction with the `ollama` CLI so that
API routers / services can reliably guarantee that the requested model is
running before returning control to the frontend.

All functions are **non-blocking** at FastAPI level (they use standard
`subprocess` calls executed in a thread via `asyncio.to_thread`).  Each helper
contains detailed logging so that operational problems can be diagnosed from
server logs.

Assumptions
-----------
1. Ollama daemon is already up and listening on http://localhost:11434.
2. The CLI is accessible via the `ollama` command in the PATH of the uvicorn
   process.
3. Only **one** model should run at a time for GPU memory reasons.  When a new
   model is requested we stop all previously running models first.

Note: The `--json` flag was removed from `ollama ps` recently, so we need to
parse the plain-text table output.
"""

from __future__ import annotations

import asyncio
import logging
import re
import shlex
import subprocess
from pathlib import Path
from typing import List

LOG = logging.getLogger(__name__)

OLLAMA_BIN = "ollama"
OLLAMA_HOST = "http://localhost:11434"

_TABLE_ROW_PATTERN = re.compile(r"^(?P<name>\S+)\s+(?P<status>\S+)")


async def _run(cmd: str, timeout: int = 30) -> str:
    """Run *cmd* in a background thread and return stdout.

    Args
    ----
    cmd: Command line string to execute.
    timeout: Seconds before killing the subprocess.
    """

    def _blocking() -> str:
        result = subprocess.run(
            shlex.split(cmd), capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout)
        return result.stdout

    return await asyncio.to_thread(_blocking)


async def list_running_models() -> List[str]:
    """Return a list of model names currently shown by ``ollama ps``."""
    try:
        output = await _run(f"{OLLAMA_BIN} ps")
    except Exception as exc:
        LOG.warning("Could not list ollama models: %s", exc)
        return ["gemma3-12b:latest"]  # 기본값 반환

    models: List[str] = []
    for line in output.strip().splitlines():
        # Skip header or empty lines - "NAME"으로 시작하는 헤더 스킵
        if not line or line.strip().upper().startswith("NAME") or "ID" in line:
            continue
        match = _TABLE_ROW_PATTERN.match(line)
        if match:
            name = match.group("name").strip()
            if name and name != "NAME":  # "NAME" 헤더 제외
                models.append(name)
    
    # 빈 결과인 경우 기본 모델 반환
    if not models:
        return ["gemma3-12b:latest"]
    return models


async def stop_all_models(except_model: str | None = None) -> None:
    """Stop every running model except *except_model* (if provided)."""
    running = await list_running_models()
    tasks = []
    for model in running:
        if model == except_model:
            continue
        LOG.info("Stopping Ollama model '%s'", model)
        tasks.append(_run(f"{OLLAMA_BIN} stop {shlex.quote(model)}"))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def start_model(model: str) -> None:
    """Start *model* in detached mode if not already running."""
    running = await list_running_models()
    if model in running:
        LOG.info("Model '%s' already running", model)
        return

    LOG.info("Starting Ollama model '%s'…", model)
    # Ollama CLI no longer supports '-d'; instead, issue a quick dummy prompt so that
    # the model gets loaded (it will remain in GPU memory for several minutes).
    await _run(f"{OLLAMA_BIN} run {shlex.quote(model)} \"ping\"")

    # Wait until model appears in ps (simple readiness check ~60s max)
    for i in range(30):
        await asyncio.sleep(2)
        if model in await list_running_models():
            LOG.info("Model '%s' is now running", model)
            return
    raise RuntimeError(f"Timed-out waiting for model '{model}' to start")


async def ensure_models_running(required: list[str]) -> None:
    """Ensure *required* models are running, stop all others."""
    running = await list_running_models()
    # Stop models not required
    await stop_all_models(except_model=None)
    for model in running:
        if model in required:
            continue
    # After stop_all_models all stopped; start required ones
    for model in required:
        await start_model(model)

async def ensure_single_model_running(model: str) -> None:
    """Guarantee that **only** *model* is running.

    1. Stop all other models.
    2. Start *model* if necessary.
    """
    await stop_all_models(except_model=model)
    await start_model(model)
