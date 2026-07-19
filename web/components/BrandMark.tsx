export function BrandMark({ size = 36 }: { size?: number }) {
  return (
    <svg
      aria-hidden="true"
      className="brand-mark"
      height={size}
      viewBox="0 0 48 48"
      width={size}
    >
      <path
        d="M24 5c-8.3 0-14 7.1-14 17.2C10 33.9 16.8 42 24 43c7.2-1 14-9.1 14-20.8C38 12.1 32.3 5 24 5Z"
        fill="currentColor"
      />
      <path d="M24 9v30M17 11.8c3.3 6.6 3.3 16.5 0 24.6M31 11.8c-3.3 6.6-3.3 16.5 0 24.6" fill="none" stroke="#fff" strokeLinecap="round" strokeWidth="2.2" />
      <path d="M24 5c1.4-2.1 3.2-3.3 5.5-3.5" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="3" />
    </svg>
  );
}
