// Layout configuration types for GAIA-BT UI/UX improvement

export type LayoutMode = 'compact' | 'normal' | 'spacious';
export type ThemeMode = 'light' | 'dark' | 'auto';

export interface LayoutConfig {
  mode: LayoutMode;
  sidebarWidth: number;
  sidebarCollapsed: boolean;
  theme: ThemeMode;
  animations: boolean;
  fontSize: 'small' | 'medium' | 'large';
  density: 'compact' | 'normal' | 'comfortable';
}

export interface GridConfig {
  columns: number;
  gap: string;
  containerWidth: string;
  padding: string;
}

export interface ResponsiveBreakpoint {
  minWidth: number;
  sidebarWidth: number;
  gridConfig: GridConfig;
  showSidebar: boolean;
  layoutMode: LayoutMode;
}

export const LAYOUT_BREAKPOINTS: ResponsiveBreakpoint[] = [
  {
    minWidth: 2560,
    sidebarWidth: 384,
    showSidebar: true,
    layoutMode: 'spacious',
    gridConfig: {
      columns: 2,
      gap: 'gap-8',
      containerWidth: 'max-w-screen-2xl',
      padding: 'p-8'
    }
  },
  {
    minWidth: 1920,
    sidebarWidth: 320,
    showSidebar: true,
    layoutMode: 'spacious',
    gridConfig: {
      columns: 1,
      gap: 'gap-6',
      containerWidth: 'max-w-6xl',
      padding: 'p-6'
    }
  },
  {
    minWidth: 1440,
    sidebarWidth: 288,
    showSidebar: true,
    layoutMode: 'normal',
    gridConfig: {
      columns: 1,
      gap: 'gap-5',
      containerWidth: 'max-w-5xl',
      padding: 'p-5'
    }
  },
  {
    minWidth: 1200,
    sidebarWidth: 256,
    showSidebar: true,
    layoutMode: 'normal',
    gridConfig: {
      columns: 1,
      gap: 'gap-4',
      containerWidth: 'max-w-4xl',
      padding: 'p-4'
    }
  },
  {
    minWidth: 1024,
    sidebarWidth: 224,
    showSidebar: true,
    layoutMode: 'compact',
    gridConfig: {
      columns: 1,
      gap: 'gap-3',
      containerWidth: 'max-w-3xl',
      padding: 'p-3'
    }
  },
  {
    minWidth: 768,
    sidebarWidth: 192,
    showSidebar: false,
    layoutMode: 'compact',
    gridConfig: {
      columns: 1,
      gap: 'gap-3',
      containerWidth: 'max-w-2xl',
      padding: 'p-3'
    }
  },
  {
    minWidth: 0,
    sidebarWidth: 320,
    showSidebar: false,
    layoutMode: 'compact',
    gridConfig: {
      columns: 1,
      gap: 'gap-2',
      containerWidth: 'max-w-sm',
      padding: 'p-2'
    }
  }
];

export const DEFAULT_LAYOUT_CONFIG: LayoutConfig = {
  mode: 'normal',
  sidebarWidth: 288,
  sidebarCollapsed: false,
  theme: 'auto',
  animations: true,
  fontSize: 'medium',
  density: 'normal'
};