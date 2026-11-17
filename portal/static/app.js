(() => {
  'use strict';

  const state = {
    user: null,
    missions: [],
    selectedMissionId: null,
    authMode: 'login',
  };

  const el = (id) => document.getElementById(id);

  // ---------------------------------------------------------------------------
  // Background Network Graph Canvas ("Who Am I" U-Bahn / Darknet nodes)
  // ---------------------------------------------------------------------------
  function initNetworkCanvas() {
    const canvas = el('network-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    const nodes = [];
    const NODE_COUNT = 44;

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    for (let i = 0; i < NODE_COUNT; i += 1) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        red: i % 5 === 0,
      });
    }

    function tick() {
      ctx.clearRect(0, 0, width, height);
      for (let i = 0; i < nodes.length; i += 1) {
        const a = nodes[i];
        a.x += a.vx;
        a.y += a.vy;
        if (a.x < 0 || a.x > width) a.vx *= -1;
        if (a.y < 0 || a.y > height) a.vy *= -1;

        for (let j = i + 1; j < nodes.length; j += 1) {
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.hypot(dx, dy);
          if (dist < 150) {
            const alpha = (1 - dist / 150) * 0.22;
            ctx.strokeStyle = a.red || b.red
              ? `rgba(255, 42, 85, ${alpha})`
              : `rgba(0, 255, 136, ${alpha * 0.8})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }

        ctx.fillStyle = a.red ? 'rgba(255, 42, 85, 0.7)' : 'rgba(0, 255, 136, 0.55)';
        ctx.beginPath();
        ctx.arc(a.x, a.y, a.red ? 2.4 : 1.7, 0, Math.PI * 2);
        ctx.fill();
      }
      window.requestAnimationFrame(tick);
    }
    tick();
  }

  // ---------------------------------------------------------------------------
  // API Helpers
  // ---------------------------------------------------------------------------
  async function api(path, options = {}) {
    const res = await fetch(path, {
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  }

  // ---------------------------------------------------------------------------
  // Terminal Simulator
  // ---------------------------------------------------------------------------
  function termPrint(text, cls = '') {
    const out = el('terminal-output');
    const line = document.createElement('div');
    line.className = `term-line ${cls}`.trim();
    line.textContent = text;
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  function printWelcome() {
    termPrint('CLAY://CYBER-ARENA v2.0 — "Kein System ist sicher"', 'ok');
    termPrint('Оқу-жаттығу терминалы іске қосылды. Барлық әрекеттер қауіпсіз оқшауланған.', 'dim');
    termPrint('Бастау үшін `help` командасын теріңіз.\n', 'dim');
  }

  async function handleTerminalCommand(raw) {
    const input = raw.trim();
    if (!input) return;
    termPrint(`root@clay:~# ${input}`, 'cmd');

    const parts = input.split(/\s+/);
    const cmd = parts[0].toLowerCase();

    if (cmd === 'clear') {
      el('terminal-output').textContent = '';
      return;
    }

    if (cmd === 'help') {
      termPrint(
        [
          'Қолжетімді командалар:',
          '  help                  — осы анықтаманы көрсету',
          '  whoami                — қазіргі оператор күйі',
          '  missions              — барлық миссиялар тізімі',
          '  open <OP-01..OP-06>   — миссияны жұмыс үстелінде ашу',
          '  curl <жол>            — портал ішінде HTTP GET сұранысын жасау (мыс: curl /robots.txt)',
          '  decode base64 <мәтін> — Base64 жолын декодтау',
          '  decode hex <мәтін>    — HEX жолын декодтау',
          '  submit <ID> <FLAG>    — флагты тексеру (мыс: submit m01_recon FLAG{...})',
          '  clear                 — экранды тазалау',
        ].join('\n')
      );
      return;
    }

    if (cmd === 'whoami') {
      if (state.user) {
        termPrint(
          `handle=${state.user.username} | score=${state.user.score} XP | solved=${state.user.solved_ids.length}/${state.missions.length}`,
          'ok'
        );
      } else {
        termPrint('guest@anonymous (Ұпай сақталуы үшін жоғарғы оң жақтан Кіру / Тіркелу жасаңыз)', 'dim');
      }
      return;
    }

    if (cmd === 'missions') {
      state.missions.forEach((m) => {
        const mark = m.solved ? '[✔]' : '[ ]';
        termPrint(`${mark} ${m.code} (${m.id}) — ${m.title} [${m.points} XP]`, m.solved ? 'ok' : '');
      });
      return;
    }

    if (cmd === 'open') {
      const target = (parts[1] || '').toUpperCase();
      const found = state.missions.find(
        (m) => m.code.toUpperCase() === target || m.id.toUpperCase() === target
      );
      if (!found) {
        termPrint('Қате: Миссия табылмады. Мысалы: open OP-01', 'err');
        return;
      }
      selectMission(found.id);
      termPrint(`Ашылды: ${found.code} — ${found.title}`, 'ok');
      return;
    }

    if (cmd === 'curl') {
      const targetPath = parts[1] || '/';
      if (!targetPath.startsWith('/')) {
        termPrint('Қауіпсіздік шектеуі: тек локалды `/` жолдары рұқсат етілген (мыс: curl /robots.txt).', 'err');
        return;
      }
      try {
        const res = await fetch(targetPath, { credentials: 'same-origin' });
        const body = await res.text();
        termPrint(`HTTP ${res.status}`, res.ok ? 'ok' : 'err');
        termPrint(body.slice(0, 1500));
      } catch (err) {
        termPrint(`Сұраныс қатесі: ${err}`, 'err');
      }
      return;
    }

    if (cmd === 'decode') {
      const mode = (parts[1] || '').toLowerCase();
      const value = parts.slice(2).join('');
      if (!value) {
        termPrint('Мысалы: decode base64 RkxBR3t0ZXN0fQ== немесе decode hex 464c4147', 'err');
        return;
      }
      if (mode === 'base64') {
        try {
          const decoded = atob(value);
          termPrint(`Decoded (Base64): ${decoded}`, 'ok');
        } catch {
          termPrint('Жарамсыз Base64 жолы.', 'err');
        }
        return;
      }
      if (mode === 'hex') {
        if (!/^[0-9a-fA-F]+$/.test(value) || value.length % 2 !== 0) {
          termPrint('Жарамсыз HEX жолы.', 'err');
          return;
        }
        let out = '';
        for (let i = 0; i < value.length; i += 2) {
          out += String.fromCharCode(parseInt(value.slice(i, i + 2), 16));
        }
        termPrint(`Decoded (HEX): ${out}`, 'ok');
        return;
      }
      termPrint('Қолдау бар форматтар: base64, hex', 'err');
      return;
    }

    if (cmd === 'submit') {
      const missionId = parts[1] || '';
      const flag = parts.slice(2).join(' ');
      if (!missionId || !flag) {
        termPrint('Қолдануы: submit <mission_id> <FLAG{...}>', 'err');
        return;
      }
      const { ok, data } = await api('/api/submit', {
        method: 'POST',
        body: JSON.stringify({ mission_id: missionId, flag }),
      });
      if (ok && data.ok) {
        termPrint(`[✔] ${data.message} (+${data.points} XP)`, 'ok');
        termPrint(`🛡️ Қорғаныс: ${data.defense_takeaway}`, 'dim');
        await refreshAll();
      } else {
        termPrint(`[✘] ${data.error || 'Қате флаг'}`, 'err');
      }
      return;
    }

    termPrint(`Белгісіз команда: ${cmd}. 'help' деп көріңіз.`, 'err');
  }

  // ---------------------------------------------------------------------------
  // Missions & Interactive Simulators
  // ---------------------------------------------------------------------------
  function renderMissions() {
    const grid = el('missions-grid');
    grid.textContent = '';

    state.missions.forEach((m) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'mission-card';
      if (m.id === state.selectedMissionId) btn.classList.add('active');
      if (m.solved) btn.classList.add('solved');

      const top = document.createElement('div');
      top.className = 'mc-top';

      const code = document.createElement('span');
      code.className = 'mc-code';
      code.textContent = `${m.code} // ${m.difficulty}`;

      const pts = document.createElement('span');
      pts.className = 'mc-pts';
      pts.textContent = m.solved ? `✔ ${m.points} XP` : `${m.points} XP`;

      top.append(code, pts);

      const title = document.createElement('div');
      title.className = 'mc-title';
      title.textContent = m.title;

      const cat = document.createElement('div');
      cat.className = 'mc-cat';
      cat.textContent = m.category;

      btn.append(top, title, cat);
      btn.addEventListener('click', () => selectMission(m.id));
      grid.appendChild(btn);
    });
  }

  function renderSimulator(mission) {
    const zone = el('ws-sim-zone');
    zone.textContent = '';

    if (mission.simulator_type === 'sqli_lab') {
      zone.classList.remove('hidden');
      const title = document.createElement('div');
      title.className = 'sim-title';
      title.textContent = '⚡ ОҚШАУЛАНҒАН SQLI ЗЕРТХАНАСЫ (IN-MEMORY SANDBOX)';

      const form = document.createElement('form');
      form.className = 'sim-form';

      const userIn = document.createElement('input');
      userIn.placeholder = "Username (мысалы: admin немесе ' OR 1=1--)";
      userIn.required = true;

      const passIn = document.createElement('input');
      passIn.type = 'password';
      passIn.placeholder = 'Password (кез келген)';
      passIn.required = true;

      const sub = document.createElement('button');
      sub.type = 'submit';
      sub.className = 'btn btn-ghost btn-sm';
      sub.textContent = 'Кіру сұранысын тексеру';

      const out = document.createElement('div');
      out.className = 'sim-out hidden';

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const { data } = await api('/api/sim/sqli', {
          method: 'POST',
          body: JSON.stringify({ username: userIn.value, password: passIn.value }),
        });
        out.classList.remove('hidden');
        if (data.ok) {
          out.textContent =
            `SQL: ${data.query}\n\n` +
            `[КІРУ СӘТТІ] Пайдаланушы: ${data.user} (${data.role})\n` +
            `Құпия жазба: ${data.secret_note}\n` +
            `Ескерту: ${data.defense_tip}`;
        } else {
          out.textContent = `${data.query ? `SQL: ${data.query}\n\n` : ''}[БАС ТАРТЫЛДЫ] ${data.error}`;
        }
      });

      form.append(userIn, passIn, sub);
      zone.append(title, form, out);
      return;
    }

    if (mission.simulator_type === 'camera_lab') {
      zone.classList.remove('hidden');
      const title = document.createElement('div');
      title.className = 'sim-title';
      title.textContent = '📹 SECURE-VIEW™ IP CAMERA СИМУЛЯТОРЫ';

      const form = document.createElement('form');
      form.className = 'sim-form';

      const userIn = document.createElement('input');
      userIn.value = 'admin';
      userIn.placeholder = 'Username';
      userIn.required = true;

      const passIn = document.createElement('input');
      passIn.type = 'password';
      passIn.placeholder = 'Зауыттық парольді тап...';
      passIn.required = true;

      const sub = document.createElement('button');
      sub.type = 'submit';
      sub.className = 'btn btn-ghost btn-sm';
      sub.textContent = 'Камераға қосылу';

      const out = document.createElement('div');
      out.className = 'sim-out hidden';

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const { data } = await api('/api/sim/camera', {
          method: 'POST',
          body: JSON.stringify({ username: userIn.value, password: passIn.value }),
        });
        out.classList.remove('hidden');
        out.textContent = data.ok
          ? `[LIVE FEED АШЫЛДЫ] ${data.device}\n${data.message}\nФлаг: ${data.flag}`
          : `[ҚАТЕ] ${data.message}`;
      });

      form.append(userIn, passIn, sub);
      zone.append(title, form, out);
      return;
    }

    if (mission.simulator_type === 'ddos_lab') {
      zone.classList.remove('hidden');
      const title = document.createElement('div');
      title.className = 'sim-title';
      title.textContent = '🛡️ WAF / NGINX АНТИ-DDOS ҚАЛҚАНЫ';

      const form = document.createElement('form');
      form.className = 'sim-form';

      const subnetIn = document.createElement('input');
      subnetIn.placeholder = 'Бұғатталатын подсеть (мыс: 192.0.2.0/24)';
      subnetIn.required = true;

      const sub = document.createElement('button');
      sub.type = 'submit';
      sub.className = 'btn btn-ghost btn-sm';
      sub.textContent = 'WAF ережесін қолдану';

      const out = document.createElement('div');
      out.className = 'sim-out hidden';

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const { data } = await api('/api/sim/ddos', {
          method: 'POST',
          body: JSON.stringify({ subnet: subnetIn.value }),
        });
        out.classList.remove('hidden');
        out.textContent = data.ok
          ? `[ҚОРҒАНЫС ІСКЕ ҚОСЫЛДЫ]\n${data.rule}\n${data.message}\nФлаг: ${data.flag}`
          : `[ҚАТЕ] ${data.message}`;
      });

      form.append(subnetIn, sub);
      zone.append(title, form, out);
      return;
    }

    zone.classList.add('hidden');
  }

  function selectMission(missionId, preserveFeedback = false) {
    const mission = state.missions.find((m) => m.id === missionId);
    if (!mission) return;
    const isSameMission = state.selectedMissionId === missionId && preserveFeedback;
    state.selectedMissionId = missionId;

    el('workspace-empty').classList.add('hidden');
    el('workspace-active').classList.remove('hidden');

    el('ws-code').textContent = mission.code;
    el('ws-cat').textContent = mission.category;
    el('ws-pts').textContent = `${mission.points} XP`;
    el('ws-title').textContent = mission.title;
    el('ws-story').textContent = mission.story;
    el('ws-objective').textContent = mission.objective;

    if (mission.artifact) {
      el('ws-artifact-wrap').classList.remove('hidden');
      el('ws-artifact').textContent = mission.artifact;
    } else {
      el('ws-artifact-wrap').classList.add('hidden');
    }

    el('ws-hint').textContent = mission.hint;
    if (!isSameMission) {
      el('ws-hint').classList.add('hidden');
      el('flag-input').value = '';
      el('flag-feedback').classList.add('hidden');
    }

    if (mission.solved) {
      el('ws-defense').classList.remove('hidden');
      el('ws-defense-text').textContent = mission.defense_takeaway;
    } else if (!isSameMission) {
      el('ws-defense').classList.add('hidden');
    }

    if (!isSameMission) {
      renderSimulator(mission);
    }
    renderMissions();
  }

  // ---------------------------------------------------------------------------
  // Auth & Leaderboard
  // ---------------------------------------------------------------------------
  function renderAuthUI() {
    const pill = el('user-pill');
    const openBtn = el('btn-open-auth');
    if (state.user) {
      pill.classList.remove('hidden');
      openBtn.classList.add('hidden');
      el('user-handle').textContent = `@${state.user.username}`;
      el('user-score').textContent = `${state.user.score} XP`;
      el('stat-progress').textContent = `${state.user.solved_ids.length} / ${state.missions.length} ШЕШІЛДІ`;
    } else {
      pill.classList.add('hidden');
      openBtn.classList.remove('hidden');
      el('stat-progress').textContent = `0 / ${state.missions.length} ШЕШІЛДІ`;
    }
    el('stat-missions').textContent = `${state.missions.length} МИССИЯ`;
  }

  function renderLeaderboard(rows) {
    const tbody = el('leaderboard-body');
    tbody.textContent = '';

    if (!rows.length) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 4;
      td.className = 'muted';
      td.textContent = 'Әзірге тіркелген операторлар жоқ. Бірінші болып тіркеліңіз!';
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }

    rows.forEach((row) => {
      const tr = document.createElement('tr');
      const rankTd = document.createElement('td');
      rankTd.textContent = `#${row.rank}`;
      const nameTd = document.createElement('td');
      nameTd.textContent = `@${row.username}`;
      const solvedTd = document.createElement('td');
      solvedTd.textContent = `${row.solved_count}`;
      const scoreTd = document.createElement('td');
      scoreTd.textContent = `${row.score} XP`;
      scoreTd.style.color = 'var(--green)';
      tr.append(rankTd, nameTd, solvedTd, scoreTd);
      tbody.appendChild(tr);
    });
  }

  async function refreshAll() {
    const [meRes, misRes, lbRes] = await Promise.all([
      api('/api/me'),
      api('/api/missions'),
      api('/api/leaderboard'),
    ]);
    state.user = meRes.data.user || null;
    state.missions = misRes.data.missions || [];
    renderAuthUI();
    renderMissions();
    renderLeaderboard(lbRes.data.leaderboard || []);
    if (state.selectedMissionId) {
      selectMission(state.selectedMissionId, true);
    }
  }

  function openAuthModal(mode = 'login') {
    state.authMode = mode;
    el('tab-login').classList.toggle('active', mode === 'login');
    el('tab-register').classList.toggle('active', mode === 'register');
    el('auth-submit-btn').textContent = mode === 'login' ? 'Кіру' : 'Тіркелу';
    el('auth-error').classList.add('hidden');
    el('auth-modal').classList.remove('hidden');
    el('auth-username').focus();
  }

  function closeAuthModal() {
    el('auth-modal').classList.add('hidden');
  }

  // ---------------------------------------------------------------------------
  // Event Wiring
  // ---------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', async () => {
    initNetworkCanvas();
    printWelcome();
    await refreshAll();

    el('terminal-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = el('terminal-input');
      const value = input.value;
      input.value = '';
      await handleTerminalCommand(value);
    });

    el('btn-toggle-hint').addEventListener('click', () => {
      el('ws-hint').classList.toggle('hidden');
    });

    el('flag-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!state.selectedMissionId) return;
      const flag = el('flag-input').value.trim();
      const fb = el('flag-feedback');
      const { ok, data } = await api('/api/submit', {
        method: 'POST',
        body: JSON.stringify({ mission_id: state.selectedMissionId, flag }),
      });
      fb.classList.remove('hidden', 'ok', 'error');
      if (ok && data.ok) {
        fb.classList.add('ok');
        fb.textContent = `✔ ${data.message} (+${data.points} XP)`;
        el('ws-defense').classList.remove('hidden');
        el('ws-defense-text').textContent = data.defense_takeaway;
        await refreshAll();
      } else {
        fb.classList.add('error');
        fb.textContent = `✘ ${data.error || 'Қате флаг.'}`;
      }
    });

    el('btn-open-auth').addEventListener('click', () => openAuthModal('login'));
    el('btn-close-auth').addEventListener('click', closeAuthModal);
    el('tab-login').addEventListener('click', () => openAuthModal('login'));
    el('tab-register').addEventListener('click', () => openAuthModal('register'));

    el('auth-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = el('auth-username').value.trim();
      const password = el('auth-password').value;
      const endpoint = state.authMode === 'login' ? '/api/login' : '/api/register';
      const { ok, data } = await api(endpoint, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      const errBox = el('auth-error');
      if (!ok) {
        errBox.textContent = data.error || 'Қате орын алды.';
        errBox.classList.remove('hidden');
        return;
      }
      closeAuthModal();
      await refreshAll();
    });

    el('btn-logout').addEventListener('click', async () => {
      await api('/api/logout', { method: 'POST', body: '{}' });
      await refreshAll();
    });

    el('btn-delete-account').addEventListener('click', async () => {
      if (!window.confirm('Аккаунтыңыз бен барлық ұпайларыңызды біржола өшіруге сенімдісіз бе?')) {
        return;
      }
      await api('/api/account', { method: 'DELETE' });
      await refreshAll();
    });
  });
})();
