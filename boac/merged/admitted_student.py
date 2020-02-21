"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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

from itertools import islice

from boac.externals import data_loch
from boac.lib.util import camelize, get_benchmarker


"""Provide merged admit data from external sources."""


def get_admitted_student_by_sid(sid):
    admit = data_loch.get_admitted_student_by_sid(sid)
    if admit['current_sir']:
        _merge_student(admit)
    return {camelize(key): admit[key] for key in admit.keys()} if admit else None


def search_for_admitted_students(
    search_phrase=None,
    order_by=None,
):
    benchmark = get_benchmarker('search_for_admitted_students')
    query_tables, query_filter, query_bindings = data_loch.get_admitted_students_query(
        search_phrase=search_phrase,
    )
    sql = f"""SELECT DISTINCT(sa.cs_empl_id),
        sa.first_name,
        sa.last_name,
        sa.current_sir,
        sa.special_program_cep,
        sa.reentry_status,
        sa.first_generation_student,
        sa.urem,
        sa.application_fee_waiver_flag,
        sa.freshman_or_transfer
        {query_tables}
        {query_filter}
        ORDER BY sa.{order_by}, sa.first_name, sa.cs_empl_id"""

    benchmark('begin admit search query')
    admits = data_loch.safe_execute_rds(sql, **query_bindings)
    benchmark('end')
    return {
        'admits': [{camelize(key): row[key] for key in row.keys()} for row in islice(admits, 50)] if admits else None,
        'totalAdmitCount': len(admits),
    }


def _merge_student(admit):
    student = data_loch.get_student_by_sid(admit['sid'])
    if student:
        admit['uid'] = student['uid']