# 🌐 CyberArena — Доменге және Серверге Шығару Нұсқаулығы

## А-нұсқасы: Тегін Лэндинг бетін шығару (Cloudflare Pages, 0 ₸, картасыз)

Егер әзірге `landing/` папкасындағы ресми сайтты онлайн доменге шығарып, адамдар GitHub-тан жүктеп алып өз ноутында `./arena.sh auto` арқылы іске қоссын десеңіз:

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git** таңдаңыз.
2. GitHub-тағы `BekbolatBolebay/CyberArena` репозиторийін таңдаңыз (репо **Public** болуы тиіс, Open Source MIT!).
3. Баптаулары:
   * **Build command:** *(бос қалдырыңыз)*
   * **Build output directory:** `landing`
4. **Save and Deploy** басыңыз — 30 секундта тегін HTTPS сайт дайын болады!
5. **Custom domains** бөлімінен өз `.kz` доменіңізді (мысалы, `arena.yourdomain.kz`) бір батырмамен байлай аласыз.

---

## Б-нұсқасы: Толық Порталды VPS серверге шығару

Бұл нұсқаулық **CyberArena** веб-порталын нақты доменге **Cloudflare + Cloudflare Tunnel** арқылы 100% қауіпсіз шығару жолын көрсетеді.

> [!IMPORTANT]
> **Неліктен `docker-compose.prod.yml` қолданамыз?**
> Жергілікті `DVWA` мен `Juice Shop` — әдейі осал жүйелер. Оларды ашық доменге тікелей шығарсаңыз, сыртқы боттар серверіңізді басып алады. Сондықтан `docker-compose.prod.yml` тек қауіпсіз оқшауланған **CyberArena Portal** (`OP-01..OP-06` миссиялары) мен **Nginx Rate-Limit** проксиін ғана интернетке шығарады.

---

## 1. Серверді (VPS) дайындау

1. Ubuntu 24.04 / Debian 12 орнатылған VPS алыңыз (1–2 vCPU, 1–2 GB RAM жеткілікті).
2. Жобаны көшіріп, Docker-ді іске қосыңыз:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2
   git clone <сіздің-репозиторийіңіз> CyberArena
   cd CyberArena
   docker compose -f docker-compose.prod.yml up -d --build
   ```
3. Тексеру (серверде ғана жауап беруі тиіс):
   ```bash
   curl -I http://127.0.0.1:8088/api/health
   ```

---

## 2. Домен мен Cloudflare Tunnel баптау (IP-ді жасыру)

**Cloudflare Tunnel** қолданғанда серверіңіздің нақты IP-мекенжайы сыртқа мүлдем көрінбейді (DDoS пен порт сканерлеуден толық қорғалады) және 80/443 порттарын сыртқа ашудың қажеті жоқ:

1. Домен сатып алып (`.kz` немесе басқа), оның NS-серверлерін **Cloudflare**-ге ауыстырыңыз.
2. VPS-те `cloudflared` орнатыңыз:
   ```bash
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
   sudo dpkg -i cloudflared.deb
   ```
3. Туннель құрып, доменге байлаңыз:
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create cyberarena
   cloudflared tunnel route dns cyberarena arena.yourdomain.kz
   ```
4. [deploy/cloudflared.example.yml](deploy/cloudflared.example.yml) үлгісі бойынша `~/.cloudflared/config.yml` жасап, жүйелік сервис ретінде қосыңыз:
   ```bash
   sudo cloudflared service install
   sudo systemctl enable --now cloudflared
   ```

---

## 3. Қосымша Cloudflare WAF қорғанысы

Cloudflare панелінде мына баптауларды қосу ұсынылады:
* **SSL/TLS → Overview:** `Full` (немесе `Full (strict)`).
* **SSL/TLS → Edge Certificates:** `Always Use HTTPS` = ON, `Automatic HTTPS Rewrites` = ON.
* **Security → Bots:** `Bot Fight Mode` = ON.
* **Security → Settings:** Security Level = `Medium` немесе `High`.
