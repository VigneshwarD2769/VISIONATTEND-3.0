import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { attendanceApi, type Session } from "@/lib/attendanceApi";

const SESSION_KEY = "visionattend.demo.session";

type SessionContextValue = {
  session: Session | null;
  isLoading: boolean;
  error: string | null;
  login: (identifier: string, password: string) => Promise<Session>;
  logout: () => void;
  clearError: () => void;
};

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

function readSession(): Session | null {
  try {
    const saved = sessionStorage.getItem(SESSION_KEY);
    return saved ? (JSON.parse(saved) as Session) : null;
  } catch {
    return null;
  }
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() => readSession());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const value = useMemo<SessionContextValue>(() => ({
    session,
    isLoading,
    error,
    async login(identifier, password) {
      setIsLoading(true);
      setError(null);
      try {
        const next = await attendanceApi.login(identifier, password);
        setSession(next);
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(next));
        return next;
      } catch (caught) {
        const message = caught instanceof Error ? caught.message : "Something went wrong. Please try again.";
        setError(message);
        throw caught;
      } finally {
        setIsLoading(false);
      }
    },
    logout() {
      setSession(null);
      sessionStorage.removeItem(SESSION_KEY);
    },
    clearError() {
      setError(null);
    },
  }), [error, isLoading, session]);

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) throw new Error("useSession must be used within SessionProvider");
  return context;
}
