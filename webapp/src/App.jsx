import { useState } from 'react';
import { ShoppingList } from './components/ShoppingList.jsx';
import { Expenses } from './components/Expenses.jsx';
import { Balance } from './components/Balance.jsx';
import { Settings } from './components/Settings.jsx';
import { Toast } from './components/Toast.jsx';
import { useToast } from './hooks/useToast.js';

const TABS = [
  { key: 'list',     icon: '🛒', label: 'Спіс' },
  { key: 'expenses', icon: '💰', label: 'Выдаткі' },
  { key: 'balance',  icon: '⚖️', label: 'Баланс' },
  { key: 'settings', icon: '⚙️', label: 'Налады' },
];

export function App() {
  const [page, setPage] = useState('list');
  const { toast, show: showToast, dismiss } = useToast();

  return (
    <>
      {page === 'list'     && <ShoppingList showToast={showToast} />}
      {page === 'expenses' && <Expenses showToast={showToast} />}
      {page === 'balance'  && <Balance />}
      {page === 'settings' && <Settings showToast={showToast} />}

      <nav class="nav">
        {TABS.map(t => (
          <button key={t.key} class={`nb${page === t.key ? ' on' : ''}`} onClick={() => setPage(t.key)}>
            <span class="ni">{t.icon}</span>
            <span class="nl">{t.label}</span>
          </button>
        ))}
      </nav>

      <Toast toast={toast} onDismiss={dismiss} />
    </>
  );
}
