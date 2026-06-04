import { useState, useEffect } from 'react';
import { fetchSettings, apiSaveSettings } from '../api.js';
import { ME, CHAT_ID, APP_VERSION, APP_UPDATED } from '../tg.js';

const NOTIFS = [
  { key: 'notif_add',     icon: '🔔', name: 'Даданне тавару',    desc: 'Нехта дадаў новы тавар у спіс' },
  { key: 'notif_take',    icon: '🙋', name: 'Узяцце тавару',     desc: 'Нехта ўзяў тавар для пакупкі' },
  { key: 'notif_bought',  icon: '✅', name: 'Пакупка тавару',    desc: 'Нехта купіў тавар' },
  { key: 'notif_delete',  icon: '🗑', name: 'Выдаленне тавару',  desc: 'Нехта выдаліў тавар са спіса' },
  { key: 'notif_expense', icon: '💰', name: 'Даданне выдатку',   desc: 'Нехта дадаў новы выдатак' },
];

export function Settings({ showToast }) {
  const [settings, setSettings] = useState({});

  useEffect(() => {
    fetchSettings().then(setSettings);
  }, []);

  async function handleToggle(key, value) {
    const updated = { ...settings, [key]: value };
    setSettings(updated);
    await apiSaveSettings(updated);
    showToast(value ? '🔔 Уключана' : '🔕 Выключана');
  }

  return (
    <div>
      <div class="hdr"><div class="hdr-row"><div class="hdr-title">⚙️ Налады</div></div></div>
      <div class="set-wrap">
        <div class="set-card">
          <div class="set-card-title">Апавяшчэнні ў групу</div>
          {NOTIFS.map(n => (
            <div class="set-row" key={n.key}>
              <div class="set-info">
                <div class="set-name">{n.icon} {n.name}</div>
                <div class="set-desc">{n.desc}</div>
              </div>
              <label class="toggle">
                <input
                  type="checkbox"
                  checked={settings[n.key] !== false}
                  onChange={e => handleToggle(n.key, e.target.checked)}
                />
                <span class="toggle-slider" />
              </label>
            </div>
          ))}
        </div>

        <div class="set-card">
          <div class="set-card-title">Інфармацыя</div>
          {[
            { name: '👤 Увайшлі як',       value: ME },
            { name: '💬 ID чата',           value: CHAT_ID },
            { name: '📦 Версія',            value: APP_VERSION },
            { name: '🕐 Апошняе абнаўленне', value: APP_UPDATED },
          ].map(row => (
            <div class="set-row" key={row.name}>
              <div class="set-info">
                <div class="set-name">{row.name}</div>
                <div class="set-desc">{row.value}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
