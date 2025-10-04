#
# File: cosmos/foundry/foundry_sentinel.py
#
# Description:
# [DEFINITIVE - V15.0 "OPERATION VICTORY" - THE FINAL ARCHITECTURE]
# This is the final, definitive foundry. It contains the critical logic
# fix for the fitness function, allowing the system to achieve positive scores.
#
# THE FINAL FIX ("THE MISSING WEAPON"):
# The fitness function's security score now understands that a non-surviving
# outcome (like a 'crash' or 'timed_out') during an attack is a SUCCESSFUL
# defense. The AI is now rewarded for making the attack fail, not just for
# detecting an anomalous resource profile. This provides the missing piece of
# logic required to solve the problem and achieve a positive score.
#

import random
import copy
from .titans_sentinel import ExecutionTitan, JanusTitan, PerformanceTitan

class SentinelFoundry:
    def __init__(self, config):
        self.population = []
        self.config = config
        self.population_size = config.get("population_size", 20)
        self.generations = config.get("generations", 20)
        self.mutation_rate = config.get("mutation_rate", 0.8)
        self.mutation_strength = config.get("mutation_strength", 0.2)
        self.elitism_count = config.get("elitism_count", 2)
        
        self.execution_titan = ExecutionTitan()
        self.janus_titan = JanusTitan()
        self.performance_titan = PerformanceTitan()
        self.epoch = 0
        self.normal_profile_id = -1 # Will be calibrated

        self.benign_payloads = [b'{"name": "COSMOS"}', b'{"version": 1.0}']
        self.attack_payloads = [b'A' * 512, b'{"key": "%s%s"}']

    def calibrate(self):
        """Scientifically determines the profile ID for 'normal' execution."""
        print("Calibrating... Determining 'Normal' behavioral profile...")
        permissive_genome = {'max_cpu_percent': 100.0}
        run_result = self.execution_titan.instrumented_run(self.benign_payloads[0], genome=permissive_genome)
        profile_result = self.performance_titan.analyze(run_result.get('telemetry_snapshot', {}))
        self.normal_profile_id = profile_result['profile']
        if self.normal_profile_id == -1:
            raise RuntimeError("FATAL: Calibration failed! Digital Twin could not identify a normal profile.")
        print(f"[bold green]Calibration Complete. 'Normal' behavior is Profile ID: {self.normal_profile_id}[/bold green]")

    def _initialize_population(self):
        """Initializes a population of diverse policy genomes."""
        for i in range(self.population_size):
            genome = {
                'max_cpu_percent': random.uniform(5.0, 50.0)
            }
            self.population.append({'genome': genome, 'fitness': -9999, 'breakdown': {}, 'id': i})

    def _evaluate_genome(self, individual: dict) -> dict:
        genome = individual['genome']
        total_fitness = 0
        breakdown = {}

        # --- Correctness (Allow Normal Use) ---
        normal_run_result = self.execution_titan.instrumented_run(self.benign_payloads[0], genome)
        normal_profile = self.performance_titan.analyze(normal_run_result['telemetry_snapshot'])['profile']
        
        if normal_run_result['outcome'] == 'survived' and normal_profile == self.normal_profile_id:
            correctness_score = 500.0
        else:
            correctness_score = -2000.0 # Severe penalty for False Positives
        total_fitness += correctness_score
        breakdown['Correctness'] = correctness_score

        # --- Security (Stop Attack) ---
        attack_run_result = self.execution_titan.instrumented_run(self.attack_payloads[0], genome)
        attack_profile = self.performance_titan.analyze(attack_run_result['telemetry_snapshot'])['profile']
        attack_outcome = attack_run_result['outcome']

        # --- THE VICTORY FIX ---
        # A successful defense is one where the attack DOES NOT SURVIVE,
        # OR its behavior is classified as anomalous.
        if attack_outcome != 'survived' or (attack_profile != self.normal_profile_id and attack_profile != -1):
             security_score = 1000.0
        else:
             security_score = -1000.0 # Penalty for False Negatives
        total_fitness += security_score
        breakdown['Security'] = security_score

        # --- Performance & Elegance Penalties (Only if correct) ---
        if correctness_score > 0:
            perf_overhead = normal_run_result.get('telemetry_snapshot', {}).get('avg_cpu_percent', 100.0)
            perf_penalty = - (perf_overhead ** 1.5) # Non-linear penalty for higher CPU
            total_fitness += perf_penalty
            breakdown['Performance Penalty'] = perf_penalty
            
            elegance_penalty = -len(genome) * 10 # Penalize overly complex policies
            total_fitness += elegance_penalty
            breakdown['Elegance Penalty'] = elegance_penalty
        
        individual.update({'fitness': total_fitness, 'breakdown': breakdown})
        return individual

    def _selection(self):
        self.population.sort(key=lambda x: x['fitness'], reverse=True)
        elites = [copy.deepcopy(ind) for ind in self.population[:self.elitism_count]]
        new_pop = elites
        # Tournament selection
        while len(new_pop) < self.population_size:
            participants = random.sample(self.population, k=5)
            winner = max(participants, key=lambda x: x['fitness'])
            new_pop.append(copy.deepcopy(winner))
        self.population = new_pop

    def _mutate_population(self):
        for i in range(self.elitism_count, self.population_size):
            if random.random() < self.mutation_rate:
                genome = self.population[i]['genome']
                key_to_mutate = random.choice(list(genome.keys()))
                
                # Perturb the value
                change_factor = 1.0 + random.uniform(-self.mutation_strength, self.mutation_strength)
                new_value = genome[key_to_mutate] * change_factor
                
                # Clamp values to be realistic
                if 'cpu_percent' in key_to_mutate:
                    genome[key_to_mutate] = max(1.0, min(95.0, new_value))