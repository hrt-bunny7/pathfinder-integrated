import Link from 'next/link';
import { uploadResume } from '@/app/actions';
import SubmitButton from '@/components/SubmitButton';
import { createClient } from '@/lib/supabase/server';

// Vercel: allow up to 60s for the AI backend (it can be slow on a cold start)
export const maxDuration = 60;

export default async function Upload({ searchParams }: { searchParams: { error?: string } }) {
  const { data: resume } = await createClient().from('resumes').select('file_path, created_at')
    .order('created_at', { ascending: false }).limit(1).maybeSingle();

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="font-display text-4xl font-bold">Your resume</h1>
      <p className="mt-2 text-ink/75">Upload a PDF or DOCX up to 4 MB. A new upload replaces your current skill profile.</p>

      {resume && (
        <p className="mt-5 rounded-lg bg-good-soft px-4 py-3 text-sm text-good-dark">
          Current file: <b>{resume.file_path?.split('/').pop()?.replace(/^\d+-/, '')}</b>, uploaded {new Date(resume.created_at).toLocaleDateString('en-IN')}.{' '}
          <Link href="/dashboard" className="font-semibold underline">View analysis</Link>
        </p>
      )}
      {searchParams.error && <p role="alert" className="mt-5 rounded-lg bg-rust-soft px-4 py-3 text-sm text-rust">{searchParams.error}</p>}

      <form action={uploadResume} className="mt-6 space-y-4">
        <label className="flex cursor-pointer flex-col items-center rounded-2xl border-2 border-dashed border-line bg-white px-6 py-12 text-center transition-colors hover:border-brand hover:bg-brand-soft/40">
          <span className="font-display text-xl font-bold">Choose your resume file</span>
          <span className="mt-1 text-sm text-ink/60">PDF or DOCX, up to 4 MB</span>
          <input type="file" name="resume" accept=".pdf,.docx" required
                 className="mt-5 text-sm file:mr-3 file:cursor-pointer file:rounded-lg file:border-0 file:bg-brand file:px-4 file:py-2 file:font-semibold file:text-white" />
        </label>
        <SubmitButton pending="Analyzing your resume...">Upload and analyze</SubmitButton>
      </form>
    </div>
  );
}
