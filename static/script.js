const API_KEY = "secret-key-123";
let isLogin = true;

// Check if already logged in
window.addEventListener('DOMContentLoaded', async () => {
  const res = await fetch('/me');
  const data = await res.json();
  if (data.logged_in) {
    showChat(data.username);
  }

  document.getElementById('input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
});

function toggleAuth() {
  isLogin = !isLogin;
  document.getElementById('authTitle').textContent = isLogin ? 'Login' : 'Register';
  document.getElementById('authSwitchText').textContent = isLogin ? "Don't have an account?" : "Already have an account?";
  document.getElementById('authSwitchLink').textContent = isLogin ? 'Register' : 'Login';
  document.getElementById('authError').textContent = '';
}

async function submitAuth() {
  const username = document.getElementById('authUsername').value.trim();
  const password = document.getElementById('authPassword').value.trim();
  const errorEl = document.getElementById('authError');

  if (!username || !password) {
    errorEl.textContent = 'Please fill in all fields.';
    return;
  }

  const endpoint = isLogin ? '/login' : '/register';
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();

  if (!res.ok) {
    errorEl.textContent = data.error;
    return;
  }

  if (!isLogin) {
    errorEl.style.color = '#16a34a';
    errorEl.textContent = 'Account created! Please log in.';
    toggleAuth();
    return;
  }

  showChat(data.username);
}

function showChat(username) {
  document.getElementById('authScreen').style.display = 'none';
  document.getElementById('chatScreen').style.display = 'flex';
  document.getElementById('headerUser').textContent = `Hi, ${username}`;
}

async function logout() {
  await fetch('/logout', { method: 'POST' });
  document.getElementById('chatScreen').style.display = 'none';
  document.getElementById('authScreen').style.display = 'flex';
  document.getElementById('authUsername').value = '';
  document.getElementById('authPassword').value = '';
  document.getElementById('authError').textContent = '';
}

async function send() {
  const input = document.getElementById('input');
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
      headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    loading.remove();

    if (res.status === 401 && data.error === 'Please log in first.') {
      logout();
      return;
    }

    addMsg(data.response || data.error, res.ok ? 'bot' : 'error');
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