import subprocess
import os
import threading
import time
from pathlib import Path
import pandas as pd
import joblib
import psutil
import json
from typing import Dict, Any, List

from rich.console import Console
console = Console()

# [DEFINITIVE - V22.0 "OPERATION OMEGA" - THE FINAL TITANS]
# This is the final, definitive version of the Titan system.
# KEY UPGRADES:
# 1. CONFIDENCE SCORING: The PerformanceTitan now returns the model's full
# probability distribution (confidence scores), which is a critical
# input for the new Omega Fitness Function.
# 2. SINGLE SOURCE OF TRUTH: It uses a centralized feature engineering function
# to ensure perfect data consistency between training and evolution.
# 3. ROBUSTNESS: Contains hardened, automatic path-finding for all model artifacts.
# --- SINGLE SOURCE OF TRUTH: Feature Engineering ---

def _engineer_fingerprint_from_telemetry(telemetry: List[Dict[str, Any]], feature_list: List[str]) -> pd.DataFrame:
    """
    Creates the exact statistical fingerprint the Pathfinder model was trained on.
    This is the single source of truth for feature engineering.
    """
    if not telemetry:
        return pd.DataFrame({feat: [0] for feat in feature_list})

    df = pd.DataFrame(telemetry).fillna(0)
    features = {}

    telemetry_cols = ['cpu_percent_total', 'memory_rss_bytes', 'io_read_bytes', 'io_write_bytes', 'num_threads']
    for col in telemetry_cols:
        if col in df.columns and not df[col].empty:
            series = df[col]
            features[f'{col}_mean'] = series.mean()
            features[f'{col}_std'] = series.std()
            features[f'{col}_max'] = series.max()
            features[f'{col}_median'] = series.median()
            features[f'{col}_p95'] = series.quantile(0.95)

    return pd.DataFrame({feat: [features.get(feat, 0)] for feat in feature_list})

