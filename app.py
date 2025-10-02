#
# File: app.py (v5.1 - "Interactive Laboratory - Corrected")
# Fixes the SyntaxError related to the global 'is_running' flag.
#

import threading
import time
from flask import Flask, jsonify, render_template, request
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from cosmos.foundry.foundry_sentinel import SentinelFoundry
from cosmos.ledger.ledger import Ledger
from cosmos.foundry.titans_sentinel import ExecutionTitan 

# --- Global State ---
foundry_thread = None
is_running = False
run_ledgers = {}

app = Flask(__name__)

def run_foundry_background(run_id, config, target_name):
    """ The foundry now accepts a config and a target name. """
    # --- FIX: Declare global at the TOP of the function ---
    global run_ledgers, is_running
    
    try:
        ledger = Ledger(output_dir=str(PROJECT_ROOT / f"artifacts/gui_runs/{run_id}"))
        run_ledgers[run_id] = ledger.events

        titan = ExecutionTitan()
        if target_name == "high_cpu":
            titan.harness_path = str(PROJECT_ROOT / "data/targets/high_cpu.c")
            titan.app_source_path, titan.header_dir = "", ""
        elif target_name == "file_io":
            titan.harness_path = str(PROJECT_ROOT / "data/targets/file_io.c")
            titan.app_source_path, titan.header_dir = "", ""
        
        # --- DYNAMIC CONFIGURATION ---
        # Pass the user's config directly to the foundry
        foundry_instance = SentinelFoundry(config)
        foundry_instance.execution_titan = titan

        ledger.record_event(0, "INITIATION", {"config": config, "target": target_name})
        
        foundry_instance.calibrate()
        ledger.record_event(0, "CALIBRATION_COMPLETE", {"normal_profile_id": foundry_instance.normal_profile_id})
        
        foundry_instance._initialize_population()
        results = [foundry_instance._evaluate_genome(ind) for ind in foundry_instance.population]
        for r in results: r['parent'] = 'GENESIS-0'
        ledger.record_event(0, "EVALUATION_COMPLETE", {"generation": 0, "evaluation_results": results})

        for gen in range(1, foundry_instance.generations):
            if not is_running: break
            
            foundry_instance.population = results
            foundry_instance._selection()
            foundry_instance._mutate_population()
            
            elites = sorted(results, key=lambda x: x.get('fitness', -9999), reverse=True)[:foundry_instance.elitism_count]
            results = []
            for i, ind in enumerate(foundry_instance.population):
                res = foundry_instance._evaluate_genome(ind)
                res['parent'] = elites[i % len(elites)]['id'] if elites else 'GENESIS-0'
                results.append(res)
            
            ledger.record_event(gen, "EVALUATION_COMPLETE", {"generation": gen, "evaluation_results": results})
            time.sleep(1)

        champion = max(results, key=lambda x: x.get('fitness', -9999))
        ledger.record_event(foundry_instance.generations, "FINAL_CHAMPION_SYNTHESIZED", {"final_champion": champion.copy()})
        ledger.save()
    except Exception as e:
        if 'ledger' in locals(): ledger.record_event(99, "ERROR", {"detail": str(e)})
    finally:
        # Now this works correctly.
        is_running = False

@app.route('/')
def index(): return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_synthesis():
    global is_running, foundry_thread
    if not is_running:
        is_running = True
        
        params = request.get_json()
        # --- DYNAMIC CONFIGURATION ---
        config = {
            "population_size": int(params.get('populationSize', 10)),
            "generations": int(params.get('generations', 10)),
            "elitism_count": 2, "mutation_rate": 0.8, "mutation_strength": 0.2 # Add other params here
        }
        target_name = params.get('target', 'cjson')
        run_id = f"run_{int(time.time())}"

        foundry_thread = threading.Thread(target=run_foundry_background, args=(run_id, config, target_name))
        foundry_thread.start()
        return jsonify({"message": "Synthesis initiated.", "run_id": run_id})
    return jsonify({"message": "Synthesis is already running."})

@app.route('/ledger/<run_id>')
def get_ledger(run_id):
    return jsonify(run_ledgers.get(run_id, []))

if __name__ == '__main__':
    print("🚀 COSMOS-Ω Interactive Laboratory")
    print("🌍 Open your web browser to http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1')