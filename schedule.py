# -----------------------------------------------------------
# This module represents a weekly schedule as a chromosome.
#
# A schedule contains room and time slots allocations for
# each lecture. The fitness of a schedule represented by
# a real number [0.0 - 1.0] is measured by how many constraints
# are fulfilled by that schedule.
# Genetic operators such as mutation and crossover are also defined.
#
#
# (C) 2020 PyShoaib
# -----------------------------------------------------------

from resources import *
from parameters import Parameters
from functools import total_ordering


@total_ordering
class Schedule:
    '''
    Represents a weekly schedule.

    Requires a `Resources` object and a `Parameters` object.
    '''
    def __init__(self, resources: Resources, parameters: Parameters):
        
        # fitness representing constraints fulfilled [0.0 - 1.0]
        self.fitness = 0.0

        # aggregate resources and parameters
        self.resources = resources
        self.parameters = parameters

        # data structure for the actual schedule
        # TODO pandas single dataframe

    def initialize(self):
        '''
        Assign random room and time slots to each lecture.

        Constraints are not considered in this step.
        '''
        pass


    def mutate(self):
        '''
        Reassign room and time slots to a (small) subset of lecture.

        Fitness of the schedule must be re-evaluated after this step.
        '''
        pass


    def crossover(self, parent1: 'Schedule', parent2: 'Schedule'):
        '''
        Copy assigned room and time slots from `parent1` and `parent2`.

        Fitness of the schedule must be re-evaluated after this step.
        '''
        pass


    def copy(self, parent: 'Schedule'):
        '''
        Copy assigned room and time slots from `parent`.

        Fitness is equal to the fitness of `parent`.
        '''
        pass


    def calculate_fitness(self):
        '''
        Checks each constraints and assigns score based on fulfilled.
        '''
        pass


    #----------------------------------------
    # PRIVATE METHODS
    #----------------------------------------


    def __gt__(self, other: 'Chromsome'):
        return self.fitness > other.fitness


    def __eq__(self, other: 'Chromsome'):
        return self.fitness == other.fitness

    
    def __repr__(self):
        return f'Fitness: {self.fitness}\n'