class ExecutionTitan:
    """[ARCHITECT ENFORCER & VM] Runs the target, enforces the stateful policy, and collects raw evidence."""
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.executable_path = project_root / "data/temp/sentinel_target.out"
        if not self.executable_path.exists():
            self.app_source_path = str(project_root / "data/genomes/cjson/cJSON.c")
            self.harness_path = str(project_root / "data/genomes/uranus/cjson_harness.c")
            self.header_dir = str(project_root / "data/genomes/cjson")
            self.compiler = "gcc"
            self.executable_path.parent.mkdir(exist_ok=True, parents=True)
            cmd = [self.compiler, "-fno-stack-protector", "-o", str(self.executable_path), self.app_source_path, self.harness_path, f"-I{self.header_dir}", "-lm"]
            compile_res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if compile_res.returncode != 0: 
                raise RuntimeError(f"FATAL: Sentinel target failed to compile!\n{compile_res.stderr}")

    def _evaluate_policy_node(self, node: dict, telemetry_reading: dict) -> bool:
        """The Recursive Omega Policy Decision Engine."""
        if node.get('type') == 'rule':
            metric, op, value = node['metric'], node['operator'], node['value']
            observed = telemetry_reading.get(metric)
            if observed is None: return False
            if op == 'GT': return observed > value
            if op == 'LT': return observed < value
            if op == 'EQ': return observed == value
            if op == 'NEQ': return observed != value
            return False
        if 'children' in node:
            outcomes = [self._evaluate_policy_node(c, telemetry_reading) for c in node['children']]
            op = node['operator']
            if op == 'AND': return all(outcomes)
            if op == 'OR': return any(outcomes)
            if op == 'NAND': return not all(outcomes)
            if op == 'NOR': return not any(outcomes)
            if op == 'XOR': return sum(1 for o in outcomes if o) == 1
        return False

    def instrumented_run(self, payload: bytes, genome: Dict, timeout: int = 5) -> Dict[str, Any]:
        telemetry: List[Dict[str, Any]] = []
        stop_monitoring = threading.Event()
        proc = None; mon_thread = None; outcome = 'unknown_error'
        current_state = genome.get('initial_state', None)
        
        try:
            proc = subprocess.Popen([str(self.executable_path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p = psutil.Process(proc.pid)
            def monitor_thread():
                nonlocal current_state, outcome
                try:
                    p.cpu_percent(interval=None); time.sleep(0.01)
                    while not stop_monitoring.is_set():
                        with p.oneshot():
                            reading = {'cpu_percent_total': p.cpu_percent(interval=0.05), 'memory_rss_bytes': p.memory_info().rss, 'io_read_bytes': p.io_counters().read_bytes, 'io_write_bytes': p.io_counters().write_bytes, 'num_threads': p.num_threads()}
                            telemetry.append(reading)
                        state_config = genome.get('states', {}).get(current_state, {})
                        if self._evaluate_policy_node(state_config.get('active_policy', {}), reading): 
                            p.kill(); outcome = 'policy_violation'
                        for t in state_config.get('transitions', []):
                            if self._evaluate_policy_node(t.get('condition', {}), reading): 
                                current_state = t.get('target_state'); break
                except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            
            mon_thread = threading.Thread(target=monitor_thread); mon_thread.start()
            proc.communicate(input=payload, timeout=timeout)
            if outcome == 'unknown_error': 
                outcome = 'survived' if proc.returncode == 0 else 'crashed'
        except subprocess.TimeoutExpired:
            outcome = 'timed_out'; p.kill() if proc and proc.poll() is None else None
        finally:
            stop_monitoring.set(); mon_thread.join(timeout=1) if mon_thread else None
        
        return {'outcome': outcome, 'raw_telemetry': telemetry}

class PerformanceTitan:
    """[PATHFINDER ORACLE] Loads the v8.3 Pathfinder Model to classify behavioral profiles."""
    def __init__(self):
        self.model_is_ready = False
        try:
            project_root = Path(__file__).resolve().parent.parent.parent
            base_data_dir = project_root / "data" / "telemetry_overdrive_v1"
            nested_dirs = list(base_data_dir.glob('COSMOS_OVERDRIVE_DATASET_*'))
            if not nested_dirs: 
                raise FileNotFoundError(f"No 'COSMOS_OVERDRIVE_DATASET_' directory found in {base_data_dir}")

            model_artifacts_dir = nested_dirs[0] / "model_artifacts_v8.3"
            pipeline_path = model_artifacts_dir / "digital_twin_v8.3_pipeline.joblib"
            features_path = model_artifacts_dir / "digital_twin_v8.3_features.json"
            
            if not pipeline_path.exists(): 
                raise FileNotFoundError(f"Pathfinder model not found at {pipeline_path}")

            self.pipeline = joblib.load(pipeline_path)
            with open(features_path, 'r') as f:
                self.feature_list = json.load(f)
            
            self.model_is_ready = True
            console.print("PerformanceTitan (Pathfinder Oracle): Digital Twin v8.3 is ONLINE.")
        except Exception as e:
            console.print(f"PerformanceTitan WARNING: Pathfinder model failed to load. Reason: {e}. Profiling is disabled.")
            raise e

    def analyze(self, raw_telemetry: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes raw telemetry and returns the predicted behavioral profile
        AND the model's confidence scores.
        """
        if not self.model_is_ready:
            return {'profile': -1, 'confidence': {}}
        try:
            df_fingerprint = _engineer_fingerprint_from_telemetry(raw_telemetry, self.feature_list)
            
            profile_id = self.pipeline.predict(df_fingerprint)[0]
            
            # --- CRITICAL UPGRADE: Get the confidence scores (probabilities) ---
            probabilities = self.pipeline.predict_proba(df_fingerprint)[0]
            confidence_map = {str(i): prob for i, prob in enumerate(probabilities)}

            return {'profile': int(profile_id), 'confidence': confidence_map}
        except Exception as e:
            console.print(f"[yellow]Pathfinder analysis failed: {e}[/yellow]")
            return {'profile': -1, 'confidence': {}}

class JanusTitan:
    """[SENTINEL OUTCOME ANALYST] Reports the final, factual outcome."""
    def analyze(self, run_result: Dict[str, Any]) -> dict:
        return {'outcome': run_result.get('outcome', 'unknown_error')}