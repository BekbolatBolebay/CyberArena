#!/usr/bin/env bash
# ==============================================================================
# CyberArena - Ноутбук қуатына бейімделетін Қауіпсіз Кибер-Полигон Пульті
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ADAPTIVE_COMPOSE="$DIR/docker-compose.adaptive.yml"

print_banner() {
    echo -e "${CYAN}"
    echo "=========================================================="
    echo "   🛡️  CYBER ARENA - АДАПТИВТІ КИБЕР-ПОЛИГОН ПУЛЬТІ"
    echo "   Open Source (MIT) | 100% Оқшауланған | Құрылғыға сай"
    echo "=========================================================="
    echo -e "${NC}"
}

compose_cmd() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

start_adaptive() {
    local forced_profile="${1:-}"
    local profile_args=()
    if [[ -n "$forced_profile" ]]; then
        profile_args+=(--profile "$forced_profile")
    fi

    print_banner
    echo -e "${YELLOW}[*] Ноутбуктің CPU / RAM / Диск қуаты тексерілуде...${NC}"
    python3 "$DIR/scripts/hardware_profile.py" "${profile_args[@]}" --write-compose "$ADAPTIVE_COMPOSE"

    local mode
    mode=$(python3 "$DIR/scripts/hardware_profile.py" "${profile_args[@]}" --json | python3 -c "import sys, json; print(json.load(sys.stdin)['mode'])")
    local profile
    profile=$(python3 "$DIR/scripts/hardware_profile.py" "${profile_args[@]}" --json | python3 -c "import sys, json; print(json.load(sys.stdin)['profile'])")

    echo ""
    if [[ "$mode" == "native" ]]; then
        echo -e "${YELLOW}[*] LIGHT режимі: Docker-сіз таза Python-да іске қосылуда (~60 MB RAM)...${NC}"
        mkdir -p "$DIR/logs"
        pkill -f "targets/ip_camera/camera_server.py" 2>/dev/null || true
        pkill -f "portal/server.py" 2>/dev/null || true
        python3 "$DIR/targets/ip_camera/camera_server.py" > "$DIR/logs/camera.log" 2>&1 &
        python3 "$DIR/portal/server.py" > "$DIR/logs/portal.log" 2>&1 &
        sleep 1
        echo -e "${GREEN}[✔] АРЕНА LIGHT РЕЖИМІНДЕ ДАЙЫН!${NC}"
        echo -e "----------------------------------------------------------"
        echo -e "🎭 0. CyberArena Portal (Who Am I UI):   ${BLUE}http://127.0.0.1:8000${NC}"
        echo -e "📹 1. IP Camera (Бейнебақылау Камерасы):  ${BLUE}http://127.0.0.1:8081${NC}"
    else
        echo -e "${YELLOW}[*] ${profile^^} режимінде бейімделген контейнерлер іске қосылуда...${NC}"
        compose_cmd -f "$ADAPTIVE_COMPOSE" up -d --build
        echo ""
        echo -e "${GREEN}[✔] АРЕНА ${profile^^} РЕЖИМІНДЕ ДАЙЫН ЖӘНЕ ОҚШАУЛАНҒАН!${NC}"
        echo -e "----------------------------------------------------------"
        echo -e "🎭 0. CyberArena Portal (Who Am I UI):   ${BLUE}http://127.0.0.1:8000${NC}"
        echo -e "🛒 1. OWASP Juice Shop (Интернет-Дүкен):  ${BLUE}http://127.0.0.1:3000${NC}"
        if [[ "$profile" == "full" ]]; then
            echo -e "🎯 2. DVWA (Осал Сервер):                ${BLUE}http://127.0.0.1:8080${NC}"
        fi
        echo -e "📹 3. IP Camera (Бейнебақылау Камерасы):  ${BLUE}http://127.0.0.1:8081${NC}"
    fi
    echo -e "----------------------------------------------------------"
    echo -e "Аренаны тоқтату үшін: ${RED}./arena.sh stop${NC}"
}

