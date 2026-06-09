import { useState, useEffect } from 'react';
import { fetchBalance } from '../api.js';

const COLS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export function Balance() {
  const [data, setData] = useState({ totals: {}, share: 0 });

  useEffect(() => {
    fetchBalance().then(setData);
  }, []);

  const { totals, share } = data;
  const total = Object.values(totals).reduce((a, b) => a + b, 0);
  const maxP = Math.max(...Object.values(totals), 1);
  const entries = Object.entries(totals);

  return (
    <div>
      <div class="hdr"><div class="hdr-row"><div class="hdr-title">⚖️ Баланс</div></div></div>
      <div class="bal-wrap">
        <div class="bal-sum">
          <div class="bal-ttl">{total.toFixed(2)} р</div>
          <div class="bal-lbl">агульныя выдаткі</div>
          <div class="bal-share">на чалавека: {share.toFixed(2)} р</div>
        </div>

        {entries.length === 0 ? (
          <div class="empty"><div class="ei">⚖️</div><h3>Няма даных</h3></div>
        ) : entries.map(([name, paid], ci) => {
          const diff = paid - share;
          let st, cls;
          if (diff > 0.5)       { st = `+${diff.toFixed(2)} р — вернуць`; cls = 'credit'; }
          else if (diff < -0.5) { st = `${diff.toFixed(2)} р — даплаціць`; cls = 'owe'; }
          else                  { st = 'у балансе ✓'; cls = 'ok'; }
          const pct = Math.round(paid / maxP * 100);

          return (
            <div class="bal-card" key={name}>
              <div class="bal-name">{name}</div>
              <div class="bal-bar">
                <div class="bal-fill" style={{ width: pct + '%', background: COLS[ci % COLS.length] }} />
              </div>
              <div class="bal-row">
                <span class="bal-paid">заплаціў/ла {paid.toFixed(2)} р</span>
                <span class={`bal-st ${cls}`}>{st}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
