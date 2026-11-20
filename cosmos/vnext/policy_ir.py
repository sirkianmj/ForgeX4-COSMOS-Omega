import copy
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from typing import Dict, Tuple


FS_MODES = ("readonly", "workspace_only", "unrestricted")


@dataclass
class PolicyIR:
    cpu_sec: int = 1
    mem_mb: int = 128
    fsize_mb: int = 32
    nofile: int = 64
    wall_ms: int = 600
    allow_execve: bool = False
    allow_net_bind: bool = False
    allow_net_outbound: bool = False
    allow_fork: bool = False
    allow_priv_ops: bool = False
    allow_debug_ops: bool = False
    fs_mode: str = "workspace_only"
    kill_on_violation: bool = True
    max_cpu_ms_budget: float = 250.0
    max_rss_kb_budget: int = 65536

    def to_dict(self) -> Dict:
        return asdict(self)

    def kernel_dict(self) -> Dict:
        return {
            "cpu_sec": self.cpu_sec,
            "mem_mb": self.mem_mb,
            "fsize_mb": self.fsize_mb,
            "nofile": self.nofile,
            "wall_ms": self.wall_ms,
            "allow_execve": self.allow_execve,
            "allow_net_bind": self.allow_net_bind,
            "allow_net_outbound": self.allow_net_outbound,
            "allow_fork": self.allow_fork,
            "allow_priv_ops": self.allow_priv_ops,
            "allow_debug_ops": self.allow_debug_ops,
            "fs_mode": self.fs_mode,
            "kill_on_violation": self.kill_on_violation,
        }

    def kernel_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.kernel_dict(), sort_keys=True).encode("utf-8")).hexdigest()[:16]

    def canonical_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]

    def privilege_surface(self) -> float:
        cap_score = (
            (0.20 if self.allow_execve else 0.0)
            + (0.10 if self.allow_net_bind else 0.0)
            + (0.16 if self.allow_net_outbound else 0.0)
            + (0.12 if self.allow_fork else 0.0)
            + (0.08 if self.allow_priv_ops else 0.0)
            + (0.08 if self.allow_debug_ops else 0.0)
            + (0.14 if self.fs_mode == "unrestricted" else (0.04 if self.fs_mode == "workspace_only" else 0.0))
        )
        res_score = 0.12 * min(
            1.0,
            (
                (self.mem_mb / 512.0)
                + (self.cpu_sec / 10.0)
                + (self.wall_ms / 5000.0)
                + (self.nofile / 256.0)
            ) / 4.0,
        )
        return round(min(1.0, cap_score + res_score), 4)

    @classmethod
    def permissive(cls) -> "PolicyIR":
        return cls(
            cpu_sec=2,
            mem_mb=512,
            fsize_mb=128,
            nofile=256,
            wall_ms=1200,
            allow_execve=True,
            allow_net_bind=True,
            allow_net_outbound=True,
            allow_fork=True,
            allow_priv_ops=True,
            allow_debug_ops=True,
            fs_mode="unrestricted",
            kill_on_violation=False,
            max_cpu_ms_budget=4000.0,
            max_rss_kb_budget=524288,
        )

    @classmethod
    def random_candidate(cls, rng: random.Random) -> "PolicyIR":
        return cls(
            cpu_sec=rng.choice([1, 2]),
            mem_mb=rng.choice([64, 128, 256]),
            fsize_mb=rng.choice([8, 32]),
            nofile=rng.choice([64, 128]),
            wall_ms=rng.choice([300, 550, 850]),
            allow_execve=rng.random() < 0.25,
            allow_net_bind=rng.random() < 0.35,
            allow_net_outbound=rng.random() < 0.25,
            allow_fork=rng.random() < 0.25,
            allow_priv_ops=rng.random() < 0.25,
            allow_debug_ops=rng.random() < 0.20,
            fs_mode=rng.choice(FS_MODES),
            kill_on_violation=True,
            max_cpu_ms_budget=rng.choice([2.0, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0]),
            max_rss_kb_budget=rng.choice([8192, 16384, 32768, 65536, 131072, 262144]),
        )

    def mutate(self, rng: random.Random) -> "PolicyIR":
        child = copy.deepcopy(self)
        field = rng.choice([
            "mem_mb", "fsize_mb", "wall_ms",
            "allow_execve", "allow_net_bind", "allow_net_outbound",
            "allow_fork", "allow_priv_ops", "allow_debug_ops", "fs_mode",
            "max_cpu_ms_budget", "max_cpu_ms_budget",
            "max_rss_kb_budget", "max_rss_kb_budget",
        ])
        if field == "mem_mb":
            child.mem_mb = rng.choice([64, 96, 128, 192, 256, 384])
        elif field == "fsize_mb":
            child.fsize_mb = rng.choice([8, 16, 32, 64])
        elif field == "wall_ms":
            child.wall_ms = rng.choice([300, 550, 850])
        elif field.startswith("allow_"):
            setattr(child, field, not getattr(child, field))
        elif field == "fs_mode":
            child.fs_mode = rng.choice(FS_MODES)
        elif field == "max_cpu_ms_budget":
            child.max_cpu_ms_budget = max(1.5, min(2000.0, round(child.max_cpu_ms_budget * rng.uniform(0.4, 1.6), 2)))
        elif field == "max_rss_kb_budget":
            child.max_rss_kb_budget = max(4096, min(524288, int(child.max_rss_kb_budget * rng.uniform(0.65, 1.4))))
        return child

    @staticmethod
    def crossover(a: "PolicyIR", b: "PolicyIR", rng: random.Random) -> Tuple["PolicyIR", "PolicyIR"]:
        da, db = a.to_dict(), b.to_dict()
        c1, c2 = {}, {}
        for k in da:
            if rng.random() < 0.5:
                c1[k], c2[k] = da[k], db[k]
            else:
                c1[k], c2[k] = db[k], da[k]
        return PolicyIR(**c1), PolicyIR(**c2)
