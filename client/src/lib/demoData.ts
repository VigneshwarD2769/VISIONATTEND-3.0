export type Role = "student" | "faculty" | "management";
export type AttendanceStatus = "present" | "absent" | "late" | "unmarked";
export type EnrollmentState =
  | "approved"
  | "in-progress"
  | "submitted"
  | "validation"
  | "rejected"
  | "not-started"
  | "closed"
  | "ineligible";

export type DemoUser = {
  id: string;
  password: string;
  role: Role;
  name: string;
  shortName: string;
  subtitle: string;
};

export type UserProfile = {
  name: string;
  registerNumber: string;
  email: string;
  course: string;
  yearSection: string;
  batch: string;
  role: Role;
  enrollmentStatus: EnrollmentState;
};

export type AttendanceRecord = {
  id: string;
  date: string;
  subject: string;
  code: string;
  period: string;
  time: string;
  room: string;
  status: AttendanceStatus;
  markedBy: string;
  hasEvidence?: boolean;
};

export type SubjectSummary = {
  subject: string;
  code: string;
  present: number;
  total: number;
  percentage: number;
  tone: "green" | "amber" | "red";
};

export type VerificationEvidence = {
  attendanceId: string;
  aiResult: "Verified" | "Needs review" | "Not available";
  rfidResult: "Verified" | "Not detected" | "Not available";
  finalStatus: "Confirmed present" | "Confirmed absent" | "Manual review";
  recordedAt: string;
  note: string;
};

export type AppNotification = {
  id: string;
  title: string;
  body: string;
  time: string;
  tone: "orange" | "green" | "gold" | "gray";
  attendanceId?: string;
  unread?: boolean;
};

export type EnrollmentInfo = {
  state: EnrollmentState;
  label: string;
  detail: string;
  currentStep: number;
  totalSteps: number;
  lastUpdated: string;
  retryAvailable: boolean;
  eligibilityNote: string;
};

export type ClassRoster = {
  classId: string;
  className: string;
  subject: string;
  code: string;
  time: string;
  room: string;
  date: string;
  students: {
    id: string;
    name: string;
    registerNumber: string;
    status: AttendanceStatus;
    verification: "Verified" | "Needs review" | "Not available";
  }[];
};

export const demoUsers: DemoUser[] = [
  {
    id: "QC2024A001",
    password: "student123",
    role: "student",
    name: "Maya Rao",
    shortName: "MR",
    subtitle: "B.Tech Computer Science · Section A",
  },
  {
    id: "FAC-104",
    password: "faculty123",
    role: "faculty",
    name: "Dr. Ananya Menon",
    shortName: "AM",
    subtitle: "Faculty · Computer Science",
  },
  {
    id: "MGT-001",
    password: "manage123",
    role: "management",
    name: "Arjun Krishnan",
    shortName: "AK",
    subtitle: "Management · Academic operations",
  },
];

export const studentProfile: UserProfile = {
  name: "Maya Rao",
  registerNumber: "QC2024A001",
  email: "maya.rao@quantumcrew.edu",
  course: "B.Tech Computer Science",
  yearSection: "Year 2 · Section A",
  batch: "2024–2028",
  role: "student",
  enrollmentStatus: "in-progress",
};

export const todayPeriods: AttendanceRecord[] = [
  {
    id: "att-1001",
    date: "2026-10-06",
    subject: "Data Structures",
    code: "CS204",
    period: "01",
    time: "09:00 – 09:50",
    room: "Lab 2 · East Wing",
    status: "present",
    markedBy: "Dr. Ananya Menon",
    hasEvidence: true,
  },
  {
    id: "att-1002",
    date: "2026-10-06",
    subject: "Computer Networks",
    code: "CS206",
    period: "02",
    time: "10:00 – 10:50",
    room: "Room 204",
    status: "present",
    markedBy: "Prof. V. Iyer",
    hasEvidence: true,
  },
  {
    id: "att-1003",
    date: "2026-10-06",
    subject: "Operating Systems",
    code: "CS208",
    period: "03",
    time: "11:10 – 12:00",
    room: "Room 108",
    status: "absent",
    markedBy: "Prof. N. Shah",
    hasEvidence: false,
  },
  {
    id: "att-1004",
    date: "2026-10-06",
    subject: "Design Studio",
    code: "DS201",
    period: "04",
    time: "13:30 – 14:20",
    room: "Studio 1",
    status: "present",
    markedBy: "Ms. Ritu Jain",
    hasEvidence: true,
  },
  {
    id: "att-1005",
    date: "2026-10-06",
    subject: "Professional Skills",
    code: "PS202",
    period: "05",
    time: "14:30 – 15:20",
    room: "Room 301",
    status: "present",
    markedBy: "Mr. Joseph George",
    hasEvidence: true,
  },
];

