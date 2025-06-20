'use client';

import { motion } from 'framer-motion';
import { skeletonVariants } from '@/utils/animations';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  animated?: boolean;
}

export function Skeleton({ 
  className = '', 
  width = '100%',
  height = '1rem',
  borderRadius = '0.375rem',
  animated = true
}: SkeletonProps) {
  const Component = animated ? motion.div : 'div';
  
  const animationProps = animated ? {
    variants: skeletonVariants,
    initial: "initial",
    animate: "animate"
  } : {};

  return (
    <Component
      className={`bg-gray-200 dark:bg-gray-700 ${className}`}
      style={{
        width,
        height,
        borderRadius,
      }}
      {...animationProps}
    />
  );
}

// Skeleton presets for common UI elements
export function MessageSkeleton({ animated = true }: { animated?: boolean }) {
  return (
    <div className="space-y-3 p-4">
      <div className="flex items-center space-x-3">
        <Skeleton width={32} height={32} borderRadius="50%" animated={animated} />
        <div className="space-y-1">
          <Skeleton width={80} height={12} animated={animated} />
          <Skeleton width={60} height={10} animated={animated} />
        </div>
      </div>
      <div className="space-y-2 ml-11">
        <Skeleton width="100%" height={16} animated={animated} />
        <Skeleton width="85%" height={16} animated={animated} />
        <Skeleton width="92%" height={16} animated={animated} />
      </div>
    </div>
  );
}

export function ChatSkeleton({ count = 3, animated = true }: { count?: number; animated?: boolean }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }, (_, i) => (
        <MessageSkeleton key={i} animated={animated} />
      ))}
    </div>
  );
}

export function CardSkeleton({ animated = true }: { animated?: boolean }) {
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center space-x-3">
        <Skeleton width={40} height={40} borderRadius="0.5rem" animated={animated} />
        <div className="space-y-2 flex-1">
          <Skeleton width="60%" height={16} animated={animated} />
          <Skeleton width="40%" height={12} animated={animated} />
        </div>
      </div>
      <div className="space-y-2">
        <Skeleton width="100%" height={14} animated={animated} />
        <Skeleton width="90%" height={14} animated={animated} />
        <Skeleton width="75%" height={14} animated={animated} />
      </div>
      <div className="flex space-x-2">
        <Skeleton width={60} height={24} borderRadius="1rem" animated={animated} />
        <Skeleton width={80} height={24} borderRadius="1rem" animated={animated} />
      </div>
    </div>
  );
}

export function ButtonSkeleton({ 
  width = 100, 
  height = 36,
  animated = true 
}: { 
  width?: number; 
  height?: number; 
  animated?: boolean; 
}) {
  return (
    <Skeleton 
      width={width} 
      height={height} 
      borderRadius="0.375rem" 
      animated={animated} 
    />
  );
}

export function AvatarSkeleton({ 
  size = 40, 
  animated = true 
}: { 
  size?: number; 
  animated?: boolean; 
}) {
  return (
    <Skeleton 
      width={size} 
      height={size} 
      borderRadius="50%" 
      animated={animated} 
    />
  );
}

export function TextSkeleton({ 
  lines = 3, 
  animated = true 
}: { 
  lines?: number; 
  animated?: boolean; 
}) {
  const widths = ['100%', '85%', '92%', '78%', '95%'];
  
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton 
          key={i}
          width={widths[i % widths.length]}
          height={16}
          animated={animated}
        />
      ))}
    </div>
  );
}