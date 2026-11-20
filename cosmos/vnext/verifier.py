import hashlib
import json
import threading
from dataclasses import dataclass
from typing import Dict, List
from z3 import And, Bool, Implies, Int, Not, Solver, unsat
from .policy_ir import PolicyIR


@dataclass
class VerificationResult:
    passed: bool
    violated_invariants: List[str]
    proof_hash: str


class FormalPolicyVerifier:
    """Thread-safe static Z3 SMT invariant verifier with capability-key caching."""

    def __init__(self):
        self._lock = threading.Lock()
        self._cache: Dict[str, VerificationResult] = {}

    def verify(
        self,
        policy: PolicyIR,
        archetype: str,
        requires_network: bool = False,
        requires_fork: bool = False,
        requires_priv_ops: bool = False,
        min_mem_floor_mb: int = 8,
    ) -> VerificationResult:
        ckey = f"{policy.kernel_hash()}:{archetype}:{requires_network}:{requires_fork}:{requires_priv_ops}:{min_mem_floor_mb}"
        with self._lock:
            if ckey in self._cache:
                return self._cache[ckey]

            allow_exec = Bool("allow_execve")
            allow_bind = Bool("allow_net_bind")
            allow_out = Bool("allow_net_outbound")
            allow_fork = Bool("allow_fork")
            allow_priv = Bool("allow_priv_ops")
            allow_dbg = Bool("allow_debug_ops")
            fs_unrestricted = Bool("fs_unrestricted")
            mem_mb = Int("mem_mb")
            cpu_sec = Int("cpu_sec")

            assignment = And(
                allow_exec == bool(policy.allow_execve),
                allow_bind == bool(policy.allow_net_bind),
                allow_out == bool(policy.allow_net_outbound),
                allow_fork == bool(policy.allow_fork),
                allow_priv == bool(policy.allow_priv_ops),
                allow_dbg == bool(policy.allow_debug_ops),
                fs_unrestricted == (policy.fs_mode == "unrestricted"),
                mem_mb == int(policy.mem_mb),
                cpu_sec == int(policy.cpu_sec),
            )

            invariants = {
                "INV1_no_arbitrary_execve": Not(allow_exec),
                "INV2_bounded_resources": And(mem_mb >= min_mem_floor_mb, mem_mb <= 512, cpu_sec >= 1, cpu_sec <= 10),
                "INV3_least_privilege_fs": Not(fs_unrestricted),
                "INV4_no_outbound_exfil": Not(allow_out),
                "INV5_no_ptrace_debug_ops": Not(allow_dbg),
            }

            if not requires_priv_ops:
                invariants["INV5b_no_unneeded_priv_ops"] = Not(allow_priv)

            if not requires_fork:
                invariants["INV6_no_unexpected_fork"] = Not(allow_fork)

            if not requires_network:
                invariants["INV7_no_socket_bind"] = Not(allow_bind)
            else:
                invariants["INV7_bind_requires_scoped_fs"] = Implies(allow_bind, Not(fs_unrestricted))

            if archetype in ("parser", "agent"):
                invariants["INV8_strict_isolation"] = And(Not(allow_exec), Not(allow_bind), Not(allow_out), Not(fs_unrestricted))

            violated = []
            for name, prop in invariants.items():
                s = Solver()
                s.add(assignment)
                s.add(Not(prop))
                if s.check() != unsat:
                    violated.append(name)

            cert = {
                "policy_hash": policy.kernel_hash(),
                "archetype": archetype,
                "passed": len(violated) == 0,
                "violated": violated,
            }
            proof_hash = hashlib.sha256(json.dumps(cert, sort_keys=True).encode("utf-8")).hexdigest()[:16]
            res = VerificationResult(passed=(len(violated) == 0), violated_invariants=violated, proof_hash=proof_hash)
            self._cache[ckey] = res
            return res
