export function Toast({ toast, onDismiss }) {
  return (
    <div class={`toast${toast.visible ? ' show' : ''}${toast.retry ? ' has-retry' : ''}`}>
      {toast.msg}
      {toast.retry && (
        <span class="toast-retry" onClick={() => { onDismiss(); toast.retry(); }}>
          Паўтарыць
        </span>
      )}
    </div>
  );
}
