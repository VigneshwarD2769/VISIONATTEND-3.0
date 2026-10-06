import {
  demoUsers,
  enrollmentInfo,
  historyRecords,
  notifications,
  staffClasses,
  studentProfile,
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
  getAttendance(session: Session): Promise<{ history: AttendanceRecord[]; subjects: typeof subjectSummaries }>;
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
let mutableEnrollment = structuredClone(enrollmentInfo);

function ensureRole(session: Session, roles: Role[]) {
  if (!roles.includes(session.role)) {
    throw new Error("You do not have permission to view this workspace.");
  }
}

const demoApi: AttendanceApi = {
  async login(identifier, password) {
    await delay(260);
    const normalized = identifier.trim().toLowerCase();
    const user = demoUsers.find((item) => item.id.toLowerCase() === normalized && item.password === password);
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
    ensureRole(session, ["student"]);
    return studentProfile;
  },

  async getStudentHome(session) {
    await delay();
    ensureRole(session, ["student"]);
    return { today: todayPeriods, percentage: 92, enrolled: mutableEnrollment };
  },

  async getAttendance(session) {
    await delay();
    ensureRole(session, ["student"]);
    return { history: historyRecords, subjects: subjectSummaries };
  },

  async getNotifications(session) {
    await delay();
    ensureRole(session, ["student"]);
    return notifications;
  },

  async getEnrollment(session) {
    await delay();
    ensureRole(session, ["student"]);
    return mutableEnrollment;
  },

  async advanceEnrollment(session) {
    await delay(420);
    ensureRole(session, ["student"]);
    const nextStep = Math.min(mutableEnrollment.currentStep + 1, mutableEnrollment.totalSteps);
    mutableEnrollment = {
      ...mutableEnrollment,
      currentStep: nextStep,
      detail: nextStep >= 5 ? "All five captures are ready for backend review." : `${nextStep} of 5 guided captures are ready for backend review.`,
      state: nextStep >= 5 ? "submitted" : "in-progress",
      label: nextStep >= 5 ? "Submitted for backend review" : "Face enrollment in progress",
      lastUpdated: "Just now",
    };
    return mutableEnrollment;
  },

  async getEvidence(session, attendanceId) {
    await delay();
    ensureRole(session, ["student"]);
    return verificationByAttendance[attendanceId] ?? null;
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
        : { ...item, students: item.students.map((student) => student.id === studentId ? { ...student, status } : student) },
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
  getAttendance(): Promise<{ history: AttendanceRecord[]; subjects: typeof subjectSummaries }> { return Promise.reject(this.unavailable()); }
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
