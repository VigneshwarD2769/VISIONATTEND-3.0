-- VISIONATTEND student identity/attendance migration
-- Run this against the real PostgreSQL database before enabling period attendance.
-- The service currently uses section B for the supplied 3rd-year/2nd-batch cohort;
-- verify that convention against the timetable before applying in production.

ALTER TABLE students ADD COLUMN IF NOT EXISTS register_number VARCHAR(64);
ALTER TABLE students ADD COLUMN IF NOT EXISTS batch VARCHAR(32) NOT NULL DEFAULT '';

CREATE UNIQUE INDEX IF NOT EXISTS uq_students_register_number
    ON students (register_number)
    WHERE register_number IS NOT NULL;

-- Backfill existing rows when the archive already contains these students.
UPDATE students
SET register_number = '222405939',
    department = 'B.Sc Computer Science',
    year = 3,
    section = 'B',
    batch = '2nd batch'
WHERE lower(trim(name)) IN ('jeevan g', 'g jeevan')
  AND (register_number IS NULL OR register_number = '222405939');

UPDATE students
SET register_number = '222405974',
    department = 'B.Sc Computer Science',
    year = 3,
    section = 'B',
    batch = '2nd batch'
WHERE lower(trim(name)) = 'sarathi m'
  AND (register_number IS NULL OR register_number = '222405974');

UPDATE students
SET register_number = '222405983',
    department = 'B.Sc Computer Science',
    year = 3,
    section = 'B',
    batch = '2nd batch'
WHERE lower(trim(name)) = 'vigneshwar d'
  AND (register_number IS NULL OR register_number = '222405983');

-- Insert missing roster rows. This migration intentionally does not create
-- passwords: the supplied backend archive has no auth/user table or login API.
INSERT INTO students (id, student_id, name, register_number, department, year, section, batch, active)
SELECT md5(random()::text || clock_timestamp()::text), 'G Jeevan', 'Jeevan G', '222405939', 'B.Sc Computer Science', 3, 'B', '2nd batch', TRUE
WHERE NOT EXISTS (SELECT 1 FROM students WHERE register_number = '222405939');

INSERT INTO students (id, student_id, name, register_number, department, year, section, batch, active)
SELECT md5(random()::text || clock_timestamp()::text), 'Sarathi M', 'Sarathi M', '222405974', 'B.Sc Computer Science', 3, 'B', '2nd batch', TRUE
WHERE NOT EXISTS (SELECT 1 FROM students WHERE register_number = '222405974');

INSERT INTO students (id, student_id, name, register_number, department, year, section, batch, active)
SELECT md5(random()::text || clock_timestamp()::text), 'Vigneshwar D', 'Vigneshwar D', '222405983', 'B.Sc Computer Science', 3, 'B', '2nd batch', TRUE
WHERE NOT EXISTS (SELECT 1 FROM students WHERE register_number = '222405983');

-- After confirming every existing row is backfilled, enforce the invariant:
-- ALTER TABLE students ALTER COLUMN register_number SET NOT NULL;
