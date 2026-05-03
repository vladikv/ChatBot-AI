async function send() {
  const input = document.getElementById('input');
  const apiKey = document.getElementById('apiKey').value.trim();
  const btn = document.getElementById('sendBtn');
  const text = input.value.trim();
  if (!text) return;

  addMsg(text, 'user');
  input.value = '';
  btn.disabled = true;

  const loading = addMsg('Thinking...', 'loading');

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    loading.remove();
    if (res.status === 401) { addMsg('Invalid API key.', 'error'); }
    else { addMsg(data.response || data.error, res.ok ? 'bot' : 'error'); }
  } catch(e) {
    loading.remove();
    addMsg('Connection error.', 'error');
  }

  btn.disabled = false;
  input.focus();
}

function addMsg(text, type) {
  const box = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = 'msg ' + type;
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
});