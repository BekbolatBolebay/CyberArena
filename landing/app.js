(() => {
  'use strict';

  const I18N = {
    kk: {
      'nav.adaptive': 'Адаптация',
      'nav.missions': 'Миссиялар',
      'nav.install': 'Орнату',
      'hero.kicker': 'KEIN SYSTEM IST SICHER // ЖЕКЕ КИБЕР-ПОЛИГОН',
      'hero.title': 'Ноутбугіңе қарай икемделетін кибер-арена.',
      'hero.lead':
        'CyberArena — студенттер мен мамандарға арналған ашық кодты зертхана. Жүйе компьютеріңіздің CPU, RAM және дискісін өзі тексеріп, қыздырмайтын оңтайлы режимді (LIGHT / BALANCED / FULL) автоматты таңдайды.',
      'hero.copy': 'Көшіру',
      'hero.copied': 'Көшірілді ✔',
      'hero.calc': 'Қуат калькуляторы',
      'hero.github': 'GitHub кодын көру',
      'ad.title': '⚡ Ноуттың қуатына автоматты адаптация',
      'ad.sub': 'Слайдты жылжытып, компьютеріңізде қай режим іске қосылатынын тексеріңіз:',
      'ad.ram': 'Жедел жады (RAM):',
      'ad.cpu': 'Процессор ядролары (CPU):',
      'ad.docker': 'Docker / Podman орнатылған',
      'ad.targets': 'Іске қосылатын жүйелер:',
      'mis.title': '🎭 «Who Am I» стиліндегі 6 миссия',
      'mis.sub': 'Әр операцияда шабуыл механизмін зерттеп, соңында Blue Team қорғанысын меңгересіз.',
      'ins.title': '30 секундта іске қосыңыз',
      'ins.sub': 'Толық ашық код (MIT лицензиясы). Жүйе порттарды тек 127.0.0.1-де ашады — сыртқы желіге қауіпсіз.',
    },
    ru: {
      'nav.adaptive': 'Адаптация',
      'nav.missions': 'Миссии',
      'nav.install': 'Установка',
      'hero.kicker': 'KEIN SYSTEM IST SICHER // ЛИЧНЫЙ КИБЕР-ПОЛИГОН',
      'hero.title': 'Кибер-арена, которая подстраивается под ваш ноутбук.',
      'hero.lead':
        'CyberArena — открытая лаборатория для студентов и разработчиков. Скрипт сам проверяет CPU, RAM и диск, выбирая безопасный режим (LIGHT / BALANCED / FULL) без перегрева.',
      'hero.copy': 'Копировать',
      'hero.copied': 'Скопировано ✔',
      'hero.calc': 'Калькулятор мощности',
      'hero.github': 'Исходный код GitHub',
      'ad.title': '⚡ Автоматическая адаптация под железо',
      'ad.sub': 'Двигайте ползунки, чтобы узнать, какой профиль запустится на вашем ПК:',
      'ad.ram': 'Оперативная память (RAM):',
      'ad.cpu': 'Ядра процессора (CPU):',
      'ad.docker': 'Установлен Docker / Podman',
      'ad.targets': 'Запускаемые цели:',
      'mis.title': '🎭 6 миссий в стиле «Кто Я»',
      'mis.sub': 'В каждом задании вы разбираете механику атаки и закрепляете защиту Blue Team.',
      'ins.title': 'Запуск за 30 секунд',
      'ins.sub': 'Открытый код (MIT). Порты привязаны только к 127.0.0.1 — безопасно для вашей сети.',
    },
    en: {
      'nav.adaptive': 'Adaptive',
      'nav.missions': 'Missions',
      'nav.install': 'Install',
      'hero.kicker': 'KEIN SYSTEM IST SICHER // PERSONAL CYBER LAB',
      'hero.title': 'A cyber arena that adapts to your laptop.',
      'hero.lead':
        'CyberArena is an open-source security lab for students and developers. It inspects your CPU, RAM, and disk, automatically selecting LIGHT, BALANCED, or FULL mode without overheating.',
      'hero.copy': 'Copy',
      'hero.copied': 'Copied ✔',
      'hero.calc': 'Hardware Calculator',
      'hero.github': 'View on GitHub',
      'ad.title': '⚡ Automatic Hardware Adaptation',
      'ad.sub': 'Adjust the sliders to preview which profile CyberArena selects for your machine:',
      'ad.ram': 'Memory (RAM):',
      'ad.cpu': 'CPU Cores:',
      'ad.docker': 'Docker / Podman installed',
      'ad.targets': 'Active targets:',
      'mis.title': '🎭 6 "Who Am I" Style Missions',
      'mis.sub': 'Each operation lets you analyze the vulnerability and master the Blue Team defense.',
      'ins.title': 'Launch in 30 seconds',
      'ins.sub': 'Open source (MIT). All services bind strictly to 127.0.0.1 for local safety.',
    },
  };

  let currentLang = 'kk';

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

  function updateCalculator() {
    const ramGb = Number(document.getElementById('ram-slider').value);
    const cpu = Number(document.getElementById('cpu-slider').value);
    const hasDocker = document.getElementById('docker-check').checked;

    document.getElementById('ram-val').textContent = `${ramGb} GB`;
    document.getElementById('cpu-val').textContent = `${cpu} Cores`;

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
        desc: 'Docker қосылмайды — таза Python серверлері іске қосылады. Ноутбук мүлдем қызбайды.',
        targets: ['Portal (:8000)', 'IP Camera (:8081)'],
      },
      balanced: {
        title: 'BALANCED (~768 MB RAM)',
        desc: 'Оңтайландырылған Docker лимиттері (0.20–0.45 CPU). Интернет-дүкен зертханасы қосылады.',
        targets: ['Portal (:8000)', 'OWASP Juice Shop (:3000)', 'IP Camera (:8081)'],
      },
      full: {
        title: 'FULL (~1.5 GB RAM)',
        desc: 'Толық қуатты полигон — барлық 4 зертхана қатар жұмыс істейді.',
        targets: ['Portal (:8000)', 'OWASP Juice Shop (:3000)', 'DVWA (:8080)', 'IP Camera (:8081)'],
      },
    }[profile];

    title.textContent = data.title;
    desc.textContent = data.desc;
    data.targets.forEach((t) => {
      const li = document.createElement('li');
      li.textContent = t;
      list.appendChild(li);
    });
  }

  function applyLang(lang) {
    currentLang = lang;
    const dict = I18N[lang] || I18N.kk;
    document.querySelectorAll('[data-i18n]').forEach((node) => {
      const key = node.getAttribute('data-i18n');
      if (dict[key]) node.textContent = dict[key];
    });
    document.querySelectorAll('.lang-switch button').forEach((btn) => {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    updateCalculator();

    document.getElementById('ram-slider').addEventListener('input', updateCalculator);
    document.getElementById('cpu-slider').addEventListener('input', updateCalculator);
    document.getElementById('docker-check').addEventListener('change', updateCalculator);

    document.querySelectorAll('.lang-switch button').forEach((btn) => {
      btn.addEventListener('click', () => applyLang(btn.getAttribute('data-lang')));
    });

    document.getElementById('btn-copy').addEventListener('click', async () => {
      const text = document.getElementById('install-cmd').textContent;
      const btn = document.getElementById('btn-copy');
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = I18N[currentLang]['hero.copied'];
        window.setTimeout(() => {
          btn.textContent = I18N[currentLang]['hero.copy'];
        }, 1800);
      } catch {
        btn.textContent = text;
      }
    });
  });
})();
