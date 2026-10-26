'use server';
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { createClient } from '@/lib/supabase/server';
import { analyzeResume, callBackend } from '@/lib/backend';
import { analyzeGap, buildFallbackRoadmap, userSkillNames } from '@/lib/matching';
import type { Job, RoadmapPlan, SkillGap, SkillProfile } from '@/lib/types';

async function requireUser() {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');
  return { supabase, user };
}

export async function logout() {
  await createClient().auth.signOut();
  redirect('/login');
}

/** Upload resume -> Member 3's analyzer -> store file -> save parsed profile */
export async function uploadResume(formData: FormData) {
  const { supabase, user } = await requireUser();
  const file = formData.get('resume') as File | null;
  if (!file || file.size === 0) redirect('/upload?error=Choose a PDF or DOCX file first.');
  const okType = /\.(pdf|docx)$/i.test(file.name);
  if (!okType) redirect('/upload?error=Only PDF and DOCX files are supported.');
  if (file.size > 4 * 1024 * 1024) redirect('/upload?error=File is larger than 4 MB.');

  // Read the resume first, so an unreadable file never leaves an orphan in storage.
  const result = await analyzeResume(file, user.id);
  if ('error' in result) redirect(`/upload?error=${encodeURIComponent(result.error)}`);
  const profile = result.profile;

  const path = `${user.id}/${Date.now()}-${file.name.replace(/[^\w.\-]/g, '_')}`;
  const { error: upErr } = await supabase.storage.from('resumes').upload(path, file, { contentType: file.type });
  if (upErr) redirect(`/upload?error=${encodeURIComponent('Upload failed: ' + upErr.message)}`);

  const { error } = await supabase.from('resumes').insert({ user_id: user.id, file_path: path, parsed_profile: profile });
  if (error) redirect(`/upload?error=${encodeURIComponent(error.message)}`);

  revalidatePath('/dashboard');
  redirect('/dashboard');
}

/** Save the chosen job, compute the skill gap, go to the job page */
export async function openJob(formData: FormData) {
  const { supabase, user } = await requireUser();
  const job = JSON.parse(String(formData.get('job'))) as Job;
  const score = Number(formData.get('score')) || 0;

  const { data: saved, error } = await supabase.from('saved_jobs').upsert({
    user_id: user.id, job_external_id: job.id, title: job.title, company: job.company,
    location: job.location, description: job.description, url: job.url, match_score: score,
  }, { onConflict: 'user_id,job_external_id' }).select('id').single();
  if (error || !saved) redirect('/jobs');

  const { data: resume } = await supabase.from('resumes').select('parsed_profile')
    .order('created_at', { ascending: false }).limit(1).maybeSingle();
  const profile = (resume?.parsed_profile ?? null) as SkillProfile | null;

  // The job-based gap is computed here (it reads the real job text). The backend builds the roadmap from it.
  const gap: SkillGap = analyzeGap(userSkillNames(profile), `${job.title}. ${job.title}. ${job.description}`);

  await supabase.from('skill_gaps').upsert({ user_id: user.id, job_id: saved.id, gap }, { onConflict: 'user_id,job_id' });
  redirect(`/jobs/${saved.id}`);
}

/** Create (or reuse) the learning roadmap for a saved job */
export async function generateRoadmap(formData: FormData) {
  const { supabase, user } = await requireUser();
  const jobId = String(formData.get('jobId'));

  const { data: existing } = await supabase.from('roadmaps').select('id').eq('job_id', jobId).maybeSingle();
  if (existing) redirect(`/roadmap/${existing.id}`);

  const { data: job } = await supabase.from('saved_jobs').select('*').eq('id', jobId).single();
  const { data: gapRow } = await supabase.from('skill_gaps').select('gap').eq('job_id', jobId).single();
  if (!job || !gapRow) redirect('/jobs');
  const gap = gapRow.gap as SkillGap;

  const plan = await callBackend<RoadmapPlan>('/roadmap/generate', { job, gap }, () => buildFallbackRoadmap(gap));
  const { data: created, error } = await supabase.from('roadmaps')
    .insert({ user_id: user.id, job_id: jobId, plan, progress: {} }).select('id').single();
  if (error || !created) redirect(`/jobs/${jobId}`);
  redirect(`/roadmap/${created.id}`);
}

/** Tick / untick a roadmap week */
export async function toggleWeek(roadmapId: string, week: number, done: boolean) {
  const { supabase } = await requireUser();
  const { data } = await supabase.from('roadmaps').select('progress').eq('id', roadmapId).single();
  const progress = { ...(data?.progress ?? {}), [week]: done };
  await supabase.from('roadmaps').update({ progress }).eq('id', roadmapId);
}
