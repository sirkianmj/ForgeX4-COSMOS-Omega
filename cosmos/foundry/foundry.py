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
# This file contains the core Foundry class, which orchestrates the
# genetic algorithm and the evolutionary process. This is a DEBUG version
# with extensive logging in the mutation step.
#
import copy
import random
from pycparser import c_ast
from cosmos.foundry.mutations import hardening
from cosmos.foundry import fitness
from cosmos.parser import parser # <-- Added Import

class Foundry:
    """
    The core evolutionary engine for the COSMOS-Ω project.
    """
    def __init__(self, initial_ast: c_ast.FileAST, config: dict):
        self.initial_ast = initial_ast
        self.population_size = config.get("population_size", 10)
        self.mutation_rate = config.get("mutation_rate", 0.1)
        self.generations = config.get("generations", 5)

        self.population = []

    def _initialize_population(self):
        """Creates the initial population from the starting AST."""
        print("Initializing population...")
        self.population = []
        for _ in range(self.population_size):
            individual = {
                'genome': copy.deepcopy(self.initial_ast),
                'fitness': 0.0
            }
            self.population.append(individual)
        print(f"Population of {self.population_size} individuals created.")

    def _evaluate_population(self):
        """
        Calculates and assigns a fitness score to each individual in the population
        by compiling and testing them in the Crucible.
        """
        print("Evaluating population fitness...")
        for i, individual in enumerate(self.population):
            print(f"  - Evaluating individual {i+1}/{self.population_size}...", end='', flush=True)
            score = fitness.evaluate_fitness(individual['genome'])
            individual['fitness'] = score
            print(f" score: {score}")

    def _mutate_population(self):
        """Applies mutations to individuals in the population."""
        print("Applying mutations...")
        for i, individual in enumerate(self.population):
            if random.random() < self.mutation_rate:
                print(f"  - Mutating individual {i}...")
                
                # --- DEBUG LOGGING START ---
                # 1. Show the code BEFORE mutation
                print("    --- BEFORE ---")
                pre_mutation_code = parser.unparse_ast_to_c(individual['genome'])
                for line in pre_mutation_code.splitlines():
                    if "gets(" in line or "fgets(" in line:
                        print(f"    {line.strip()}")
                
                # 2. Apply the mutation
                mutated_ast = hardening.mutate_gets_to_fgets(individual['genome'])
                individual['genome'] = mutated_ast # Make sure we save it back

                # 3. Show the code AFTER mutation
                print("    --- AFTER ---")
                post_mutation_code = parser.unparse_ast_to_c(individual['genome'])
                for line in post_mutation_code.splitlines():
                    if "gets(" in line or "fgets(" in line:
                        print(f"    {line.strip()}")
                print("    ---------------")
                # --- DEBUG LOGGING END ---

    def run(self):
        """Runs the entire evolutionary process."""
        self._initialize_population()

        for gen in range(self.generations):
            print(f"\n--- Generation {gen + 1}/{self.generations} ---")

            # Corrected loop order: Mutate first, then evaluate.
            self._mutate_population()
            self._evaluate_population()

            best_fitness = max(ind['fitness'] for ind in self.population)
            print(f"Best fitness in generation {gen + 1}: {best_fitness:.2f}")

        print("\nEvolutionary run complete.")