# -----------------------------------------------------------
# This module represents University resources.
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

import numpy as np


class Room:
    """
    Represents a classroom where a lecture can be held.

    Rooms specify certain time slots when they can be used.
    """

    def __init__(self, room):
        self.id = room['id']
        self.name = room['name']
        self.capacity = room['capacity']

        # time slots when this room is available for lectures
        self.available_slots = np.array(room['availableSlots'])

    def __repr__(self):
        return (
            f'ID: {self.id}\n'
            f'Name: {self.name}\n'
            f'Capacity: {self.capacity}\n'
        )


class Course:
    """
    Represents a course offered.

    Courses impose room and time slot constraints on their lectures.
    """

    def __init__(self, course):
        self.id = course['id']
        self.course_code = course['courseCode']
        self.title = course['title']
        self.department = course['department']
        self.duration = course['duration']

        # course details
        self.theory_course_id = course['theoryCourseId']
        self.is_core_course = course['isCoreCourse']
        self.is_lab_course = True if self.theory_course_id else False

        # relationships with other offered courses
        self.elective_pair_ids = set()
        self.prerequisite_ids = set(course['prerequisiteIds'])

        # preferences of space and time for the course
        self.available_room_ids = set(course['availableRooms'])
        self.available_slots = np.array(course['availableSlots'])

    def __repr__(self):
        return (
            f'ID: {self.id}\n'
            f'Course: {self.course_code}\n'
            f'Duration: {self.duration}\n'
        )


class Teacher:
    """
    Represents a teacher assigned to lectures.

    Teachers impose room and time slot constraints on their lectures.
    """

    def __init__(self, teacher):
        self.id = teacher['id']
        self.name = teacher['name']
        self.department = teacher['department']

        # lectures assigned to this teacher
        self.lecture_ids = set()

        # preferences of space and time for this teacher
        self.available_room_ids = set(teacher['availableRooms'])
        self.available_slots = np.array(teacher['availableSlots'])

    def __repr__(self):
        return (
            f'ID: {self.id}\n'
            f'Name: {self.name}\n'
        )


class Section:
    """
    Represents a student section enrolled in lectures.

    Sections impose room constraints on thier lectures.
    """

    def __init__(self, section):
        self.id = section['id']
        self.name = section['name']
        self.batch = section['batch']
        self.department = section['department']

        # lectures enrolled
        self.lecture_ids = set()

    def __repr__(self):
        return (
            f'ID: {self.id}\n'
            f'Name: {self.name}\n'
            f'Batch: {self.batch}\n'
            f'Dept.: {self.department}\n'
        )


class Lecture:
    """
    Represents a lecture involving a course, section(s), and teacher(s).

    Lectures are scheduled according to course's duration and type.
    Constraints of involved teachers and sections are also followed.
    """

    def __init__(self, lecture):
        self.id = lecture['id']
        self.name = lecture['name']
        self.strength = lecture['strength']

        # involved entities
        self.course_id = lecture['courseId']
        self.teacher_ids = lecture['teacherIds']
        self.section_ids = lecture['atomicSectionIds']

        # clashing lectures
        self.noncurrent_lecture_ids = set()

    def __repr__(self):
        return (
            f'ID: {self.id}\n'
            f'Name: {self.name}\n'
            f'Strength: {self.strength}\n'
        )


class Resources:
    """
    Contains all the resources.
    """

    def __init__(self):
        self.rooms = {}
        self.courses = {}
        self.teachers = {}
        self.sections = {}
        self.lectures = {}

    def __repr__(self):
        return (
            f'Rooms: {len(self.rooms)}\n'
            f'Courses: {len(self.courses)}\n'
            f'Teachers: {len(self.teachers)}\n'
            f'Sections: {len(self.sections)}\n'
            f'Lectures: {len(self.lectures)}\n'
        )
