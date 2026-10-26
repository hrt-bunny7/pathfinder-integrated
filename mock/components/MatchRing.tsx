// The signature element: a ring gauge for match %
export default function MatchRing({ value, size = 64 }: { value: number; size?: number }) {
  const stroke = size > 70 ? 7 : 5;
  const r = size / 2 - stroke;
  const c = 2 * Math.PI * r;
  const color = value >= 70 ? '#12A150' : value >= 40 ? '#FF9F1C' : '#D93F2B';
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }} role="img" aria-label={`${value}% match`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E4E9F3" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round"
                strokeDasharray={c} strokeDashoffset={c - (c * Math.min(value, 100)) / 100} />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center font-display font-bold" style={{ fontSize: size / 3.6 }}>
        {value}<span style={{ fontSize: size / 6 }}>%</span>
      </span>
    </div>
  );
}
