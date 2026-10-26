import Link from 'next/link';
import { createClient } from '@/lib/supabase/server';
import { recommendCareers } from '@/lib/backend';
import { canonicalSkill } from '@/lib/skills';
import Chip from '@/components/Chip';
import MatchRing from '@/components/MatchRing';
import type { SkillProfile } from '@/lib/types';

// Vercel: allow up to 60s for the AI backend (it can be slow on a cold start)
export const maxDuration = 60;

export default async function Dashboard() {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const { data: p } = await supabase.from('profiles').select('full_name').eq('id', user!.id).maybeSingle();
  const { data: resume } = await supabase.from('resumes').select('parsed_profile, created_at')
    .order('created_at', { ascending: false }).limit(1).maybeSingle();
  const { data: saved } = await supabase.from('saved_jobs').select('id, title, company, match_score')
    .order('created_at', { ascending: false }).limit(5);

  const profile = (resume?.parsed_profile ?? null) as SkillProfile | null;
  const name = p?.full_name?.split(' ')[0] ?? 'there';

  if (!profile) {
    return (
      <div className="mx-auto max-w-xl rounded-2xl bg-ink p-10 text-white">
        <h1 className="font-display text-4xl font-bold">Welcome, {name}</h1>
        <p className="mt-3 text-lg text-white/80">Upload your resume and we will read your skills, suggest careers, and rank open jobs by how well you fit.</p>
        <Link href="/upload" className="btn mt-7 px-6 py-3">Upload resume</Link>
      </div>
    );
  }

  const careers = await recommendCareers(profile);
  const groups = new Map<string, Set<string>>();
  for (const s of profile.skills ?? []) {
    const cat = (s.category ?? 'other').toLowerCase();
    if (!groups.has(cat)) groups.set(cat, new Set());
    groups.get(cat)!.add(canonicalSkill(s.name) ?? s.name);
  }
  const total = [...groups.values()].reduce((n, g) => n + g.size, 0);

  return (
    <div className="space-y-10">
      <section className="rounded-2xl bg-ink p-8 text-white">
        <h1 className="font-display text-4xl font-bold">Hi {name}</h1>
        {profile.summary && <p className="mt-3 max-w-2xl text-lg leading-relaxed text-white/80">{profile.summary}</p>}
        <dl className="mt-7 flex flex-wrap gap-x-10 gap-y-4 text-sm">
          <div><dt className="text-white/60">Skills found</dt><dd className="font-display text-2xl font-bold">{total}</dd></div>
          <div><dt className="text-white/60">Experience</dt><dd className="font-display text-2xl font-bold">{profile.experience_years ?? 0} yr</dd></div>
          {profile.education && <div><dt className="text-white/60">Education</dt><dd className="font-display text-2xl font-bold">{profile.education}</dd></div>}
          <div><dt className="text-white/60">Jobs opened</dt><dd className="font-display text-2xl font-bold">{saved?.length ?? 0}</dd></div>
        </dl>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link href="/jobs" className="btn">Find matching jobs</Link>
          <Link href="/upload" className="inline-flex items-center rounded-lg border border-white/30 px-4 py-2.5 text-sm font-semibold hover:bg-white/10">Update resume</Link>
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold">Your skills</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[...groups.entries()].map(([cat, set]) => (
            <div key={cat} className="panel">
              <h3 className="text-sm font-semibold capitalize text-ink/60">{cat}</h3>
              <div className="mt-3 flex flex-wrap gap-2">{[...set].map((s) => <Chip key={s} tone="have">{s}</Chip>)}</div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold">Careers that suit you</h2>
        {careers.length === 0 && <p className="panel mt-4 text-ink/70">Career suggestions are not available right now. Your skills and job matches still work, so try again in a minute.</p>}
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {careers.map((c) => (
            <Link key={c.role} href={`/jobs?q=${encodeURIComponent(c.role)}`} className="panel block transition-colors hover:border-brand">
              <div className="flex items-center gap-3">
                <MatchRing value={c.fit} size={56} />
                <h3 className="font-display text-lg font-bold leading-tight">{c.role}</h3>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-ink/75">{c.reason}</p>
              <p className="mt-3 text-sm font-semibold text-brand">See jobs for this role</p>
            </Link>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold">Jobs you opened</h2>
        {saved?.length ? (
          <ul className="panel mt-4 divide-y divide-line p-0">
            {saved.map((j) => (
              <li key={j.id}>
                <Link href={`/jobs/${j.id}`} className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-paper">
                  <span className="min-w-0"><span className="font-semibold">{j.title}</span> <span className="text-ink/60">at {j.company}</span></span>
                  <MatchRing value={j.match_score ?? 0} size={44} />
                </Link>
              </li>
            ))}
          </ul>
        ) : <p className="panel mt-4 text-ink/70">Nothing yet. Open a job to see which skills you are missing.</p>}
      </section>
    </div>
  );
}
