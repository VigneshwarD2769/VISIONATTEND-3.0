from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.core import Base


# ================================================================
# STUDENT
# ================================================================

class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    student_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(180),
    )

    register_number: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    department: Mapped[str] = mapped_column(
        String(120),
    )

    year: Mapped[int] = mapped_column(
        Integer,
    )

    section: Mapped[str] = mapped_column(
        String(32),
    )

    batch: Mapped[str] = mapped_column(
        String(32),
        default="",
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    attendance: Mapped[list["Attendance"]] = relationship(
        back_populates="student",
    )

    face_templates: Mapped[list["FaceTemplate"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    presence_sessions: Mapped[list["PresenceSession"]] = relationship(
        back_populates="student",
    )


# ================================================================
# FACE TEMPLATE
# ================================================================

class FaceTemplate(Base):
    __tablename__ = "face_templates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    student_ref: Mapped[str] = mapped_column(
        ForeignKey(
            "students.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    embedding: Mapped[bytes] = mapped_column(
        LargeBinary,
    )

    model_version: Mapped[str] = mapped_column(
        String(120),
    )

    source_sample: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    student: Mapped[Student] = relationship(
        back_populates="face_templates",
    )


# ================================================================
# CAMERA
# ================================================================

class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(20),
    )

    source_uri: Mapped[str] = mapped_column(
        Text,
    )

    location: Mapped[str] = mapped_column(
        String(180),
        default="",
    )

    room: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    direction: Mapped[str] = mapped_column(
        String(20),
        default="ENTRY",
        index=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ================================================================
# ATTENDANCE
# ================================================================

class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    student_ref: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        index=True,
    )

    camera_ref: Mapped[str | None] = mapped_column(
        ForeignKey("cameras.id"),
        nullable=True,
    )

    attendance_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    attendance_session: Mapped[str] = mapped_column(
        String(120),
        default="default",
        index=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
    )

    track_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    reason: Mapped[str] = mapped_column(
        String(120),
    )

    student: Mapped[Student] = relationship(
        back_populates="attendance",
    )

    __table_args__ = (
        UniqueConstraint(
            "student_ref",
            "attendance_session",
            name="uq_student_attendance_session",
        ),
    )


# ================================================================
# ATTENDANCE EVENT
# ================================================================

class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    student_ref: Mapped[str | None] = mapped_column(
        ForeignKey("students.id"),
        nullable=True,
        index=True,
    )

    camera_ref: Mapped[str | None] = mapped_column(
        ForeignKey("cameras.id"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    track_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reason: Mapped[str] = mapped_column(
        String(180),
    )

    session_name: Mapped[str] = mapped_column(
        String(120),
        default="default",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )


# ================================================================
# UNKNOWN DETECTION
# ================================================================

class UnknownDetection(Base):
    """
    Represents an unrecognized person detected by VISIONATTEND.

    One database row represents one tracked unknown person.

    Lifecycle:

        UNKNOWN detected
             ↓
        OPEN
             ↓
        update last_seen_at
             ↓
        update duration
             ↓
        person disappears
             ↓
        CLOSED
    """

    __tablename__ = "unknown_detections"

    # PostgreSQL column:
    # id | uuid | not null | gen_random_uuid()

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # PostgreSQL:
    # camera_ref | character varying | nullable

    camera_ref: Mapped[str | None] = mapped_column(
        ForeignKey(
            "cameras.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # PostgreSQL:
    # room | character varying(100)

    room: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # PostgreSQL:
    # track_id | character varying(100)

    track_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # PostgreSQL:
    # first_seen_at | timestamp with time zone | not null

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # PostgreSQL:
    # last_seen_at | timestamp with time zone | not null

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # PostgreSQL:
    # duration_seconds | double precision

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # PostgreSQL:
    # recognition_confidence | double precision

    recognition_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # PostgreSQL:
    # reason | character varying(100)

    reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # PostgreSQL:
    # status | character varying(30)
    # DEFAULT 'OPEN'

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="OPEN",
        index=True,
    )

    # PostgreSQL:
    # created_at | timestamp with time zone
    # DEFAULT now()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # PostgreSQL:
    # updated_at | timestamp with time zone
    # DEFAULT now()

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ================================================================
# PRESENCE SESSION
# ================================================================

class PresenceSession(Base):
    """
    Represents one continuous period during which a student
    is physically inside a monitored room or designated area.

    Lifecycle:

        ENTRY camera
            ↓
        INSIDE
            ↓
        EXIT camera
            ↓
        COMPLETED
            ↓
        duration_seconds
    """

    __tablename__ = "presence_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    student_ref: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        index=True,
    )

    room: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
        index=True,
    )

    entry_camera_ref: Mapped[str | None] = mapped_column(
        ForeignKey("cameras.id"),
        nullable=True,
    )

    exit_camera_ref: Mapped[str | None] = mapped_column(
        ForeignKey("cameras.id"),
        nullable=True,
    )

    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )

    exited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="INSIDE",
        index=True,
    )

    entry_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    exit_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    entry_track_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    exit_track_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    student: Mapped[Student] = relationship(
        back_populates="presence_sessions",
    )


# ================================================================
# SYSTEM LOG
# ================================================================

class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    level: Mapped[str] = mapped_column(
        String(20),
        index=True,
    )

    component: Mapped[str] = mapped_column(
        String(80),
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
