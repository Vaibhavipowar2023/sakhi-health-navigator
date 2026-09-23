/**
 * Sakhi logo — stylized woman silhouette with flowing elements.
 * Represents freedom, strength, and care.
 */
export default function Logo({ size = 48, className = "" }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* outer glow circle */}
      <circle cx="60" cy="60" r="58" fill="url(#glow)" opacity="0.15" />

      {/* main circle */}
      <circle cx="60" cy="60" r="50" fill="url(#gradient)" />

      {/* woman silhouette — head */}
      <circle cx="60" cy="38" r="10" fill="white" />

      {/* body — flowing dress/figure */}
      <path
        d="M60 48 C60 48, 45 58, 42 78 C40 88, 50 92, 60 92 C70 92, 80 88, 78 78 C75 58, 60 48, 60 48Z"
        fill="white"
        opacity="0.95"
      />

      {/* arms spread open — freedom pose */}
      <path
        d="M48 56 C42 52, 32 48, 26 50 C24 51, 24 54, 28 55 C34 57, 42 58, 48 58Z"
        fill="white"
        opacity="0.9"
      />
      <path
        d="M72 56 C78 52, 88 48, 94 50 C96 51, 96 54, 92 55 C86 57, 78 58, 72 58Z"
        fill="white"
        opacity="0.9"
      />

      {/* heart symbol at center */}
      <path
        d="M55 68 C55 65, 52 63, 50 63 C47 63, 45 66, 45 68 C45 72, 55 78, 55 78 C55 78, 65 72, 65 68 C65 66, 63 63, 60 63 C58 63, 55 65, 55 68Z"
        fill="url(#heart)"
        opacity="0.85"
      />

      {/* flowing hair strands */}
      <path
        d="M50 34 C46 30, 40 32, 38 38 C36 44, 40 48, 44 50"
        stroke="white"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        opacity="0.7"
      />
      <path
        d="M70 34 C74 30, 80 32, 82 38 C84 44, 80 48, 76 50"
        stroke="white"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        opacity="0.7"
      />

      <defs>
        <linearGradient id="gradient" x1="10" y1="10" x2="110" y2="110">
          <stop offset="0%" stopColor="#8B5CF6" />
          <stop offset="50%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
        <radialGradient id="glow" cx="60" cy="60" r="58">
          <stop offset="0%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#A855F7" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="heart" x1="45" y1="63" x2="65" y2="78">
          <stop offset="0%" stopColor="#F472B6" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
      </defs>
    </svg>
  );
}
