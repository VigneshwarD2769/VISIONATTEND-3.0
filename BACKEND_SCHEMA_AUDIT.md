# VISIONATTEND Backend Schema Audit

Audit date: 2026-10-06
Source: `VISIONATTEND3.0(1).zip` supplied with the project

## Result

The current Preview attendance tracking works for the three supplied student accounts through the isolated demo adapter. The attached archive does **not** contain a database dump, SQLite/PostgreSQL file, SQL migration, or seed data, so the real FastAPI database could not be queried from this Preview.

## Blocking schema mismatch

`backend/app/services/period_attendance.py` queries these `students` columns:

- `register_number`
- `department`
- `year`
- `section`
- `batch`
- `active`

However, `backend/app/database/models.py` defines `Student` without `register_number` and `batch`. `init_db.py` only calls `Base.metadata.create_all()`, so it cannot add those missing columns to an already-created database. As a result, the period attendance endpoints can fail when resolving a student or returning period attendance.

### Required backend migration

Before connecting the frontend to FastAPI, add and backfill the missing identity fields with a real migration. The three supplied records should be represented as:

| Name | Register number | Department | Year | Batch | Email |
| --- | --- | --- | --- | --- | --- |
| Jeevan G | `222405939` | B.Sc Computer Science | 3 | 2nd batch | `jeevang@srmasc.ac.in` |
| Sarathi M | `222405974` | B.Sc Computer Science | 3 | 2nd batch | `sarathim@srmasc.ac.in` |
| Vigneshwar D | `222405983` | B.Sc Computer Science | 3 | 2nd batch | `vigneshwar.d@srmasc.ac.in` |

Use the backend's actual `section` convention consistently. The current period service hardcodes `year = 3` and `section = 'B'`; confirm that “2nd batch” maps to section `B` before inserting timetable/attendance records.

Recommended constraints/indexes:

- `students.register_number` should be `NOT NULL`, unique, and indexed.
- Keep `students.student_id` as the backend identity used by face-recognition templates, or define a documented one-to-one mapping to register number.
- `attendance.student_ref` must reference `students.id`.
- `attendance_session` must identify the date/period/session, not remain the same generic `default` for every class period; the existing unique constraint `(student_ref, attendance_session)` is the duplicate-protection boundary.

## Frontend verification performed

The Preview demo adapter now scopes profile, attendance history, provider percentage, summary counts, notifications, evidence, enrollment progress, and staff roster entries by register number.

- Jeevan G / `222405939`: login by name succeeded; profile and **88%** attendance rendered.
- Sarathi M / `222405974`: login by name succeeded; profile and **91%** attendance rendered.
- Vigneshwar D / `222405983`: login by name succeeded; profile and **95%** attendance rendered.
- Vigneshwar’s attendance page showed scoped **95%**, **10 / 15** present-period summary, **3** review items, and 15 scoped records.

The frontend remains in Demo mode until the final authenticated FastAPI contract and base URL are supplied. It does not connect directly to PostgreSQL or store face embeddings.
