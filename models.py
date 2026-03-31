from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
ATTENDANCE_STATUSES = ("Present", "Absent", "Late", "Excused")


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(64), nullable=True)
    student_year = db.Column(db.String(32), nullable=True)
    level_name = db.Column(db.String(64), nullable=False, index=True)
    parent_email = db.Column(db.String(255), nullable=True, index=True)
    parent_whatsapp = db.Column(db.String(32), nullable=True, index=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=True, index=True)

    level = db.relationship("Level", backref=db.backref("students", lazy=True))

    def __repr__(self) -> str:
        return f"<Student id={self.id} code={self.student_code} name={self.full_name}>"


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    subject_name = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    level_name = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<Teacher id={self.id} name={self.full_name}>"


class Level(db.Model):
    __tablename__ = "levels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=True, index=True)
    order_index = db.Column(db.Integer, nullable=True, index=True)
    zoom_email = db.Column(db.String(255), nullable=True)
    zoom_link = db.Column(db.String(512), nullable=True)
    zoom_meeting_id = db.Column(db.String(64), nullable=True)
    zoom_passcode = db.Column(db.String(64), nullable=True)
    homework_padlet_url = db.Column(db.String(512), nullable=True)
    announcements_padlet_url = db.Column(db.String(512), nullable=True)
    syllabus_edit_open = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false(),
    )

    teacher = db.relationship("Teacher", backref=db.backref("levels", lazy=True))

    def __repr__(self) -> str:
        return (
            f"<Level id={self.id} name={self.name} "
            f"teacher_id={self.teacher_id} order_index={self.order_index}>"
        )


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('Present', 'Absent', 'Late', 'Excused')",
            name="ck_attendance_status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=True, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    student = db.relationship("Student", backref=db.backref("attendance_records", lazy=True))
    level = db.relationship("Level", backref=db.backref("attendance_records", lazy=True))

    def __repr__(self) -> str:
        return (
            f"<Attendance id={self.id} student_id={self.student_id} "
            f"date={self.attendance_date} status={self.status}>"
        )


class StudentMonthlyNote(db.Model):
    __tablename__ = "student_monthly_notes"
    __table_args__ = (
        db.UniqueConstraint("student_id", "month_key", name="uq_student_month_note"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    month_key = db.Column(db.String(7), nullable=False, index=True)  # YYYY-MM
    note_text = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    student = db.relationship("Student", backref=db.backref("monthly_notes", lazy=True))

    def __repr__(self) -> str:
        return f"<StudentMonthlyNote student_id={self.student_id} month_key={self.month_key}>"


class ClassRecording(db.Model):
    __tablename__ = "class_recordings"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    recording_url = db.Column(db.String(1024), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False, index=True)
    summary = db.Column(db.Text, nullable=True)
    homework = db.Column(db.Text, nullable=True)

    level = db.relationship("Level", backref=db.backref("recordings", lazy=True))

    def __repr__(self) -> str:
        return f"<ClassRecording id={self.id} class_id={self.class_id} title={self.title}>"


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    resource_link = db.Column(db.String(1024), nullable=True)
    resource_file_name = db.Column(db.String(255), nullable=True)
    resource_file_path = db.Column(db.String(1024), nullable=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    level = db.relationship("Level", backref=db.backref("assignments", lazy=True))

    def __repr__(self) -> str:
        return f"<Assignment id={self.id} level_id={self.level_id} title={self.title}>"


class AssignmentSubmission(db.Model):
    __tablename__ = "assignment_submissions"
    __table_args__ = (
        db.UniqueConstraint("assignment_id", "student_id", name="uq_assignment_submission"),
    )

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    submission_text = db.Column(db.Text, nullable=True)
    submission_link = db.Column(db.String(1024), nullable=True)
    submission_file_name = db.Column(db.String(255), nullable=True)
    submission_file_path = db.Column(db.String(1024), nullable=True)
    score_value = db.Column(db.String(64), nullable=True)
    teacher_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False, default="Pending", server_default="Pending")
    submitted_at = db.Column(db.DateTime, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    assignment = db.relationship("Assignment", backref=db.backref("submissions", lazy=True, cascade="all, delete-orphan"))
    student = db.relationship("Student", backref=db.backref("assignment_submissions", lazy=True))

    def __repr__(self) -> str:
        return f"<AssignmentSubmission assignment_id={self.assignment_id} student_id={self.student_id} status={self.status}>"


class ActionLog(db.Model):
    __tablename__ = "action_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_role = db.Column(db.String(32), nullable=False, index=True)
    actor_id = db.Column(db.Integer, nullable=True, index=True)
    actor_name = db.Column(db.String(255), nullable=False, index=True)
    action_type = db.Column(db.String(64), nullable=False, index=True)
    entity_type = db.Column(db.String(64), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    entity_label = db.Column(db.String(255), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=True, index=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), index=True)

    level = db.relationship("Level", backref=db.backref("action_logs", lazy=True))

    def __repr__(self) -> str:
        return f"<ActionLog id={self.id} actor={self.actor_role}:{self.actor_name} action={self.action_type}>"


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    audience = db.Column(db.String(32), nullable=False, default="all", server_default="all", index=True)
    category = db.Column(db.String(32), nullable=False, default="general", server_default="general", index=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=True, index=True)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true(), index=True)
    starts_on = db.Column(db.Date, nullable=True, index=True)
    expires_on = db.Column(db.Date, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    level = db.relationship("Level", backref=db.backref("announcements", lazy=True))

    def __repr__(self) -> str:
        return f"<Announcement id={self.id} audience={self.audience} category={self.category} active={self.is_active}>"


class HolidayPeriod(db.Model):
    __tablename__ = "holiday_periods"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true(), index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self) -> str:
        return f"<HolidayPeriod id={self.id} title={self.title} start={self.start_date} end={self.end_date}>"


class AcademicCalendarEvent(db.Model):
    __tablename__ = "academic_calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(64), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    is_instructional = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false(),
        index=True,
    )
    sort_order = db.Column(db.Integer, nullable=False, default=0, server_default="0", index=True)
    note_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<AcademicCalendarEvent id={self.id} type={self.event_type} "
            f"title={self.title} start={self.start_date} end={self.end_date}>"
        )


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    level = db.relationship("Level", backref=db.backref("subjects", lazy=True, cascade="all, delete-orphan"))

    def __repr__(self) -> str:
        return f"<Subject id={self.id} level_id={self.level_id} name={self.name}>"


