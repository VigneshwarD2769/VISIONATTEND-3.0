import {
  demoUsers,
  enrollmentInfo,
  historyRecords,
  notifications,
  staffClasses,
  studentProfile,
  studentDataById,
  subjectSummaries,
  todayPeriods,
  verificationByAttendance,
  type AttendanceRecord,
  type AttendanceStatus,
  type ClassRoster,
  type DemoUser,
  type EnrollmentInfo,
  type Role,
  type UserProfile,
} from "./demoData";

export type Session = {
  token: string;
  userId: string;
  role: Role;
  name: string;
  shortName: string;
  subtitle: string;
  mode: "demo" | "backend";
};

export type AttendanceApi = {
  login(identifier: string, password: string): Promise<Session>;
  getProfile(session: Session): Promise<UserProfile>;
  getStudentHome(session: Session): Promise<{ today: AttendanceRecord[]; percentage: number; enrolled: EnrollmentInfo }>;
  getAttendance(session: Session): Promise<{ history: AttendanceRecord[]; subjects: typeof subjectSummaries; percentage: number; summary: { present: number; total: number; review: number } }>;
  getNotifications(session: Session): Promise<typeof notifications>;
  getEnrollment(session: Session): Promise<EnrollmentInfo>;
  advanceEnrollment(session: Session): Promise<EnrollmentInfo>;
  getEvidence(session: Session, attendanceId: string): Promise<(typeof verificationByAttendance)[string] | null>;
  getStaffOverview(session: Session): Promise<{ classes: ClassRoster[]; totalStudents: number; todayMarked: number; needsReview: number }>;
  getRoster(session: Session, classId: string): Promise<ClassRoster>;
  updateAttendance(session: Session, classId: string, studentId: string, status: AttendanceStatus): Promise<ClassRoster>;
};

const delay = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));

let mutableClasses = structuredClone(staffClasses);
let mutableEnrollments = Object.fromEntries(Object.entries(studentDataById).map(([id, data]) => [id, structuredClone(data.enrollment)]));

function ensureRole(session: Session, roles: Role[]) {
  if (!roles.includes(session.role)) {
    throw new Error("You do not have permission to view this workspace.");
  }
}

function getStudentDataset(session: Session) {
  ensureRole(session, ["student"]);
  const dataset = studentDataById[session.userId];
  if (!dataset) throw new Error("This student account is not provisioned in the preview.");
  return dataset;
}

