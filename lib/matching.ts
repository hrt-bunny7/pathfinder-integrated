import { RELATED, PREREQS, canonicalSkill, extractSkills } from './skills';
import type { Job, RoadmapPlan, SkillGap, SkillProfile } from './types';

export function userSkillNames(profile: SkillProfile | null): string[] {
  if (!profile) return [];
  const set = new Set<string>();
  for (const s of profile.skills ?? []) set.add(canonicalSkill(s.name) ?? s.name);
  return [...set];
}

/** Compare a user's skills with the skills a job text asks for. */
export function analyzeGap(userSkills: string[], jobText: string): SkillGap {
  const required = extractSkills(jobText);
  const have = new Set(userSkills);
  const matched: SkillGap['matched'] = [];
  const partial: SkillGap['partial'] = [];
  const missing: SkillGap['missing'] = [];

  for (const req of required) {
    if (have.has(req.name)) { matched.push(req); continue; }
    const rel = RELATED.find(([a, b]) => (a === req.name && have.has(b)) || (b === req.name && have.has(a)));
    if (rel) partial.push({ ...req, via: rel[0] === req.name ? rel[1] : rel[0] });
    else missing.push(req);
  }
  const total = required.reduce((s, r) => s + r.weight, 0);
  const got = matched.reduce((s, r) => s + r.weight, 0) + partial.reduce((s, r) => s + r.weight * 0.5, 0);
  return { score: total ? Math.round((got / total) * 100) : 0, matched, partial, missing };
}

export function scoreJob(userSkills: string[], job: Job): number {
  return analyzeGap(userSkills, `${job.title}. ${job.title}. ${job.description}`).score;
}

/** Match % after the learner has finished some skills (used on the roadmap page). */
export function scoreWithProgress(gap: SkillGap, doneSkills: string[]): number {
  const all = [...gap.matched, ...gap.partial, ...gap.missing];
  const total = all.reduce((s, r) => s + r.weight, 0);
  if (!total) return 0;
  let got = gap.matched.reduce((s, r) => s + r.weight, 0);
  for (const p of gap.partial) got += p.weight * (doneSkills.includes(p.name) ? 1 : 0.5);
  for (const m of gap.missing) if (doneSkills.includes(m.name)) got += m.weight;
  return Math.round((got / total) * 100);
}

// ---- Local fallback roadmap (used when AI_BACKEND_URL is not set) ----
function depth(skill: string, seen = new Set<string>()): number {
  if (seen.has(skill)) return 0;
  seen.add(skill);
  const pre = PREREQS[skill] ?? [];
  return pre.length ? 1 + Math.max(...pre.map((p) => depth(p, seen))) : 0;
}

export function buildFallbackRoadmap(gap: SkillGap, limit = 6): RoadmapPlan {
  const targets = [...gap.missing, ...gap.partial]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, limit)
    .sort((a, b) => depth(a.name) - depth(b.name)); // prerequisites first
  const q = (s: string) => encodeURIComponent(s);
  return {
    weeks: targets.map((t, i) => ({
      week: i + 1,
      skill: t.name,
      topics: [`${t.name} fundamentals and setup`, `Core concepts of ${t.name} with daily practice`, `${t.name} in real-world workflows and best practices`],
      project: `Build a small project that uses ${t.name} and push it to GitHub.`,
      resources: [
        { title: `${t.name} tutorials on YouTube`, url: `https://www.youtube.com/results?search_query=${q(t.name + ' full course')}` },
        { title: `freeCodeCamp: ${t.name}`, url: `https://www.freecodecamp.org/news/search?query=${q(t.name)}` },
        { title: `roadmap.sh guides`, url: `https://roadmap.sh` },
      ],
    })),
  };
}
