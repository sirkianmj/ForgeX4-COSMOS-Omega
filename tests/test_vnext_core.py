import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from cosmos.vnext import AuditLedger, FormalPolicyVerifier, PolicyIR, load_catalog


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCOSMOSvNextCore(unittest.TestCase):
    def test_policy_hashes_and_surface(self):
        p1 = PolicyIR(mem_mb=128, max_cpu_ms_budget=50.0)
        p2 = PolicyIR(mem_mb=128, max_cpu_ms_budget=200.0)
        self.assertEqual(p1.kernel_hash(), p2.kernel_hash())
        self.assertNotEqual(p1.canonical_hash(), p2.canonical_hash())
        self.assertGreater(PolicyIR.permissive().privilege_surface(), p1.privilege_surface())

    def test_z3_verifier_enforces_invariants(self):
        v = FormalPolicyVerifier()
        safe = PolicyIR(allow_execve=False, allow_net_bind=False, allow_net_outbound=False, fs_mode="workspace_only")
        self.assertTrue(v.verify(safe, archetype="parser").passed)

        unsafe_exec = PolicyIR(allow_execve=True, fs_mode="workspace_only")
        res = v.verify(unsafe_exec, archetype="parser")
        self.assertFalse(res.passed)
        self.assertIn("INV1_no_arbitrary_execve", res.violated_invariants)

        daemon_ok = PolicyIR(allow_net_bind=True, allow_fork=True, allow_priv_ops=True, fs_mode="workspace_only")
        self.assertTrue(
            v.verify(daemon_ok, archetype="daemon", requires_network=True, requires_fork=True, requires_priv_ops=True).passed
        )

    def test_audit_ledger_immutability_and_chain(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = AuditLedger(Path(td), run_name="unit")
            payload = {"target": "nginx", "score": 1.0}
            ledger.record("eval", payload)
            payload["split"] = "mutated_after_record"
            saved = json.loads(ledger.save().read_text())
            ev = saved["events"][0]
            self.assertNotIn("split", ev["data"])
            check = {k: v for k, v in ev.items() if k != "hash"}
            self.assertEqual(hashlib.sha256(json.dumps(check, sort_keys=True).encode()).hexdigest(), ev["hash"])

    def test_load_all_115_targets(self):
        t1 = load_catalog(PROJECT_ROOT / "targets/catalog/batch1_50.yaml", PROJECT_ROOT)
        t2 = load_catalog(PROJECT_ROOT / "targets/catalog/batch2_50.yaml", PROJECT_ROOT)
        t3 = load_catalog(PROJECT_ROOT / "targets/catalog/complex_apps_15.yaml", PROJECT_ROOT)
        all_targets = t1 + t2 + t3
        self.assertEqual(len(all_targets), 115)
        self.assertEqual(len({t.id for t in all_targets}), 115)
        for t in all_targets:
            self.assertGreaterEqual(len(t.benign_probes), 1)
            self.assertGreaterEqual(len(t.attack_probes), 1)


if __name__ == "__main__":
    unittest.main()