const demoApi: AttendanceApi = {
  async login(identifier, password) {
    await delay(260);
    const normalized = identifier.trim().toLowerCase();
    const user = demoUsers.find((item) => (item.id.toLowerCase() === normalized || item.name.toLowerCase() === normalized || item.aliases?.some((alias) => alias.toLowerCase() === normalized)) && item.password === password);
    if (!user) throw new Error("We couldn’t sign you in with those details. Check your ID and password.");
    return {
      token: `demo-${user.role}-${Date.now()}`,
      userId: user.id,
      role: user.role,
      name: user.name,
      shortName: user.shortName,
      subtitle: user.subtitle,
      mode: "demo",
    };
  },

  async getProfile(session) {
    await delay();
    return getStudentDataset(session).profile;
  },

  async getStudentHome(session) {
    await delay();
    const dataset = getStudentDataset(session);
    return { today: dataset.today, percentage: dataset.percentage, enrolled: mutableEnrollments[session.userId] ?? dataset.enrollment };
  },

  async getAttendance(session) {
    await delay();
    const dataset = getStudentDataset(session);
    return { history: dataset.history, subjects: dataset.subjects, percentage: dataset.percentage, summary: dataset.summary };
  },

  async getNotifications(session) {
    await delay();
    return getStudentDataset(session).notifications;
  },

  async getEnrollment(session) {
    await delay();
    const dataset = getStudentDataset(session);
    return mutableEnrollments[session.userId] ?? dataset.enrollment;
  },

  async advanceEnrollment(session) {
    await delay(420);
    const dataset = getStudentDataset(session);
    const current = mutableEnrollments[session.userId] ?? dataset.enrollment;
    const nextStep = Math.min(current.currentStep + 1, current.totalSteps);
    const updated: EnrollmentInfo = {
      ...current,
      currentStep: nextStep,
      detail: nextStep >= 5 ? "All five captures are ready for backend review." : `${nextStep} of 5 guided captures are ready for backend review.`,
      state: nextStep >= 5 ? "submitted" : "in-progress",
      label: nextStep >= 5 ? "Submitted for backend review" : "Face enrollment in progress",
      lastUpdated: "Just now",
    };
    mutableEnrollments = { ...mutableEnrollments, [session.userId]: updated };
    return updated;
  },

  async getEvidence(session, attendanceId) {
    await delay();
    return getStudentDataset(session).evidence[attendanceId] ?? null;
  },

  async getStaffOverview(session) {
    await delay();
    ensureRole(session, ["faculty", "management"]);
    const classes = session.role === "faculty" ? mutableClasses.slice(0, 2) : mutableClasses;
    const totalStudents = classes.reduce((total, item) => total + item.students.length, 0);
    const todayMarked = classes.reduce((total, item) => total + item.students.filter((student) => student.status !== "unmarked").length, 0);
    const needsReview = classes.reduce((total, item) => total + item.students.filter((student) => student.verification === "Needs review").length, 0);
    return { classes, totalStudents, todayMarked, needsReview };
  },

  async getRoster(session, classId) {
    await delay();
    ensureRole(session, ["faculty", "management"]);
    const roster = mutableClasses.find((item) => item.classId === classId);
    if (!roster) throw new Error("This class is no longer available.");
    return roster;
  },

  async updateAttendance(session, classId, studentId, status) {
    await delay(320);
    ensureRole(session, ["faculty", "management"]);
    mutableClasses = mutableClasses.map((item) =>
      item.classId !== classId
        ? item
        : { ...item, students: item.students.map((student) => student.id === studentId ? {
          ...student,
          status,
          verification: status === "present" ? "Verified" : status === "late" ? "Needs review" : "Not available",
        } : student) },
    );
    const updated = mutableClasses.find((item) => item.classId === classId);
    if (!updated) throw new Error("Could not save this attendance update.");
    return updated;
  },
};

/**
 * Future backend adapter boundary. The final FastAPI contract must be verified before activation.
 * Proposed routes are documented in the handoff; the client must only call authenticated HTTPS APIs.
 */
export class FastApiAttendanceApi implements AttendanceApi {
  constructor(private readonly baseUrl: string) {}
  private unavailable(): never {
    throw new Error(`Backend adapter is not connected yet. Configure the VISIONATTEND API base URL (${this.baseUrl}).`);
  }
  login(): Promise<Session> { return Promise.reject(this.unavailable()); }
  getProfile(): Promise<UserProfile> { return Promise.reject(this.unavailable()); }
  getStudentHome(): Promise<{ today: AttendanceRecord[]; percentage: number; enrolled: EnrollmentInfo }> { return Promise.reject(this.unavailable()); }
  getAttendance(): Promise<{ history: AttendanceRecord[]; subjects: typeof subjectSummaries; percentage: number; summary: { present: number; total: number; review: number } }> { return Promise.reject(this.unavailable()); }
  getNotifications(): Promise<typeof notifications> { return Promise.reject(this.unavailable()); }
  getEnrollment(): Promise<EnrollmentInfo> { return Promise.reject(this.unavailable()); }
  advanceEnrollment(): Promise<EnrollmentInfo> { return Promise.reject(this.unavailable()); }
  getEvidence(): Promise<(typeof verificationByAttendance)[string] | null> { return Promise.reject(this.unavailable()); }
  getStaffOverview(): Promise<{ classes: ClassRoster[]; totalStudents: number; todayMarked: number; needsReview: number }> { return Promise.reject(this.unavailable()); }
  getRoster(): Promise<ClassRoster> { return Promise.reject(this.unavailable()); }
  updateAttendance(): Promise<ClassRoster> { return Promise.reject(this.unavailable()); }
}

export const attendanceApi: AttendanceApi = import.meta.env.VITE_VISIONATTEND_API_BASE_URL
  ? new FastApiAttendanceApi(import.meta.env.VITE_VISIONATTEND_API_BASE_URL)
  : demoApi;

export const demoCredentials = demoUsers.map((user: DemoUser) => ({
  role: user.role,
  label: user.role === "student" ? "Student preview" : user.role === "faculty" ? "Faculty preview" : "Management preview",
  id: user.id,
  password: user.password,
}));
