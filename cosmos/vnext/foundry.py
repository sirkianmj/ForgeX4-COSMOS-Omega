import random
import threading
from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from .audit_ledger import AuditLedger
from .drivers import BaseTargetDriver
from .policy_ir import PolicyIR
from .sandbox_client import SandboxClient
from .verifier import FormalPolicyVerifier


ARCH_TO_ID = {"parser": 0.0, "cli": 1.0, "daemon": 2.0, "agent": 3.0}


def _policy_to_vec(p: PolicyIR, calib: Dict[str, float], target: BaseTargetDriver) -> List[float]:
    return [
        float(p.cpu_sec),
        float(p.mem_mb),
        float(p.fsize_mb),
        float(p.nofile),
        float(p.wall_ms),
        1.0 if p.allow_execve else 0.0,
        1.0 if p.allow_net_bind else 0.0,
        1.0 if p.allow_net_outbound else 0.0,
        1.0 if p.allow_fork else 0.0,
        1.0 if p.allow_priv_ops else 0.0,
        1.0 if p.allow_debug_ops else 0.0,
        0.0 if p.fs_mode == "readonly" else (1.0 if p.fs_mode == "workspace_only" else 2.0),
        float(p.max_cpu_ms_budget),
        float(p.max_rss_kb_budget),
        float(calib.get("benign_wall_ms", 10.0)),
        float(calib.get("benign_cpu_ms", 5.0)),
        float(calib.get("benign_rss_kb", 4096.0)),
        ARCH_TO_ID.get(target.archetype, 0.0),
        1.0 if target.requires_network else 0.0,
        1.0 if target.requires_fork else 0.0,
    ]


class CrossTargetDigitalTwin:
    """Low-heat cross-target physics surrogate supporting zero-shot transfer."""

    def __init__(self):
        self._lock = threading.Lock()
        self.X: List[List[float]] = []
        self.y: List[float] = []
        self.model = RandomForestRegressor(n_estimators=25, max_depth=8, n_jobs=1, random_state=42)
        self.ready = False

    def observe(self, p: PolicyIR, calib: Dict[str, float], target: BaseTargetDriver, score: float):
        vec = _policy_to_vec(p, calib, target)
        with self._lock:
            self.X.append(vec)
            self.y.append(score)
            if len(self.X) >= 120 and len(self.X) % 120 == 0:
                self.model.fit(np.array(self.X), np.array(self.y))
                self.ready = True

    def fit_now(self):
        with self._lock:
            if len(self.X) >= 12:
                self.model.fit(np.array(self.X), np.array(self.y))
                self.ready = True

    def predict(self, p: PolicyIR, calib: Dict[str, float], target: BaseTargetDriver) -> float:
        vec = _policy_to_vec(p, calib, target)
        with self._lock:
            if not self.ready:
                return 0.0
            return float(self.model.predict(np.array([vec]))[0])


