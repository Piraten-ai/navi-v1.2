import { useState, useEffect, ReactNode } from 'react';
import { SettingsContext, Settings, WidgetConfig } from './SettingsContext';

const DEFAULT_SETTINGS: Settings = {
  naviPrompts: true, // Hey Listen! enabled by default
  battleModeKey: 'b',
  idleTimeout: 60000,
  showScreensaver: true,
  theme: 'arctic',
  widgets: [
    { id: 'speed', type: 'gauge', position: { x: 0, y: 0 }, size: { w: 2, h: 2 }, visible: true },
    { id: 'heading', type: 'gauge', position: { x: 2, y: 0 }, size: { w: 2, h: 2 }, visible: true },
    { id: 'depth', type: 'gauge', position: { x: 0, y: 2 }, size: { w: 2, h: 2 }, visible: true },
    { id: 'temp', type: 'gauge', position: { x: 2, y: 2 }, size: { w: 2, h: 2 }, visible: true },
  ],
};

// SettingsProvider component only

export const SettingsProvider = ({ children }: { children: ReactNode }) => {
  const [settings, setSettings] = useState<Settings>(() => {
    const saved = localStorage.getItem('aads-settings');
    if (saved) {
      try {
        return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
      } catch {
        return DEFAULT_SETTINGS;
      }
    }
    return DEFAULT_SETTINGS;
  });

  useEffect(() => {
    localStorage.setItem('aads-settings', JSON.stringify(settings));
  }, [settings]);

  const updateSettings = (updates: Partial<Settings>) => {
    setSettings(prev => ({ ...prev, ...updates }));
  };

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
    localStorage.removeItem('aads-settings');
  };

  const toggleNaviPrompts = () => {
    setSettings(prev => ({ ...prev, naviPrompts: !prev.naviPrompts }));
  };

  const updateWidget = (widgetId: string, updates: Partial<WidgetConfig>) => {
    setSettings(prev => ({
      ...prev,
      widgets: prev.widgets.map(w => 
        w.id === widgetId ? { ...w, ...updates } : w
      ),
    }));
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, resetSettings, toggleNaviPrompts, updateWidget }}>
      {children}
    </SettingsContext.Provider>
  );
};


