import { CHAT_ID, GROUP_CHAT_ID, INIT_DATA, ME, USER_ID } from './tg.js';

const API = window.location.origin;

export async function api(path, method = 'GET', body = null) {
  const opts = {
	method,
	headers: { 'Content-Type': 'application/json', 'X-Init-Data': INIT_DATA },
  };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(API + path, opts);
  return r.json();
}

export function notify(action, name, amount = '') {
  fetch(`${API}/api/notify`, {
	method: 'POST',
	headers: { 'Content-Type': 'application/json', 'X-Init-Data': INIT_DATA },
	body: JSON.stringify({ action, name, amount, user: ME, user_id: USER_ID, chat_id: CHAT_ID, group_chat_id: GROUP_CHAT_ID }),
  }).catch(e => console.log('notify error:', e));
}

// ── Items ────────────────────────────────────────────────────────
export const fetchItems    = ()           => api(`/api/items?chat_id=${CHAT_ID}`);
export const apiAddItems   = (names)      => api(`/api/items?chat_id=${CHAT_ID}&action=add`,     'POST', { names, added_by: ME, group_chat_id: GROUP_CHAT_ID });
export const apiTakeItem   = (id)         => api(`/api/items?chat_id=${CHAT_ID}&action=take`,    'POST', { id, user: ME, group_chat_id: GROUP_CHAT_ID });
export const apiReleaseItem= (id)         => api(`/api/items?chat_id=${CHAT_ID}&action=release`, 'POST', { id, group_chat_id: GROUP_CHAT_ID });
export const apiBuyItem    = (id)         => api(`/api/items?chat_id=${CHAT_ID}&action=buy`,     'POST', { id, user: ME, group_chat_id: GROUP_CHAT_ID });
export const apiDeleteItem = (id)         => api(`/api/items?chat_id=${CHAT_ID}&action=delete`,  'POST', { id, group_chat_id: GROUP_CHAT_ID });

// ── Expenses ─────────────────────────────────────────────────────
export const fetchExpenses = ()           => api(`/api/expenses?chat_id=${CHAT_ID}`);
export const fetchBalance  = ()           => api(`/api/expenses?chat_id=${CHAT_ID}&action=balance`);
export const apiAddExpense = (amt, desc)  => api(`/api/expenses?chat_id=${CHAT_ID}`, 'POST', { paid_by: ME, amount: amt, description: desc });

// ── Settings ─────────────────────────────────────────────────────
export const fetchSettings = ()           => api(`/api/settings?chat_id=${CHAT_ID}`);
export const apiSaveSettings = (s)        => api(`/api/settings?chat_id=${CHAT_ID}`, 'POST', s);