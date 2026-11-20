import base64
import json
import os
import signal
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ENFORCER = "/usr/local/bin/cosmos_enforcer"
WORK_ROOT = Path("/tmp/cosmos_work")
BIN_ROOT = Path("/opt/cosmos_targets")
WORK_ROOT.mkdir(parents=True, exist_ok=True)
BIN_ROOT.mkdir(parents=True, exist_ok=True)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _stage_files(tmpdir: str, files: dict):
    base = Path(tmpdir).resolve()
    for rel, b64_content in (files or {}).items():
        dest = (base / rel).resolve()
        if not str(dest).startswith(str(base)):
            raise ValueError(f"Unsafe staged path: {rel}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(base64.b64decode(b64_content))


def _enforcer_flags(policy: dict, tmpdir: str, meta_path: str) -> list:
    allow_net_legacy = policy.get("allow_network", False)
    allow_bind = policy.get("allow_net_bind", allow_net_legacy)
    allow_out = policy.get("allow_net_outbound", allow_net_legacy)
    flags = [
        ENFORCER,
        "--meta-file", meta_path,
        "--cpu-sec", str(int(policy.get("cpu_sec", 2))),
        "--mem-bytes", str(int(policy.get("mem_mb", 256)) * 1024 * 1024),
        "--fsize-bytes", str(int(policy.get("fsize_mb", 64)) * 1024 * 1024),
        "--nofile", str(int(policy.get("nofile", 128))),
        "--wall-ms", str(int(policy.get("wall_ms", 3000))),
        "--allow-execve", "1" if policy.get("allow_execve", False) else "0",
        "--allow-net-bind", "1" if allow_bind else "0",
        "--allow-net-outbound", "1" if allow_out else "0",
        "--allow-fork", "1" if policy.get("allow_fork", False) else "0",
        "--allow-priv-ops", "1" if policy.get("allow_priv_ops", False) else "0",
        "--allow-debug-ops", "1" if policy.get("allow_debug_ops", False) else "0",
        "--kill-on-violation", "1" if policy.get("kill_on_violation", True) else "0",
    ]
    fs_mode = policy.get("fs_mode", "workspace_only")
    if fs_mode == "workspace_only":
        flags.extend(["--ro-path", "/", "--rw-path", tmpdir])
    elif fs_mode == "readonly":
        flags.extend(["--ro-path", "/"])
    return flags


def _probe_http(port: int, probes: list) -> list:
    results = []
    expanded = []
    for p in probes:
        for _ in range(int(p.get("repeat", 1))):
            expanded.append(p)
    for p in expanded:
        method = p.get("method", "GET")
        path = p.get("path", "/")
        body = p.get("body", "")
        if not body and p.get("body_bytes"):
            body = "A" * int(p["body_bytes"])
        elif not body and p.get("body_kb"):
            body = "A" * (int(p["body_kb"]) * 1024)
        url = f"http://127.0.0.1:{port}{path}"
        data = body.encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                resp_body = resp.read().decode("utf-8", errors="replace")
                results.append({"status": resp.status, "body": resp_body, "error": ""})
        except urllib.error.HTTPError as e:
            results.append({"status": e.code, "body": e.read().decode("utf-8", errors="replace"), "error": str(e)})
        except Exception as e:
            results.append({"status": 0, "body": "", "error": str(e)})
    return results


def _probe_tcp(port: int, tcp_probes: list) -> list:
    results = []
    for p in tcp_probes:
        payload = p.get("send", "")
        if p.get("send_repeat"):
            payload = payload * int(p["send_repeat"])
        raw = payload.encode("utf-8")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.5) as s:
                s.settimeout(1.0)
                s.sendall(raw)
                resp = s.recv(4096).decode("utf-8", errors="replace")
                results.append({"status": 200, "body": resp, "error": ""})
        except Exception as e:
            results.append({"status": 0, "body": "", "error": str(e)})
    return results


class SandboxHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send_json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "enforcer": Path(ENFORCER).exists()})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(length).decode("utf-8"))

        if self.path == "/compile":
            target_id = req["target_id"]
            sources = req["sources"]
            ldflags = req.get("ldflags", [])
            cflags = req.get("cflags", ["-O2"])
            out_bin = BIN_ROOT / target_id
            with tempfile.TemporaryDirectory(dir=WORK_ROOT) as tmpdir:
                _stage_files(tmpdir, sources)
                c_files = [
                    str(Path(tmpdir) / name)
                    for name in sources.keys()
                    if name.endswith(".c") or name.endswith(".cpp")
                ]
                compiler = "g++" if any(f.endswith(".cpp") for f in c_files) else "gcc"
                cmd = [compiler] + cflags + ["-I", tmpdir, "-o", str(out_bin)] + c_files + ldflags
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if res.returncode != 0:
                    self._send_json(400, {"ok": False, "stderr": res.stderr})
                    return
                self._send_json(200, {"ok": True, "binary_path": str(out_bin)})
            return

        if self.path == "/run":
            policy = req.get("policy", {})
            stdin_data = base64.b64decode(req.get("stdin_b64", ""))
            with tempfile.TemporaryDirectory(dir=WORK_ROOT) as tmpdir:
                _stage_files(tmpdir, req.get("files", {}))
                cmd = [arg.replace("{WORKDIR}", tmpdir) for arg in req["cmd"]]
                meta_path = str(Path(tmpdir) / ".cosmos_meta.json")
                full_cmd = _enforcer_flags(policy, tmpdir, meta_path) + ["--"] + cmd
                proc = subprocess.run(
                    full_cmd,
                    input=stdin_data,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir,
                    timeout=max(5, int(policy.get("wall_ms", 3000) / 1000) + 5),
                )
                mp = Path(meta_path)
                meta = json.loads(mp.read_text()) if mp.exists() else {}
                self._send_json(200, {
                    "meta": meta,
                    "enforcer_rc": proc.returncode,
                    "stdout_b64": base64.b64encode(proc.stdout).decode("ascii"),
                    "stderr_b64": base64.b64encode(proc.stderr).decode("ascii"),
                })
            return

        if self.path == "/run_daemon":
            policy = req.get("policy", {})
            probes = req.get("probes", [])
            tcp_probes = req.get("tcp_probes", [])
            port = _free_port()
            with tempfile.TemporaryDirectory(dir=WORK_ROOT) as tmpdir:
                staged = {}
                for k, b64v in (req.get("files", {}) or {}).items():
                    txt = base64.b64decode(b64v).decode("utf-8", errors="replace")
                    txt = txt.replace("{PORT}", str(port)).replace("{WORKDIR}", tmpdir)
                    staged[k] = base64.b64encode(txt.encode("utf-8")).decode("ascii")
                _stage_files(tmpdir, staged)
                cmd = [
                    arg.replace("{WORKDIR}", tmpdir).replace("{PORT}", str(port))
                    for arg in req["cmd"]
                ]
                meta_path = str(Path(tmpdir) / ".cosmos_meta.json")
                full_cmd = _enforcer_flags(policy, tmpdir, meta_path) + ["--"] + cmd
                proc = subprocess.Popen(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir,
                )
                ready = False
                for _ in range(50):
                    if proc.poll() is not None:
                        break
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.05):
                            ready = True
                            break
                    except OSError:
                        time.sleep(0.025)

                if ready and tcp_probes:
                    probe_results = _probe_tcp(port, tcp_probes)
                elif ready:
                    probe_results = _probe_http(port, probes)
                else:
                    probe_results = []

                if proc.poll() is None:
                    proc.send_signal(signal.SIGTERM)
                try:
                    out, err = proc.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    out, err = proc.communicate()

                mp = Path(meta_path)
                meta = json.loads(mp.read_text()) if mp.exists() else {}
                self._send_json(200, {
                    "meta": meta,
                    "ready": ready,
                    "probe_results": probe_results,
                    "enforcer_rc": proc.returncode,
                    "stdout_b64": base64.b64encode(out).decode("ascii"),
                    "stderr_b64": base64.b64encode(err).decode("ascii"),
                })
            return

        self._send_json(404, {"error": "not_found"})


if __name__ == "__main__":
    port = int(os.environ.get("COSMOS_SANDBOX_PORT", "8787"))
    server = ThreadingHTTPServer(("0.0.0.0", port), SandboxHandler)
    print(f"cosmos-sandboxd listening on :{port}", flush=True)
    server.serve_forever()