case "${1:-}" in
    auto|start)
        forced=""
        if [[ "${2:-}" == "--profile" && -n "${3:-}" ]]; then
            forced="$3"
        fi
        start_adaptive "$forced"
        ;;

    profile)
        print_banner
        python3 "$DIR/scripts/hardware_profile.py"
        ;;

    portal)
        print_banner
        echo -e "${YELLOW}[*] CyberArena Portal (Who Am I Edition) іске қосылуда...${NC}"
        echo -e "🎭 Ашу: ${BLUE}http://127.0.0.1:8000${NC}"
        python3 "$DIR/portal/server.py"
        ;;

    stop)
        print_banner
        echo -e "${YELLOW}[*] Арена серверлері тоқтатылуда...${NC}"
        if [[ -f "$ADAPTIVE_COMPOSE" ]]; then
            compose_cmd -f "$ADAPTIVE_COMPOSE" down 2>/dev/null || true
        fi
        compose_cmd down 2>/dev/null || true
        pkill -f "targets/ip_camera/camera_server.py" 2>/dev/null || true
        pkill -f "portal/server.py" 2>/dev/null || true
        echo -e "${GREEN}[✔] Барлық серверлер сөндірілді. Жад пен процессор босатылды!${NC}"
        ;;

    status)
        print_banner
        python3 "$DIR/scripts/hardware_profile.py"
        echo ""
        echo -e "${BLUE}[*] Қазіргі контейнерлердің күйі мен ресурстары:${NC}"
        docker ps --filter "name=arena_" 2>/dev/null || true
        echo ""
        echo -e "${BLUE}[*] Ресурс қолданылуы:${NC}"
        docker stats --no-stream $(docker ps -q --filter "name=arena_") 2>/dev/null || echo "Белсенді Docker контейнерлері жоқ (немесе LIGHT режимінде)."
        ;;

    logs)
        print_banner
        echo -e "${YELLOW}[*] Нақты уақыттағы сервер логтары (Blue Team қорғаныс режимі):${NC}"
        echo -e "Тоқтату үшін Ctrl + C басыңыз."
        if [[ -f "$ADAPTIVE_COMPOSE" ]]; then
            compose_cmd -f "$ADAPTIVE_COMPOSE" logs -f
        else
            compose_cmd logs -f
        fi
        ;;

    sniff)
        print_banner
        PCAP_FILE="$DIR/pcaps/capture_$(date +%Y%m%d_%H%M%S).pcap"
        echo -e "${GREEN}[✔] Трафикті ауадан/желіден ұстау басталды!${NC}"
        echo -e "Файл сақталуда: ${BLUE}$PCAP_FILE${NC}"
        echo -e "${YELLOW}[*] Аренаның 3000 және 8080 порттарының бүкіл трафигі жазылуда...${NC}"
        echo -e "Тоқтату үшін ${RED}Ctrl + C${NC} басыңыз."
        echo ""
        sudo tcpdump -i lo -nn -s 0 "port 3000 or port 8080" -w "$PCAP_FILE"
        echo ""
        echo -e "${GREEN}[✔] Трафик жазылды! Оны Wireshark-та көру үшін:${NC}"
        echo -e "   wireshark $PCAP_FILE &"
        ;;

    *)
        print_banner
        echo "Қолдану тәсілі:"
        echo "  ./arena.sh auto                      - Ноут қуатына сай автоматты іске қосу"
        echo "  ./arena.sh start --profile <түрі>    - Нақты режиммен қосу (light | balanced | full)"
        echo "  ./arena.sh profile                   - Жүйе қуаты мен ұсынылған режимді көру"
        echo "  ./arena.sh portal                    - Тек CyberArena веб-порталын іске қосу (Python)"
        echo "  ./arena.sh stop                      - Барлық серверлерді сөндіру"
        echo "  ./arena.sh status                    - Ресурс қолданылуын тексеру"
        echo "  ./arena.sh sniff                     - Трафикті нақты уақытта ұстау (Sniffing)"
        echo "  ./arena.sh logs                      - Нақты уақыттағы сервер логтарын көру"
        echo ""
        ;;
esac
