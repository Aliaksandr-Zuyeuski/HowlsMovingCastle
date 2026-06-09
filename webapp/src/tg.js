// Telegram WebApp context
const tg = window.Telegram?.WebApp;
if (tg) { tg.ready(); tg.expand(); }

const params = new URLSearchParams(window.location.search);

export const APP_VERSION = '0.1.0-beta';
export const APP_UPDATED = '30.05.2026 09:44';
export const ME = tg?.initDataUnsafe?.user?.first_name || 'Участник';
export const USER_ID = tg?.initDataUnsafe?.user?.id || params.get('user_id') || '0';

const startParam = tg?.initDataUnsafe?.start_param || '';
export const GROUP_CHAT_ID = startParam.startsWith('g')
  ? '-' + startParam.slice(1)
  : params.get('group_chat_id') || null;
export const CHAT_ID = GROUP_CHAT_ID || USER_ID;
export const INIT_DATA = tg?.initData || '';

export const haptic = {
  light:   () => tg?.HapticFeedback?.impactOccurred('light'),
  medium:  () => tg?.HapticFeedback?.impactOccurred('medium'),
  rigid:   () => tg?.HapticFeedback?.impactOccurred('rigid'),
  success: () => tg?.HapticFeedback?.notificationOccurred('success'),
};
