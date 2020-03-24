

from itertools import combinations

from resources import Resources


def set_lectures_noncurrency(resources: Resources):
    '''
    Add clashing lectures to `noncurrentLectures` set.
    '''

    # check noncurrency for common teacher(s)
    _set_teachers_noncurrency(resources.teachers, resources.lectures)

    # check noncurrency for common section(s)
    _set_sections_noncurrency(resources.sections, resources.lectures, resources.courses)


def _set_teachers_noncurrency(teachers, lectures):
    '''
    Checks if two lectures share a common teacher.
    '''
    for teacher in teachers.values():
        # get every combination of two lectures
        for lectureId1, lectureId2 in combinations(teacher.lecture_ids, 2):

            lecture1, lecture2 = lectures[lectureId1], lectures[lectureId2]

            lecture1.noncurrent_lecture_ids.add(lectureId2)
            lecture2.noncurrent_lecture_ids.add(lectureId1)


def _set_sections_noncurrency(sections, lectures, courses):
    '''
    Checks if two lectures share a common section.
    '''
    for section in sections.values():

        # get every combination of two lectures
        for lectureId1, lectureId2 in combinations(section.lecture_ids, 2):

            lecture1, lecture2 = lectures[lectureId1], lectures[lectureId2]

            # check whether the two lectures are elective pairs or prerequisite
            if(
                lecture1 in lecture2.noncurrent_lecture_ids
                or lecture2 in lecture1.noncurrent_lecture_ids
                or _prerequisite_lectures(lecture1, lecture2, courses)
                or _elective_lectures(lecture1, lecture2, courses)
            ):
                continue

            lecture1.noncurrent_lecture_ids.add(lectureId2)
            lecture2.noncurrent_lecture_ids.add(lectureId1)

def _prerequisite_lectures(lecture1, lecture2, courses):
    '''
    Checks if two lectures share a prerequisite relation
    '''
    courseId1, courseId2 = lecture1.course_id, lecture2.course_id

    # if course is a lab course, get its theory id instead
    if(courses[courseId1].is_lab_course):
        courseId1 = courses[courseId1].theory_course_id

    if(courses[courseId2].is_lab_course):
        courseId2 = courses[courseId2].theory_course_id

    # check whether one of them is a prerequisite of the other
    return (
        courseId1 in courses[courseId2].prerequisite_ids
        or courseId2 in courses[courseId1].prerequisite_ids
    )

def _elective_lectures(lecture1, lecture2, courses):
    '''
    Checks if two lectures share a common elective pairing
    '''
    course1, course2 = courses[lecture1.course_id], courses[lecture2.course_id]

    # return True if a common pairing exists, False otherwise.
    return not(
        course1.elective_pair_ids.isdisjoint(course2.elective_pair_ids)
    )
