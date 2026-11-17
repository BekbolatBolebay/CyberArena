(() => {
  'use strict';

  const I18N = {
    kk: {
      pageTitle: 'CyberArena — Адаптивті Кибер-Полигон | Open Source (MIT)',
      'badge.oss': 'MIT OPEN SOURCE',
      'nav.adaptive': 'Адаптация',
      'nav.demo': 'Терминал',
      'nav.missions': 'Миссиялар',
      'nav.install': 'Орнату',
      'hero.kicker': 'KEIN SYSTEM IST SICHER // ЖЕКЕ КИБЕР-ПОЛИГОН',
      'hero.title': 'Ноутбугіңе қарай икемделетін кибер-арена.',
      'hero.lead':
        'CyberArena — студенттер мен мамандарға арналған ашық кодты зертхана. Жүйе компьютеріңіздің CPU, RAM және дискісін өзі тексеріп, қыздырмайтын оңтайлы режимді (LIGHT / BALANCED / FULL) автоматты таңдайды.',
      'gh.starsDefault': '★ Open Source (MIT)',
      'gh.updatedDefault': 'v2.0 · Адаптивті',
      'gh.updatedPrefix': 'Жаңартылды',
      'hero.copy': 'Көшіру',
      'hero.copied': 'Көшірілді ✔',
      'hero.zip': 'ZIP жүктеу',
      'hero.calc': 'Қуат калькуляторы',
      'hero.github': 'GitHub кодын көру',
      'ad.title': '⚡ Ноуттың қуатына автоматты адаптация',
      'ad.sub': 'Слайдты жылжытып, компьютеріңізде қай режим іске қосылатынын тексеріңіз:',
      'ad.ram': 'Жедел жады (RAM):',
      'ad.cpu': 'Процессор ядролары (CPU):',
      'ad.cpuUnit': 'ядро',
      'ad.docker': 'Docker / Podman орнатылған',
      'ad.targets': 'Іске қосылатын жүйелер:',
      'tier.lightTitle': '≤ 4 GB RAM немесе Docker-сіз',
      'tier.lightDesc': 'Тек таза Python-да Portal + IP Camera (~60 MB RAM). Ескі ноутбуктерде де қызбайды.',
      'tier.balancedTitle': '5–11 GB RAM + Docker',
      'tier.balancedDesc': 'Portal + IP Camera + OWASP Juice Shop (қатаң CPU/RAM лимитімен).',
      'tier.fullTitle': '12+ GB RAM, 6+ CPU + Docker',
      'tier.fullDesc': 'Толық полигон: Portal + Juice Shop + DVWA + IP Camera.',
      'calc.lightDesc': 'Docker қосылмайды — таза Python серверлері іске қосылады. Ноутбук мүлдем қызбайды.',
      'calc.balancedDesc': 'Оңтайландырылған Docker лимиттері (0.20–0.45 CPU). Интернет-дүкен зертханасы қосылады.',
      'calc.fullDesc': 'Толық қуатты полигон — барлық 4 зертхана қатар жұмыс істейді.',
      'demo.title': '>_ CLAY Терминал Демосы',
      'demo.sub': 'Төмендегі интерактивті терминалда help, profile, missions командаларын жазып көріңіз:',
      'demo.placeholder': 'help, profile, missions, clear',
      'demo.run': 'Орындау',
      'demo.welcome1': 'CLAY://CYBER-ARENA — Demo Terminal v2.0',
      'demo.welcome2': 'Бастау үшін `help` немесе `missions` жазып көріңіз.\n',
      'demo.help': 'Командалар: help, profile, missions, who-am-i, clear',
      'demo.profilePrefix': 'Калькулятор бойынша таңдалған профиль:',
      'demo.whoami': 'KEIN SYSTEM IST SICHER. Білім — ең мықты қорғаныс.',
      'demo.unknown': "Белгісіз команда: {cmd}. 'help' деп жазыңыз.",
      'mis.title': '🎭 «Who Am I» стиліндегі 6 миссия',
      'mis.sub': 'Әр операцияда шабуыл механизмін зерттеп, соңында Blue Team қорғанысын меңгересіз.',
      'm1.title': 'Жасырын із',
      'm1.desc': '/robots.txt пен жасырын каталогтарды тексеру арқылы бастапқы барлау.',
      'm2.title': 'Ашық Wi-Fi торы',
      'm2.desc': 'Шифрланбаған HTTP трафик пен Base64 токенін талдау.',
      'm3.title': 'Темір есікті алдау',
      'm3.desc': 'Оқшауланған in-memory симуляторда SQL инъекциясын және Prepared Statement-ті үйрену.',
      'm4.title': 'Кіреберістегі тыңшы',
      'm4.desc': 'Формадан дерек ұрлайтын JS скриптті табу және CSP қорғанысы.',
      'm5.title': 'Көлеңкелі камера',
      'm5.desc': 'IP-камерадағы зауыттық құпия сөздер қаупін тексеру.',
      'm6.title': 'Анти-DDoS Қалқан',
      'm6.desc': 'Nginx access-логтарынан ботнет подсетін анықтап, WAF ережесімен жабу.',
      'ins.title': '30 секундта іске қосыңыз',
      'ins.sub': 'Толық ашық код (MIT лицензиясы). Жүйе порттарды тек 127.0.0.1-де ашады — сыртқы желіге қауіпсіз.',
      'ins.cli':
        '# 1-жол: Git арқылы\n' +
        'git clone https://github.com/BekbolatBolebay/CyberArena.git\n' +
        'cd CyberArena\n' +
        './arena.sh profile   # Өз ноутыңыздың қуатын тексеру\n' +
        './arena.sh auto      # Бейімделген режимді іске қосу\n\n' +
        '# 2-жол: Тікелей ZIP арқылы (Git-сіз)\n' +
        'unzip CyberArena-main.zip && cd CyberArena-main\n' +
        'chmod +x arena.sh scripts/hardware_profile.py && ./arena.sh auto',
      'footer.text': 'CyberArena · Open Source (MIT) · 100% Білім беру және қорғаныс мақсатында',
    },
    ru: {
      pageTitle: 'CyberArena — Адаптивный Кибер-Полигон | Open Source (MIT)',
      'badge.oss': 'MIT OPEN SOURCE',
      'nav.adaptive': 'Адаптация',
      'nav.demo': 'Терминал',
      'nav.missions': 'Миссии',
      'nav.install': 'Установка',
      'hero.kicker': 'KEIN SYSTEM IST SICHER // ЛИЧНЫЙ КИБЕР-ПОЛИГОН',
      'hero.title': 'Кибер-арена, которая подстраивается под ваш ноутбук.',
      'hero.lead':
        'CyberArena — открытая лаборатория для студентов и разработчиков. Скрипт сам проверяет CPU, RAM и диск, выбирая безопасный режим (LIGHT / BALANCED / FULL) без перегрева.',
      'gh.starsDefault': '★ Open Source (MIT)',
      'gh.updatedDefault': 'v2.0 · Адаптивный',
      'gh.updatedPrefix': 'Обновлено',
      'hero.copy': 'Копировать',
      'hero.copied': 'Скопировано ✔',
      'hero.zip': 'Скачать ZIP',
      'hero.calc': 'Калькулятор мощности',
      'hero.github': 'Исходный код GitHub',
      'ad.title': '⚡ Автоматическая адаптация под железо',
      'ad.sub': 'Двигайте ползунки, чтобы узнать, какой профиль запустится на вашем ПК:',
      'ad.ram': 'Оперативная память (RAM):',
      'ad.cpu': 'Ядра процессора (CPU):',
      'ad.cpuUnit': 'ядер',
      'ad.docker': 'Установлен Docker / Podman',
      'ad.targets': 'Запускаемые цели:',
      'tier.lightTitle': '≤ 4 GB RAM или без Docker',
      'tier.lightDesc': 'Только чистый Python: Portal + IP Camera (~60 MB RAM). Не греет даже слабые ноутбуки.',
      'tier.balancedTitle': '5–11 GB RAM + Docker',
      'tier.balancedDesc': 'Portal + IP Camera + OWASP Juice Shop со строгими лимитами CPU/RAM.',
      'tier.fullTitle': '12+ GB RAM, 6+ CPU + Docker',
      'tier.fullDesc': 'Полный полигон: Portal + Juice Shop + DVWA + IP Camera.',
      'calc.lightDesc': 'Docker не запускается — работают лёгкие Python-серверы. Ноутбук вообще не греется.',
      'calc.balancedDesc': 'Оптимальные лимиты Docker (0.20–0.45 CPU). Запускается лаборатория интернет-магазина.',
      'calc.fullDesc': 'Полноценный полигон — все 4 лаборатории работают одновременно.',
      'demo.title': '>_ Демо терминала CLAY',
      'demo.sub': 'Попробуйте ввести help, profile или missions в интерактивном терминале ниже:',
      'demo.placeholder': 'help, profile, missions, clear',
      'demo.run': 'Выполнить',
      'demo.welcome1': 'CLAY://CYBER-ARENA — Demo Terminal v2.0',
      'demo.welcome2': 'Введите `help` или `missions`, чтобы начать.\n',
      'demo.help': 'Команды: help, profile, missions, who-am-i, clear',
      'demo.profilePrefix': 'Выбранный профиль по калькулятору:',
      'demo.whoami': 'KEIN SYSTEM IST SICHER. Знания — лучшая защита.',
      'demo.unknown': "Неизвестная команда: {cmd}. Введите 'help'.",
      'mis.title': '🎭 6 миссий в стиле «Кто Я»',
      'mis.sub': 'В каждом задании вы разбираете механику атаки и закрепляете защиту Blue Team.',
      'm1.title': 'Скрытый след',
      'm1.desc': 'Базовая разведка через проверку /robots.txt и скрытых директорий.',
      'm2.title': 'Открытый Wi-Fi',
      'm2.desc': 'Анализ незашифрованного HTTP-трафика и декодирование Base64-токена.',
      'm3.title': 'Обход SQL-запроса',
      'm3.desc': 'Изучение SQL-инъекций и защиты через Prepared Statements в изолированной песочнице.',
      'm4.title': 'Шпион на входе',
      'm4.desc': 'Поиск скрипта formjacking (кража ввода формы) и настройка строгого CSP.',
      'm5.title': 'Теневая камера',
      'm5.desc': 'Аудит заводских паролей по умолчанию на IoT IP-камере.',
      'm6.title': 'Анти-DDoS Щит',
      'm6.desc': 'Поиск подсети ботнета в access-логах Nginx и блокировка через WAF.',
      'ins.title': 'Запуск за 30 секунд',
      'ins.sub': 'Открытый код (MIT). Порты привязаны только к 127.0.0.1 — безопасно для вашей сети.',
      'ins.cli':
        '# Вариант 1: Через Git\n' +
        'git clone https://github.com/BekbolatBolebay/CyberArena.git\n' +
        'cd CyberArena\n' +
        './arena.sh profile   # Проверить мощность ноутбука\n' +
        './arena.sh auto      # Запустить адаптированный режим\n\n' +
        '# Вариант 2: Скачать ZIP (без Git)\n' +
        'unzip CyberArena-main.zip && cd CyberArena-main\n' +
        'chmod +x arena.sh scripts/hardware_profile.py && ./arena.sh auto',
      'footer.text': 'CyberArena · Open Source (MIT) · Исключительно в образовательных и защитных целях',
    },
    en: {
      pageTitle: 'CyberArena — Adaptive Cyber Range | Open Source (MIT)',
      'badge.oss': 'MIT OPEN SOURCE',
      'nav.adaptive': 'Adaptive',
      'nav.demo': 'Terminal',
      'nav.missions': 'Missions',
      'nav.install': 'Install',
      'hero.kicker': 'KEIN SYSTEM IST SICHER // PERSONAL CYBER LAB',
      'hero.title': 'A cyber arena that adapts to your laptop.',
      'hero.lead':
        'CyberArena is an open-source security lab for students and developers. It inspects your CPU, RAM, and disk, automatically selecting LIGHT, BALANCED, or FULL mode without overheating.',
      'gh.starsDefault': '★ Open Source (MIT)',
      'gh.updatedDefault': 'v2.0 · Adaptive',
      'gh.updatedPrefix': 'Updated',
      'hero.copy': 'Copy',
      'hero.copied': 'Copied ✔',
      'hero.zip': 'Download ZIP',
      'hero.calc': 'Hardware Calculator',
      'hero.github': 'View on GitHub',
      'ad.title': '⚡ Automatic Hardware Adaptation',
      'ad.sub': 'Adjust the sliders to preview which profile CyberArena selects for your machine:',
      'ad.ram': 'Memory (RAM):',
      'ad.cpu': 'CPU Cores:',
      'ad.cpuUnit': 'Cores',
      'ad.docker': 'Docker / Podman installed',
      'ad.targets': 'Active targets:',
      'tier.lightTitle': '≤ 4 GB RAM or No Docker',
      'tier.lightDesc': 'Pure Python Portal + IP Camera (~60 MB RAM). Runs cool even on low-spec laptops.',
      'tier.balancedTitle': '5–11 GB RAM + Docker',
      'tier.balancedDesc': 'Portal + IP Camera + OWASP Juice Shop with strict CPU/RAM limits.',
      'tier.fullTitle': '12+ GB RAM, 6+ CPU + Docker',
      'tier.fullDesc': 'Full cyber range: Portal + Juice Shop + DVWA + IP Camera.',
      'calc.lightDesc': 'Skips Docker and runs pure Python services. Zero heat and minimal memory use.',
      'calc.balancedDesc': 'Tuned Docker limits (0.20–0.45 CPU). Adds the OWASP Juice Shop web lab.',
      'calc.fullDesc': 'Full capacity lab — all 4 vulnerable and defensive targets run concurrently.',
      'demo.title': '>_ CLAY Terminal Demo',
      'demo.sub': 'Try typing help, profile, or missions in the interactive terminal below:',
      'demo.placeholder': 'help, profile, missions, clear',
      'demo.run': 'Run',
      'demo.welcome1': 'CLAY://CYBER-ARENA — Demo Terminal v2.0',
      'demo.welcome2': 'Type `help` or `missions` to get started.\n',
      'demo.help': 'Commands: help, profile, missions, who-am-i, clear',
      'demo.profilePrefix': 'Selected calculator profile:',
      'demo.whoami': 'KEIN SYSTEM IST SICHER. Knowledge is the strongest defense.',
      'demo.unknown': "Unknown command: {cmd}. Type 'help'.",
      'mis.title': '🎭 6 "Who Am I" Style Missions',
      'mis.sub': 'Each operation lets you analyze the vulnerability and master the Blue Team defense.',
      'm1.title': 'Hidden Trail',
      'm1.desc': 'Initial reconnaissance by inspecting /robots.txt and hidden endpoints.',
      'm2.title': 'Open Wi-Fi Sniffing',
      'm2.desc': 'Inspecting cleartext HTTP traffic and decoding Base64 tokens.',
      'm3.title': 'Bypassing the Gate',
      'm3.desc': 'Understanding SQL injection and Prepared Statements in an in-memory sandbox.',
      'm4.title': 'Formjacking Spy',
      'm4.desc': 'Detecting malicious form-capture JavaScript and enforcing strict CSP headers.',
      'm5.title': 'Shadow Camera',
      'm5.desc': 'Auditing default factory credentials on a simulated IoT IP camera.',
      'm6.title': 'Anti-DDoS Shield',
      'm6.desc': 'Identifying botnet subnets in Nginx access logs and applying WAF rules.',
      'ins.title': 'Launch in 30 seconds',
      'ins.sub': 'Open source (MIT). All services bind strictly to 127.0.0.1 for local safety.',
      'ins.cli':
        '# Option 1: Via Git\n' +
        'git clone https://github.com/BekbolatBolebay/CyberArena.git\n' +
        'cd CyberArena\n' +
        './arena.sh profile   # Check your laptop specs\n' +
        './arena.sh auto      # Start adaptive profile\n\n' +
        '# Option 2: Direct ZIP (no Git needed)\n' +
        'unzip CyberArena-main.zip && cd CyberArena-main\n' +
        'chmod +x arena.sh scripts/hardware_profile.py && ./arena.sh auto',
      'footer.text': 'CyberArena · Open Source (MIT) · 100% Educational & Defensive Security Lab',
    },
  };

  let currentLang = 'kk';
  let lastRepoUpdatedDate = null;

  function t(key) {
    const dict = I18N[currentLang] || I18N.kk;
    return dict[key] || I18N.kk[key] || key;
  }

  function initCanvas() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let w = 0;
    let h = 0;
    const nodes = [];

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    for (let i = 0; i < 36; i += 1) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        red: i % 5 === 0,
      });
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      for (let i = 0; i < nodes.length; i += 1) {
        const a = nodes[i];
        a.x += a.vx;
        a.y += a.vy;
        if (a.x < 0 || a.x > w) a.vx *= -1;
        if (a.y < 0 || a.y > h) a.vy *= -1;
        for (let j = i + 1; j < nodes.length; j += 1) {
          const b = nodes[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < 140) {
            ctx.strokeStyle = a.red || b.red
              ? `rgba(255,42,85,${(1 - d / 140) * 0.2})`
              : `rgba(0,255,136,${(1 - d / 140) * 0.16})`;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
        ctx.fillStyle = a.red ? 'rgba(255,42,85,0.65)' : 'rgba(0,255,136,0.5)';
        ctx.beginPath();
        ctx.arc(a.x, a.y, 2, 0, Math.PI * 2);
        ctx.fill();
      }
      window.requestAnimationFrame(draw);
    }
    draw();
  }

  function renderGitHubUpdatedPill() {
    const el = document.getElementById('gh-updated');
    if (lastRepoUpdatedDate) {
      el.textContent = `${t('gh.updatedPrefix')}: ${lastRepoUpdatedDate}`;
    } else {
      el.textContent = t('gh.updatedDefault');
    }
  }

  async function loadGitHubStats() {
    try {
      const res = await fetch('https://api.github.com/repos/BekbolatBolebay/CyberArena');
      if (!res.ok) return;
      const data = await res.json();
      if (typeof data.stargazers_count === 'number') {
        document.getElementById('gh-stars').textContent = `★ ${data.stargazers_count} Stars · MIT`;
      }
      if (data.pushed_at) {
        lastRepoUpdatedDate = String(data.pushed_at).slice(0, 10);
        renderGitHubUpdatedPill();
      }
    } catch {
      // Keep default offline pills if GitHub API is unreachable
    }
  }

  function updateCalculator() {
    const ramGb = Number(document.getElementById('ram-slider').value);
    const cpu = Number(document.getElementById('cpu-slider').value);
    const hasDocker = document.getElementById('docker-check').checked;

    document.getElementById('ram-val').textContent = `${ramGb} GB`;
    document.getElementById('cpu-val').textContent = `${cpu} ${t('ad.cpuUnit')}`;

    let profile = 'full';
    if (!hasDocker || ramGb <= 4 || cpu <= 2) {
      profile = 'light';
    } else if (ramGb < 12 || cpu < 6) {
      profile = 'balanced';
    }

    const badge = document.getElementById('res-profile');
    const title = document.getElementById('res-title');
    const desc = document.getElementById('res-desc');
    const list = document.getElementById('res-list');

    badge.className = `res-badge ${profile}`;
    badge.textContent = profile.toUpperCase();
    list.textContent = '';

    const data = {
      light: {
        title: 'LIGHT (~60 MB RAM)',
        desc: t('calc.lightDesc'),
        targets: ['Portal (:8000)', 'IP Camera (:8081)'],
      },
      balanced: {
        title: 'BALANCED (~768 MB RAM)',
        desc: t('calc.balancedDesc'),
        targets: ['Portal (:8000)', 'OWASP Juice Shop (:3000)', 'IP Camera (:8081)'],
      },
      full: {
        title: 'FULL (~1.5 GB RAM)',
        desc: t('calc.fullDesc'),
        targets: ['Portal (:8000)', 'OWASP Juice Shop (:3000)', 'DVWA (:8080)', 'IP Camera (:8081)'],
      },
    }[profile];

    title.textContent = data.title;
    desc.textContent = data.desc;
    data.targets.forEach((target) => {
      const li = document.createElement('li');
      li.textContent = target;
      list.appendChild(li);
    });
  }

  function termPrint(text, cls = '') {
    const out = document.getElementById('demo-out');
    const line = document.createElement('div');
    line.className = `demo-line ${cls}`.trim();
    line.textContent = text;
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  function resetTerminalWelcome() {
    document.getElementById('demo-out').textContent = '';
    termPrint(t('demo.welcome1'), 'ok');
    termPrint(t('demo.welcome2'), 'dim');
  }

  function handleDemoCmd(raw) {
    const cmd = raw.trim().toLowerCase();
    if (!cmd) return;
    termPrint(`root@clay:~# ${raw.trim()}`, 'cmd');

    if (cmd === 'clear') {
      document.getElementById('demo-out').textContent = '';
      return;
    }
    if (cmd === 'help') {
      termPrint(t('demo.help'));
      return;
    }
    if (cmd === 'profile') {
      const p = document.getElementById('res-profile').textContent;
      const titleText = document.getElementById('res-title').textContent;
      termPrint(`${t('demo.profilePrefix')} ${p} — ${titleText}`, 'ok');
      return;
    }
    if (cmd === 'missions') {
      termPrint(
        [
          `OP-01: ${t('m1.title')} (Recon / robots.txt)`,
          `OP-02: ${t('m2.title')} (Sniffing / Base64)`,
          `OP-03: ${t('m3.title')} (SQL Injection Sandbox)`,
          `OP-04: ${t('m4.title')} (Formjacking & CSP)`,
          `OP-05: ${t('m5.title')} (IoT Default Passwords)`,
          `OP-06: ${t('m6.title')} (Blue Team Anti-DDoS WAF)`,
        ].join('\n'),
        'ok'
      );
      return;
    }
    if (cmd === 'who-am-i' || cmd === 'whoami') {
      termPrint(t('demo.whoami'), 'ok');
      return;
    }
    termPrint(t('demo.unknown').replace('{cmd}', cmd), 'err');
  }

  function applyLang(lang) {
    currentLang = I18N[lang] ? lang : 'kk';
    document.documentElement.lang = currentLang;
    document.title = t('pageTitle');

    try {
      window.localStorage.setItem('cyberarena_lang', currentLang);
    } catch {
      // Ignore storage failures in private mode
    }

    document.querySelectorAll('[data-i18n]').forEach((node) => {
      const key = node.getAttribute('data-i18n');
      if (key) node.textContent = t(key);
    });

    document.getElementById('demo-input').placeholder = t('demo.placeholder');
    document.getElementById('cli-block').textContent = t('ins.cli');

    document.querySelectorAll('.lang-switch button').forEach((btn) => {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === currentLang);
    });

    renderGitHubUpdatedPill();
    updateCalculator();
    resetTerminalWelcome();
  }

  document.addEventListener('DOMContentLoaded', () => {
    initCanvas();

    let savedLang = 'kk';
    try {
      const stored = window.localStorage.getItem('cyberarena_lang');
      if (stored && I18N[stored]) savedLang = stored;
    } catch {
      // Fallback to default kk
    }

    applyLang(savedLang);
    loadGitHubStats();

    document.getElementById('ram-slider').addEventListener('input', updateCalculator);
    document.getElementById('cpu-slider').addEventListener('input', updateCalculator);
    document.getElementById('docker-check').addEventListener('change', updateCalculator);

    document.getElementById('demo-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('demo-input');
      const val = input.value;
      input.value = '';
      handleDemoCmd(val);
    });

    document.querySelectorAll('.lang-switch button').forEach((btn) => {
      btn.addEventListener('click', () => applyLang(btn.getAttribute('data-lang')));
    });

    document.getElementById('btn-copy').addEventListener('click', async () => {
      const text = document.getElementById('install-cmd').textContent;
      const btn = document.getElementById('btn-copy');
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = t('hero.copied');
        window.setTimeout(() => {
          btn.textContent = t('hero.copy');
        }, 1800);
      } catch {
        btn.textContent = text;
      }
    });
  });
})();
