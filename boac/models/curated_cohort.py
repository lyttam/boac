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


from boac import db, std_commit
from boac.merged.student import get_api_json
from boac.models.base import Base
from boac.models.db_relationships import CuratedCohortStudent
from flask import current_app as app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError


class CuratedCohort(Base):
    __tablename__ = 'student_groups'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    owner_id = db.Column(db.String(80), db.ForeignKey('authorized_users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    students = db.relationship('CuratedCohortStudent', back_populates='curated_cohort', cascade='all')

    __table_args__ = (db.UniqueConstraint(
        'owner_id',
        'name',
        name='student_groups_owner_id_name_unique_constraint',
    ),)

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    @classmethod
    def find_by_id(cls, curated_cohort_id):
        return cls.query.filter_by(id=curated_cohort_id).first()

    @classmethod
    def get_curated_cohorts_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).order_by(cls.name).all()

    @classmethod
    def create(cls, owner_id, name):
        curated_cohort = cls(name, owner_id)
        db.session.add(curated_cohort)
        std_commit()
        return curated_cohort

    @classmethod
    def add_student(cls, curated_cohort_id, sid):
        curated_cohort = cls.query.filter_by(id=curated_cohort_id).first()
        if curated_cohort:
            try:
                membership = CuratedCohortStudent(sid=sid, curated_cohort_id=curated_cohort_id)
                db.session.add(membership)
                std_commit()
            except (FlushError, IntegrityError):
                app.logger.warn(f'Database error in add_student with curated_cohort_id={curated_cohort_id}, sid {sid}')
        return curated_cohort

    @classmethod
    def add_students(cls, curated_cohort_id, sids):
        curated_cohort = cls.query.filter_by(id=curated_cohort_id).first()
        if curated_cohort:
            try:
                for sid in set(sids):
                    membership = CuratedCohortStudent(sid=sid, curated_cohort_id=curated_cohort_id)
                    db.session.add(membership)
                std_commit()
            except (FlushError, IntegrityError):
                app.logger.warn(f'Database error in add_students with curated_cohort_id={curated_cohort_id}, sid {sid}')
        return curated_cohort

    @classmethod
    def remove_student(cls, curated_cohort_id, sid):
        curated_cohort = cls.find_by_id(curated_cohort_id)
        membership = CuratedCohortStudent.query.filter_by(sid=sid, curated_cohort_id=curated_cohort_id).first()
        if curated_cohort and membership:
            db.session.delete(membership)
            std_commit()

    @classmethod
    def rename(cls, curated_cohort_id, name):
        curated_cohort = cls.query.filter_by(id=curated_cohort_id).first()
        curated_cohort.name = name
        std_commit()
        return curated_cohort

    @classmethod
    def delete(cls, curated_cohort_id):
        curated_cohort = cls.query.filter_by(id=curated_cohort_id).first()
        if curated_cohort:
            db.session.delete(curated_cohort)
            std_commit()

    def to_api_json(self, sids_only=False, include_students=True):
        api_json = {
            'id': self.id,
            'ownerId': self.owner_id,
            'name': self.name,
            'studentCount': len(self.students),
        }
        if sids_only:
            api_json['students'] = [{'sid': s.sid} for s in self.students]
        elif include_students:
            api_json['students'] = get_api_json([s.sid for s in self.students])
        return api_json
