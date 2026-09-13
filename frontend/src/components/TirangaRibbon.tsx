import React from 'react';

interface TirangaRibbonProps {
  height?: number | string;
  showChakra?: boolean;
  className?: string;
}

export const TirangaRibbon: React.FC<TirangaRibbonProps> = ({
  height = 4,
  className = '',
}) => {
  return (
    <div
      className={`w-full flex select-none overflow-hidden ${className}`}
      style={{ height }}
      role="presentation"
      title="Tiranga - Flag of India (Saffron, White, India Green)"
    >
      {/* Saffron (Kesari) Stripe */}
      <div className="flex-1 bg-[#FF671F]" />
      {/* White Stripe with Navy Ashoka Blue Accent */}
      <div className="flex-1 bg-white relative flex items-center justify-center">
        <div className="w-1.5 h-1.5 rounded-full bg-[#000080]" />
      </div>
      {/* India Green (Kavach) Stripe */}
      <div className="flex-1 bg-[#046A38]" />
    </div>
  );
};
