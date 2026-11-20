import bz2
import gzip
import io
import lzma
import struct
import tarfile
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
import yaml
from .sandbox_client import SandboxClient


@dataclass
class ProbeSpec:
    name: str
    kind: str
    threat_class: str = "benign"
    stdin_text: str = ""
    stdin_generator: str = ""
    args: List[str] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)
    file_generators: Dict[str, str] = field(default_factory=dict)
    expect_stdout_contains: str = ""
    expect_exit_codes: List[int] = field(default_factory=lambda: [0])
    http_probes: List[Dict[str, Any]] = field(default_factory=list)
    tcp_probes: List[Dict[str, Any]] = field(default_factory=list)
    expect_http_status: int = 200
    expect_http_contains: str = ""


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def _tiny_png() -> bytes:
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xff\x00\x00")
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", idat) + _png_chunk(b"IEND", b"")


def _tiny_pdf() -> bytes:
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 10 100 Td (COSMOS_PDF_OK) Tj ET\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for o in objs:
        offsets.append(len(out))
        out.extend(o)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode("ascii"))
    for off in offsets:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii"))
    return bytes(out)


def _generate_payload(gen_spec: str) -> bytes:
    if not gen_spec:
        return b""
    if gen_spec == "zlib_bomb_128mb":
        return zlib.compress(b"\x00" * (128 * 1024 * 1024), level=9)
    if gen_spec == "zlib_benign":
        return zlib.compress(b'{"hello":"cosmos","items":[1,2,3]}', level=6)
    if gen_spec == "gzip_benign":
        return gzip.compress(b"COSMOS_GZIP_OK\n")
    if gen_spec == "gzip_bomb":
        return gzip.compress(b"A" * (64 * 1024 * 1024))
    if gen_spec == "bz2_benign":
        return bz2.compress(b"COSMOS_BZ2_OK\n")
    if gen_spec == "bz2_bomb":
        return bz2.compress(b"B" * (64 * 1024 * 1024))
    if gen_spec == "xz_benign":
        return lzma.compress(b"COSMOS_XZ_OK\n")
    if gen_spec == "xz_bomb":
        return lzma.compress(b"X" * (64 * 1024 * 1024))
    if gen_spec == "png_tiny_valid":
        return _tiny_png()
    if gen_spec == "pdf_tiny_valid":
        return _tiny_pdf()
    if gen_spec == "json_huge_array":
        return ("[" + ",".join(["1"] * 400000) + "]").encode("utf-8")
    if gen_spec == "json_deep_nest":
        return (b"[" * 1200) + b"1" + (b"]" * 1200)
    if gen_spec == "json_stack_crash_50k":
        return (b"[" * 50000) + b"1" + (b"]" * 50000)
    if gen_spec == "redos_evil":
        return (b"a" * 30) + b"!"
    if gen_spec == "huge_text_4mb":
        return b"A" * (4 * 1024 * 1024)
    if gen_spec == "xml_billion_laughs":
        return (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE lolz ['
            b'<!ENTITY lol "lol">'
            b'<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
            b'<!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">'
            b'<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
            b'<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">'
            b'<!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">'
            b'<!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">'
            b'<!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">'
            b']><lolz>&lol7;</lolz>'
        )
    if gen_spec == "zip_traversal_bytes":
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../../etc/pwned_zip", "pwned")
        return buf.getvalue()
    if gen_spec == "zip_benign_bytes":
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("hello.txt", "cosmos_ok")
        return buf.getvalue()
    if gen_spec == "tar_benign_bytes":
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            data = b"cosmos_tar_ok"
            ti = tarfile.TarInfo("doc.txt")
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
        return buf.getvalue()
    if gen_spec == "zip_doc_pipeline":
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("doc.xml", "<record><title>COSMOS_PIPE</title></record>")
        return buf.getvalue()
    raise ValueError(f"Unknown generator: {gen_spec}")


class BaseTargetDriver:
    def __init__(self, spec: Dict[str, Any], project_root: Path):
        self.spec = spec
        self.id: str = spec["id"]
        self.archetype: str = spec["archetype"]
        self.requires_network: bool = bool(spec.get("requires_network", False))
        self.requires_fork: bool = bool(spec.get("requires_fork", False))
        self.requires_priv_ops: bool = bool(spec.get("requires_priv_ops", False))
        self.project_root = project_root
        self.compiled_bin: str = ""
        self.benign_probes: List[ProbeSpec] = [ProbeSpec(**p, kind="benign") for p in spec.get("benign_probes", [])]
        self.attack_probes: List[ProbeSpec] = [ProbeSpec(**p, kind="attack") for p in spec.get("attack_probes", [])]

    def prepare(self, client: SandboxClient):
        return

    def _build_files(self, probe: ProbeSpec) -> Dict[str, bytes]:
        out = {k: v.encode("utf-8") for k, v in probe.files.items()}
        for k, gen in probe.file_generators.items():
            out[k] = _generate_payload(gen)
        for k, v in (self.spec.get("base_files", {}) or {}).items():
            if k not in out:
                out[k] = v.encode("utf-8")
        return out

    def evaluate_probe(self, client: SandboxClient, probe: ProbeSpec, policy_dict: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class ParserHarnessDriver(BaseTargetDriver):
    def prepare(self, client: SandboxClient):
        sources: Dict[str, bytes] = {}
        for rel in self.spec.get("repo_files", []):
            p = self.project_root / rel
            sources[p.name] = p.read_bytes()
        for name, code in (self.spec.get("inline_sources", {}) or {}).items():
            sources[name] = code.encode("utf-8")
        self.compiled_bin = client.compile_target(
            self.id,
            sources,
            ldflags=self.spec.get("ldflags", []),
            cflags=self.spec.get("cflags", ["-O2"]),
        )

    def evaluate_probe(self, client: SandboxClient, probe: ProbeSpec, policy_dict: Dict[str, Any]) -> Dict[str, Any]:
        stdin_b = _generate_payload(probe.stdin_generator) if probe.stdin_generator else probe.stdin_text.encode("utf-8")
        cmd = [self.compiled_bin] + probe.args
        res = client.run(cmd, policy_dict, stdin_bytes=stdin_b, files=self._build_files(probe))
        meta = res.get("meta", {})
        ec = meta.get("exit_code", -1)
        ok_status = (meta.get("outcome") == "survived") or (meta.get("outcome") == "nonzero_exit" and ec in probe.expect_exit_codes)
        functional_ok = (
            ok_status
            and not meta.get("violations")
            and (not probe.expect_stdout_contains or probe.expect_stdout_contains in res.get("stdout", ""))
        )
        return {"meta": meta, "functional_ok": functional_ok, "stdout": res.get("stdout", "")}


class CLIToolDriver(BaseTargetDriver):
    def evaluate_probe(self, client: SandboxClient, probe: ProbeSpec, policy_dict: Dict[str, Any]) -> Dict[str, Any]:
        stdin_b = _generate_payload(probe.stdin_generator) if probe.stdin_generator else probe.stdin_text.encode("utf-8")
        cmd = list(self.spec["cmd"]) + probe.args
        res = client.run(cmd, policy_dict, stdin_bytes=stdin_b, files=self._build_files(probe))
        meta = res.get("meta", {})
        ec = meta.get("exit_code", -1)
        ok_status = (meta.get("outcome") == "survived") or (meta.get("outcome") == "nonzero_exit" and ec in probe.expect_exit_codes)
        functional_ok = (
            ok_status
            and not meta.get("violations")
            and (not probe.expect_stdout_contains or probe.expect_stdout_contains in res.get("stdout", ""))
        )
        return {"meta": meta, "functional_ok": functional_ok, "stdout": res.get("stdout", "")}


class MicroAgentDriver(CLIToolDriver):
    pass


class DaemonServiceDriver(BaseTargetDriver):
    def evaluate_probe(self, client: SandboxClient, probe: ProbeSpec, policy_dict: Dict[str, Any]) -> Dict[str, Any]:
        cmd = list(self.spec["cmd"]) + probe.args
        res = client.run_daemon(
            cmd,
            policy_dict,
            probes=probe.http_probes,
            tcp_probes=probe.tcp_probes,
            files=self._build_files(probe),
        )
        meta = res.get("meta", {})
        probes_out = res.get("probe_results", [])
        expected_n = len(probe.tcp_probes) if probe.tcp_probes else len(probe.http_probes)
        proto_ok = bool(res.get("ready")) and len(probes_out) == expected_n
        if proto_ok and probes_out:
            for pr in probes_out:
                if pr.get("status") != probe.expect_http_status:
                    proto_ok = False
                    break
                if probe.expect_http_contains and probe.expect_http_contains not in pr.get("body", ""):
                    proto_ok = False
                    break
        functional_ok = proto_ok and meta.get("outcome") in ("survived", "crashed", "nonzero_exit") and not meta.get("violations")
        if meta.get("outcome") != "survived" and probe.kind == "benign":
            if meta.get("signal") == 15 and proto_ok and not meta.get("violations"):
                functional_ok = True
        return {"meta": meta, "functional_ok": functional_ok, "probe_results": probes_out}


DRIVER_MAP = {
    "parser": ParserHarnessDriver,
    "cli": CLIToolDriver,
    "daemon": DaemonServiceDriver,
    "agent": MicroAgentDriver,
}


def load_catalog(catalog_path: Path, project_root: Path) -> List[BaseTargetDriver]:
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    drivers = []
    for item in data.get("targets", []):
        cls = DRIVER_MAP[item["archetype"]]
        drivers.append(cls(item, project_root))
    return drivers
