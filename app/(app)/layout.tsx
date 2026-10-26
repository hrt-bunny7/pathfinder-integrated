import Nav from '@/components/Nav';
import { createClient } from '@/lib/supabase/server';

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { data: { user } } = await createClient().auth.getUser();
  return (
    <>
      <Nav email={user?.email} />
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </>
  );
}
