import Link from 'next/link';
import { createClient } from '@/lib/supabase/server';
import MatchRing from '@/components/MatchRing';

export default async function VisitedJobs() {
  const supabase = createClient();
  const { data: rows } = await supabase.from('saved_jobs').select('*').order('created_at', { ascending: false });
  const jobs = rows ?? [];

  return (
    <div>
      <h1 className="font-display text-4xl font-bold">Visited jobs</h1>
      <p className="mt-1 text-ink/70">Jobs you have opened. They are added here automatically.</p>

      {!jobs.length && (
        <div className="panel mt-6 max-w-xl">
          <p className="text-ink/80">You have not opened any jobs yet. Open a job from the Jobs page and it will show up here.</p>
          <Link href="/jobs" className="btn mt-4">Browse jobs</Link>
        </div>
      )}

      <ul className="mt-6 space-y-4">
        {jobs.map((job) => (
          <li key={job.id} className="panel flex flex-col gap-4 sm:flex-row sm:items-center">
            <MatchRing value={job.match_score ?? 0} size={72} />
            <div className="min-w-0 flex-1">
              <h2 className="font-display text-xl font-bold leading-tight">{job.title}</h2>
              <p className="text-sm text-ink/65">{job.company}{job.location && `, ${job.location}`}</p>
              <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-ink/80">{job.description}</p>
            </div>
            <Link href={`/jobs/${job.id}`} className="btn sm:w-40">Open again</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
