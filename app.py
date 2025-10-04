#
# File: app.py (v7.0 - "Daemon Sentry Interface")
# This definitive version is upgraded to orchestrate the NGINX experiment.
#
# KEY UPGRADES:
# 1. TARGET PIVOT: The entire workflow is now built around the "Daemon Sentry"
#    approach, using NGINX as the complex, real-world target.
# 2. BEHAVIORAL PAYLOADS: The worker function no longer sends simple byte
#    strings. It now instructs the ExecutionTitan to run full behavioral
#    scripts ("benign" web client vs. "malicious" crypto miner).
# 3. SIMPLIFIED GENOME: The foundry is now configured to evolve the simpler
#    but more powerful profile-based genomes suitable for anomaly detection.
#
import sys
import time
import json
import threading
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from flask import Flask, jsonify, render_template, request

# --- Project Setup ---
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# --- CRITICAL UPGRADE: Import the definitive Foundry AND the new Titan ---
from cosmos.foundry.foundry_pathfinder import SentinelFoundry
from cosmos.foundry.titans_pathfinder import ExecutionTitan # Import the new Titan
from cosmos.ledger.ledger import Ledger

# --- Global State Management ---
run_states = {}
run_states_lock = threading.Lock()

# --- MULTIPROCESSING WORKER SETUP ---
worker_execution_titan = None

def init_worker():
    """
    Initializes each worker process by creating its own ExecutionTitan instance.
    This ensures NGINX is checked and paths are set in each parallel process.
    """
    global worker_execution_titan
    try:
        worker_execution_titan = ExecutionTitan()
    except Exception as e:
        # This will cause the worker to fail, and the main thread will report it.
        print(f"WORKER INIT FAILED: {e}")
        raise e

def evaluate_genome_worker(individual: dict) -> dict:
    """
    The core task for each worker. It now uses behavioral payloads.
    """
    genome = individual['genome']
    
    # --- PIVOT: Instruct the Titan to run behavioral scripts, not send strings ---
    benign_result = worker_execution_titan.instrumented_run(payload_type="benign", genome=genome)
    malicious_result = worker_execution_titan.instrumented_run(payload_type="malicious", genome=genome)
    
    # Return the "truth packet" for the main thread to score
    return {
        'id': individual['id'],
        'genome': genome,
        'benign_outcome': benign_result['outcome'],
        'benign_telemetry': benign_result['raw_telemetry'],
        'attack_outcome': malicious_result['outcome'],
        'attack_telemetry': malicious_result['raw_telemetry']
    }

# --- Main Application Thread ---
app = Flask(__name__)

