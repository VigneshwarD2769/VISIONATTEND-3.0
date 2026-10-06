# VISIONATTEND backend schema patch

This patch is based on the attached `VISIONATTEND3.0(1).zip`.

## Included

- `backend/app/database/models.py`
  - Adds `Student.register_number` as a unique indexed identity field.
  - Adds `Student.batch` as an indexed cohort field.
- `backend/app/services/period_attendance.py`
  - Uses student year, section, and batch when selecting the current period/timetable.
  - Resolves attendance by register number, backend student ID, or case-insensitive name.
  - Keeps default year 3 / section B behavior for existing staff and period endpoints.
- `backend/app/database/20261006_add_student_identity_fields.sql`
  - Adds/backfills the missing columns and inserts the three supplied students when absent.

## Important activation limitation

The supplied archive has no authentication/user table or login endpoint, and no database dump was included. This patch therefore fixes attendance identity and period selection, but it cannot by itself implement login passwords or make the existing web Preview use real FastAPI data.

To leave Demo mode, provide a reachable authenticated FastAPI base URL and a PostgreSQL database with this migration applied. The frontend project currently contains only a placeholder `FastApiAttendanceApi` and does not contain the backend source.

Before applying the migration, confirm that the institution's “2nd batch” maps to timetable `section = 'B'`. If it does not, change the seed/backfill section and timetable selection accordingly.
