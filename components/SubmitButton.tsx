'use client';
import { useFormStatus } from 'react-dom';

export default function SubmitButton({ children, pending = 'Working...', className = 'btn' }:
  { children: React.ReactNode; pending?: string; className?: string }) {
  const { pending: busy } = useFormStatus();
  return <button className={className} disabled={busy}>{busy ? pending : children}</button>;
}
