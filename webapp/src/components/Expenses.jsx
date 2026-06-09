import { useState, useEffect } from 'react';
import { fetchExpenses, apiAddExpense, notify } from '../api.js';
import { haptic } from '../tg.js';

export function Expenses({ showToast }) {
  const [expenses, setExpenses] = useState([]);
  const [amt, setAmt] = useState('');
  const [desc, setDesc] = useState('');

  useEffect(() => {
    fetchExpenses().then(setExpenses);
  }, []);

  async function handleAdd() {
    const amount = parseFloat(amt);
    if (!amount || amount <= 0) { showToast('Увядзіце суму'); return; }
    await apiAddExpense(amount, desc);
    notify('expense', desc || 'выдатак', amount.toFixed(2));
    showToast(`Выдатак ${amount.toFixed(2)} р дададзены`);
    haptic.light();
    setAmt(''); setDesc('');
    fetchExpenses().then(setExpenses);
  }

  return (
    <div>
      <div class="hdr"><div class="hdr-row"><div class="hdr-title">💰 Выдаткі</div></div></div>
      <div class="exp-wrap">
        <div class="form-card">
          <h3>Дадаць выдатак</h3>
          <div class="flabel">Сума (р)</div>
          <input class="finp" type="number" placeholder="0.00" step="0.01" value={amt} onInput={e => setAmt(e.target.value)} />
          <div class="flabel">Апісанне</div>
          <input class="finp" placeholder="Крама, рынак..." value={desc} onInput={e => setDesc(e.target.value)} />
          <button class="sub-btn" onClick={handleAdd}>Дадаць выдатак</button>
        </div>

        <div class="exp-cards">
          {expenses.length === 0 ? (
            <div class="empty">
              <div class="ei">💸</div>
              <h3>Няма выдаткаў</h3>
              <p>Дадайце першы выдатак</p>
            </div>
          ) : expenses.map(e => (
            <div class="exp-card" key={e.id}>
              <div class="exp-top">
                <span class="exp-who">{e.paid_by}</span>
                <span class="exp-amt">{parseFloat(e.amount).toFixed(2)} р</span>
              </div>
              <div class="exp-desc">{e.description || '—'}</div>
              <div style="font-size:10.5px;color:var(--hint);margin-top:3px;font-weight:600">{e.created_at}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
