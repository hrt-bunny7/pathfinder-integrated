'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { logout } from '@/app/actions';
import Logo from './Logo';

const links = [['Dashboard', '/dashboard'], ['Resume', '/upload'], ['Jobs', '/jobs']];

export default function Nav({ email }: { email?: string }) {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-10 border-b border-line bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center gap-2 px-6 py-3 text-sm font-semibold">
        <Link href="/dashboard" className="mr-4"><Logo /></Link>
        {links.map(([label, href]) => (
          <Link key={href} href={href}
            className={`rounded-lg px-3 py-2 transition-colors ${path.startsWith(href) ? 'bg-brand-soft text-brand-dark' : 'text-ink/70 hover:bg-paper hover:text-ink'}`}>
            {label}
          </Link>
        ))}
        <div className="ml-auto flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ink text-xs font-bold uppercase text-white" title={email}>
            {email?.[0] ?? '?'}
          </span>
          <form action={logout}><button className="rounded-lg px-3 py-2 text-ink/70 hover:bg-rust-soft hover:text-rust">Log out</button></form>
        </div>
      </nav>
    </header>
  );
}
