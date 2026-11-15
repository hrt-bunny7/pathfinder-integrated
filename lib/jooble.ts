import type { Job } from './types';

type Q = { what?: string; whatOr?: string; where?: string; page?: number };

const clean = (s: unknown) =>
  String(s ?? '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();

/** Jobs from Jooble (free key from jooble.org/api/about). Returns [] if there is no key or anything fails. */
export async function fetchJoobleJobs(q: Q): Promise<Job[]> {
  const key = process.env.JOOBLE_API_KEY;
  if (!key) return [];
  try {
    const res = await fetch(`https://jooble.org/api/${key}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keywords: q.what || q.whatOr || '', location: q.where || 'India', page: String(q.page ?? 1) }),
      next: { revalidate: 3600 },
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) throw new Error(String(res.status));
    const data = await res.json();
    return (data.jobs ?? []).map((r: any): Job => ({
      id: `jooble-${r.id ?? r.link}`,
      title: clean(r.title) || 'Untitled',
      company: clean(r.company) || 'Unknown company',
      location: clean(r.location),
      description: clean(r.snippet),
      url: r.link ?? '#',
      salary: clean(r.salary) || null,
      created: r.updated,
    }));
  } catch {
    return [];
  }
}
