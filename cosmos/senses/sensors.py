# cosmos/senses/sensors.py

#
# ForgeX4 COSMOS-Ω
#
# Author: Gemini, AI Lead Engineer
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/senses/sensors.py
# Date: 2025-09-27
#
# Description:
# This module provides the core functions for collecting "Tier A" hardware
# telemetry from the host system. It is the primary interface for the 
# Digital Twin's data collection process.
#

import psutil
import time
from typing import Dict, Any, List, Optional

def get_tier_a_snapshot() -> Dict[str, Any]:
    """
    Captures a single, comprehensive snapshot of Tier A telemetry data.
    
    Tier A includes:
    - Timestamp
    - Overall CPU Utilization (%)
    - Per-Core CPU Utilization (%)
    - CPU Frequencies (current, min, max)
    - System Temperatures (°C)
    
    Returns:
        A dictionary containing the telemetry data point.
    """
    snapshot = {}
    
    # 1. Timestamp
    snapshot['timestamp'] = time.time()
    
    # 2. CPU Utilization
    snapshot['cpu_util_overall'] = psutil.cpu_percent(interval=None)
    per_cpu_util = psutil.cpu_percent(interval=None, percpu=True)
    for i, util in enumerate(per_cpu_util):
        snapshot[f'cpu_util_core_{i}'] = util
        
    # 3. CPU Frequency
    try:
        freq = psutil.cpu_freq()
        snapshot['cpu_freq_current_mhz'] = freq.current
        snapshot['cpu_freq_min_mhz'] = freq.min
        snapshot['cpu_freq_max_mhz'] = freq.max
    except (NotImplementedError, AttributeError):
        # Some systems might not support this
        snapshot['cpu_freq_current_mhz'] = None
        snapshot['cpu_freq_min_mhz'] = None
        snapshot['cpu_freq_max_mhz'] = None

    # 4. System Temperatures
    # This is highly hardware-dependent. We will try to find the core temps.
    temps = psutil.sensors_temperatures()
    core_temps = []
    
    # Common keys for CPU core temperatures
    cpu_temp_keys = ['coretemp', 'k10temp', 'zenpower'] 
    
    found_temps = False
    for key in cpu_temp_keys:
        if key in temps:
            for entry in temps[key]:
                # Look for labels like 'Core X' or 'Tdie'
                if 'core' in entry.label.lower() or 'tdie' in entry.label.lower():
                    core_temps.append(entry.current)
            if core_temps:
                found_temps = True
                break # Stop after finding the first valid set
    
    if found_temps:
        snapshot['cpu_temp_celsius_avg'] = sum(core_temps) / len(core_temps)
    else:
        # Fallback if specific core temps aren't found
        snapshot['cpu_temp_celsius_avg'] = None

    return snapshot

if __name__ == '__main__':
    # For testing purposes: print a single snapshot
    import json
    snapshot_data = get_tier_a_snapshot()
    print(json.dumps(snapshot_data, indent=2))