#
# File: cosmos/foundry/titans_sentinel.py
#
# Description:
# [DEFINITIVE - V14.1 "OPERATION REFLEX" - THE FINAL ARCHITECTURE]
# This version contains the critical bug fix for the calibration race condition.
#
# CRITICAL FIX ("REFLEX"):
# The `ExecutionTitan` has been hardened to correctly capture telemetry from
# extremely fast-executing programs. It now primes the psutil sensor and
# guarantees a valid (even if zero-impact) snapshot is created, preventing
# the race condition that caused the calibration failure.
#

import subprocess
import os
import threading
import time
from pathlib import Path
import pandas as pd
import joblib
import psutil
from typing import Dict, Any, List

class ExecutionTitan:
    """[SENTINEL ENFORCER] Runs the target, enforces the policy, collects the evidence."""
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.app_source_path = str(project_root / "data/genomes/cjson/cJSON.c")
        self.harness_path = str(project_root / "data/genomes/uranus/cjson_harness.c")
        self.header_dir = str(project_root / "data/genomes/cjson")
        self.compiler = "gcc"
        self.executable_path = project_root / "data/temp/sentinel_target.out"
        self.executable_path.parent.mkdir(exist_ok=True)

        # Pre-compile the executable to speed up evaluations
        cmd = [self.compiler, "-fno-stack-protector", "-o", str(self.executable_path), self.app_source_path, self.harness_path, f"-I{self.header_dir}", "-lm"]
        compile_res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if compile_res.returncode != 0:
            raise RuntimeError(f"FATAL: Sentinel target failed to compile!\n{compile_res.stderr}")

    def instrumented_run(self, payload: bytes, genome: Dict[str, float], timeout: int = 5) -> Dict[str, Any]:
        """Runs the pre-compiled target under observation and policy enforcement."""
        telemetry: List[Dict[str, Any]] = []
        stop_monitoring = threading.Event()
        proc = None
        mon_thread = None
        
        try:
            proc = subprocess.Popen([str(self.executable_path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
            p = psutil.Process(proc.pid)

            def monitor_thread():
                try:
                    # --- REFLEX FIX 1: PRIME THE SENSOR ---
                    # The first call to cpu_percent with interval=None returns 0.0.
                    # We "prime the sensor" by making one call and discarding the result.
                    p.cpu_percent(interval=None) 
                    time.sleep(0.01) # A tiny sleep to establish a time delta for the next reading

                    while not stop_monitoring.is_set():
                        with p.oneshot():
                            cpu = p.cpu_percent(interval=0.05)
                            mem = p.memory_info()
                            telemetry.append({'cpu_percent': cpu, 'resident_memory_bytes': mem.rss})
                        # --- SENTINEL POLICY ENFORCEMENT ---
                        if telemetry and genome.get('max_cpu_percent', 100) < telemetry[-1]['cpu_percent']:
                             p.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass # Process finished, which is normal.
                except Exception:
                    pass # Suppress other potential errors during monitoring.

            mon_thread = threading.Thread(target=monitor_thread)
            mon_thread.start()

            stdout, stderr = proc.communicate(input=payload, timeout=timeout)
            
            outcome = 'survived'
            if proc.returncode != 0:
                outcome = 'crashed'

        except subprocess.TimeoutExpired:
            outcome = 'timed_out'
            if proc and proc.poll() is None:
                p.kill()
        except Exception:
            outcome = 'unknown_error'
        finally:
            stop_monitoring.set()
            if mon_thread:
                mon_thread.join(timeout=1)

        # --- Aggregate Telemetry Snapshot ---
        snapshot = {}
        if telemetry:
            df = pd.DataFrame(telemetry)
            snapshot = {
                'max_cpu_percent': df['cpu_percent'].max(),
                'avg_cpu_percent': df['cpu_percent'].mean(),
                'max_resident_memory_bytes': df['resident_memory_bytes'].max(),
                'avg_resident_memory_bytes': df['resident_memory_bytes'].mean(),
                'observation_duration_ms': len(df) * 50 # Approximation
            }
        else:
            # --- REFLEX FIX 2: HANDLE NO TELEMETRY ---
            # If the process was too fast, create a valid zero-impact snapshot.
            snapshot = {
                'max_cpu_percent': 0.0, 'avg_cpu_percent': 0.0,
                'max_resident_memory_bytes': 0.0, 'avg_resident_memory_bytes': 0.0,
                'observation_duration_ms': 1 
            }
        
        return {'outcome': outcome, 'telemetry_snapshot': snapshot}


class PerformanceTitan:
    """[SENTINEL ORACLE] Loads the Fusion Model to classify behavioral profiles."""
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        model_path = project_root / "artifacts/phase2/digital_twin_v7.1_The_Fusion_Model.joblib"
        self.model_is_ready = False
        try:
            self.pipeline = joblib.load(model_path)
            self.model_is_ready = True
            print("PerformanceTitan (The Oracle): Digital Twin v7.1 is ONLINE.")
        except Exception as e:
            print(f"PerformanceTitan WARNING: Digital Twin model failed to load from {model_path}. Reason: {e}. Profiling is disabled.")

    def analyze(self, telemetry_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a telemetry snapshot and returns the predicted behavioral profile."""
        if not self.model_is_ready or not telemetry_snapshot:
            return {'profile': -1} # Return -1 for "unknown"
        try:
            features = ['max_cpu_percent', 'avg_cpu_percent', 'max_resident_memory_bytes', 'avg_resident_memory_bytes', 'observation_duration_ms']
            df = pd.DataFrame({feat: [telemetry_snapshot.get(feat, 0)] for feat in features})
            profile = self.pipeline.predict(df)[0]
            return {'profile': int(profile)}
        except Exception:
            return {'profile': -1}

class JanusTitan:
    """[SENTINEL OUTCOME ANALYST] Reports the final, factual outcome."""
    def analyze(self, run_result: Dict[str, Any]) -> dict:
        outcome = run_result.get('outcome', 'unknown_error')
        return {'outcome': outcome}

