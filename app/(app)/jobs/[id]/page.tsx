import Link from 'next/link';
import { notFound } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import { generateRoadmap } from '@/app/actions';
import Chip from '@/components/Chip';
import MatchRing from '@/components/MatchRing';
import SubmitButton from '@/components/SubmitButton';
import type { SkillGap } from '@/lib/types';

// Vercel: allow up to 60s for the AI backend (it can be slow on a cold start)
export const maxDuration = 60;

export default async function JobDetail({ params }: { params: { id: string } }) {
  const supabase = createClient();
  const { data: job } = await supabase.from('saved_jobs').select('*').eq('id', params.id).maybeSingle();
  if (!job) notFound();
  const { data: gapRow } = await supabase.from('skill_gaps').select('gap').eq('job_id', job.id).maybeSingle();
  const { data: roadmap } = await supabase.from('roadmaps').select('id').eq('job_id', job.id).maybeSingle();
  const gap = gapRow?.gap as SkillGap | undefined;
  const needsLearning = !!gap && (gap.missing.length > 0 || gap.partial.length > 0);

  return (
    <div className="space-y-6">
      <Link href="/jobs" className="text-sm font-semibold text-brand underline">Back to jobs</Link>

      <section className="panel flex flex-col gap-5 sm:flex-row sm:items-center">
        {gap && <MatchRing value={gap.score} size={104} />}
        <div className="flex-1">
          <h1 className="font-display text-3xl font-bold leading-tight">{job.title}</h1>
          <p className="mt-1 text-ink/70">{job.company}{job.location && `, ${job.location}`}</p>
          {job.url && job.url !== '#' && (
            <a href={job.url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-sm font-semibold text-brand underline">View original posting</a>
          )}
        </div>
        {needsLearning && (
          roadmap
            ? <Link href={`/roadmap/${roadmap.id}`} className="btn px-6 py-3">Open my roadmap</Link>
            : <form action={generateRoadmap}>
                <input type="hidden" name="jobId" value={job.id} />
                <SubmitButton pending="Building roadmap..." className="btn px-6 py-3">Build my learning roadmap</SubmitButton>
              </form>
        )}
      </section>

      {gap ? (
        <section className="grid gap-4 md:grid-cols-3">
          <div className="panel border-t-4 border-t-good">
            <h2 className="font-display text-lg font-bold">You have ({gap.matched.length})</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {gap.matched.length ? gap.matched.map((s) => <Chip key={s.name} tone="have">{s.name}</Chip>) : <p className="text-sm text-ink/60">None yet.</p>}
            </div>
          </div>
          <div className="panel border-t-4 border-t-amber">
            <h2 className="font-display text-lg font-bold">Close ({gap.partial.length})</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {gap.partial.length ? gap.partial.map((s) => <Chip key={s.name} tone="partial">{s.name} (you know {s.via})</Chip>) : <p className="text-sm text-ink/60">None.</p>}
            </div>
          </div>
          <div className="panel border-t-4 border-t-rust">
            <h2 className="font-display text-lg font-bold">Missing ({gap.missing.length})</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {gap.missing.length ? gap.missing.map((s) => <Chip key={s.name} tone="missing">{s.name}</Chip>) : <p className="text-sm text-ink/60">Nothing missing. You can apply now.</p>}
            </div>
            <p className="mt-3 text-xs text-ink/60">Most important first.</p>
          </div>
        </section>
      ) : <p className="panel text-ink/70">The skill gap is not ready. Go back and open this job again.</p>}

      <section className="panel">
        <h2 className="font-display text-lg font-bold">Job description</h2>
        <p className="mt-2 max-w-3xl whitespace-pre-line text-sm leading-relaxed text-ink/80">{job.description}</p>
      </section>
    </div>
  );
}