class CurriculumItem(db.Model):
    __tablename__ = "curriculum_items"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_link = db.Column(db.String(1024), nullable=True)
    visibility_scope = db.Column(
        db.String(32),
        nullable=False,
        default="student_and_teacher",
        server_default="student_and_teacher",
        index=True,
    )
    order_index = db.Column(db.Integer, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    subject = db.relationship("Subject", backref=db.backref("curriculum_items", lazy=True, cascade="all, delete-orphan"))

    def __repr__(self) -> str:
        return f"<CurriculumItem id={self.id} subject_id={self.subject_id} title={self.title}>"


class CurriculumProgress(db.Model):
    __tablename__ = "curriculum_progress"
    __table_args__ = (
        db.UniqueConstraint("level_id", "curriculum_item_id", name="uq_curriculum_progress_level_item"),
    )

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False, index=True)
    curriculum_item_id = db.Column(db.Integer, db.ForeignKey("curriculum_items.id"), nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False, default="pending", server_default="pending", index=True)
    note_text = db.Column(db.Text, nullable=True)
    completed_on = db.Column(db.Date, nullable=True, index=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    level = db.relationship("Level", backref=db.backref("curriculum_progress_rows", lazy=True, cascade="all, delete-orphan"))
    curriculum_item = db.relationship(
        "CurriculumItem",
        backref=db.backref("progress_rows", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return f"<CurriculumProgress level_id={self.level_id} item_id={self.curriculum_item_id} status={self.status}>"


class SyllabusPlanEntry(db.Model):
    __tablename__ = "syllabus_plan_entries"

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False, index=True)
    week_number = db.Column(db.Integer, nullable=True, index=True)
    session_number = db.Column(db.Integer, nullable=True, index=True)
    book_name = db.Column(db.String(255), nullable=True)
    unit_name = db.Column(db.String(255), nullable=True)
    lesson_title = db.Column(db.String(255), nullable=False)
    source_reference = db.Column(db.String(255), nullable=True)
    learning_objective = db.Column(db.Text, nullable=True)
    planned_homework = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False, default="planned", server_default="planned", index=True)
    completed_on = db.Column(db.Date, nullable=True, index=True)
    note_text = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    level = db.relationship("Level", backref=db.backref("syllabus_plan_entries", lazy=True, cascade="all, delete-orphan"))

    def __repr__(self) -> str:
        return f"<SyllabusPlanEntry id={self.id} level_id={self.level_id} week={self.week_number} session={self.session_number} title={self.lesson_title}>"


class ExamResult(db.Model):
    __tablename__ = "exam_results"
    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "exam_title",
            "subject_name",
            name="uq_exam_result_student_exam_subject",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=True, index=True)
    exam_title = db.Column(db.String(255), nullable=False, index=True)
    subject_name = db.Column(db.String(255), nullable=False, index=True)
    score_value = db.Column(db.String(64), nullable=False)
    max_score = db.Column(db.String(64), nullable=True)
    exam_date = db.Column(db.Date, nullable=True, index=True)
    notes = db.Column(db.Text, nullable=True)
    source_file_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    student = db.relationship("Student", backref=db.backref("exam_results", lazy=True))
    level = db.relationship("Level", backref=db.backref("exam_results", lazy=True))

    def __repr__(self) -> str:
        return (
            f"<ExamResult id={self.id} student_id={self.student_id} "
            f"exam_title={self.exam_title} subject={self.subject_name}>"
        )


