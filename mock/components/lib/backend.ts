import careersMock from '@/mock/careers.json';
import profileMock from '@/mock/profile.json';
import type { Career, SkillProfile } from './types';

// The teammates' FastAPI service (see /backend). Leave AI_BACKEND_URL empty for demo mode (mock data).
const BASE = process.env.AI_BACKEND_URL?.replace(/\/$/, '');
const KEY = process.env.AI_BACKEND_KEY; // optional shared secret, must equal BACKEND_API_KEY on the backend
const TIMEOUT_MS = 45_000;
const RESUME_TIMEOUT_MS = 60_000;

const authHeaders = (): Record<string, string> => (KEY ? { 'X-API-Key': KEY } : {});

/** POST JSON to the FastAPI service. Falls back to local logic if it's not configured, slow, or fails. */
export async function callBackend<T>(path: string, body: unknown, fallback: () => T | Promise<T>): Promise<T> {
  if (!BASE) return fallback();
  try {
    const res = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
      cache: 'no-store',
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    if (!res.ok) throw new Error(`${path} -> ${res.status}`);
    return (await res.json()) as T;
  } catch (e) {
    console.error('[backend]', e);
    return fallback();
  }
}

export type ResumeResult = { profile: SkillProfile } | { error: string };

/** Member 3: resume file -> skill profile.
 *  Demo mode (no backend URL): returns the mock profile.
 *  Real mode: never shows someone else's mock data. If the resume can't be read, the user gets a message. */
export async function analyzeResume(file: File, userId: string): Promise<ResumeResult> {
  if (!BASE) return { profile: { ...(profileMock as SkillProfile), user_id: userId } };
  try {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('user_id', userId);
    const res = await fetch(`${BASE}/resume/analyze`, {
      method: 'POST', headers: authHeaders(), body: fd, cache: 'no-store', signal: AbortSignal.timeout(RESUME_TIMEOUT_MS),
    });
    if (res.ok) return { profile: (await res.json()) as SkillProfile };
    if (res.status === 422) {
      const j = await res.json().catch(() => null);
      return { error: typeof j?.detail === 'string' ? j.detail : 'We could not read this resume. Try a different PDF or DOCX.' };
    }
    console.error('[backend] resume ->', res.status);
  } catch (e) {
    console.error('[backend] resume', e);
  }
  return { error: 'The resume reader is not responding right now. Please try again in a minute.' };
}

/** Member 2: skill profile -> career paths. In real mode a failure shows no careers rather than fake ones. */
export async function recommendCareers(profile: SkillProfile): Promise<Career[]> {
  if (!BASE) return careersMock as Career[];
  return callBackend<Career[]>('/careers/recommend', profile, () => []);
}
