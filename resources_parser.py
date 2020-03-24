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

from resources import *

from clashes import set_lectures_noncurrency


def read_json(json_file):
    '''
    Reads resources from `json_file`.

    Returns `Resources` object.
    '''
    resources = Resources()

    with open(json_file, 'r') as file:
        serial_resources = json.load(file)

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
            resources.courses[course_id].elective_pair_ids.add(
                serial_elective['id']
            )

    # set lectures noncurrency
    set_lectures_noncurrency(resources)

    return resources