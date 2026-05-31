const fs = require('fs');

// Читаем версию из CHANGELOG.md
const changelog = fs.readFileSync('CHANGELOG.md', 'utf8');
const versionMatch = changelog.match(/^## \[(.+?)\]/m);
if (!versionMatch) {
  console.error('❌ Версия не найдена в CHANGELOG.md');
  process.exit(1);
}
const version = versionMatch[1];

// Текущая дата и время
const now = new Date();
const pad = n => String(n).padStart(2, '0');
const buildDate = `${pad(now.getDate())}.${pad(now.getMonth()+1)}.${now.getFullYear()} ${pad(now.getHours())}:${pad(now.getMinutes())}`;

// Вписываем в webapp.html
let html = fs.readFileSync('webapp.html', 'utf8');
html = html.replace(/const APP_VERSION = '.*?';/, `const APP_VERSION = '${version}';`);
html = html.replace(/const APP_UPDATED = '.*?';/, `const APP_UPDATED = '${buildDate}';`);
fs.writeFileSync('webapp.html', html);

console.log(`✅ Version: ${version}`);
console.log(`✅ Build date: ${buildDate}`);
