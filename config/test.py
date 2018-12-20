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


SQLALCHEMY_DATABASE_URI = 'postgres://boac:boac@localhost:5432/boac_test'
DATA_LOCH_URI = 'postgres://boac:boac@localhost:5432/boac_loch_test'
DATA_LOCH_RDS_URI = 'postgres://boac:boac@localhost:5432/boac_loch_test'
TESTING = True

LOGGING_LOCATION = 'STDOUT'

ALERT_HOLDS_ENABLED = False
ALERT_INFREQUENT_ACTIVITY_ENABLED = False
ALERT_WITHDRAWAL_ENABLED = False

VUE_ENABLED = True
INDEX_HTML = 'tests/static/test-index-legacy.html'
INDEX_HTML_VUE = 'tests/static/test-index-vue.html'
VUE_PATHS = {
    '/admin': '/admin',
    r'/cohort/curated/([0-9]+).*': r'/curated_group/\1',
    '/cohorts/all': '/cohorts/all',
    r'/student/([0-9]+).*': r'/student/\1',
}