export const historyRecords: AttendanceRecord[] = [
  ...todayPeriods,
  { id: "att-0999", date: "2026-10-05", subject: "Data Structures", code: "CS204", period: "01", time: "09:00 – 09:50", room: "Lab 2", status: "present", markedBy: "Dr. Ananya Menon", hasEvidence: true },
  { id: "att-0998", date: "2026-10-05", subject: "Computer Networks", code: "CS206", period: "02", time: "10:00 – 10:50", room: "Room 204", status: "present", markedBy: "Prof. V. Iyer", hasEvidence: true },
  { id: "att-0997", date: "2026-10-04", subject: "Operating Systems", code: "CS208", period: "03", time: "11:10 – 12:00", room: "Room 108", status: "late", markedBy: "Prof. N. Shah", hasEvidence: true },
  { id: "att-0996", date: "2026-10-04", subject: "Design Studio", code: "DS201", period: "04", time: "13:30 – 14:20", room: "Studio 1", status: "present", markedBy: "Ms. Ritu Jain", hasEvidence: true },
  { id: "att-0995", date: "2026-10-03", subject: "Professional Skills", code: "PS202", period: "05", time: "14:30 – 15:20", room: "Room 301", status: "present", markedBy: "Mr. Joseph George", hasEvidence: true },
  { id: "att-0994", date: "2026-10-02", subject: "Data Structures", code: "CS204", period: "01", time: "09:00 – 09:50", room: "Lab 2", status: "absent", markedBy: "Dr. Ananya Menon", hasEvidence: false },
  { id: "att-0993", date: "2026-10-01", subject: "Computer Networks", code: "CS206", period: "02", time: "10:00 – 10:50", room: "Room 204", status: "present", markedBy: "Prof. V. Iyer", hasEvidence: true },
  { id: "att-0992", date: "2026-09-30", subject: "Operating Systems", code: "CS208", period: "03", time: "11:10 – 12:00", room: "Room 108", status: "present", markedBy: "Prof. N. Shah", hasEvidence: true },
  { id: "att-0991", date: "2026-09-29", subject: "Design Studio", code: "DS201", period: "04", time: "13:30 – 14:20", room: "Studio 1", status: "present", markedBy: "Ms. Ritu Jain", hasEvidence: true },
  { id: "att-0990", date: "2026-09-29", subject: "Professional Skills", code: "PS202", period: "05", time: "14:30 – 15:20", room: "Room 301", status: "late", markedBy: "Mr. Joseph George", hasEvidence: true },
];

export const subjectSummaries: SubjectSummary[] = [
  { subject: "Data Structures", code: "CS204", present: 22, total: 24, percentage: 92, tone: "green" },
  { subject: "Computer Networks", code: "CS206", present: 20, total: 23, percentage: 87, tone: "green" },
  { subject: "Operating Systems", code: "CS208", present: 18, total: 22, percentage: 82, tone: "amber" },
  { subject: "Design Studio", code: "DS201", present: 25, total: 26, percentage: 96, tone: "green" },
  { subject: "Professional Skills", code: "PS202", present: 21, total: 24, percentage: 88, tone: "green" },
];

export const notifications: AppNotification[] = [
  { id: "n-1", title: "Attendance updated", body: "Data Structures · Period 01 was marked present.", time: "18 min ago", tone: "green", attendanceId: "att-1001", unread: true },
  { id: "n-2", title: "Absence recorded", body: "Operating Systems · Period 03 needs your attention.", time: "2 hr ago", tone: "orange", attendanceId: "att-1003", unread: true },
  { id: "n-3", title: "Enrollment review in progress", body: "Your face self-enrollment is being checked by the backend.", time: "Yesterday", tone: "gold", unread: false },
  { id: "n-4", title: "Monthly attendance ready", body: "September attendance summary is available to view.", time: "Sep 30", tone: "gray", unread: false },
];

