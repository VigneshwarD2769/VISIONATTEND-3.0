# VISIONATTEND 3.0 MVP Handoff

## What is implemented

This preview is a mobile-first responsive Manus-hosted web app for Quantum Crew with three demo roles:

- **Student:** personal dashboard, attendance history and summaries, verification evidence detail, notifications, read-only profile, and five-step face self-enrollment guidance.
- **Faculty:** staff dashboard and attendance workspace scoped to assigned classes.
- **Management:** staff dashboard and broader attendance workspace across the demo class set.

Faculty and management can edit attendance status only. Student identity, enrollment evidence, AI/RFID evidence, and official percentages are read-only. A persistent **Demo mode** label appears throughout the authenticated app.

## Preview access

The app uses demo credentials because no production backend API base URL or final contract was provided:

| Role | ID | Password |
| --- | --- | --- |
| Student | `QC2024A001` | `student123` |
| Faculty | `FAC-104` | `faculty123` |
| Management | `MGT-001` | `manage123` |

The login screen also includes role preview buttons that fill these credentials without exposing any production account data.

## Local setup

From the project directory:

```bash
cd /home/ubuntu/visionattend
pnpm check
pnpm dev
```

The WebDev runtime uses port 3000. The app is frontend-driven for the current preview and does not require a database. The managed project retains the server capability for the future authenticated backend adapter.

## API integration boundary

All UI data is accessed through `client/src/lib/attendanceApi.ts`. The current default is `DemoAttendanceApi` backed by `client/src/lib/demoData.ts`. A `FastApiAttendanceApi` placeholder is present and is selected only when `VITE_VISIONATTEND_API_BASE_URL` is configured.

Before activation, verify the real FastAPI contract for:

- `POST /auth/login`
- `POST /enrollment/start`, `/enrollment/images`, `/enrollment/submit`, `/enrollment/retry`
- `GET /enrollment/status`
- `GET /students/me`
- `GET /attendance/today`, `/attendance/history`, `/attendance/periods`, `/attendance/summary`
- `GET /notifications`
- `GET /attendance/{id}/evidence`
- Staff attendance read/update endpoints and their role authorization behavior.

The final integration must use authenticated HTTPS APIs only. The app must not connect directly to PostgreSQL, create an attendance database, calculate conflicting official percentages, store face embeddings/templates, expose raw AI scores, or let one student view another student’s data.

## Required backend configuration before production integration

Provide the final API base URL, OpenAPI/contract details, authentication and refresh/session scheme, role claims for faculty and management, CORS policy, enrollment multipart upload format, upload retry/idempotency semantics, staff attendance-edit permissions, and the safe user-facing status/error payloads.

For the browser camera flow, confirm the required permissions and upload endpoint behavior. The current preview intentionally uses a camera-style demo surface and never uploads or stores an image.

## Known limitations

- Demo credentials and sample data are not real attendance.
- The FastAPI adapter is a typed connection boundary, not a completed production integration.
- Browser camera capture is represented as guided demo UI until the finalized enrollment upload contract is supplied.
- No public deployment has been performed.
- Production readiness, legal compliance, and scale characteristics have not been claimed or verified.
