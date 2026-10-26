const tones = {
  have: 'bg-good-soft text-good-dark',
  partial: 'bg-amber-soft text-amber-dark',
  missing: 'bg-rust-soft text-rust',
  brand: 'bg-brand-soft text-brand-dark',
  plain: 'bg-white border border-line text-ink',
};
export default function Chip({ children, tone = 'plain', title }: { children: React.ReactNode; tone?: keyof typeof tones; title?: string }) {
  return <span title={title} className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${tones[tone]}`}>{children}</span>;
}
