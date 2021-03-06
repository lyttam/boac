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


from boac import std_commit
from boac.models.alert import Alert
from boac.models.curated_cohort import CuratedCohort
import pytest


@pytest.mark.usefixtures('db_session')
class TestCacheUtils:
    """Test cache utils."""

    def test_creates_alert_for_midterm_grade(self, app):
        from boac.api.cache_utils import refresh_alerts
        refresh_alerts(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')['shown']
        assert 1 == len(alerts)
        assert 0 < alerts[0]['id']
        assert 'midterm' == alerts[0]['alertType']
        assert '2178_90100' == alerts[0]['key']
        assert 'BURMESE 1A midterm grade of D+.' == alerts[0]['message']

    def test_update_curated_cohort_lists(self, app):
        from boac.api.cache_utils import update_curated_cohort_lists
        cohort = CuratedCohort.query.filter_by(name='Cool Kids').first()
        cohort_id = cohort.id
        original_sids = [s.sid for s in cohort.students]
        sid_not_in_data_loch = '19040616'
        CuratedCohort.add_student(cohort_id, sid_not_in_data_loch)
        std_commit(allow_test_environment=True)
        revised_sids = [s.sid for s in CuratedCohort.find_by_id(cohort_id).students]
        assert sid_not_in_data_loch in revised_sids
        update_curated_cohort_lists()
        std_commit(allow_test_environment=True)
        final_sids = [s.sid for s in CuratedCohort.find_by_id(cohort_id).students]
        assert sid_not_in_data_loch not in final_sids
        assert set(final_sids) == set(original_sids)
