import base64
import json
import subprocess
import time
import urllib.request
from typing import Any, Dict, List, Optional


class SandboxClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8787, image: str = "cosmos-sandbox:v3"):
        self.base_url = f"http://{host}:{port}"
        self.port = port
        self.image = image
        self.container_name = "cosmos-sandboxd"

    def ensure_running(self):
        if self._is_healthy():
            return
        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True)
        res = subprocess.run(
            [
                "docker", "run", "-d",
                "--name", self.container_name,
                "-p", f"127.0.0.1:{self.port}:8787",
                self.image,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        for _ in range(50):
            if self._is_healthy():
                return
            time.sleep(0.1)
        raise RuntimeError(f"cosmos-sandboxd failed to become healthy: {res.stdout} {res.stderr}")

    def _is_healthy(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/health", timeout=0.5) as r:
                return r.status == 200
        except Exception:
            return False

    def _post(self, path: str, payload: Dict[str, Any], timeout: int = 35) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def compile_target(self, target_id: str, sources: Dict[str, bytes], ldflags: Optional[List[str]] = None, cflags: Optional[List[str]] = None) -> str:
        encoded = {k: base64.b64encode(v).decode("ascii") for k, v in sources.items()}
        res = self._post("/compile", {
            "target_id": target_id,
            "sources": encoded,
            "ldflags": ldflags or [],
            "cflags": cflags or ["-O2"],
        })
        if not res.get("ok"):
            raise RuntimeError(f"Compile failed for {target_id}: {res.get('stderr')}")
        return res["binary_path"]

    def run(self, cmd: List[str], policy: Dict[str, Any], stdin_bytes: bytes = b"", files: Optional[Dict[str, bytes]] = None) -> Dict[str, Any]:
        encoded_files = {k: base64.b64encode(v).decode("ascii") for k, v in (files or {}).items()}
        res = self._post("/run", {
            "cmd": cmd,
            "policy": policy,
            "stdin_b64": base64.b64encode(stdin_bytes).decode("ascii"),
            "files": encoded_files,
        })
        res["stdout"] = base64.b64decode(res.get("stdout_b64", "")).decode("utf-8", errors="replace")
        res["stderr"] = base64.b64decode(res.get("stderr_b64", "")).decode("utf-8", errors="replace")
        return res

    def run_daemon(
        self,
        cmd: List[str],
        policy: Dict[str, Any],
        probes: Optional[List[Dict[str, Any]]] = None,
        tcp_probes: Optional[List[Dict[str, Any]]] = None,
        files: Optional[Dict[str, bytes]] = None,
    ) -> Dict[str, Any]:
        encoded_files = {k: base64.b64encode(v).decode("ascii") for k, v in (files or {}).items()}
        res = self._post("/run_daemon", {
            "cmd": cmd,
            "policy": policy,
            "probes": probes or [],
            "tcp_probes": tcp_probes or [],
            "files": encoded_files,
        })
        res["stdout"] = base64.b64decode(res.get("stdout_b64", "")).decode("utf-8", errors="replace")
        res["stderr"] = base64.b64decode(res.get("stderr_b64", "")).decode("utf-8", errors="replace")
        return res
