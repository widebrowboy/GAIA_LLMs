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
        LOG.debug(f"ollama ps raw output: {repr(output)}")
    except Exception as exc:
        LOG.warning("Could not list ollama models: %s", exc)
        return []  # 빈 목록 반환

    models: List[str] = []
    lines = output.strip().splitlines()
    LOG.debug(f"ollama ps lines: {lines}")
    
    for line_num, line in enumerate(lines):
        LOG.debug(f"Processing line {line_num}: {repr(line)}")
        
        # Skip header or empty lines - "NAME"으로 시작하는 헤더 스킵
        if not line or line.strip().upper().startswith("NAME") or "ID" in line:
            LOG.debug(f"Skipping header/empty line: {repr(line)}")
            continue
            
        match = _TABLE_ROW_PATTERN.match(line)
        if match:
            name = match.group("name").strip()
            LOG.debug(f"Found model name: {repr(name)}")
            if name and name != "NAME":  # "NAME" 헤더 제외
                models.append(name)
        else:
            LOG.debug(f"No match for line: {repr(line)}")
    
    LOG.info(f"Final running models list: {models}")
    # 빈 결과는 빈 목록으로 반환 (기본값 반환하지 않음)
    return models


def _is_embedding_model(model_name: str) -> bool:
    """Check if a model is an embedding model based on naming convention."""
    model_lower = model_name.lower()
    embedding_keywords = ['embed', 'embedding', 'mxbai']
    return any(keyword in model_lower for keyword in embedding_keywords)

async def stop_all_models(except_model: str | None = None) -> None:
    """Stop every running model except *except_model* and embedding models."""
    running = await list_running_models()
    tasks = []
    for model in running:
        if model == except_model:
            continue
        # 임베딩 모델은 중지하지 않음 (다중 실행 허용)
        if _is_embedding_model(model):
            LOG.info("Keeping embedding model '%s' running", model)
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
    
    # 임베딩 모델과 일반 모델에 따라 다른 시작 방법 사용
    if _is_embedding_model(model):
        LOG.info("Detected embedding model '%s', using API embeddings endpoint", model)
        # 임베딩 모델은 API를 통해 시작
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                LOG.info("Attempting to load embedding model via API: %s", model)
                response = await client.post(
                    "http://localhost:11434/api/embeddings",
                    json={
                        "model": model,
                        "prompt": "test embedding load"
                    }
                )
                if response.status_code == 200:
                    LOG.info("Embedding model '%s' loaded successfully via API", model)
                    return
                else:
                    LOG.warning("API embedding load failed with status %d: %s", 
                              response.status_code, response.text)
        except Exception as e:
            LOG.warning("API embedding load failed: %s", e)
        
        # 폴백: pull 명령어만 시도
        start_attempts = [
            (f"{OLLAMA_BIN} pull {shlex.quote(model)}", 120),
        ]
    else:
        LOG.info("Detected chat model '%s', using generate endpoint", model)
        start_attempts = [
            # 일반 모델: run with prompt (백그라운드에서 실행)
            (f"{OLLAMA_BIN} run {shlex.quote(model)} \"Hello\"", 30),
            # 폴백: pull 명령어
            (f"{OLLAMA_BIN} pull {shlex.quote(model)}", 120),
        ]
    
    for cmd, timeout in start_attempts:
        try:
            LOG.info("Attempting to start model with command: %s", cmd)
            # 백그라운드에서 실행하도록 subprocess 직접 사용
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 짧은 시간만 대기 (모델 로딩이 시작되면 충분)
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                # 타임아웃은 정상 - 모델이 백그라운드에서 실행 중
                LOG.info("Model loading started in background")
            
        except Exception as e:
            LOG.warning("Failed with method: %s, error: %s", cmd, e)
            continue

    # Wait until model appears in ps (확장된 readiness check ~90s max)
    LOG.info("Waiting for model '%s' to appear in running list...", model)
    for i in range(45):  # 45회 * 2초 = 90초
        await asyncio.sleep(2)
        current_running = await list_running_models()
        
        # 디버그: 현재 실행 중인 모델 목록 출력
        if i % 5 == 0:  # 10초마다 상태 출력
            LOG.info("Current running models (attempt %d/45): %s", i + 1, current_running)
        
        if model in current_running:
            LOG.info("Model '%s' is now running (attempt %d/45)", model, i + 1)
            
            # 추가 안정성 확인 - 몇 초 더 대기하여 모델이 완전히 로드되었는지 확인
            LOG.info("Verifying model '%s' stability...", model)
            await asyncio.sleep(3)
            
            final_check = await list_running_models()
            if model in final_check:
                LOG.info("Model '%s' is stable and ready", model)
                return
            else:
                LOG.warning("Model '%s' disappeared during stability check, retrying...", model)
        else:
            LOG.debug("Model '%s' not yet running (attempt %d/45)", model, i + 1)
    
    # 최종 실패
    final_running = await list_running_models()
    raise RuntimeError(f"Timed-out waiting for model '{model}' to start. Current running models: {final_running}")


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
    """Guarantee that **only** *model* is running (excluding embedding models).

    1. Stop all other non-embedding models.
    2. Start *model* if necessary.
    3. Verify model is actually running.
    
    Note: Embedding models (mxbai-embed-large, etc.) are preserved and can run alongside.
    """
    LOG.info(f"🎯 단일 모델 실행 보장 시작: {model}")
    
    # 1단계: 모든 비임베딩 모델 중지 (요청된 모델 및 임베딩 모델 제외)
    await stop_all_models(except_model=model)
    
    # 2단계: 요청된 모델이 실행 중인지 확인
    running_models = await list_running_models()
    LOG.info(f"📋 중지 후 실행 중인 모델들: {running_models}")
    
    # 3단계: 요청된 모델 시작 (이미 실행 중이 아닌 경우)
    if model not in running_models:
        LOG.info(f"🚀 모델 {model} 시작 중...")
        await start_model(model)
    else:
        LOG.info(f"✅ 모델 {model} 이미 실행 중")
    
    # 4단계: 최종 확인 - 요청된 모델이 실행되고 있는지 검증
    final_running = await list_running_models()
    LOG.info(f"📋 최종 실행 중인 모델들: {final_running}")
    
    if model not in final_running:
        raise RuntimeError(f"모델 {model} 시작에 실패했습니다. 현재 실행 중: {final_running}")
    
    # 임베딩이 아닌 다른 모델들이 여전히 실행 중인 경우 경고 (임베딩 모델은 허용)
    other_running = [m for m in final_running if m != model and not _is_embedding_model(m)]
    if other_running:
        LOG.warning(f"⚠️ 다른 비임베딩 모델들이 여전히 실행 중: {other_running}")
    
    # 임베딩 모델 목록 출력 (정보용)
    embedding_running = [m for m in final_running if _is_embedding_model(m)]
    if embedding_running:
        LOG.info(f"🔧 실행 중인 임베딩 모델들 (유지됨): {embedding_running}")
    
    LOG.info(f"✅ 단일 모델 실행 보장 완료: {model}")
