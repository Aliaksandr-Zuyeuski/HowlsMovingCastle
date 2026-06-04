import { useRef } from 'react';
import { em, fmtDate } from '../utils.js';
import { ME } from '../tg.js';

function CardSub({ item }) {
  if (item.done) return <div class="card-sub done-s">✅ купіў/ла {item.taken_by}</div>;
  if (item.taken_by) return <div class="card-sub taken">🙋 бярэ {item.taken_by}</div>;
  const date = item.created_at ? ' · ' + fmtDate(item.created_at) : '';
  return <div class="card-sub">дадаў/ла {item.added_by}{date}</div>;
}

function CardActions({ item, onTake, onBuy, onRelease }) {
  if (item.taken_by) return (
    <div class="card-acts">
      <button class="act bought" onClick={() => onBuy(item.id)}>
        ✅ Купіў{item.taken_by === ME ? '!' : ''}
      </button>
      {item.taken_by === ME && (
        <button class="act rel" onClick={() => onRelease(item.id)}>Адмяніць</button>
      )}
    </div>
  );
  return (
    <div class="card-acts">
      <button class="act take" onClick={() => onTake(item.id)}>🙋 Бяру</button>
      <button class="act bought" onClick={() => onBuy(item.id)}>✅ Ужо купіў</button>
    </div>
  );
}

export function Card({ item, isNew, onTake, onBuy, onDelete, onRelease }) {
  const ref = useRef(null);

  return (
    <div
      class={`card${item.done ? ' done-card' : ''}`}
      id={`c${item.id}`}
      ref={ref}
      style={isNew ? { animation: 'si .25s cubic-bezier(.34,1.56,.64,1) forwards' } : {}}
    >
      <div class="card-main">
        <div class="card-icon">{em(item.name)}</div>
        <div class="card-info">
          <div class="card-name">{item.name}</div>
          <CardSub item={item} />
        </div>
        <button class="card-del" onClick={() => onDelete(item.id)}>✕</button>
      </div>
      {!item.done && (
        <CardActions item={item} onTake={onTake} onBuy={onBuy} onRelease={onRelease} />
      )}
    </div>
  );
}
