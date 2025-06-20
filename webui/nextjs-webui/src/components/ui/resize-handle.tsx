'use client';

import { useEffect, useRef } from 'react';

interface ResizeHandleProps {
  onResize: (delta: number) => void;
  onStartDrag: () => void;
  onEndDrag: () => void;
  orientation?: 'vertical' | 'horizontal';
  className?: string;
}

export function ResizeHandle({
  onResize,
  onStartDrag,
  onEndDrag,
  orientation = 'vertical',
  className = ''
}: ResizeHandleProps) {
  const startXRef = useRef<number>(0);
  const startYRef = useRef<number>(0);
  const isDraggingRef = useRef(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;

      const delta = orientation === 'vertical' 
        ? e.clientX - startXRef.current
        : e.clientY - startYRef.current;

      onResize(delta);
      
      if (orientation === 'vertical') {
        startXRef.current = e.clientX;
      } else {
        startYRef.current = e.clientY;
      }
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        onEndDrag();
      }
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [onResize, onEndDrag, orientation]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    isDraggingRef.current = true;
    startXRef.current = e.clientX;
    startYRef.current = e.clientY;
    onStartDrag();
  };

  const baseClasses = orientation === 'vertical'
    ? 'w-1 h-full cursor-col-resize hover:bg-blue-500/30 transition-colors'
    : 'h-1 w-full cursor-row-resize hover:bg-blue-500/30 transition-colors';

  return (
    <div
      className={`${baseClasses} ${className} group relative`}
      onMouseDown={handleMouseDown}
    >
      {/* Visual indicator on hover */}
      <div 
        className={`
          absolute bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity
          ${orientation === 'vertical' 
            ? 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-0.5 h-12' 
            : 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-0.5 w-12'}
        `}
      />
    </div>
  );
}