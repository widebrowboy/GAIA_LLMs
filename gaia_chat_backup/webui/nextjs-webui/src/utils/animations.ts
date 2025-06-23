// Animation configurations and utilities for GAIA-BT

import { Variants, Transition } from 'framer-motion';

// Animation presets
export const animationPresets = {
  // Easing functions
  easing: {
    smooth: [0.25, 0.46, 0.45, 0.94],
    bounce: [0.68, -0.55, 0.265, 1.55],
    elastic: [0.175, 0.885, 0.32, 1.275],
    sharp: [0.4, 0, 0.2, 1],
  },
  
  // Duration presets
  duration: {
    fast: 0.15,
    normal: 0.3,
    slow: 0.5,
    slower: 0.8,
  },
  
  // Common transitions
  transition: {
    smooth: {
      type: "tween",
      ease: [0.25, 0.46, 0.45, 0.94],
      duration: 0.3,
    },
    bounce: {
      type: "spring",
      damping: 15,
      stiffness: 300,
    },
    elastic: {
      type: "spring",
      damping: 10,
      stiffness: 100,
    },
    gentle: {
      type: "spring",
      damping: 20,
      stiffness: 100,
    },
  } as Record<string, Transition>,
};

// Page transition variants
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.98,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: animationPresets.transition.smooth,
  },
  exit: {
    opacity: 0,
    y: -20,
    scale: 0.98,
    transition: animationPresets.transition.smooth,
  },
};

// Message animation variants
export const messageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 30,
    scale: 0.9,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      ...animationPresets.transition.gentle,
      duration: 0.4,
    },
  },
  exit: {
    opacity: 0,
    x: -100,
    scale: 0.8,
    transition: animationPresets.transition.smooth,
  },
  hover: {
    scale: 1.02,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 300,
    },
  },
};

// Button animation variants
export const buttonVariants: Variants = {
  initial: {
    scale: 1,
  },
  hover: {
    scale: 1.05,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 400,
    },
  },
  tap: {
    scale: 0.95,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 400,
    },
  },
  loading: {
    scale: [1, 1.1, 1],
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Modal animation variants
export const modalVariants: Variants = {
  initial: {
    opacity: 0,
    scale: 0.8,
    y: 50,
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      ...animationPresets.transition.bounce,
      duration: 0.4,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    y: 50,
    transition: animationPresets.transition.smooth,
  },
};

// Sidebar animation variants
export const sidebarVariants: Variants = {
  closed: {
    x: "-100%",
    transition: animationPresets.transition.smooth,
  },
  open: {
    x: 0,
    transition: animationPresets.transition.smooth,
  },
};

// Floating animation variants
export const floatingVariants: Variants = {
  animate: {
    y: [-2, 2, -2],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Skeleton loading variants
export const skeletonVariants: Variants = {
  initial: {
    opacity: 0.6,
  },
  animate: {
    opacity: [0.6, 1, 0.6],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Stagger animation for lists
export const staggerContainerVariants: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

export const staggerItemVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: animationPresets.transition.gentle,
  },
};

// Notification animation variants
export const notificationVariants: Variants = {
  initial: {
    opacity: 0,
    x: 100,
    scale: 0.8,
  },
  animate: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: animationPresets.transition.bounce,
  },
  exit: {
    opacity: 0,
    x: 100,
    scale: 0.8,
    transition: animationPresets.transition.smooth,
  },
};

// Card hover effects
export const cardVariants: Variants = {
  initial: {
    scale: 1,
    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
  },
  hover: {
    scale: 1.02,
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 300,
    },
  },
  tap: {
    scale: 0.98,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 400,
    },
  },
};

// Loading dots animation
export const loadingDotsVariants: Variants = {
  initial: {
    y: 0,
  },
  animate: {
    y: [-8, 0, -8],
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Progress bar animation
export const progressVariants: Variants = {
  initial: {
    scaleX: 0,
    originX: 0,
  },
  animate: {
    scaleX: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
};

// Typing indicator animation
export const typingVariants: Variants = {
  initial: {
    opacity: 0,
    scale: 0.8,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      ...animationPresets.transition.gentle,
      duration: 0.3,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    transition: {
      duration: 0.2,
    },
  },
};

// Utility functions for conditional animations
export const getAnimationProps = (
  enableAnimations: boolean,
  variants: Variants,
  options?: {
    initial?: string;
    animate?: string;
    exit?: string;
    whileHover?: string;
    whileTap?: string;
  }
) => {
  if (!enableAnimations) {
    return {};
  }

  return {
    variants,
    initial: options?.initial || "initial",
    animate: options?.animate || "animate",
    exit: options?.exit || "exit",
    whileHover: options?.whileHover || "hover",
    whileTap: options?.whileTap || "tap",
  };
};

// Animation delay utilities
export const createStaggerDelay = (index: number, baseDelay: number = 0.1) => ({
  delay: baseDelay * index,
});

export const createRandomDelay = (min: number = 0, max: number = 0.5) => ({
  delay: Math.random() * (max - min) + min,
});

// Reduced motion utilities
export const getReducedMotionProps = () => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return {
      initial: false,
      animate: !prefersReducedMotion,
      transition: prefersReducedMotion ? { duration: 0 } : undefined,
    };
  }
  return {};
};