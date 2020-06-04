# -----------------------------------------------------------
# This module represents a GeneticAlgorithm.
#
# A genetic algorithm must be provided with:
# (1) chromosome length,
# (2) population size,
# (3) and number of generations
#
# After initialization, a single method 'run' will
# operate to generate new generations until a solution is found.
#
#
# (C) 2020 PyShoaib
# -----------------------------------------------------------

from schedule import Schedule
from parameters import Parameters
from resources import Resources
import numpy as np


class GeneticAlgorithm:

    def __init__(self, resources: Resources, parameters: Parameters):
        self.resources = resources
        self.parameters = parameters

        self.generation = 0
        self.optimum_reached = False
        self.best_fitness = 0.0
        self.best_schedule = None

        self._population = np.empty(
            shape=parameters.population_size,
            dtype=Schedule
        )

    def run(self):
        self._initialize()
        while (not self.optimum_reached) and (self.generation < self.parameters.maximum_generations):
            self._reproduce()
            self.generation += 1
            print(f'Gen: {self.generation}  Best: {self.best_fitness}')

        return self.optimum_reached

    def _initialize(self):
        """
        Initialize the population of schedules.
        """
        for idx in range(self.parameters.population_size):
            self._population[idx] = Schedule(self.resources, self.parameters)
            self._population[idx].initialize()
            self._population[idx].calculate_fitness()

        self._track_best()

    def _reproduce(self):
        population = np.empty_like(self._population)

        for idx in range(self.parameters.population_size - 1):

            # crossover
            parent1, parent2 = self._tournament_selection(), self._tournament_selection()

            while parent1 is parent2:
                parent2 = self._tournament_selection()

            child = Schedule(self.resources, self.parameters)

            if np.random.binomial(1, p=self.parameters.crossover_rate):
                child.crossover(parent1, parent2)
            else:
                child.copy(np.random.choice([parent1, parent2]))

            # mutation
            if np.random.binomial(1, self.parameters.mutation_rate):
                child.mutate()

            child.calculate_fitness()

            population[idx] = child

        # preserve the best
        child = Schedule(self.resources, self.parameters)
        if self.best_schedule is not None:
            child.copy(self.best_schedule)
        else:
            child.initialize()
        population[-1] = child

        self._population = population
        self._track_best()

    def _tournament_selection(self):
        pressure = self.parameters.selection_pressure
        return np.amax(np.random.choice(self._population, size=pressure))

    def _track_best(self):
        self.best_schedule = np.amax(self._population)
        self.best_fitness = self.best_schedule.fitness

        self.optimum_reached = self.best_fitness == 1.0
