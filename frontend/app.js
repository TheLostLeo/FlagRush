(function(){
  const cfg = (window.CONFIG || { MAIN_API_URL: 'http://localhost:5000' });
  const api = cfg.MAIN_API_URL.replace(/\/$/, '');

  const els = {
    status: document.getElementById('status'),
    backendUrl: document.getElementById('backend-url'),
    authSection: document.getElementById('auth-section'),
    appSection: document.getElementById('app-section'),
    tabLogin: document.getElementById('tab-login'),
    tabRegister: document.getElementById('tab-register'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    loginUsername: document.getElementById('login-username'),
    loginPassword: document.getElementById('login-password'),
    regUsername: document.getElementById('reg-username'),
    regEmail: document.getElementById('reg-email'),
    regPassword: document.getElementById('reg-password'),
    authMessage: document.getElementById('auth-message'),
    currentUser: document.getElementById('current-user'),
    logoutBtn: document.getElementById('logout-btn'),
    challenges: document.getElementById('challenges'),
    challengeDetails: document.getElementById('challenge-details'),
    submitFlagForm: document.getElementById('submit-flag-form'),
    flagInput: document.getElementById('flag-input'),
    submitResult: document.getElementById('submit-result'),
    leaderboard: document.getElementById('leaderboard'),
    stats: document.getElementById('stats'),
  };

  els.backendUrl.textContent = api;

  // Tabs
  els.tabLogin.addEventListener('click', () => {
    els.tabLogin.classList.add('active');
    els.tabRegister.classList.remove('active');
    els.loginForm.classList.add('visible');
    els.registerForm.classList.remove('visible');
  });
  els.tabRegister.addEventListener('click', () => {
    els.tabRegister.classList.add('active');
    els.tabLogin.classList.remove('active');
    els.registerForm.classList.add('visible');
    els.loginForm.classList.remove('visible');
  });

  // State
  let token = localStorage.getItem('token') || '';
  let me = null;
  let selectedChallenge = null;

  function setStatus(msg) { els.status.textContent = msg || ''; }
  function setAuthMessage(html) { els.authMessage.innerHTML = html || ''; }
  function setSubmitResult(html) { els.submitResult.innerHTML = html || ''; }

  function headers(auth) {
    const h = { 'Content-Type': 'application/json' };
    if (auth && token) h['Authorization'] = `Bearer ${token}`;
    return h;
  }

  async function checkHealth() {
    try {
      const res = await fetch(`${api}/health`);
      const j = await res.json();
      setStatus(`Health: ${j.status}, DB: ${j.database}`);
    } catch (e) {
      setStatus('Health: unavailable');
    }
  }

  async function register(ev) {
    ev.preventDefault();
    setAuthMessage('');
    try {
      const body = {
        username: els.regUsername.value.trim(),
        email: els.regEmail.value.trim(),
        password: els.regPassword.value
      };
      const res = await fetch(`${api}/api/auth/register`, {
        method: 'POST', headers: headers(), body: JSON.stringify(body)
      });
      const j = await res.json();
      if (!res.ok) throw new Error(j.message || 'Registration failed');
      setAuthMessage(`<span style="color:#86efac">Registered user: ${j.data.username}</span>`);
      // switch to login
      els.tabLogin.click();
      els.loginUsername.value = body.username;
      els.loginPassword.value = '';
    } catch (e) {
      setAuthMessage(`<span style="color:#fca5a5">${e.message}</span>`);
    }
  }

  async function login(ev) {
    ev.preventDefault();
    setAuthMessage('');
    try {
      const body = { username: els.loginUsername.value.trim(), password: els.loginPassword.value };
      const res = await fetch(`${api}/api/auth/login`, { method: 'POST', headers: headers(), body: JSON.stringify(body) });
      const j = await res.json();
      if (!res.ok) throw new Error(j.message || 'Login failed');
      token = j.data.access_token; localStorage.setItem('token', token);
      me = j.data.user;
      afterLogin();
    } catch (e) {
      setAuthMessage(`<span style="color:#fca5a5">${e.message}</span>`);
    }
  }

  function logout() {
    token = ''; localStorage.removeItem('token'); me = null; selectedChallenge = null;
    els.appSection.classList.add('hidden');
    els.authSection.classList.remove('hidden');
    els.challenges.innerHTML=''; els.leaderboard.innerHTML=''; els.stats.innerHTML=''; els.challengeDetails.textContent='';
    els.submitFlagForm.classList.add('hidden');
    setSubmitResult('');
  }

  async function loadProfile() {
    const res = await fetch(`${api}/api/auth/profile`, { headers: headers(true) });
    if (!res.ok) throw new Error('Profile');
    const j = await res.json(); me = j.data; return me;
  }

  async function loadChallenges() {
    const res = await fetch(`${api}/api/challenges/`, { headers: headers(true) });
    const j = await res.json();
    if (!res.ok) throw new Error(j.message || 'Challenges');
    els.challenges.innerHTML = '';
    j.data.forEach(ch => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${ch.title}</strong> <small>(${ch.category})</small>\n<span>${ch.points} pts</span>\n<button data-id="${ch.id}">View</button>`;
      li.querySelector('button').addEventListener('click', () => showChallenge(ch.id));
      els.challenges.appendChild(li);
    });
  }

  async function showChallenge(id) {
    const res = await fetch(`${api}/api/challenges/${id}`, { headers: headers(true) });
    const j = await res.json();
    if (!res.ok) { els.challengeDetails.textContent = j.message || 'Error'; return; }
    selectedChallenge = j.data;
    els.challengeDetails.textContent = `${selectedChallenge.title}\n\n${selectedChallenge.description}\n\nPoints: ${selectedChallenge.points}\nCategory: ${selectedChallenge.category}`;
    els.submitFlagForm.classList.remove('hidden');
    setSubmitResult('');
  }

  async function submitFlag(ev) {
    ev.preventDefault(); setSubmitResult('');
    if (!selectedChallenge) return;
    const body = { challenge_id: selectedChallenge.id, flag: els.flagInput.value.trim() };
    const res = await fetch(`${api}/api/submissions/`, { method: 'POST', headers: headers(true), body: JSON.stringify(body) });
    const j = await res.json();
    if (!res.ok) { setSubmitResult(`<span style="color:#fca5a5">${j.message || 'Error'}</span>`); return; }
    const color = j.data.is_correct ? '#86efac' : '#fca5a5';
    setSubmitResult(`<span style="color:${color}">${j.message}</span>`);
    els.flagInput.value='';
    // refresh parts
    loadLeaderboard(); loadStats();
  }

  async function loadLeaderboard() {
    const res = await fetch(`${api}/api/submissions/leaderboard`, { headers: headers(true) });
    const j = await res.json(); if (!res.ok) return;
    els.leaderboard.innerHTML = '';
    j.data.forEach(u => {
      const li = document.createElement('li');
      li.textContent = `${u.username} — ${u.score} pts (${u.solved_challenges} solves)`;
      els.leaderboard.appendChild(li);
    });
  }

  async function loadStats() {
    const res = await fetch(`${api}/api/submissions/stats`, { headers: headers(true) });
    const j = await res.json(); if (!res.ok) return;
    const s = j.data;
    els.stats.textContent = `Submissions: ${s.total_submissions}\nCorrect: ${s.correct_submissions}\nAccuracy: ${s.accuracy.toFixed(1)}%\nScore: ${s.current_score}`;
  }

  async function afterLogin() {
    els.currentUser.textContent = me?.username || '';
    els.authSection.classList.add('hidden');
    els.appSection.classList.remove('hidden');
    await Promise.all([loadChallenges(), loadLeaderboard(), loadStats()]);
  }

  // Events
  els.registerForm.addEventListener('submit', register);
  els.loginForm.addEventListener('submit', login);
  els.logoutBtn.addEventListener('click', logout);
  els.submitFlagForm.addEventListener('submit', submitFlag);

  // Boot
  checkHealth();
  if (token) {
    loadProfile().then(afterLogin).catch(() => logout());
  }
})();
