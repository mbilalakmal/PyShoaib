# -----------------------------------------------------------
# This module provides a JSON parser for the resources.
#
# It defines:
# (1) Rooms
# (2) Courses
# (3) Teachers
# (4) Sections
# (5) Lectures
#
#
# (C) 2020 PyShoaib
# -----------------------------------------------------------

import json

from clashes import set_lectures_noncurrency
from parameters import *
from resources import *
from resources import Resources


def read_json(json_file):
    """
    Reads resources from `json_file`.

    Returns `Resources` object.
    """
    with open(json_file, 'r') as file:
        serial_resources = json.load(file)

    return _extract_resources(serial_resources)


def read_parameters(json_file):
    """
    Reads parameters from `json_file`.

    Returns `Parameters` object.
    """
    with open(json_file, 'r') as file:
        serial_parameters = json.load(file)

    return Parameters(
        population_size=serial_parameters.get('population_size'),
        maximum_generations=serial_parameters.get('maximum_generations'),
        mutation_rate=serial_parameters.get('mutation_rate'),
        mutation_size=serial_parameters.get('mutation_size'),
        crossover_rate=serial_parameters.get('crossover_rate'),
        crossover_size=serial_parameters.get('crossover_size'),
        selection_pressure=serial_parameters.get('selection_pressure'),
        week_days=serial_parameters.get('week_days'),
        daily_hours=serial_parameters.get('daily_hours'),
    )


def _extract_resources(serial_resources):
    resources: Resources = Resources()
    serial_rooms = serial_resources['rooms']
    serial_courses = serial_resources['courses']
    serial_teachers = serial_resources['teachers']
    serial_sections = serial_resources['atomicSections']
    serial_lectures = serial_resources['entries']
    serial_electives = serial_resources['constraints']

    for serial_room in serial_rooms:
        room = Room(serial_room)
        resources.rooms[room.id] = room

    for serial_course in serial_courses:
        course = Course(serial_course)
        resources.courses[course.id] = course

    for serial_teacher in serial_teachers:
        teacher = Teacher(serial_teacher)
        resources.teachers[teacher.id] = teacher

    for serial_section in serial_sections:
        section = Section(serial_section)
        resources.sections[section.id] = section

    for serial_lecture in serial_lectures:
        lecture = Lecture(serial_lecture)
        resources.lectures[lecture.id] = lecture

        # reflect lecture association
        for teacher_id in lecture.teacher_ids:
            teacher = resources.teachers[teacher_id]
            teacher.lecture_ids.add(lecture.id)

        for section_id in lecture.section_ids:
            section = resources.sections[section_id]
            section.lecture_ids.add(lecture.id)

    for serial_elective in serial_electives:
        for course_id in serial_elective['pairedCourses']:
            course = resources.courses[course_id]
            course.elective_pair_ids.add(serial_elective['id'])

    set_lectures_noncurrency(resources)  # set lectures' noncurrency

    return resources
