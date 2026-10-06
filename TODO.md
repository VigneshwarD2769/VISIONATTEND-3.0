# VISIONATTEND 3.0 Delivery Checklist

## Role-based access and demo session

- Implement a login screen with register number/student ID and password, generic invalid-credential feedback, loading state, and logout.
- Provide clearly labeled demo credentials or role quick-entry controls for Student, Faculty, and Management review.
- Keep session state in an app-level provider, never persist passwords, and show a persistent Demo mode label whenever demo data is active.
- Route users to the correct role dashboard after login and keep student, faculty, and management permissions distinct.
- Handle session expiry, unauthorized actions, offline mode, request timeout, server errors, and retry with understandable messages.

## Student read-only portal

- Provide a student home dashboard with greeting, today’s present/absent/total counts, provider-returned attendance percentage, today’s periods, enrollment state, and verification summary.
- Provide attendance views with date filters, period/subject/time/status rows, month-grouped history, and subject-wise summaries.
- Display attendance percentages from the provider and do not calculate conflicting official percentages in the client.
- Provide attendance verification details showing backend/demo AI result, RFID evidence, and final status without allowing student changes or conflict resolution.
- Provide a newest-first notifications list with an affordance to open the associated attendance record.
- Provide a read-only profile showing name, register number, course, year/section, batch, and enrollment status.

## Guided enrollment flow

- Provide eligibility/status display and safe handling for already enrolled, in progress, closed, and ineligible cases.
- Provide five guided capture steps: Front; Slight left; Slight right; Slight upward tilt; Slight downward tilt.
- Show a live camera-style preview or clearly labeled demo capture surface, pose instruction, lighting/visibility guidance, step progress, capture and retake controls, and upload/processing status.
- Provide retry after rejection and make it explicit in Demo mode that images are simulated and not uploaded or stored.
- Do not create, expose, download, or store face embeddings or official face templates in the client.

## Faculty and management attendance workspace

- Provide a staff dashboard with role label, attendance overview, today’s classes, pending verification/enrollment signals, and recent updates.
- Provide class/date/subject filters and a student list with present, absent, late, and unmarked states.
- Keep faculty scoped to assigned-class context and provide management with broader class/section filters.
- Allow faculty and management to edit attendance status only, with explicit save feedback and local demo-provider updates.
- Prevent staff from editing enrollment evidence, AI/RFID evidence, official percentages, or student identity fields.
- Include a compact audit/activity panel with current demo editor and last saved time.

## Backend-ready data boundary and routing

- Isolate all data access behind typed adapter interfaces with DemoAttendanceApi and a future authenticated HTTPS FastApiAttendanceApi.
- Use the proposed endpoint names only as configurable placeholders and document that the final FastAPI contract must be verified before activation.
- Do not connect directly to PostgreSQL, create a separate attendance database, expose raw AI scores, or leak one student’s data to another student.
- Add `public/manus-routes.json` covering `/`, `/login`, `/student`, `/student/attendance`, `/student/enrollment`, `/student/notifications`, `/student/profile`, `/staff`, `/staff/attendance`, and `/404`.

## Responsive design and handoff

- Use the approved editorial campus operations / calm utility design with warm ivory surfaces, ink text, Signal Orange brand accent, and the supplied semantic status colors.
- Provide a desktop left rail/content canvas and mobile bottom navigation/stacked cards with accessible focus states and reduced-motion support.
- Include a distinctive VISIONATTEND wordmark with signal mark, evidence rails, and persistent Demo mode pill.
- Add setup, demo credentials, API replacement points, required backend configuration, API gaps, and known limitations to the handoff documentation.
- Do not publish publicly; keep the result in Preview for review.
