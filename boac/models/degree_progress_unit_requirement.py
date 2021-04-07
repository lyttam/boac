"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.base import Base
from boac.models.degree_progress_template import DegreeProgressTemplate


class DegreeProgressUnitRequirement(Base):
    __tablename__ = 'degree_progress_unit_requirements'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    created_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    min_units = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('degree_progress_templates.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    template = db.relationship(DegreeProgressTemplate.__name__, back_populates='unit_requirements')

    __table_args__ = (db.UniqueConstraint(
        'name',
        'template_id',
        name='degree_progress_unit_requirements_name_template_id_unique_const',
    ),)

    def __init__(self, created_by, min_units, name, template_id, updated_by):
        self.created_by = created_by
        self.min_units = min_units
        self.name = name
        self.template_id = template_id
        self.updated_by = updated_by

    def __repr__(self):
        return f"""<DegreeProgressUnitRequirement id={self.id},
                    name={self.name},
                    min_units={self.min_units},
                    template_id={self.template_id},
                    created_at={self.created_at},
                    created_by={self.created_by},
                    updated_at={self.updated_at},
                    updated_by={self.updated_by}>"""

    @classmethod
    def create(cls, created_by, min_units, name, template_id):
        unit_requirement = cls(
            created_by=created_by,
            min_units=min_units,
            name=name,
            template_id=template_id,
            updated_by=created_by,
        )
        template = DegreeProgressTemplate.find_by_id(template_id)
        template.unit_requirements.append(unit_requirement)
        std_commit()
        return unit_requirement