import React from 'react';
import { useSettings } from '../hooks/useSettingsContext';

interface SettingsProps {
  onClose: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ onClose }) => {
  const { settings, updateSettings, toggleNaviPrompts, resetSettings } = useSettings();

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>SYSTEM SETTINGS</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="settings-content">
          {/* Navi Prompts */}
          <div className="setting-group">
            <h3>NAVI ASSISTANT</h3>
            <div className="setting-item">
              <label>
                <input
                  id="navi-prompts"
                  name="naviPrompts"
                  type="checkbox"
                  checked={settings.naviPrompts}
                  onChange={toggleNaviPrompts}
                />
                <span>Enable "Hey! Listen!" Prompts</span>
              </label>
              <div className="setting-description">
                Show floating alerts when NAVI has important messages (Zelda-style soul of the project)
              </div>
            </div>
          </div>

          {/* Display Settings */}
          <div className="setting-group">
            <h3>DISPLAY</h3>
            <div className="setting-item">
              <label>
                <input
                  id="screensaver"
                  name="showScreensaver"
                  type="checkbox"
                  checked={settings.showScreensaver}
                  onChange={(e) => updateSettings({ showScreensaver: e.target.checked })}
                />
                <span>Enable Screensaver</span>
              </label>
              <div className="setting-description">
                Show logo animation after idle timeout
              </div>
            </div>

            <div className="setting-item">
              <label htmlFor="idle-timeout">Idle Timeout (seconds)</label>
              <input
                id="idle-timeout"
                name="idleTimeout"
                type="number"
                min="10"
                max="600"
                value={settings.idleTimeout / 1000}
                onChange={(e) => updateSettings({ idleTimeout: parseInt(e.target.value) * 1000 })}
                className="setting-input-number"
              />
            </div>
          </div>

          {/* Theme */}
          <div className="setting-group">
            <h3>THEME</h3>
            <div className="setting-item">
              <label htmlFor="theme">Color Scheme</label>
              <select
                id="theme"
                name="theme"
                value={settings.theme}
                onChange={(e) => updateSettings({ theme: e.target.value as 'arctic' | 'battle' })}
                className="setting-select"
              >
                <option value="arctic">Arctic Cyan</option>
                <option value="battle">Battle Red</option>
              </select>
            </div>
          </div>

          {/* Battle Mode */}
          <div className="setting-group">
            <h3>BATTLE MODE</h3>
            <div className="setting-item">
              <label htmlFor="battle-key">Activation Key</label>
              <input
                id="battle-key"
                name="battleModeKey"
                type="text"
                maxLength={1}
                value={settings.battleModeKey}
                onChange={(e) => updateSettings({ battleModeKey: e.target.value.toLowerCase() })}
                className="setting-input-key"
              />
              <div className="setting-description">
                Press this key to toggle battle mode (default: B)
              </div>
            </div>
          </div>

          {/* Reset */}
          <div className="setting-group">
            <button 
              className="reset-btn"
              onClick={() => {
                if (confirm('Reset all settings to defaults?')) {
                  resetSettings();
                }
              }}
            >
              RESET TO DEFAULTS
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
