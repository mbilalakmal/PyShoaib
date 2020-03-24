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

import random


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
        for lecture in self.resources.lectures.values():
            print(lecture)

            self._assign_lecture(lecture)

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

        import time
        # 1. Pauli Exclusion
        a = time.time()
        # count unique room and time slots
        # unique_slots = self.entries.groupby(
        #     ['day', 'hour', 'room_id']
        #     ).count()

        # unique_slots = len(self.entries.groupby(
        #     ['day', 'hour', 'room_id']
        #     ))

        unique_slots = self.entries.groupby(
            ['day', 'hour', 'room_id']
            ).ngroups

        c = time.time()

        total_slots = len(self.entries.index)

        b = time.time()

        print('unique', unique_slots)
        print('total', total_slots)
        print(b-a, c-a)

        # 2. capacity

        capacity_slots = 0

        course_slots = 0
        course_rooms = 0

        teacher_slots = 0
        teacher_rooms = 0

        lecture_slots = 0

        a = time.time()
        for row in self.entries.itertuples(index=False, name=None):
            # print(row)
            day, hour, room_id, lecture_id = row
            lecture = self.resources.lectures[lecture_id]
            room = self.resources.rooms[room_id]
            if room.capacity >= lecture.strength:
                capacity_slots += 1

            course = self.resources.courses[lecture.course_id]
            if course.available_slots[day][hour] == True:
                course_slots += 1
            if room_id in course.available_room_ids:
                course_rooms += 1

            teachers = [
                self.resources.teachers[t_id] for t_id in lecture.teacher_ids
            ]

            nteachers = len(teachers)

            for teacher in teachers:
                if teacher.available_slots[day][hour] == True:
                    teacher_slots += 1/nteachers
                if room_id in teacher.available_room_ids:
                    teacher_rooms += 1/nteachers

            concurrent_lecture_ids = set(self.entries[
                (self.entries['day'] == day) &
                (self.entries['hour'] == hour)
            ]['lecture_id'])

            if concurrent_lecture_ids.isdisjoint(lecture.noncurrent_lecture_ids) == True:
                lecture_slots += 1

        b = time.time()
        print('cap', capacity_slots)
        print('courses', course_slots)
        print('courser', course_rooms)
        print('teachers', teacher_slots)
        print('teacherr', teacher_rooms)
        print('lectures', lecture_slots)
        print(b-a)




    #----------------------------------------
    # PRIVATE METHODS
    #----------------------------------------


    def _assign_lecture(self, lecture: Lecture):
        '''
        Assigns room and time slots of `lecture`.
        '''

        course = self.resources.courses[lecture.course_id]
        duration = course.duration

        if course.is_lab_course == True:
            slots = self._get_random_lab_slots(duration)
        else:
            slots = self._get_random_theory_slots(duration)

        # add the fourth column
        for slot in slots:
            slot.append(lecture.id)

        # slots is a list of lists
        self.entries = self.entries.append(
            pd.DataFrame(slots, columns=self.entries.columns)
            )


    def _get_random_lab_slots(self, duration):
        '''
        Returns `duration` room and time slots for a lab.
        '''
        slots = []

        day = random.choice(
            range(self.parameters.week_days)
        )

        room_id = random.choice(
            list(self.resources.rooms.keys())
        )

        hour = random.choice(
            range(self.parameters.daily_hours - duration + 1)
        )

        for i in range(duration):
            slot = [day, hour+i, room_id]
            slots.append(slot)

        return slots


    def _get_random_theory_slots(self, duration):
        '''
        Returns `duration` room and time slots for a theory.
        '''
        slots = []

        days = random.sample(
            range(self.parameters.week_days), k=duration
        )

        room_ids = random.choices(
            list(self.resources.rooms.keys()), k=duration
        )

        hours = random.choices(
            range(self.parameters.daily_hours), k=duration
        )

        for i in range(duration):
            slot = [days[i], hours[i], room_ids[i]]
            slots.append(slot)

        return slots


    def __gt__(self, other: 'Chromsome'):
        return self.fitness > other.fitness


    def __eq__(self, other: 'Chromsome'):
        return self.fitness == other.fitness

    
    def __repr__(self):
        return f'Fitness: {self.fitness}\n'
