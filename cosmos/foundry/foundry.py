#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/foundry/foundry.py
# Date: 2025-09-25
#
# Description:
# This definitive Phase 1 version implements robust champion tracking and a
# standard elitism selection strategy to ensure evolutionary progress.
#
import copy
import random
from pycparser import c_ast
from cosmos.foundry.mutations import hardening
from cosmos.foundry import fitness
from cosmos.parser import parser

class Foundry:
    """
    The core evolutionary engine for the COSMOS-Ω project.
    """
    def __init__(self, initial_ast: c_ast.FileAST, config: dict):
        self.initial_ast = initial_ast
        self.population_size = config.get("population_size", 20)
        self.mutation_rate = config.get("mutation_rate", 0.2)
        self.generations = config.get("generations", 5)
        self.elitism_count = config.get("elitism_count", 1)

        self.population = []
        self.champion = { 'genome': None, 'fitness': -float('inf') }

    def _initialize_population(self):
        print("Initializing population...")
        self.population = []
        for _ in range(self.population_size):
            self.population.append({ 'genome': copy.deepcopy(self.initial_ast), 'fitness': 0.0 })
        print(f"Population of {self.population_size} individuals created.")

    def _evaluate_population(self):
        print("Evaluating population fitness...")
        for i, individual in enumerate(self.population):
            print(f"  - Evaluating individual {i+1}/{self.population_size}...", end='', flush=True)
            score = fitness.evaluate_fitness(individual['genome'])
            individual['fitness'] = score
            print(f" score: {score}")

            if score > self.champion['fitness'] and score > 0:
                print(f"  *** NEW CHAMPION FOUND! Fitness: {score} ***")
                self.champion['genome'] = copy.deepcopy(individual['genome'])
                self.champion['fitness'] = score
    
    def _selection(self):
        """
        Selects individuals for the next generation. Implements elitism.
        """
        print("Performing selection...")
        self.population.sort(key=lambda ind: ind['fitness'], reverse=True)
        
        elites = self.population[:self.elitism_count]
        
        next_generation = []
        # Breed the rest of the population from the elites.
        for _ in range(self.population_size - self.elitism_count):
            parent = random.choice(elites)
            next_generation.append({ 'genome': copy.deepcopy(parent['genome']), 'fitness': 0.0 })
            
        self.population = elites + next_generation

    def _mutate_population(self):
        print("Applying mutations...")
        # Skip mutating the elites.
        for i, individual in enumerate(self.population[self.elitism_count:]):
            if random.random() < self.mutation_rate:
                print(f"  - Mutating non-elite individual {self.elitism_count + i}...")
                mutated_ast = hardening.mutate_gets_to_fgets(individual['genome'])
                individual['genome'] = mutated_ast

    def run(self) -> dict:
        self._initialize_population()
        
        print(f"\n--- Initial Evaluation (Generation 0) ---")
        self._evaluate_population()

        for gen in range(self.generations):
            print(f"\n--- Generation {gen + 1}/{self.generations} ---")

            self._selection()
            self._mutate_population()
            self._evaluate_population()

            # --- CORRECTED LOGGING ---
            # Find the actual best fitness in the current population.
            best_fitness_in_gen = max(ind['fitness'] for ind in self.population)
            print(f"Best fitness in generation {gen + 1}: {best_fitness_in_gen:.2f}")
            print(f"Overall champion fitness: {self.champion['fitness']:.2f}")

        print("\nEvolutionary run complete.")
        return self.champion