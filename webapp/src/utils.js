const EM = {
  mleko:'🥛', chleb:'🍞', masło:'🧈', maslo:'🧈', jajka:'🥚', ser:'🧀',
  jogurt:'🥛', pomidory:'🍅', ogórki:'🥒', jabłka:'🍎', banany:'🍌',
  woda:'💧', sok:'🧃', kawa:'☕', herbata:'🍵', ryba:'🐟', mięso:'🥩', mieso:'🥩',
  ziemniaki:'🥔', marchew:'🥕', cebula:'🧅', makaron:'🍝', ryż:'🍚',
  молоко:'🥛', хлеб:'🍞', масло:'🧈', яйца:'🥚', мясо:'🥩', вода:'💧',
};

export function em(name) {
  const l = name.toLowerCase();
  for (const [k, v] of Object.entries(EM)) if (l.includes(k)) return v;
  return '🛒';
}

export function fmtDate(str) {
  if (!str) return '';
  const d = new Date(str.replace(' ', 'T') + 'Z');
  return d.toLocaleString('ru', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }).replace(',', '');
}
