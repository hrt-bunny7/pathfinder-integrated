'use client';
import { useState, useTransition } from 'react';
import { toggleWeek } from '@/app/actions';
import MatchRing from './MatchRing';
import type { RoadmapPlan, SkillGap } from '@/lib/types';
import { scoreWithProgress } from '@/lib/matching';

export default function RoadmapChecklist({ roadmapId, plan, gap, initial }:
  { roadmapId: string; plan: RoadmapPlan; gap: SkillGap; initial: Record<string, boolean> }) {
  const [done, setDone] = useState(initial);
  const [, start] = useTransition();

  const doneSkills = plan.weeks.filter((w) => done[w.week]).map((w) => w.skill);
  const score = scoreWithProgress(gap, doneSkills);
  const pct = plan.weeks.length ? Math.round((doneSkills.length / plan.weeks.length) * 100) : 0;

  function toggle(week: number) {
    const next = !done[week];
    setDone({ ...done, [week]: next });
    start(() => toggleWeek(roadmapId, week, next));
  }

  return (
    <>
      <div className="panel flex items-center gap-5">
        <MatchRing value={score} size={84} />
        <div>
          <p className="font-display text-lg font-bold">Your match: {gap.score}% now {score > gap.score && <>→ {score}%</>}</p>
          <p className="text-sm text-ink/70">{doneSkills.length} of {plan.weeks.length} weeks done ({pct}%). Tick a week when you finish it and your match rises.</p>
        </div>
      </div>

      <ol className="mt-6 space-y-4">
        {plan.weeks.map((w) => (
          <li key={w.week} className={`panel ${done[w.week] ? 'border-good bg-good-soft/50' : ''}`}>
            <label className="flex cursor-pointer items-start gap-3">
              <input type="checkbox" className="mt-1.5 h-5 w-5 accent-[#2F54EB]" checked={!!done[w.week]} onChange={() => toggle(w.week)} />
              <div>
                <h3 className="font-display text-xl font-bold">Week {w.week}: {w.skill}</h3>
              </div>
            </label>
            <div className="ml-8 mt-3 space-y-3 text-sm">
              <ul className="list-disc pl-5">{w.topics.map((t) => <li key={t}>{t}</li>)}</ul>
              <p><span className="font-semibold">Mini project:</span> {w.project}</p>
              <ul className="flex flex-wrap gap-2">
                {w.resources.map((r) => (
                  <li key={r.url}><a className="rounded-md border border-line px-2.5 py-1 font-semibold text-brand hover:border-brand" href={r.url} target="_blank" rel="noreferrer">{r.title}</a></li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ol>
    </>
  );
}
