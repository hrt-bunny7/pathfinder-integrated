import Link from 'next/link';
import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import Logo from '@/components/Logo';
import MatchRing from '@/components/MatchRing';
import Chip from '@/components/Chip';

const demo = [
  { title: 'Python Backend Developer', co: 'DataNest, Pune', score: 78, have: ['Python', 'SQL', 'Git'], miss: ['Docker', 'Redis'] },
  { title: 'Data Analyst', co: 'InsightWorks, Hyderabad', score: 64, have: ['SQL', 'Python'], miss: ['Power BI', 'Tableau'] },
  { title: 'DevOps Engineer', co: 'CloudLoom, Noida', score: 32, have: ['Linux'], miss: ['Kubernetes', 'AWS'] },
];

const steps = [
  ['Upload your resume', 'Drop in a PDF or DOCX. We read your skills and sort them by area.'],
  ['See jobs ranked by fit', 'Every opening gets a match percentage, with the skills you have and the ones you lack.'],
  ['Follow your roadmap', 'Pick a job and get a week-by-week plan. Tick off each week and watch your match rise.'],
];

export default async function Landing() {
  const { data: { user } } = await createClient().auth.getUser();
  if (user) redirect('/dashboard');
  return (
    <div className="min-h-screen" style={{ backgroundImage: 'radial-gradient(#DCE2EE 1px, transparent 1px)', backgroundSize: '22px 22px' }}>
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Logo />
        <div className="flex items-center gap-2">
          <Link href="/login" className="rounded-lg px-4 py-2 text-sm font-semibold hover:bg-white">Log in</Link>
          <Link href="/signup" className="btn">Sign up free</Link>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl items-center gap-12 px-6 pb-20 pt-12 lg:grid-cols-[1.05fr_1fr]">
        <div>
          <h1 className="font-display text-5xl font-extrabold leading-[1.05] tracking-tight sm:text-6xl">
            Find jobs that fit you. Learn what is missing.
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-ink/75">
            Upload your resume and Pathfinder shows which openings suit your skills, exactly what you are missing for
            the one you pick, and a plan to close the gap.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link href="/signup" className="btn px-6 py-3 text-base">Create free account</Link>
            <Link href="/login" className="btn-ghost px-6 py-3 text-base">Log in</Link>
          </div>
          <p className="mt-4 text-sm text-ink/60">Free to use. Works with PDF and DOCX resumes.</p>
        </div>

        <div className="relative space-y-4 lg:pl-6" aria-label="Example job matches">
          {demo.map((d, i) => (
            <div key={d.title} className="rounded-2xl border border-line bg-white p-5 shadow-[0_12px_30px_-12px_rgba(16,25,54,0.25)]"
                 style={{ marginLeft: i === 1 ? 28 : 0, marginRight: i === 1 ? 0 : 28 }}>
              <div className="flex items-center gap-4">
                <MatchRing value={d.score} size={60} />
                <div>
                  <p className="font-display text-lg font-bold leading-tight">{d.title}</p>
                  <p className="text-sm text-ink/60">{d.co}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {d.have.map((s) => <Chip key={s} tone="have">{s}</Chip>)}
                {d.miss.map((s) => <Chip key={s} tone="missing">{s}</Chip>)}
              </div>
            </div>
          ))}
        </div>
      </main>

      <section className="border-t border-line bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="font-display text-3xl font-bold">How it works</h2>
          <ol className="mt-8 grid gap-6 md:grid-cols-3">
            {steps.map(([t, d], i) => (
              <li key={t} className="rounded-xl bg-paper p-6">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand font-display font-bold text-white">{i + 1}</span>
                <h3 className="mt-4 font-display text-xl font-bold">{t}</h3>
                <p className="mt-2 text-ink/75">{d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>
      <footer className="bg-ink py-6 text-center text-sm text-white/70">Pathfinder: a student career assistant project</footer>
    </div>
  );
}
