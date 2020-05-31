from itertools import combinations

from resources import Resources


def set_lectures_noncurrency(resources: Resources):
    """
    Add clashing lectures to `noncurrentLectures` set.
    """

    _set_teachers_noncurrency(resources.teachers, resources.lectures)

    _set_sections_noncurrency(resources.sections, resources.lectures, resources.courses)


def _set_teachers_noncurrency(teachers, lectures):
    """
    Checks if two lectures share a common teacher.
    """
    for teacher in teachers.values():

        # get every combo of two lectures
        for lecture1_id, lecture2_id in combinations(teacher.lecture_ids, 2):
            lecture1, lecture2 = lectures[lecture1_id], lectures[lecture2_id]

            lecture1.noncurrent_lecture_ids.add(lecture2_id)
            lecture2.noncurrent_lecture_ids.add(lecture1_id)


def _set_sections_noncurrency(sections, lectures, courses):
    """
    Checks if two lectures share a common section.
    """
    for section in sections.values():

        # get every combo of two lectures
        for lecture1_id, lecture2_id in combinations(section.lecture_ids, 2):
            lecture1, lecture2 = lectures[lecture1_id], lectures[lecture2_id]

            # check if an elective or prerequisite relation exists
            if(
                lecture1_id in lecture2.noncurrent_lecture_ids or
                _prerequisite_lectures(lecture1, lecture2, courses) or
                _elective_lectures(lecture1, lecture2, courses)
            ):
                continue
            lecture1.noncurrent_lecture_ids.add(lecture2_id)
            lecture2.noncurrent_lecture_ids.add(lecture1_id)


def _prerequisite_lectures(lecture1, lecture2, courses):
    """
    Checks if two lectures share a prerequisite relation
    """
    course1, course2 = courses[lecture1.course_id], courses[lecture2.course_id]

    # if it's a lab course, get its theory course instead
    if course1.is_lab_course:
        course1 = courses[course1.theory_course_id]
    if course2.is_lab_course:
        course2 = courses[course2.theory_course_id]

    # check whether one is a prerequisite of the other
    return(
        course1.id in course2.prerequisite_ids or
        course2.id in course1.prerequisite_ids
    )


def _elective_lectures(lecture1, lecture2, courses):
    """
    Checks if two lectures share a common elective pairing
    """
    course1, course2 = courses[lecture1.course_id], courses[lecture2.course_id]

    # return True if a common pairing exists, False otherwise.
    return not (course1.elective_pair_ids.isdisjoint(course2.elective_pair_ids))
