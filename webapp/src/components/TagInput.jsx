import { useState, useRef } from 'react';
import { em } from '../utils.js';

export function TagInput({ onSubmit }) {
  const [tags, setTags] = useState([]);
  const [buyMode, setBuyMode] = useState(false);
  const [focused, setFocused] = useState(false);
  const inputRef = useRef(null);

  function pushTag(raw) {
    const parts = raw.split(',').map(s => s.trim()).filter(Boolean);
    setTags(prev => {
      const next = [...prev];
      parts.forEach(p => { if (p && !next.includes(p)) next.push(p); });
      return next;
    });
  }

  function removeTag(i) {
    setTags(prev => prev.filter((_, idx) => idx !== i));
  }

  function handleKeyDown(e) {
    const val = e.target.value;
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const trimmed = val.trim().replace(/,$/, '');
      if (trimmed) pushTag(trimmed);
      else if (tags.length) handleSubmit();
      e.target.value = '';
    } else if (e.key === 'Backspace' && !val && tags.length) {
      setTags(prev => prev.slice(0, -1));
    }
  }

  function handleInput(e) {
    if (e.target.value.includes(',')) {
      pushTag(e.target.value);
      e.target.value = '';
    }
  }

  function handleSubmit() {
    const val = inputRef.current?.value?.trim().replace(/,$/, '');
    if (val) pushTag(val);
    if (!tags.length && !val) return;
    const finalTags = val ? [...tags, val].filter((t, i, a) => a.indexOf(t) === i) : [...tags];
    if (!finalTags.length) return;
    if (inputRef.current) inputRef.current.value = '';
    setTags([]);
    setBuyMode(false);
    onSubmit(finalTags, buyMode);
  }

  const count = tags.length;
  const submitLabel = count > 1
    ? (buyMode ? `Купіў усё (${count})` : `Дадаць усё (${count})`)
    : (buyMode ? 'Купіў' : 'Дадаць');

  return (
    <div class="add-row">
      <div
        class={`tag-field${focused ? ' focus' : ''}`}
        onClick={() => inputRef.current?.focus()}
      >
        {tags.map((name, i) => (
          <div class="tag" key={name} style={{ background: buyMode ? 'var(--g)' : 'var(--btn)' }}>
            {em(name)} {name}
            <button class="tag-x" onClick={e => { e.stopPropagation(); removeTag(i); }}>✕</button>
          </div>
        ))}
        <input
          ref={inputRef}
          class="tag-inp"
          placeholder="Дадаць тавар..."
          maxLength={80}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        />
      </div>

      {count > 0 && (
        <div class="add-bottom show">
          <button
            class="add-submit"
            style={{ background: buyMode ? 'var(--g)' : 'var(--btn)' }}
            onClick={handleSubmit}
          >
            {submitLabel}
          </button>
          <div
            class={`buy-toggle${buyMode ? ' on' : ''}`}
            onClick={() => setBuyMode(b => !b)}
          >
            <div class={`buy-toggle-cb`}>{buyMode ? '✓' : ''}</div>
            <span class="buy-toggle-lbl">Ужо купіў</span>
          </div>
        </div>
      )}
    </div>
  );
}
