export default function Logo({ light = false }: { light?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2 font-display text-xl font-bold">
      <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
        <rect width="28" height="28" rx="8" fill="#2F54EB" />
        <path d="M8 20 L14 7 L20 20 L14 16 Z" fill="#fff" />
        <circle cx="14" cy="21.5" r="1.6" fill="#FF9F1C" />
      </svg>
      <span className={light ? 'text-white' : 'text-ink'}>Pathfinder</span>
    </span>
  );
}