def run_foundry_background(run_id, config):
    """
    Main background thread that manages a single evolutionary run.
    """
    try:
        ledger = Ledger(output_dir=str(PROJECT_ROOT / f"artifacts/gui_runs/{run_id}"))
        foundry = SentinelFoundry(config=config)
    except Exception as e:
        with run_states_lock:
            run_states[run_id] = {'status': 'ERROR', 'events': [{'block_height': 0, 'event_type': 'FATAL_ERROR', 'details': {'error': f"Initialization failed: {str(e)}"}}]}
        return

    with run_states_lock:
        run_states[run_id] = {'status': 'Initializing', 'events': ledger.events, 'is_running': True}

    ledger.record_event(block_height=0, event_type="INITIATION", details={"config": config, "target": "NGINX Web Server (Daemon Sentry Mode)"})

    # --- Step 1: Calibration (Now learns NGINX's normal behavior) ---
    with run_states_lock: run_states[run_id]['status'] = 'Calibrating'
    try:
        foundry.calibrate()
        ledger.record_event(block_height=0, event_type="CALIBRATION_COMPLETE", details={"normal_profile_id": foundry.normal_profile_id})
    except Exception as e:
        with run_states_lock:
             run_states[run_id]['status'] = 'ERROR'
             ledger.record_event(block_height=0, event_type="FATAL_ERROR", details={"error": f"Calibration failed: {e}. Is NGINX running correctly?"})
             ledger.save()
        return


    # --- Step 2: Initialization (Now creates simpler, profile-based genomes) ---
    with run_states_lock: run_states[run_id]['status'] = 'Creating Genesis Population'
    foundry._initialize_population() # This will now create the simpler genomes
    ledger.record_event(block_height=0, event_type="INITIAL_POPULATION_CREATED", details={"population": [ind.copy() for ind in foundry.population]})

    # --- Step 3: Main Evolutionary Loop ---
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count(), initializer=init_worker) as executor:
        for gen in range(config.get("generations", 10)):
            with run_states_lock:
                if not run_states[run_id].get('is_running', True): break
                run_states[run_id]['status'] = f"Epoch {gen}: Evaluating Population"

            futures = {executor.submit(evaluate_genome_worker, ind): ind for ind in foundry.population}
            raw_results = [future.result() for future in as_completed(futures)]

            # --- OMEGA FITNESS FUNCTION (Modified for Anomaly Detection) ---
            scored_results = []
            for res in raw_results:
                total_fitness, breakdown = 0, {}
                benign_profile_analysis = foundry.performance_titan.analyze(res['benign_telemetry'])
                
                # Correctness: Did it correctly classify the BENIGN run as NORMAL?
                if benign_profile_analysis.get('profile') == foundry.normal_profile_id:
                    confidence = benign_profile_analysis.get('confidence', {}).get(str(foundry.normal_profile_id), 0.0)
                    breakdown['Correctness'] = 500 * (confidence ** 2)
                else:
                    breakdown['Correctness'] = -2000.0 # Severe penalty for False Positives
                total_fitness += breakdown['Correctness']
                
                # Security: Did it correctly classify the MALICIOUS run as ANOMALOUS?
                malicious_profile_analysis = foundry.performance_titan.analyze(res['attack_telemetry'])
                if malicious_profile_analysis.get('profile') != foundry.normal_profile_id:
                     breakdown['Security'] = 1000.0
                else:
                    breakdown['Security'] = -1000.0 # Penalty for False Negatives
                total_fitness += breakdown['Security']
                
                res.update({'fitness': total_fitness, 'breakdown': breakdown})
                scored_results.append(res)
            
            ledger.record_event(block_height=gen + 1, event_type="EVALUATION_COMPLETE", details={"generation": gen, "evaluation_results": scored_results})

            # --- Step 4: Evolution ---
            with run_states_lock: run_states[run_id]['status'] = f"Epoch {gen}: Evolving..."
            for result in scored_results:
                for pop_ind in foundry.population:
                    if pop_ind['id'] == result['id']:
                        pop_ind.update(result)
                        break
            foundry._evolve_population()
            ledger.record_event(block_height=gen + 1, event_type="CHAMPION_UPDATED", details={"generation": gen, "champion": foundry.population[0].copy()})
            time.sleep(0.5)

    # --- Step 5: Finalization ---
    with run_states_lock: run_states[run_id]['status'] = 'Finalizing'
    if foundry.population:
        final_champion = max(foundry.population, key=lambda x: x.get('fitness', -9999))
        ledger.record_event(block_height=config.get("generations", 10) + 1, event_type="FINAL_CHAMPION_SYNTHESIZED", details={"final_champion": final_champion.copy()})
    ledger.save()
    with run_states_lock:
        run_states[run_id]['status'] = 'Complete'
        run_states[run_id]['is_running'] = False

# --- FLASK ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_synthesis():
    params = request.get_json()
    run_id = f"run_{int(time.time())}"
    config = {
        "population_size": int(params.get('populationSize', 20)), "generations": int(params.get('generations', 10)),
        "elitism_count": int(params.get('elitismCount', 2)), "crossover_rate": float(params.get('crossoverRate', 0.7)),
        "mutation_rate": float(params.get('mutationRate', 0.9)), "mutation_strength": 0.2
    }
    thread = threading.Thread(target=run_foundry_background, args=(run_id, config))
    thread.daemon = True
    thread.start()
    return jsonify({"message": "Synthesis initiated.", "run_id": run_id})

@app.route('/ledger/<run_id>')
def get_ledger(run_id):
    with run_states_lock:
        events = run_states.get(run_id, {}).get('events', [])
    return jsonify(events)

if __name__ == '__main__':
    try:
        multiprocessing.set_start_method('fork', force=True)
    except (ValueError, RuntimeError):
        pass # Not required on all OSes
    print("🚀 COSMOS-Ω Interactive Laboratory (Daemon Sentry Edition)")
    print("🌍 Open your web browser to http://127.0.0.1:5000")
    app.run(debug=False, host='0.0.0.0')