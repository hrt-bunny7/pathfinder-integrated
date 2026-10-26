// Shared data contracts (must match shared/schemas.py on the backend)
export type Skill = { name: string; level?: 'beginner' | 'intermediate' | 'advanced'; category?: string };

export type SkillProfile = {
  user_id?: string;
  skills: Skill[];
  experience_years?: number;
  education?: string;
  domains?: string[];
  summary?: string;
};

export type Career = { role: string; fit: number; reason: string };

export type Job = {
  id: string; title: string; company: string; location: string;
  description: string; url: string; salary?: string | null; created?: string;
};

export type WeightedSkill = { name: string; weight: number };

export type SkillGap = {
  score: number;                       // match % before learning
  matched: WeightedSkill[];
  partial: (WeightedSkill & { via: string })[];
  missing: WeightedSkill[];
};

export type RoadmapWeek = {
  week: number; skill: string; topics: string[]; project: string;
  resources: { title: string; url: string }[];
};
export type RoadmapPlan = { weeks: RoadmapWeek[] };
