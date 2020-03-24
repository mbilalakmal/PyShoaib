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

from functools import total_ordering

import pandas as pd

from parameters import Parameters
from resources import *


@total_ordering
class Schedule:
    '''
    Represents a weekly schedule.

    Requires a `Resources` object and a `Parameters` object.
    '''
    def __init__(self, resources: Resources, parameters: Parameters):
        
        # fitness representing constraints fulfilled [0.0 - 1.0]
        self.fitness = 0.0

        # if dirty then re-evaluate fitness
        self.dirty_bit = False

        # aggregate resources and parameters
        self.resources = resources
        self.parameters = parameters

        # data structure for the actual schedule
        self.entries = pd.DataFrame(
            columns=['day', 'hour', 'room_id', 'lecture_id']
        )


    def initialize(self):
        '''
        Assign random room and time slots to each lecture.

        Constraints are not considered in this step.
        '''
        pass
        # for each lecture*duration assign a row in entries

        # turn on dirty bit
        self.dirty_bit = True


    def mutate(self):
        '''
        Reassign room and time slots to a (small) subset of lecture.

        Fitness of the schedule must be re-evaluated after this step.
        '''
        pass
        # for MSIZE*lectures modify a row in entries

        # turn on dirty bit
        self.dirty_bit = True


    def crossover(self, parent1: 'Schedule', parent2: 'Schedule'):
        '''
        Copy assigned room and time slots from `parent1` and `parent2`.

        Fitness of the schedule must be re-evaluated after this step.
        '''
        pass
        # copy half rows(lecture-wise) from each parent

        # turn on dirty bit
        self.dirty_bit = True


    def copy(self, parent: 'Schedule'):
        '''
        Copy assigned room and time slots from `parent`.

        Fitness is equal to the fitness of `parent`.
        '''
        pass
        # copy the whole dataframe and fitness

        self.fitness = parent.fitness


    def calculate_fitness(self):
        '''
        Checks each constraints and assigns score based on fulfilled.
        '''
        pass

        # check if fitness needs to be evaluated
        if self.dirty_bit == False:
            return

        # calculate fitness


    #----------------------------------------
    # PRIVATE METHODS
    #----------------------------------------


    def __gt__(self, other: 'Chromsome'):
        return self.fitness > other.fitness


    def __eq__(self, other: 'Chromsome'):
        return self.fitness == other.fitness

    
    def __repr__(self):
        return f'Fitness: {self.fitness}\n'
