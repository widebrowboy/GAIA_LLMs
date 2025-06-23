'use client';

import { useState, useEffect, useCallback } from 'react';
import { LayoutConfig, LAYOUT_BREAKPOINTS, DEFAULT_LAYOUT_CONFIG } from '@/types/layout';

const STORAGE_KEY = 'gaia-bt-layout-config';

export function useLayoutConfig() {
  const [config, setConfig] = useState<LayoutConfig>(DEFAULT_LAYOUT_CONFIG);
  const [isDragging, setIsDragging] = useState(false);
  const [currentBreakpoint, setCurrentBreakpoint] = useState(LAYOUT_BREAKPOINTS[0]);

  // Load saved config from localStorage
  useEffect(() => {
    const savedConfig = localStorage.getItem(STORAGE_KEY);
    if (savedConfig) {
      try {
        const parsed = JSON.parse(savedConfig);
        setConfig({ ...DEFAULT_LAYOUT_CONFIG, ...parsed });
      } catch (e) {
        console.error('Failed to parse saved layout config:', e);
      }
    }

    // Apply theme
    applyTheme(config.theme);
  }, []);

  // Save config to localStorage when it changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  // Update breakpoint based on window size
  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth;
      const breakpoint = LAYOUT_BREAKPOINTS.find(bp => width >= bp.minWidth) || LAYOUT_BREAKPOINTS[LAYOUT_BREAKPOINTS.length - 1];
      setCurrentBreakpoint(breakpoint);
    };

    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
    return () => window.removeEventListener('resize', updateBreakpoint);
  }, []);

  // Apply theme to document
  const applyTheme = useCallback((theme: LayoutConfig['theme']) => {
    const root = document.documentElement;
    
    if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    } else {
      root.classList.toggle('dark', theme === 'dark');
    }
  }, []);

  // Update specific config property
  const updateConfig = useCallback((updates: Partial<LayoutConfig>) => {
    setConfig(prev => {
      const newConfig = { ...prev, ...updates };
      
      if (updates.theme !== undefined) {
        applyTheme(updates.theme);
      }
      
      return newConfig;
    });
  }, [applyTheme]);

  // Handle sidebar resize
  const handleSidebarResize = useCallback((delta: number) => {
    setConfig(prev => ({
      ...prev,
      sidebarWidth: Math.max(192, Math.min(480, prev.sidebarWidth + delta))
    }));
  }, []);

  // Start dragging
  const startDragging = useCallback(() => {
    setIsDragging(true);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, []);

  // Stop dragging
  const stopDragging = useCallback(() => {
    setIsDragging(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  // Toggle sidebar collapse
  const toggleSidebarCollapse = useCallback(() => {
    updateConfig({ sidebarCollapsed: !config.sidebarCollapsed });
  }, [config.sidebarCollapsed, updateConfig]);

  // Cycle through layout modes
  const cycleLayoutMode = useCallback(() => {
    const modes: LayoutConfig['mode'][] = ['compact', 'normal', 'spacious'];
    const currentIndex = modes.indexOf(config.mode);
    const nextIndex = (currentIndex + 1) % modes.length;
    updateConfig({ mode: modes[nextIndex] });
  }, [config.mode, updateConfig]);

  // Reset to defaults
  const resetToDefaults = useCallback(() => {
    setConfig(DEFAULT_LAYOUT_CONFIG);
    applyTheme(DEFAULT_LAYOUT_CONFIG.theme);
    localStorage.removeItem(STORAGE_KEY);
  }, [applyTheme]);

  return {
    config,
    currentBreakpoint,
    isDragging,
    updateConfig,
    handleSidebarResize,
    startDragging,
    stopDragging,
    toggleSidebarCollapse,
    cycleLayoutMode,
    resetToDefaults
  };
}