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

import random
from functools import total_ordering

from pandas import Series, DataFrame

from parameters import Parameters
from resources import *


@total_ordering
class Schedule:
    """
    Represents a weekly schedule.

    Requires a `Resources` object and a `Parameters` object.
    """

    def __init__(self, resources: Resources, parameters: Parameters):
        self.resources = resources
        self.parameters = parameters

        self.fitness = 0.0
        self.dirty_bit = False  # indicate current fitness is obsolete

        self.fulfilled = dict.fromkeys(
            ['unique_slots',
             'capacity_rooms',
             'course_slots',
             'course_rooms',
             'teacher_slots',
             'teacher_rooms',
             'lecture_slots', ],
            False
        )

        # data structure for the actual schedule
        self.entries = DataFrame(columns=['day', 'hour', 'room_id', 'lecture_id'])

    def initialize(self):
        """
        Assign random room and time slots to each lecture.

        Constraints are not considered in this step.
        """
        for lecture in self.resources.lectures.values():
            self._assign_lecture(lecture)

        self.dirty_bit = True  # indicate current fitness is obsolete

    def mutate(self):
        """
        Reassign room and time slots of a (small) subset of lecture.

        Fitness of the schedule must be re-evaluated after this step.
        """
        sample = int(self.parameters.mutation_size * len(self.resources.lectures))
        target_ids = random.sample(self.resources.lectures.keys(), sample)
        lectures = [self.resources.lectures[target_id] for target_id in target_ids]

        for lecture in lectures:
            self._remove_lecture(lecture)
            self._assign_lecture(lecture)

        self.dirty_bit = True  # indicate current fitness is obsolete

    def crossover(self, parent1: 'Schedule', parent2: 'Schedule'):
        """
        Copy assigned room and time slots from `parent1` and `parent2`.

        Fitness of the schedule must be re-evaluated after this step.
        """
        lecture_ids = list(self.resources.lectures.keys())
        random.shuffle(lecture_ids)
        parent1_ids = lecture_ids[:int(len(lecture_ids) / 2)]
        parent2_ids = lecture_ids[int(len(lecture_ids) / 2):]

        self.entries = self.entries.iloc[0:0]

        # pick from parent1
        self.entries = self.entries.append(
            parent1.entries.loc[parent1.entries['lecture_id'].isin(parent1_ids), :], ignore_index=True
        )

        # pick from parent2
        self.entries = self.entries.append(
            parent2.entries.loc[parent2.entries['lecture_id'].isin(parent2_ids), :], ignore_index=True
        )

        self.dirty_bit = True  # indicate current fitness is obsolete

    def copy(self, parent: 'Schedule'):
        """
        Copy assigned room and time slots from `parent`.

        Fitness is equal to the fitness of `parent`.
        """
        self.entries = DataFrame.copy(parent.entries, deep=True)
        self.fitness = parent.fitness

        self.dirty_bit = False

    def calculate_fitness(self):
        """
        Checks each constraints and assigns score based on fulfilled.
        """
        if self.dirty_bit is False:
            return
        self.dirty_bit = False

        total_slots: int = len(self.entries.index)

        scores: Series = Series(0, index=self.fulfilled.keys())

        # 1. Pauli Exclusion [no two entries have the same day, hour, and room_id]
        unique_groups = self.entries.groupby(['day', 'hour', 'room_id']).count()
        scores.unique_slots = unique_groups[unique_groups == 1].sum()[0]

        for _, row in self.entries.iterrows():
            day, hour, room_id, lecture_id = row

            room = self.resources.rooms[room_id]
            lecture = self.resources.lectures[lecture_id]
            course = self.resources.courses[lecture.course_id]

            teachers = [self.resources.teachers[t_id] for t_id in lecture.teacher_ids]

            # entries with the same day and hour
            concurrent_l_ids = set(
                self.entries.loc[
                    (self.entries['day'] == day) &
                    (self.entries['hour'] == hour)
                    ]['lecture_id']
            )

            # 2. Room's capacity is greater than lecture's strength
            scores.capacity_rooms += (room.capacity >= lecture.strength)
            # 3. Course is available at this day and hour
            scores.course_slots += course.available_slots[day][hour]
            # 4. Course is available at this room
            scores.course_rooms += (room_id in course.available_room_ids)

            teacher_slots: Series = Series(index=range(len(teachers)), dtype=bool)
            teacher_rooms: Series = Series(index=range(len(teachers)), dtype=bool)
            for idx, teacher in enumerate(teachers):
                # 5. Teacher is available at this day and hour
                teacher_slots[idx] = teacher.available_slots[day][hour]
                # 6. Teacher is available at this room
                teacher_rooms[idx] = room_id in teacher.available_room_ids
            scores.teacher_slots += teacher_slots.mean()
            scores.teacher_rooms += teacher_rooms.mean()

            # 7. No noncurrent lecture at this day and hour
            scores.lecture_slots += concurrent_l_ids.isdisjoint(lecture.noncurrent_lecture_ids)

        # scale each score between 0 and 1
        scores = scores.div(total_slots)

        for constraint in self.fulfilled.keys():
            self.fulfilled[constraint] = scores.loc[constraint]  # == 1.0

        self.fitness = scores.mean()

    def save_slots(self):
        """
        Save assigned_slots from this schedule's entries to resources.lectures
        """
        entries: DataFrame = self.entries.rename(
            columns={'hour': 'time', 'room_id': 'roomId', 'lecture_id': 'id'}
        )

        for lecture_id, lecture_group in entries.groupby(['id']):
            assigned_slots = lecture_group.drop(columns=['id']).to_dict(orient='records')
            self.resources.lectures[lecture_id].assigned_slots = assigned_slots

    # ----------------------------------------
    # PRIVATE METHODS
    # ----------------------------------------

    def _assign_lecture(self, lecture: Lecture):
        """
        Assigns room and time slots of `lecture`.
        """
        course = self.resources.courses[lecture.course_id]

        if course.is_lab_course is True:
            slots = self._get_random_lab_slots(course.duration)
        else:
            slots = self._get_random_theory_slots(course.duration)

        # add the fourth column
        for slot in slots:
            slot.append(lecture.id)

        self.entries = self.entries.append(DataFrame(slots, columns=self.entries.columns))

    def _get_random_lab_slots(self, duration):
        """
        Returns `duration` room and time slots for a lab.
        """
        day = random.choice(range(self.parameters.week_days))
        room_id = random.choice(list(self.resources.rooms.keys()))
        hour = random.choice(range(self.parameters.daily_hours - duration + 1))

        slots = [[day, hour + i, room_id] for i in range(duration)]
        return slots

    def _get_random_theory_slots(self, duration):
        """
        Returns `duration` room and time slots for a theory.
        """
        days = random.sample(range(self.parameters.week_days), k=duration)
        room_ids = random.choices(list(self.resources.rooms.keys()), k=duration)
        hours = random.choices(range(self.parameters.daily_hours), k=duration)

        slots = [[days[i], hours[i], room_ids[i]] for i in range(duration)]
        return slots

    def _remove_lecture(self, lecture: Lecture):
        """
        Remove room and time slots of `lecture`.
        """
        self.entries = self.entries[self.entries['lecture_id'] != lecture.id]

    def __gt__(self, other: 'Schedule'):
        return self.fitness > other.fitness

    def __eq__(self, other: 'Schedule'):
        return self.fitness == other.fitness

    def __repr__(self):
        return f'Fitness: {self.fitness}\n'
