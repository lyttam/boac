"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from functools import wraps
import json
from boac.lib import util
from boac.lib.berkeley import get_dept_codes
from boac.merged import athletics
from boac.merged import calnet
from boac.merged.student import query_students
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from flask import current_app as app, request
from flask_login import current_user

"""Utility module containing standard API-feed translations of data objects."""


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        auth_key = app.config['API_KEY']
        login_ok = current_user.is_authenticated and current_user.is_admin
        api_key_ok = auth_key and (request.headers.get('App-Key') == auth_key)
        if login_ok or api_key_ok:
            return func(*args, **kw)
        else:
            app.logger.warn(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def add_alert_counts(alert_counts, students):
    students_by_sid = {student['sid']: student for student in students}
    for alert_count in alert_counts:
        student = students_by_sid.get(alert_count['sid'], None)
        if student:
            student.update({
                'alertCount': alert_count['alertCount'],
            })
    return students


def authorized_users_api_feed(users, sort_by='lastName'):
    if not users:
        return []
    profiles = []
    for user in users:
        profile = calnet.get_calnet_user_for_uid(app, user.uid)
        profile.update({
            'is_admin': user.is_admin,
            'departments': {},
        })
        for m in user.department_memberships:
            profile['departments'].update({
                m.university_dept.dept_code: {
                    'isAdvisor': m.is_advisor,
                    'isDirector': m.is_director,
                },
            })
        profiles.append(profile)
    return sorted(profiles, key=lambda p: p.get(sort_by) or '')


def canvas_course_api_feed(course):
    return {
        'canvasCourseId': course.get('canvas_course_id'),
        'courseName': course.get('canvas_course_name'),
        'courseCode': course.get('canvas_course_code'),
        'courseTerm': course.get('canvas_course_term'),
    }


def canvas_courses_api_feed(courses):
    if not courses:
        return []
    return [canvas_course_api_feed(course) for course in courses]


def decorate_cohort(
    cohort,
    order_by=None,
    offset=0,
    limit=50,
    include_students=True,
    include_profiles=False,
    include_alerts_for_uid=None,
):
    criteria = cohort if isinstance(cohort.filter_criteria, dict) else json.loads(cohort.filter_criteria)
    advisor_ldap_uids = util.get(criteria, 'advisorLdapUids')
    if not isinstance(advisor_ldap_uids, list):
        advisor_ldap_uids = [advisor_ldap_uids] if advisor_ldap_uids else None
    # In odd circumstances we override the cohort's actual name
    cohort_name = cohort.label
    current_user_uid = current_user.uid if current_user and hasattr(current_user, 'uid') else None
    decorated = {
        'id': cohort.id,
        'code': cohort.id,
        'isOwnedByCurrentUser': current_user_uid in [o.uid for o in cohort.owners],
        'label': cohort_name,
        'name': cohort_name,
        'owners': [user.uid for user in cohort.owners],
    }
    gpa_ranges = util.get(criteria, 'gpaRanges', [])
    group_codes = util.get(criteria, 'groupCodes', [])
    levels = util.get(criteria, 'levels', [])
    majors = util.get(criteria, 'majors', [])
    unit_ranges = util.get(criteria, 'unitRanges', [])
    in_intensive_cohort = util.to_bool_or_none(util.get(criteria, 'inIntensiveCohort'))
    is_inactive_asc = util.get(criteria, 'isInactiveAsc')
    team_groups = athletics.get_team_groups(group_codes) if group_codes else []
    decorated.update({
        'filterCriteria': {
            'advisorLdapUids': advisor_ldap_uids,
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'levels': levels,
            'majors': majors,
            'unitRanges': unit_ranges,
            'inIntensiveCohort': in_intensive_cohort,
            'isInactiveAsc': is_inactive_asc,
        },
        'teamGroups': team_groups,
    })

    if not include_students and not include_alerts_for_uid and cohort.student_count is not None:
        # No need for a students query; return the database-stashed student count.
        decorated.update({
            'totalStudentCount': cohort.student_count,
        })
        return decorated
    owner = cohort.owners[0] if len(cohort.owners) else None
    if owner and 'UWASC' in get_dept_codes(owner):
        is_active_asc = not is_inactive_asc
    else:
        is_active_asc = None if is_inactive_asc is None else not is_inactive_asc
    results = query_students(
        include_profiles=(include_students and include_profiles),
        advisor_ldap_uids=advisor_ldap_uids,
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=is_active_asc,
        levels=levels,
        majors=majors,
        unit_ranges=unit_ranges,
        order_by=order_by,
        offset=offset,
        limit=limit,
        sids_only=not include_students,
    )
    if results:
        # If the cohort is newly created or a cache refresh is underway, store the student count in the database
        # to save future queries.
        if cohort.student_count is None:
            cohort.update_student_count(results['totalStudentCount'])
        decorated.update({
            'totalStudentCount': results['totalStudentCount'],
        })
        if include_students:
            decorated.update({
                'students': results['students'],
            })
        if include_alerts_for_uid:
            viewer = AuthorizedUser.find_by_uid(include_alerts_for_uid)
            if viewer:
                alert_counts = Alert.current_alert_counts_for_sids(viewer.id, results['sids'])
                decorated.update({
                    'alerts': alert_counts,
                })
    return decorated


def sis_enrollment_class_feed(enrollment):
    return {
        'displayName': enrollment['sis_course_name'],
        'title': enrollment['sis_course_title'],
        'canvasSites': [],
        'sections': [],
    }


def sis_enrollment_section_feed(enrollment):
    section_data = enrollment.get('classSection', {})
    grades = enrollment.get('grades', [])
    grading_basis = enrollment.get('gradingBasis', {}).get('code')
    return {
        'ccn': section_data.get('id'),
        'component': section_data.get('component', {}).get('code'),
        'sectionNumber': section_data.get('number'),
        'enrollmentStatus': enrollment.get('enrollmentStatus', {}).get('status', {}).get('code'),
        'units': enrollment.get('enrolledUnits', {}).get('taken'),
        'gradingBasis': translate_grading_basis(grading_basis),
        'grade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'OFFL'), None),
        'midtermGrade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'MID'), None),
        'primary': False if grading_basis == 'NON' else True,
    }


def sort_students_by_name(students):
    return sorted(students, key=lambda s: (s['lastName'], s['firstName']))


def strip_analytics(student_term_data):
    if student_term_data.get('analytics'):
        del student_term_data['analytics']
    # The enrolled units count is the one piece of term data we want to preserve.
    if student_term_data.get('term'):
        student_term_data['term'] = {'enrolledUnits': student_term_data['term'].get('enrolledUnits')}
    return student_term_data


def translate_grading_basis(code):
    bases = {
        'CNC': 'C/NC',
        'EPN': 'P/NP',
        'ESU': 'S/U',
        'GRD': 'Letter',
        'LAW': 'Law',
        'PNP': 'P/NP',
        'SUS': 'S/U',
    }
    return bases.get(code) or code


def can_current_user_view_dept(dept_code):
    return current_user.is_admin or dept_code in get_dept_codes(current_user)


def is_current_user_asc_affiliated():
    return 'UWASC' in get_dept_codes(current_user)