export const verificationByAttendance: Record<string, VerificationEvidence> = {
  "att-1001": { attendanceId: "att-1001", aiResult: "Verified", rfidResult: "Verified", finalStatus: "Confirmed present", recordedAt: "09:52 · 06 Oct 2026", note: "Both verification signals were returned as verified by the attendance backend." },
  "att-1003": { attendanceId: "att-1003", aiResult: "Not available", rfidResult: "Not detected", finalStatus: "Confirmed absent", recordedAt: "12:02 · 06 Oct 2026", note: "No verification evidence was attached to this attendance record." },
  "att-0997": { attendanceId: "att-0997", aiResult: "Verified", rfidResult: "Verified", finalStatus: "Confirmed present", recordedAt: "11:14 · 04 Oct 2026", note: "Late arrival was retained as returned by the backend." },
};

export const enrollmentInfo: EnrollmentInfo = {
  state: "in-progress",
  label: "Face enrollment in progress",
  detail: "2 of 5 guided captures are ready for backend review.",
  currentStep: 2,
  totalSteps: 5,
  lastUpdated: "Updated 11 minutes ago",
  retryAvailable: false,
  eligibilityNote: "Eligible for initial enrollment. Your official status is decided by the VISIONATTEND backend.",
};

export const staffClasses: ClassRoster[] = [
  {
    classId: "class-cs204-a",
    className: "Year 2 · Section A",
    subject: "Data Structures",
    code: "CS204",
    time: "09:00 – 09:50",
    room: "Lab 2 · East Wing",
    date: "06 Oct 2026",
    students: [
      { id: "s1", name: "Maya Rao", registerNumber: "QC2024A001", status: "present", verification: "Verified" },
      { id: "s2", name: "Ishaan Mehta", registerNumber: "QC2024A002", status: "present", verification: "Verified" },
      { id: "s3", name: "Nivedita Paul", registerNumber: "QC2024A003", status: "late", verification: "Needs review" },
      { id: "s4", name: "Kabir Joshi", registerNumber: "QC2024A004", status: "absent", verification: "Not available" },
      { id: "s5", name: "Tara Menon", registerNumber: "QC2024A005", status: "unmarked", verification: "Not available" },
    ],
  },
  {
    classId: "class-cs206-a",
    className: "Year 2 · Section A",
    subject: "Computer Networks",
    code: "CS206",
    time: "10:00 – 10:50",
    room: "Room 204",
    date: "06 Oct 2026",
    students: [
      { id: "s1", name: "Maya Rao", registerNumber: "QC2024A001", status: "present", verification: "Verified" },
      { id: "s2", name: "Ishaan Mehta", registerNumber: "QC2024A002", status: "absent", verification: "Not available" },
      { id: "s3", name: "Nivedita Paul", registerNumber: "QC2024A003", status: "present", verification: "Verified" },
      { id: "s4", name: "Kabir Joshi", registerNumber: "QC2024A004", status: "present", verification: "Verified" },
      { id: "s5", name: "Tara Menon", registerNumber: "QC2024A005", status: "present", verification: "Needs review" },
    ],
  },
  {
    classId: "class-os-b",
    className: "Year 2 · Section B",
    subject: "Operating Systems",
    code: "CS208",
    time: "11:10 – 12:00",
    room: "Room 108",
    date: "06 Oct 2026",
    students: [
      { id: "s6", name: "Anika Shah", registerNumber: "QC2024B012", status: "present", verification: "Verified" },
      { id: "s7", name: "Rohan Das", registerNumber: "QC2024B013", status: "late", verification: "Needs review" },
      { id: "s8", name: "Meera Nair", registerNumber: "QC2024B014", status: "absent", verification: "Not available" },
      { id: "s9", name: "Aditya Rao", registerNumber: "QC2024B015", status: "present", verification: "Verified" },
    ],
  },
];
