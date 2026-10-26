import Link from 'next/link';
import { notFound } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import RoadmapChecklist from '@/components/RoadmapChecklist';
import type { RoadmapPlan, SkillGap } from '@/lib/types';

export default async function RoadmapPage({ params }: { params: { id: string } }) {
  const supabase = createClient();
  const { data: rm } = await supabase.from('roadmaps').select('*').eq('id', params.id).maybeSingle();
  if (!rm) notFound();
  const { data: job } = await supabase.from('saved_jobs').select('id, title, company').eq('id', rm.job_id).single();
  const { data: gapRow } = await supabase.from('skill_gaps').select('gap').eq('job_id', rm.job_id).single();

  return (
    <div>
      <Link href={`/jobs/${rm.job_id}`} className="text-sm font-semibold text-brand underline">Back to job</Link>
      <h1 className="mb-6 mt-2 font-display text-3xl font-bold">Roadmap: {job?.title} at {job?.company}</h1>
      <RoadmapChecklist roadmapId={rm.id} plan={rm.plan as RoadmapPlan} gap={gapRow!.gap as SkillGap}
                        initial={(rm.progress ?? {}) as Record<string, boolean>} />
    </div>
  );
}
