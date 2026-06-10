import { useState, useEffect, useCallback, useRef } from 'react';
import { Card } from './Card.jsx';
import { TagInput } from './TagInput.jsx';
import { fetchItems, apiAddItems, apiTakeItem, apiReleaseItem, apiBuyItem, apiDeleteItem } from '../api.js';
import { haptic, ME } from '../tg.js';

const FILTERS = [
  { key: 'all',  label: 'Усе' },
  { key: 'free', label: 'Вольныя' },
  { key: 'mine', label: 'Мае 🙋' },
  { key: 'done', label: 'Куплена ✅' },
];

const EMPTY = {
  all:  { icon: '🛒', title: 'Спіс пусты',       sub: 'Дадайце першы тавар' },
  free: { icon: '✅', title: 'Усё ўзята!',        sub: 'Няма вольных тавараў' },
  mine: { icon: '🙋', title: 'Нічога не ўзята',   sub: 'Націсніце Бяру' },
  done: { icon: '🎉', title: 'Нічога не куплена', sub: 'Адзначайце Купіў' },
};

function animateCard(id, type) {
  const card = document.getElementById('c' + id);
  if (!card) return Promise.resolve();
  return new Promise(resolve => {
	card.style.pointerEvents = 'none';
	const h = card.offsetHeight;
	if (type === 'take') {
	  card.style.transition = 'transform .15s ease, box-shadow .15s ease';
	  card.style.transform = 'scale(1.02)';
	  card.style.boxShadow = '0 0 0 3px var(--o)';
	  setTimeout(() => {
		card.style.opacity = '0';
		card.style.transform = 'scale(.98)';
		card.style.transition = 'opacity .18s ease, transform .18s ease';
	  }, 150);
	  setTimeout(() => {
		card.style.transition = 'max-height .26s cubic-bezier(.4,0,.2,1), margin-bottom .26s, opacity .1s';
		card.style.overflow = 'hidden';
		card.style.maxHeight = h + 'px';
		card.offsetHeight;
		card.style.maxHeight = '0';
		card.style.marginBottom = '0';
		setTimeout(resolve, 270);
	  }, 300);
	  return;
	}
	card.style.transition = 'opacity .22s ease, transform .22s ease, box-shadow .22s ease';
	if (type === 'buy') {
	  card.style.boxShadow = '0 0 0 3px var(--g)';
	  card.style.transform = 'scale(1.02)';
	  setTimeout(() => { card.style.opacity = '0'; card.style.transform = 'scale(.97)'; }, 140);
	} else {
	  card.style.opacity = '0';
	  card.style.transform = 'translateX(28px)';
	}
	setTimeout(() => {
	  card.style.transition = 'max-height .28s cubic-bezier(.4,0,.2,1), margin-bottom .28s, padding .28s, opacity .1s';
	  card.style.overflow = 'hidden';
	  card.style.maxHeight = h + 'px';
	  card.offsetHeight;
	  card.style.maxHeight = '0';
	  card.style.marginBottom = '0';
	  setTimeout(resolve, 290);
	}, type === 'buy' ? 320 : 200);
  });
}

