'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { logout } from '@/app/actions';
import Logo from './Logo';

const links = [['Dashboard', '/dashboard'], ['Resume', '/upload'], ['Jobs', '/jobs'], ['Visited', '/visited']];

export default function Nav({ email }: { email?: string }) {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-10 border-b border-line bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-2 gap-y-1 px-4 py-2 text-sm font-semibold sm:px-6 md:flex-nowrap md:py-3">
        <Link href="/dashboard" className="mr-2 shrink-0 md:mr-4"><Logo /></Link>

        <div className="no-scrollbar order-last flex w-full gap-1 overflow-x-auto pb-1 md:order-none md:w-auto md:overflow-visible md:pb-0">
          {links.map(([label, href]) => (
            <Link key={href} href={href}
              className={`shrink-0 whitespace-nowrap rounded-lg px-3 py-2 transition-colors ${path.startsWith(href) ? 'bg-brand-soft text-brand-dark' : 'text-ink/70 hover:bg-paper hover:text-ink'}`}>
              {label}
            </Link>
          ))}
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-1 sm:gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ink text-xs font-bold uppercase text-white" title={email}>
            {email?.[0] ?? '?'}
          </span>
          <form action={logout}><button className="rounded-lg px-2 py-2 text-ink/70 hover:bg-rust-soft hover:text-rust sm:px-3">Log out</button></form>
        </div>
      </nav>
    </header>
  );
}