class GeneralistFoundry:
    def __init__(
        self,
        client: SandboxClient,
        ledger: AuditLedger,
        seed: int = 42,
        shared_twin: CrossTargetDigitalTwin = None,
    ):
        self.client = client
        self.ledger = ledger
        self.seed = seed
        self.verifier = FormalPolicyVerifier()
        self.twin = shared_twin or CrossTargetDigitalTwin()
        self._lock = threading.Lock()
        self.kernel_cache: Dict[str, Dict[str, Any]] = {}
        self.eval_cache: Dict[str, Dict[str, Any]] = {}
        self.docker_calls = 0
        self.cache_hits = 0

    @staticmethod
    def _is_contained(meta: Dict[str, Any], policy: PolicyIR) -> bool:
        outcome = meta.get("outcome", "survived")
        if outcome in ("policy_killed", "timed_out", "rlimit_cpu_killed", "rlimit_fsize_killed", "nonzero_exit", "crashed"):
            return True
        cpu_ms = float(meta.get("cpu_user_ms", 0.0)) + float(meta.get("cpu_sys_ms", 0.0))
        rss_kb = int(meta.get("max_rss_kb", 0))
        return cpu_ms > policy.max_cpu_ms_budget or rss_kb > policy.max_rss_kb_budget

    def _run_kernel_bundle(self, target: BaseTargetDriver, policy: PolicyIR) -> Dict[str, Any]:
        kkey = f"{target.id}:{policy.kernel_hash()}"
        with self._lock:
            if kkey in self.kernel_cache:
                self.cache_hits += 1
                return self.kernel_cache[kkey]

        pdict = policy.to_dict()
        benign_runs = []
        for bp in target.benign_probes:
            r = target.evaluate_probe(self.client, bp, pdict)
            benign_runs.append({"meta": r["meta"], "functional_ok": r["functional_ok"]})

        attack_runs = []
        for ap in target.attack_probes:
            r = target.evaluate_probe(self.client, ap, pdict)
            attack_runs.append({"probe": ap.name, "threat_class": ap.threat_class, "meta": r["meta"]})

        bundle = {"benign": benign_runs, "attack": attack_runs}
        with self._lock:
            self.docker_calls += len(benign_runs) + len(attack_runs)
            self.kernel_cache[kkey] = bundle
        return bundle

    def evaluate_policy(
        self,
        target: BaseTargetDriver,
        policy: PolicyIR,
        calib: Dict[str, float],
        benign_floor_mb: int = 8,
    ) -> Dict[str, Any]:
        key = f"{target.id}:{policy.canonical_hash()}"
        with self._lock:
            if key in self.eval_cache:
                return self.eval_cache[key]

        v = self.verifier.verify(
            policy,
            archetype=target.archetype,
            requires_network=target.requires_network,
            requires_fork=target.requires_fork,
            requires_priv_ops=target.requires_priv_ops,
            min_mem_floor_mb=benign_floor_mb,
        )
        if not v.passed:
            out = {
                "policy": policy.to_dict(),
                "z3_verified": False,
                "violated_invariants": v.violated_invariants,
                "proof_hash": v.proof_hash,
                "benign_pass_rate": 0.0,
                "attack_block_rate": 0.0,
                "privilege_surface": policy.privilege_surface(),
                "mean_benign_wall_ms": 0.0,
                "attack_details": [],
                "fitness": -5000.0 - 100.0 * len(v.violated_invariants),
            }
            with self._lock:
                self.eval_cache[key] = out
            return out

        bundle = self._run_kernel_bundle(target, policy)
        benign_ok = sum(1 for b in bundle["benign"] if b["functional_ok"])
        benign_walls = [float(b["meta"].get("wall_ms", 0.0)) for b in bundle["benign"]]

        attack_blocked = 0
        attack_details = []
        for a in bundle["attack"]:
            blocked = self._is_contained(a["meta"], policy)
            if blocked:
                attack_blocked += 1
            attack_details.append({
                "probe": a["probe"],
                "threat_class": a["threat_class"],
                "blocked": blocked,
                "outcome": a["meta"].get("outcome"),
                "violations": a["meta"].get("violations", ""),
                "wall_ms": a["meta"].get("wall_ms", 0),
            })

        benign_rate = benign_ok / max(1, len(bundle["benign"]))
        block_rate = attack_blocked / max(1, len(bundle["attack"]))
        mean_wall = sum(benign_walls) / max(1, len(benign_walls))
        priv = policy.privilege_surface()

        if benign_rate < 1.0:
            fitness = -2000.0 * (1.0 - benign_rate) + 400.0 * block_rate - 50.0 * priv
        else:
            fitness = 1000.0 * block_rate + 500.0 * benign_rate - 250.0 * priv - 0.1 * mean_wall

        out = {
            "policy": policy.to_dict(),
            "z3_verified": True,
            "violated_invariants": [],
            "proof_hash": v.proof_hash,
            "benign_pass_rate": benign_rate,
            "attack_block_rate": block_rate,
            "privilege_surface": priv,
            "mean_benign_wall_ms": round(mean_wall, 2),
            "attack_details": attack_details,
            "fitness": round(fitness, 3),
        }
        with self._lock:
            self.eval_cache[key] = out
        self.twin.observe(policy, calib, target, out["fitness"])
        return out

    def calibrate_benign_baseline(self, target: BaseTargetDriver) -> Dict[str, float]:
        permissive = PolicyIR.permissive().to_dict()
        walls, cpus, rsss = [], [], []
        for bp in target.benign_probes:
            r = target.evaluate_probe(self.client, bp, permissive)
            m = r["meta"]
            walls.append(float(m.get("wall_ms", 1.0)))
            cpus.append(float(m.get("cpu_user_ms", 0.0)) + float(m.get("cpu_sys_ms", 0.0)))
            rsss.append(float(m.get("max_rss_kb", 4096)))
        return {
            "benign_wall_ms": max(walls) if walls else 50.0,
            "benign_cpu_ms": max(cpus) if cpus else 20.0,
            "benign_rss_kb": max(rsss) if rsss else 8192.0,
        }

    def run_quantile_baseline(self, target: BaseTargetDriver, calib: Dict[str, float]) -> Dict[str, Any]:
        q_policy = PolicyIR(
            cpu_sec=1,
            mem_mb=max(64 if target.archetype == "daemon" else 48, int(np.ceil((calib["benign_rss_kb"] * 2.0) / 1024.0))),
            fsize_mb=32,
            nofile=128,
            wall_ms=max(400, min(900, int(calib["benign_wall_ms"] * 3.0))),
            allow_execve=True,
            allow_net_bind=True,
            allow_net_outbound=True,
            allow_fork=True,
            allow_priv_ops=True,
            allow_debug_ops=True,
            fs_mode="unrestricted",
            kill_on_violation=False,
            max_cpu_ms_budget=max(10.0, calib["benign_cpu_ms"] * 1.5),
            max_rss_kb_budget=max(8192, int(calib["benign_rss_kb"] * 1.4)),
        )
        bundle = self._run_kernel_bundle(target, q_policy)
        benign_ok = sum(1 for b in bundle["benign"] if b["functional_ok"])
        atk_blocked = sum(1 for a in bundle["attack"] if self._is_contained(a["meta"], q_policy))
        return {
            "benign_pass_rate": benign_ok / max(1, len(bundle["benign"])),
            "attack_block_rate": atk_blocked / max(1, len(bundle["attack"])),
            "privilege_surface": q_policy.privilege_surface(),
        }

    def run_random_search(self, target: BaseTargetDriver, budget: int, calib: Dict[str, float], benign_floor_mb: int, rng: random.Random) -> Dict[str, Any]:
        best = None
        for _ in range(budget):
            cand = PolicyIR.random_candidate(rng)
            res = self.evaluate_policy(target, cand, calib, benign_floor_mb=benign_floor_mb)
            if best is None or res["fitness"] > best["fitness"]:
                best = res
        return best

    def synthesize(self, target: BaseTargetDriver, pop_size: int = 8, generations: int = 4, use_twin: bool = True) -> Dict[str, Any]:
        rng = random.Random(f"{self.seed}:{target.id}")
        target.prepare(self.client)
        calib = self.calibrate_benign_baseline(target)
        floor_mb = max(64 if target.archetype == "daemon" else 16, int(calib["benign_rss_kb"] / 1024.0) * 2)
        min_wall = 550 if target.archetype == "daemon" else 300

        pop: List[Tuple[PolicyIR, Dict[str, Any]]] = []
        for idx in range(pop_size):
            p = PolicyIR.random_candidate(rng)
            p.allow_net_bind = bool(target.requires_network) if idx < int(pop_size * 0.75) else p.allow_net_bind
            p.allow_net_outbound = False
            p.allow_fork = bool(target.requires_fork)
            p.allow_priv_ops = bool(target.requires_priv_ops) if idx < int(pop_size * 0.75) else p.allow_priv_ops
            p.allow_execve = False
            p.allow_debug_ops = False
            if p.fs_mode == "unrestricted" or (target.archetype == "daemon" and idx < int(pop_size * 0.75)):
                p.fs_mode = "workspace_only"
            if p.mem_mb < floor_mb:
                p.mem_mb = min(384, max(64, floor_mb * 2))
            if p.wall_ms < min_wall:
                p.wall_ms = min_wall
            res = self.evaluate_policy(target, p, calib, benign_floor_mb=floor_mb)
            pop.append((p, res))

        z3_rejects = sum(1 for _, r in pop if not r["z3_verified"])
        for _ in range(generations):
            pop.sort(key=lambda x: x[1]["fitness"], reverse=True)
            elites = pop[:2]
            candidates: List[PolicyIR] = []
            while len(candidates) < (pop_size - 2) * 2:
                if rng.random() < 0.65:
                    p1, p2 = rng.sample([x[0] for x in pop[: max(3, pop_size // 2)]], 2)
                    c1, c2 = PolicyIR.crossover(p1, p2, rng)
                    candidates.extend([c1.mutate(rng), c2.mutate(rng)])
                else:
                    parent = max(rng.sample(pop, min(4, len(pop))), key=lambda x: x[1]["fitness"])[0]
                    candidates.append(parent.mutate(rng))

            if use_twin and self.twin.ready:
                candidates.sort(key=lambda c: self.twin.predict(c, calib, target), reverse=True)
            selected = candidates[: pop_size - 2]

            new_pop = list(elites)
            for c in selected:
                r = self.evaluate_policy(target, c, calib, benign_floor_mb=floor_mb)
                if not r["z3_verified"]:
                    z3_rejects += 1
                new_pop.append((c, r))
            pop = new_pop

        pop.sort(key=lambda x: x[1]["fitness"], reverse=True)
        _, champion_res = pop[0]
        quantile_res = self.run_quantile_baseline(target, calib)
        random_res = self.run_random_search(target, budget=min(10, pop_size * 2), calib=calib, benign_floor_mb=floor_mb, rng=rng)

        summary = {
            "target_id": target.id,
            "archetype": target.archetype,
            "calibration": calib,
            "cosmos_omega": champion_res,
            "baseline_quantile_2float": quantile_res,
            "baseline_random_search": {
                "benign_pass_rate": random_res["benign_pass_rate"],
                "attack_block_rate": random_res["attack_block_rate"],
                "privilege_surface": random_res["privilege_surface"],
                "fitness": random_res["fitness"],
            },
            "z3_pre_exec_rejects": z3_rejects,
        }
        with self._lock:
            self.ledger.record("target_synthesis", summary)
        return summary