class UpcomingExam(db.Model):
    __tablename__ = "upcoming_exams"

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    subject_name = db.Column(db.String(255), nullable=True)
    exam_date = db.Column(db.Date, nullable=False, index=True)
    exam_time = db.Column(db.String(64), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    level = db.relationship("Level", backref=db.backref("upcoming_exams", lazy=True))

    def __repr__(self) -> str:
        return f"<UpcomingExam id={self.id} level_id={self.level_id} title={self.title}>"


class StudentNameAlias(db.Model):
    __tablename__ = "student_name_aliases"
    __table_args__ = (
        db.UniqueConstraint("alias_name", "level_name", name="uq_student_name_alias_level"),
    )

    id = db.Column(db.Integer, primary_key=True)
    alias_name = db.Column(db.String(255), nullable=False, index=True)
    level_name = db.Column(db.String(128), nullable=True, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    student = db.relationship("Student", backref=db.backref("name_aliases", lazy=True))

    def __repr__(self) -> str:
        return f"<StudentNameAlias id={self.id} alias_name={self.alias_name} student_id={self.student_id}>"


class ExamImportIssue(db.Model):
    __tablename__ = "exam_import_issues"
    __table_args__ = (
        db.UniqueConstraint(
            "source_file_name",
            "alias_name",
            "level_name",
            name="uq_exam_import_issue_file_alias_level",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    source_file_name = db.Column(db.String(255), nullable=False, index=True)
    alias_name = db.Column(db.String(255), nullable=False, index=True)
    level_name = db.Column(db.String(128), nullable=True, index=True)
    exam_title = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def __repr__(self) -> str:
        return f"<ExamImportIssue id={self.id} alias_name={self.alias_name} source_file_name={self.source_file_name}>"


class ExamTemplate(db.Model):
    __tablename__ = "exam_templates"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False, index=True)
    exam_date = db.Column(db.Date, nullable=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self) -> str:
        return f"<ExamTemplate id={self.id} title={self.title}>"


class ExamTemplateBranch(db.Model):
    __tablename__ = "exam_template_branches"

    id = db.Column(db.Integer, primary_key=True)
    exam_template_id = db.Column(db.Integer, db.ForeignKey("exam_templates.id"), nullable=False, index=True)
    branch_name = db.Column(db.String(255), nullable=False)
    max_score = db.Column(db.String(64), nullable=True)
    order_index = db.Column(db.Integer, nullable=True, index=True)

    exam_template = db.relationship(
        "ExamTemplate",
        backref=db.backref("branches", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return f"<ExamTemplateBranch id={self.id} template_id={self.exam_template_id} branch={self.branch_name}>"


class ExamPublication(db.Model):
    __tablename__ = "exam_publications"

    id = db.Column(db.Integer, primary_key=True)
    exam_title = db.Column(db.String(255), unique=True, nullable=False, index=True)
    is_published = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self) -> str:
        return f"<ExamPublication id={self.id} exam_title={self.exam_title} published={self.is_published}>"


class StudentExamVisibility(db.Model):
    __tablename__ = "student_exam_visibility"
    __table_args__ = (
        db.UniqueConstraint("student_id", "exam_title", name="uq_student_exam_visibility"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    exam_title = db.Column(db.String(255), nullable=False, index=True)
    is_hidden = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    student = db.relationship("Student", backref=db.backref("exam_visibility_overrides", lazy=True))

    def __repr__(self) -> str:
        return f"<StudentExamVisibility student_id={self.student_id} exam_title={self.exam_title} hidden={self.is_hidden}>"
