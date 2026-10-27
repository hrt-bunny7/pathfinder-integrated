import Link from 'next/link';
import { createClient } from '@/lib/supabase/server';
import { fetchJobs } from '@/lib/adzuna';
import { analyzeGap, userSkillNames } from '@/lib/matching';
import { openJob } from '@/app/actions';
import MatchRing from '@/components/MatchRing';
import Chip from '@/components/Chip';
import SubmitButton from '@/components/SubmitButton';
import type { SkillProfile } from '@/lib/types';

export default async function Jobs({ searchParams }: { searchParams: { q?: string; where?: string; min?: string } }) {
  const supabase = createClient();
  const { data: resume } = await supabase.from('resumes').select('parsed_profile')
    .order('created_at', { ascending: false }).limit(1).maybeSingle();
  const profile = (resume?.parsed_profile ?? null) as SkillProfile | null;

  if (!profile) {
    return (
      <div className="mx-auto max-w-xl rounded-2xl bg-ink p-10 text-white">
        <h1 className="font-display text-4xl font-bold">Jobs</h1>
        <p className="mt-3 text-white/80">We need your skills first, so we can rank jobs for you.</p>
        <Link href="/upload" className="btn mt-6">Upload resume</Link>
      </div>
    );
  }

    const { data: visitedRows } = await supabase.from('saved_jobs').select('job_external_id');
  const visitedIds = new Set((visitedRows ?? []).map((r) => r.job_external_id as string));
  
  const skills = userSkillNames(profile);
  const q = searchParams.q?.trim();
  const { jobs, live } = await fetchJobs({
    what: q || undefined,
    whatOr: q ? undefined : skills.slice(0, 3).join(' '),
    where: searchParams.where?.trim() || undefined,
  });

  const min = Number(searchParams.min) || 0;
  const ranked = jobs
    .map((job) => ({ job, gap: analyzeGap(skills, `${job.title}. ${job.title}. ${job.description}`) }))
    .filter((r) => r.gap.score >= min)
    .sort((a, b) => b.gap.score - a.gap.score);

  return (
    <div>
      <h1 className="font-display text-4xl font-bold">Jobs for you</h1>
      <p className="mt-1 text-ink/70">Ranked by how many of the required skills you already have.</p>

      <form className="panel mt-6 flex flex-wrap gap-2">
        <input name="q" defaultValue={q} placeholder="Role or keyword" className="field max-w-xs" />
        <input name="where" defaultValue={searchParams.where} placeholder="City" className="field max-w-[180px]" />
        <select name="min" defaultValue={searchParams.min ?? '0'} className="field max-w-[170px]">
          <option value="0">Any match</option><option value="30">30%+ match</option>
          <option value="50">50%+ match</option><option value="70">70%+ match</option>
        </select>
        <button className="btn">Search</button>
      </form>

      {!live && (
        <p className="mt-4 rounded-lg bg-amber-soft px-4 py-3 text-sm text-amber-dark">
          Showing sample jobs. Add your Adzuna keys to .env.local to see live openings.
        </p>
      )}

      <ul className="mt-6 space-y-4">
        {ranked.map(({ job, gap }) => {
          const need = gap.matched.length + gap.partial.length + gap.missing.length;
          return (
            <li key={job.id} className="panel flex flex-col gap-4 sm:flex-row sm:items-center">
              <MatchRing value={gap.score} size={72} />
              <div className="min-w-0 flex-1">
                <h2 className="font-display text-xl font-bold leading-tight">{job.title}{visitedIds.has(job.id) && <span className="ml-2 align-middle"><Chip tone="brand">Visited</Chip></span>}</h2>
                <p className="text-sm text-ink/65">{job.company}{job.location && `, ${job.location}`}{job.salary && `, ${job.salary}`}</p>
                <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-ink/80">{job.description}</p>
                {need > 0 && (
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold text-ink/60">You have {gap.matched.length} of {need}</span>
                    {gap.matched.slice(0, 3).map((s) => <Chip key={s.name} tone="have">{s.name}</Chip>)}
                    {gap.missing.slice(0, 3).map((s) => <Chip key={s.name} tone="missing">{s.name}</Chip>)}
                  </div>
                )}
              </div>
              <form action={openJob}>
                <input type="hidden" name="job" value={JSON.stringify(job)} />
                <input type="hidden" name="score" value={gap.score} />
                <SubmitButton pending="Opening...">See skill gap</SubmitButton>
              </form>
            </li>
          );
        })}
      </ul>
      {!ranked.length && <p className="panel mt-6 text-ink/70">No jobs match these filters. Try a lower match % or a broader keyword.</p>}
    </div>
  );
}
