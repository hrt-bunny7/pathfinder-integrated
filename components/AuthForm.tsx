'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import Logo from './Logo';

export default function AuthForm({ mode }: { mode: 'login' | 'signup' }) {
  const router = useRouter();
  const supabase = createClient();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true); setError(''); setInfo('');
    if (mode === 'signup') {
      const { data, error } = await supabase.auth.signUp({
        email, password,
        options: { data: { full_name: name }, emailRedirectTo: `${location.origin}/auth/callback` },
      });
      if (error) setError(error.message);
      else if (!data.session) setInfo('Check your email and click the confirmation link to finish signing up.');
      else { router.push('/dashboard'); router.refresh(); }
    } else {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) setError(error.message);
      else { router.push('/dashboard'); router.refresh(); }
    }
    setBusy(false);
  }

  async function google() {
    await supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: `${location.origin}/auth/callback` } });
  }

  return (
    <div className="grid min-h-screen md:grid-cols-[1fr_1.1fr]">
      <aside className="hidden flex-col justify-between bg-ink p-10 text-white md:flex">
        <Link href="/"><Logo light /></Link>
        <div>
          <p className="font-display text-4xl font-bold leading-tight">Know where you stand, then close the gap.</p>
          <ul className="mt-8 space-y-3 text-white/80">
            <li>Skills read from your resume</li>
            <li>Jobs ranked by how well you fit</li>
            <li>A weekly plan for every missing skill</li>
          </ul>
        </div>
        <p className="text-sm text-white/50">Your resume stays private to your account.</p>
      </aside>

      <main className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <Link href="/" className="md:hidden"><Logo /></Link>
          <h1 className="mt-6 font-display text-3xl font-bold md:mt-0">{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1>
          <p className="mt-1 text-sm text-ink/70">{mode === 'login' ? 'Log in to see your matches.' : 'It takes less than a minute.'}</p>
          <form onSubmit={submit} className="mt-6 space-y-3">
            {mode === 'signup' && <input className="field" placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} required />}
            <input className="field" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <input className="field" type="password" placeholder="Password (min 6 characters)" minLength={6}
                   value={password} onChange={(e) => setPassword(e.target.value)} required />
            {error && <p role="alert" className="rounded-lg bg-rust-soft px-3 py-2 text-sm text-rust">{error}</p>}
            {info && <p className="rounded-lg bg-good-soft px-3 py-2 text-sm text-good-dark">{info}</p>}
            <button className="btn w-full py-3" disabled={busy}>{busy ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Sign up'}</button>
          </form>
          <div className="my-4 flex items-center gap-3 text-xs text-ink/50"><span className="h-px flex-1 bg-line" />or<span className="h-px flex-1 bg-line" /></div>
          <button onClick={google} className="btn-ghost w-full py-3">Continue with Google</button>
          <p className="mt-6 text-sm text-ink/70">
            {mode === 'login' ? 'New here? ' : 'Already have an account? '}
            <Link className="font-semibold text-brand underline" href={mode === 'login' ? '/signup' : '/login'}>
              {mode === 'login' ? 'Create an account' : 'Log in'}
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
