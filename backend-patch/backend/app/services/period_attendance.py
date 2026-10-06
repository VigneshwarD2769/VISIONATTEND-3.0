from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import text


DEFAULT_YEAR = 3
DEFAULT_SECTION = "B"


# ============================================================
# PERIOD CONTEXT
# ============================================================

@dataclass
class PeriodContext:
    attendance_date: date
    day_order: str
    period_number: int
    start_time: time
    end_time: time
    timetable_ref: str
    subject_code: str | None
    subject_name: str | None
    is_lab: bool


# ============================================================
# PERIOD ATTENDANCE SERVICE
# ============================================================

class PeriodAttendanceService:

    def __init__(self, session_factory):
        self.session_factory = session_factory

        # Compatibility session.
        #
        # The runtime attendance methods use fresh sessions so that
        # one failed transaction cannot poison later operations.
        self.db = session_factory()

    # ========================================================
    # INTERNAL HELPERS
    # ========================================================

    def _new_session(self):
        return self.session_factory()

    # ========================================================
    # DAY ORDER
    # ========================================================

    def get_day_order(
        self,
        requested_date: date | None = None,
    ) -> str | None:

        requested_date = requested_date or date.today()

        db = self._new_session()

        try:
            row = db.execute(
                text(
                    """
                    SELECT
                        day_order
                    FROM academic_calendar
                    WHERE calendar_date = :attendance_date
                      AND working_day = TRUE
                    LIMIT 1
                    """
                ),
                {
                    "attendance_date": requested_date,
                },
            ).mappings().first()

            if row is None:
                return None

            return row["day_order"]

        finally:
            db.close()

    # ========================================================
    # CURRENT PERIOD
    # ========================================================

    def current_period(
        self,
        when: datetime | None = None,
        year: int | None = DEFAULT_YEAR,
        section: str | None = DEFAULT_SECTION,
        class_batch: str | None = None,
    ) -> PeriodContext | None:

        when = when or datetime.now()

        requested_date = when.date()
        current_time = when.time()

        db = self._new_session()

        try:

            row = db.execute(
                text(
                    """
                    SELECT
                        ac.calendar_date,
                        ac.day_order,

                        pd.period_number,
                        pd.start_time,
                        pd.end_time,

                        ts.id AS timetable_ref,
                        ts.subject_code,
                        ts.subject_name,
                        ts.is_lab

                    FROM academic_calendar ac

                    JOIN period_definitions pd
                        ON pd.active = TRUE
                       AND :current_time >= pd.start_time
                       AND :current_time < pd.end_time

                    JOIN timetable_slots ts
                        ON ts.day_order = ac.day_order
                       AND ts.period_number = pd.period_number
                       AND (:year IS NULL OR ts.year = :year)
                       AND (:section IS NULL OR ts.section = :section)
                       AND (:class_batch IS NULL OR ts.class_batch = :class_batch)
                       AND ts.active = TRUE

                    WHERE ac.calendar_date = :attendance_date
                      AND ac.working_day = TRUE

                    ORDER BY pd.period_number

                    LIMIT 1
                    """
                ),
                {
                    "attendance_date": requested_date,
                    "current_time": current_time,
                    "year": year,
                    "section": section,
                    "class_batch": class_batch,
                },
            ).mappings().first()

            if row is None:
                return None

            return PeriodContext(
                attendance_date=row["calendar_date"],
                day_order=row["day_order"],
                period_number=row["period_number"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                timetable_ref=str(row["timetable_ref"]),
                subject_code=row["subject_code"],
                subject_name=row["subject_name"],
                is_lab=bool(row["is_lab"]),
            )

        finally:
            db.close()

    # ========================================================
    # TIMETABLE SLOT
    # ========================================================

    def _get_timetable_slot(
        self,
        day_order: str,
        period_number: int,
        year: int | None = DEFAULT_YEAR,
        section: str | None = DEFAULT_SECTION,
        class_batch: str | None = None,
    ) -> dict[str, Any] | None:

        db = self._new_session()

        try:

            row = db.execute(
                text(
                    """
                    SELECT
                        id,
                        day_order,
                        period_number,
                        course,
                        year,
                        section,
                        class_batch,
                        subject_code,
                        subject_name,
                        is_lab

                    FROM timetable_slots

                    WHERE day_order = :day_order
                      AND period_number = :period_number
                      AND (:year IS NULL OR year = :year)
                      AND (:section IS NULL OR section = :section)
                      AND (:class_batch IS NULL OR class_batch = :class_batch)
                      AND active = TRUE

                    LIMIT 1
                    """
                ),
                {
                    "day_order": day_order,
                    "period_number": period_number,
                    "year": year,
                    "section": section,
                    "class_batch": class_batch,
                },
            ).mappings().first()

            return dict(row) if row else None

        finally:
            db.close()

    # ========================================================
    # STUDENT RESOLUTION
    # ========================================================

    def _resolve_student(
        self,
        student_id: str,
    ) -> dict[str, Any] | None:

        db = self._new_session()

        try:

            # IMPORTANT:
            #
            # Current database contains register numbers such as
            # 222405939 in students.register_number.
            #
            # students.student_id currently contains values such
            # as "G Jeevan" for some existing records.
            #
            # Therefore register_number is prioritized.

            row = db.execute(
                text(
                    """
                    SELECT
                        id,
                        student_id,
                        name,
                        register_number,
                        department,
                        year,
                        section,
                        batch,
                        active

                    FROM students

                    WHERE active = TRUE
                      AND (
                            register_number = :student_id
                            OR student_id = :student_id
                            OR lower(name) = lower(:student_id)
                      )

                    ORDER BY
                        CASE
                            WHEN register_number = :student_id
                            THEN 0
                            WHEN student_id = :student_id
                            THEN 1
                            ELSE 2
                        END

                    LIMIT 1
                    """
                ),
                {
                    "student_id": student_id,
                },
            ).mappings().first()

            return dict(row) if row else None

        finally:
            db.close()

    # ========================================================
    # RECORD PRESENT
    # ========================================================

    def record_present(
        self,
        student_id: str,
        confidence: float | None = None,
        when: datetime | None = None,
    ) -> bool:

        when = when or datetime.now()

        # ----------------------------------------------------
        # Resolve student
        # ----------------------------------------------------

        student = self._resolve_student(student_id)

        if student is None:
            return False

        # ----------------------------------------------------
        # Current period
        # ----------------------------------------------------

        period = self.current_period(
            when,
            year=int(student["year"]),
            section=student["section"],
            class_batch=student.get("batch") or None,
        )

        if period is None:
            return False

        # ----------------------------------------------------
        # Verify timetable
        # ----------------------------------------------------

        timetable = self._get_timetable_slot(
            day_order=period.day_order,
            period_number=period.period_number,
            year=int(student["year"]),
            section=student["section"],
            class_batch=student.get("batch") or None,
        )

        if timetable is None:
            return False

        db = self._new_session()

        try:

            # ------------------------------------------------
            # Find the normal attendance record.
            #
            # attendance_ref is nullable and references
            # attendance.id.
            #
            # We use the student's internal students.id,
            # not the register number.
            # ------------------------------------------------

            attendance_row = db.execute(
                text(
                    """
                    SELECT
                        id

                    FROM attendance

                    WHERE student_ref = :student_ref
                      AND attendance_date::date = :attendance_date

                    ORDER BY created_at DESC

                    LIMIT 1
                    """
                ),
                {
                    "student_ref": str(student["id"]),
                    "attendance_date": period.attendance_date,
                },
            ).mappings().first()

            attendance_ref = (
                str(attendance_row["id"])
                if attendance_row
                else None
            )

            # ------------------------------------------------
            # Insert / update period attendance
            # ------------------------------------------------

            result = db.execute(
                text(
                    """
                    INSERT INTO period_attendance (
                        student_ref,
                        attendance_date,
                        day_order,
                        period_number,
                        timetable_ref,
                        attendance_ref,
                        status,
                        confidence,
                        reason,
                        marked_at,
                        finalized_at,
                        created_at,
                        updated_at
                    )

                    VALUES (
                        :student_ref,
                        :attendance_date,
                        :day_order,
                        :period_number,
                        :timetable_ref,
                        :attendance_ref,
                        'PRESENT',
                        :confidence,
                        'AI_CONFIRMED',
                        :marked_at,
                        NULL,
                        NOW(),
                        NOW()
                    )

                    ON CONFLICT (
                        student_ref,
                        period_number,
                        attendance_date
                    )

                    DO UPDATE SET

                        status =
                            CASE
                                WHEN period_attendance.status
                                    IN ('ABSENT', 'VERIFICATION_REQUIRED')
                                THEN 'PRESENT'
                                ELSE period_attendance.status
                            END,

                        confidence =
                            CASE
                                WHEN period_attendance.status
                                    IN ('ABSENT', 'VERIFICATION_REQUIRED')
                                THEN EXCLUDED.confidence
                                ELSE period_attendance.confidence
                            END,

                        reason =
                            CASE
                                WHEN period_attendance.status
                                    IN ('ABSENT', 'VERIFICATION_REQUIRED')
                                THEN 'AI_CONFIRMED'
                                ELSE period_attendance.reason
                            END,

                        marked_at =
                            CASE
                                WHEN period_attendance.status
                                    IN ('ABSENT', 'VERIFICATION_REQUIRED')
                                THEN EXCLUDED.marked_at
                                ELSE period_attendance.marked_at
                            END,

                        finalized_at = NULL,

                        attendance_ref =
                            COALESCE(
                                EXCLUDED.attendance_ref,
                                period_attendance.attendance_ref
                            ),

                        updated_at = NOW()
                    """
                ),
                {
                    "student_ref": str(student["id"]),
                    "attendance_date": period.attendance_date,
                    "day_order": period.day_order,
                    "period_number": period.period_number,
                    "timetable_ref": str(timetable["id"]),
                    "attendance_ref": attendance_ref,
                    "confidence": confidence,
                    "marked_at": when,
                },
            )

            db.commit()

            return result.rowcount > 0

        except Exception:

            db.rollback()
            raise

        finally:
            db.close()

    # ========================================================
    # FINALIZE EXPIRED PERIODS
    # ========================================================

    def finalize_expired_periods(
        self,
        when: datetime | None = None,
    ) -> int:

        when = when or datetime.now()

        requested_date = when.date()
        current_time = when.time()

        db = self._new_session()

        try:

            # ------------------------------------------------
            # Get today's academic calendar entry
            # ------------------------------------------------

            calendar = db.execute(
                text(
                    """
                    SELECT
                        calendar_date,
                        day_order,
                        working_day

                    FROM academic_calendar

                    WHERE calendar_date = :attendance_date

                    LIMIT 1
                    """
                ),
                {
                    "attendance_date": requested_date,
                },
            ).mappings().first()

            if not calendar or not calendar["working_day"]:
                return 0

            day_order = calendar["day_order"]

            # ------------------------------------------------
            # Find periods that have already ended
            # ------------------------------------------------

            expired_periods = db.execute(
                text(
                    """
                    SELECT
                        period_number,
                        start_time,
                        end_time

                    FROM period_definitions

                    WHERE active = TRUE
                      AND end_time <= :current_time

                    ORDER BY period_number
                    """
                ),
                {
                    "current_time": current_time,
                },
            ).mappings().all()

            if not expired_periods:
                return 0

            finalized_count = 0

            # ------------------------------------------------
            # Process each expired period
            # ------------------------------------------------

            for period in expired_periods:

                period_number = period["period_number"]

                # --------------------------------------------
                # Timetable slot
                # --------------------------------------------

                timetable = db.execute(
                    text(
                        """
                        SELECT
                            id,
                            subject_code,
                            subject_name,
                            is_lab

                        FROM timetable_slots

                        WHERE day_order = :day_order
                          AND period_number = :period_number
                          AND year = 3
                          AND section = 'B'
                          AND active = TRUE

                        LIMIT 1
                        """
                    ),
                    {
                        "day_order": day_order,
                        "period_number": period_number,
                    },
                ).mappings().first()

                if timetable is None:
                    continue

                timetable_ref = str(timetable["id"])

                # --------------------------------------------
                # All active students in III BSc CS Section B
                # --------------------------------------------

                students = db.execute(
                    text(
                        """
                        SELECT
                            id,
                            student_id,
                            name,
                            register_number

                        FROM students

                        WHERE active = TRUE
                          AND year = 3
                          AND section = 'B'

                        ORDER BY name
                        """
                    )
                ).mappings().all()

                for student in students:

                    student_ref = str(student["id"])

                    # ----------------------------------------
                    # Check existing period attendance
                    # ----------------------------------------

                    existing = db.execute(
                        text(
                            """
                            SELECT
                                id,
                                status

                            FROM period_attendance

                            WHERE student_ref = :student_ref
                              AND attendance_date = :attendance_date
                              AND period_number = :period_number

                            LIMIT 1
                            """
                        ),
                        {
                            "student_ref": student_ref,
                            "attendance_date": requested_date,
                            "period_number": period_number,
                        },
                    ).mappings().first()

                    # ----------------------------------------
                    # Already PRESENT
                    # ----------------------------------------

                    if existing:

                        if existing["status"] == "PRESENT":

                            result = db.execute(
                                text(
                                    """
                                    UPDATE period_attendance

                                    SET finalized_at = COALESCE(
                                            finalized_at,
                                            NOW()
                                        ),
                                        updated_at = NOW()

                                    WHERE id = :id
                                      AND finalized_at IS NULL
                                    """
                                ),
                                {
                                    "id": str(existing["id"]),
                                },
                            )

                            if result.rowcount:
                                finalized_count += result.rowcount

                            continue

                        # ------------------------------------
                        # VERIFICATION_REQUIRED
                        # ------------------------------------

                        if existing["status"] == "VERIFICATION_REQUIRED":

                            result = db.execute(
                                text(
                                    """
                                    UPDATE period_attendance

                                    SET finalized_at = NOW(),
                                        updated_at = NOW()

                                    WHERE id = :id
                                      AND finalized_at IS NULL
                                    """
                                ),
                                {
                                    "id": str(existing["id"]),
                                },
                            )

                            if result.rowcount:
                                finalized_count += result.rowcount

                            continue

                        # ------------------------------------
                        # Existing ABSENT
                        # ------------------------------------

                        if existing["status"] == "ABSENT":

                            result = db.execute(
                                text(
                                    """
                                    UPDATE period_attendance

                                    SET finalized_at = COALESCE(
                                            finalized_at,
                                            NOW()
                                        ),
                                        updated_at = NOW()

                                    WHERE id = :id
                                      AND finalized_at IS NULL
                                    """
                                ),
                                {
                                    "id": str(existing["id"]),
                                },
                            )

                            if result.rowcount:
                                finalized_count += result.rowcount

                            continue

                    # ----------------------------------------
                    # No record exists.
                    #
                    # Therefore AI never confirmed this
                    # student during the period.
                    # ----------------------------------------

                    db.execute(
                        text(
                            """
                            INSERT INTO period_attendance (
                                student_ref,
                                attendance_date,
                                day_order,
                                period_number,
                                timetable_ref,
                                attendance_ref,
                                status,
                                confidence,
                                reason,
                                marked_at,
                                finalized_at,
                                created_at,
                                updated_at
                            )

                            VALUES (
                                :student_ref,
                                :attendance_date,
                                :day_order,
                                :period_number,
                                :timetable_ref,
                                NULL,
                                'ABSENT',
                                NULL,
                                'PERIOD_FINALIZED_NO_AI_CONFIRMATION',
                                NULL,
                                NOW(),
                                NOW(),
                                NOW()
                            )

                            ON CONFLICT (
                                student_ref,
                                period_number,
                                attendance_date
                            )

                            DO NOTHING
                            """
                        ),
                        {
                            "student_ref": student_ref,
                            "attendance_date": requested_date,
                            "day_order": day_order,
                            "period_number": period_number,
                            "timetable_ref": timetable_ref,
                        },
                    )

                    finalized_count += 1

            db.commit()

            return finalized_count

        except Exception:

            db.rollback()
            raise

        finally:
            db.close()

    # ========================================================
    # TIMETABLE FOR DATE
    # ========================================================

    def periods_for_date(
        self,
        requested_date: date,
    ) -> list[dict[str, Any]]:

        db = self._new_session()

        try:

            calendar = db.execute(
                text(
                    """
                    SELECT
                        calendar_date,
                        day_order,
                        working_day,
                        special_event

                    FROM academic_calendar

                    WHERE calendar_date = :attendance_date

                    LIMIT 1
                    """
                ),
                {
                    "attendance_date": requested_date,
                },
            ).mappings().first()

            if not calendar or not calendar["working_day"]:
                return []

            rows = db.execute(
                text(
                    """
                    SELECT
                        ts.id,
                        ts.day_order,
                        ts.period_number,
                        ts.course,
                        ts.year,
                        ts.section,
                        ts.class_batch,
                        ts.subject_code,
                        ts.subject_name,
                        ts.is_lab,

                        pd.start_time,
                        pd.end_time

                    FROM timetable_slots ts

                    JOIN period_definitions pd
                        ON pd.period_number = ts.period_number
                       AND pd.active = TRUE

                    WHERE ts.day_order = :day_order
                      AND ts.year = 3
                      AND ts.section = 'B'
                      AND ts.active = TRUE

                    ORDER BY ts.period_number
                    """
                ),
                {
                    "day_order": calendar["day_order"],
                },
            ).mappings().all()

            return [
                {
                    "id": str(row["id"]),
                    "day_order": row["day_order"],
                    "period_number": row["period_number"],
                    "course": row["course"],
                    "year": row["year"],
                    "section": row["section"],
                    "class_batch": row["class_batch"],
                    "subject_code": row["subject_code"],
                    "subject_name": row["subject_name"],
                    "is_lab": bool(row["is_lab"]),
                    "start_time": (
                        row["start_time"].isoformat()
                        if row["start_time"]
                        else None
                    ),
                    "end_time": (
                        row["end_time"].isoformat()
                        if row["end_time"]
                        else None
                    ),
                }
                for row in rows
            ]

        finally:
            db.close()

    # ========================================================
    # ATTENDANCE FOR DATE
    # ========================================================

    def attendance_for_date(
        self,
        requested_date: date,
        student_id: str | None = None,
    ) -> list[dict[str, Any]]:

        db = self._new_session()

        try:

            params: dict[str, Any] = {
                "attendance_date": requested_date,
            }

            student_filter = ""

            if student_id:

                student_filter = """
                    AND (
                        s.register_number = :student_id
                        OR s.student_id = :student_id
                        OR lower(s.name) = lower(:student_id)
                    )
                """

                params["student_id"] = student_id

            rows = db.execute(
                text(
                    f"""
                    SELECT
                        pa.id,
                        pa.attendance_date,
                        pa.day_order,
                        pa.period_number,

                        pa.status,
                        pa.confidence,
                        pa.reason,

                        pa.marked_at,
                        pa.finalized_at,

                        s.id AS student_ref,
                        s.student_id,
                        s.name AS student_name,
                        s.register_number,

                        ts.subject_code,
                        ts.subject_name,
                        ts.is_lab,

                        pd.start_time,
                        pd.end_time

                    FROM period_attendance pa

                    JOIN students s
                        ON s.id = pa.student_ref

                    LEFT JOIN timetable_slots ts
                        ON ts.id = pa.timetable_ref

                    LEFT JOIN period_definitions pd
                        ON pd.period_number = pa.period_number

                    WHERE pa.attendance_date = :attendance_date

                    {student_filter}

                    ORDER BY
                        pa.period_number,
                        s.name
                    """
                ),
                params,
            ).mappings().all()

            return [
                {
                    "id": str(row["id"]),

                    "attendance_date": row["attendance_date"],
                    "day_order": row["day_order"],
                    "period_number": row["period_number"],

                    "student_ref": str(row["student_ref"]),
                    "student_id": row["student_id"],
                    "student_name": row["student_name"],
                    "register_number": row["register_number"],

                    "status": row["status"],
                    "confidence": row["confidence"],
                    "reason": row["reason"],

                    "subject_code": row["subject_code"],
                    "subject_name": row["subject_name"],
                    "is_lab": bool(row["is_lab"])
                    if row["is_lab"] is not None
                    else False,

                    "start_time": (
                        row["start_time"].isoformat()
                        if row["start_time"]
                        else None
                    ),

                    "end_time": (
                        row["end_time"].isoformat()
                        if row["end_time"]
                        else None
                    ),

                    "marked_at": row["marked_at"],
                    "finalized_at": row["finalized_at"],
                }
                for row in rows
            ]

        finally:
            db.close()

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):
        """
        Compatibility cleanup for code that owns this service
        instance directly.
        """

        try:
            self.db.close()
        except Exception:
            pass