export function ShoppingList({ showToast }) {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState('all');
  const [newNames, setNewNames] = useState(new Set());
  const itemsRef = useRef(items);
  itemsRef.current = items;

  const load = useCallback(async () => {
	const fresh = await fetchItems();
	setItems(Array.isArray(fresh) ? fresh : []);
  }, []);

  // polling
  useEffect(() => {
	load();
	const timer = setInterval(async () => {
	  try {
		const fresh = await fetchItems();
		if (Array.isArray(fresh) && JSON.stringify(fresh) !== JSON.stringify(itemsRef.current)) setItems(fresh);
	  } catch (e) {}
	}, 12000);
	return () => clearInterval(timer);
  }, []);

  // visibilitychange
  useEffect(() => {
	const handler = () => { if (document.visibilityState === 'visible') load(); };
	document.addEventListener('visibilitychange', handler);
	return () => document.removeEventListener('visibilitychange', handler);
  }, []);

  async function handleSubmit(tags, buyMode) {
	await apiAddItems(tags);
	if (buyMode) {
	  const fresh = await fetchItems();
	  for (const name of tags) {
		const item = fresh.find(i => i.name === name && !i.done);
		if (item) await apiBuyItem(item.id);
	  }
	  haptic.success();
	  showToast(tags.length > 1 ? `Куплена ${tags.length} тавары ✅` : `Куплена: ${tags[0]} ✅`);
	} else {
	  haptic.light();
	  showToast(tags.length > 1 ? `Дадана ${tags.length} тавары 🛒` : `Дадана: ${tags[0]}`);
	}
	setNewNames(new Set(tags));
	await load();
	setNewNames(new Set());
  }

  async function handleTake(id) {
	const name = items.find(i => i.id === id)?.name || '';
	haptic.medium();
	await animateCard(id, 'take');
	setItems(prev => prev.map(i => i.id === id ? { ...i, taken_by: ME } : i));
	setNewNames(new Set([name]));
	setTimeout(() => setNewNames(new Set()), 500);
	apiTakeItem(id)
	  .catch(() => showToast('⚠️ Не атрымалася ўзяць. ', () => handleTake(id)));
  }

  async function handleRelease(id) {
	const name = items.find(i => i.id === id)?.name || '';
	haptic.light();
	setItems(prev => prev.map(i => i.id === id ? { ...i, taken_by: null } : i));
	apiReleaseItem(id)
	  .catch(() => showToast('⚠️ Памылка. ', () => handleRelease(id)));
  }

  async function handleBuy(id) {
	const name = items.find(i => i.id === id)?.name || '';
	await animateCard(id, 'buy');
	setItems(prev => prev.map(i => i.id === id ? { ...i, done: true, taken_by: ME } : i));
	haptic.success();
	showToast('Куплена: ' + name + ' 🎉');
	apiBuyItem(id)
	  .catch(() => showToast('⚠️ Не атрымалася купіць. ', () => handleBuy(id)));
  }

  async function handleDelete(id) {
	const name = items.find(i => i.id === id)?.name || '';
	haptic.rigid();
	await animateCard(id, 'del');
	setItems(prev => prev.filter(i => i.id !== id));
	apiDeleteItem(id)
	  .catch(() => showToast('⚠️ Не атрымалася выдаліць. ', () => handleDelete(id)));
  }

  // filter
  const filtered = items.filter(i => {
	if (filter === 'free') return !i.taken_by && !i.done;
	if (filter === 'mine') return i.taken_by === ME && !i.done;
	if (filter === 'done') return i.done;
	return true;
  });

  const active = items.filter(i => !i.done).length;
  const done   = items.filter(i => i.done).length;

  const free  = filtered.filter(i => !i.taken_by && !i.done);
  const taken = filtered.filter(i => i.taken_by && !i.done);
  const doneI = filtered.filter(i => i.done);

  return (
	<div>
	  <div class="hdr">
		<div class="hdr-row">
		  <div class="hdr-title">🛒 Кошык</div>
		  <div class="pills">
			<div class="pill blue">{active}</div>
			<div class="pill green">{done} ✅</div>
		  </div>
		</div>
		<TagInput onSubmit={handleSubmit} />
	  </div>

	  <div class="ftabs">
		{FILTERS.map(f => (
		  <button key={f.key} class={`ftab${filter === f.key ? ' on' : ''}`} onClick={() => setFilter(f.key)}>
			{f.label}
		  </button>
		))}
	  </div>

	  <div class="list">
		{filtered.length === 0 ? (
		  <div class="empty">
			<div class="ei">{EMPTY[filter].icon}</div>
			<h3>{EMPTY[filter].title}</h3>
			<p>{EMPTY[filter].sub}</p>
		  </div>
		) : (
		  <>
			{filter === 'all' && free.length > 0  && <div class="sec-label">Да пакупкі</div>}
			{free.map(i  => <Card key={i.id} item={i} isNew={newNames.has(i.name)} onTake={handleTake} onBuy={handleBuy} onDelete={handleDelete} onRelease={handleRelease} />)}
			{filter === 'all' && taken.length > 0 && <div class="sec-label">Нехта бярэ</div>}
			{taken.map(i => <Card key={i.id} item={i} isNew={newNames.has(i.name)} onTake={handleTake} onBuy={handleBuy} onDelete={handleDelete} onRelease={handleRelease} />)}
			{filter === 'all' && doneI.length > 0 && <div class="sec-label">Куплена</div>}
			{doneI.map(i => <Card key={i.id} item={i} isNew={false} onTake={handleTake} onBuy={handleBuy} onDelete={handleDelete} onRelease={handleRelease} />)}
		  </>
		)}
	  </div>
	</div>
  );
}
