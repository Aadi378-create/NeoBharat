import React from 'react';

interface ChakraLogoProps {
  size?: number;
  className?: string;
  animate?: boolean;
}

export const ChakraLogo: React.FC<ChakraLogoProps> = ({
  size = 48,
  className = '',
  animate = false,
}) => {
  // Ashoka Chakra has exactly 24 spokes spaced at 15 degrees (360 / 24 = 15 deg)
  const spokes = Array.from({ length: 24 }, (_, i) => i * 15);
  // Navy Blue color strictly defined by the Flag code: #000080 (Navy Blue)
  const CHAKRA_BLUE = '#000080';

  return (
    <div
      className={`inline-flex items-center justify-center relative select-none ${className}`}
      style={{ width: size, height: size }}
      title="Ashoka Chakra - 24 Spokes (Dharmachakra)"
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`w-full h-full drop-shadow-sm ${animate ? 'animate-spin-slow' : ''}`}
        style={animate ? { animation: 'spin 40s linear infinite' } : undefined}
      >
        {/* Outer White backing for crisp visibility on dark or light backgrounds */}
        <circle cx="50" cy="50" r="47.5" fill="#FFFFFF" fillOpacity="0.96" />

        {/* Outer Heavy Rim in Ashoka Navy Blue */}
        <circle
          cx="50"
          cy="50"
          r="46"
          stroke={CHAKRA_BLUE}
          strokeWidth="3.2"
          fill="none"
        />

        {/* Inner Border Rim */}
        <circle
          cx="50"
          cy="50"
          r="41.5"
          stroke={CHAKRA_BLUE}
          strokeWidth="1.2"
          fill="none"
        />

        {/* 24 Outer Semicircle Petals between rims */}
        {spokes.map((angle) => {
          const rad = (angle * Math.PI) / 180;
          const x = 50 + 43.8 * Math.cos(rad);
          const y = 50 + 43.8 * Math.sin(rad);
          return (
            <circle
              key={`petal-${angle}`}
              cx={x}
              cy={y}
              r="1.4"
              fill={CHAKRA_BLUE}
            />
          );
        })}

        {/* 24 Spoke Lines radiating from center to inner rim */}
        {spokes.map((angle) => (
          <g key={`spoke-${angle}`} transform={`rotate(${angle} 50 50)`}>
            {/* Triangular tapered spoke shape for authentic Indian Flag Chakra representation */}
            <polygon
              points="49.3,50 50.7,50 51.1,10 48.9,10"
              fill={CHAKRA_BLUE}
            />
          </g>
        ))}

        {/* Central Outer Ring */}
        <circle
          cx="50"
          cy="50"
          r="10.5"
          stroke={CHAKRA_BLUE}
          strokeWidth="1.8"
          fill="#FFFFFF"
        />

        {/* Central Hub Disc */}
        <circle cx="50" cy="50" r="6" fill={CHAKRA_BLUE} />

        {/* Central Point */}
        <circle cx="50" cy="50" r="2" fill="#FFFFFF" />
      </svg>
    </div>
  );
};
