import { createContext } from 'react';

export interface Settings {
  naviPrompts: boolean;
  battleModeKey: string;
  idleTimeout: number;
  showScreensaver: boolean;
  theme: 'arctic' | 'battle';
  widgets: WidgetConfig[];
}

export interface WidgetConfig {
  id: string;
  type: string;
  position: { x: number; y: number };
  size: { w: number; h: number };
  visible: boolean;
}

export interface SettingsContextType {
  settings: Settings;
  updateSettings: (updates: Partial<Settings>) => void;
  resetSettings: () => void;
  toggleNaviPrompts: () => void;
  updateWidget: (widgetId: string, updates: Partial<WidgetConfig>) => void;
}

export const SettingsContext = createContext<SettingsContextType | undefined>(undefined);
