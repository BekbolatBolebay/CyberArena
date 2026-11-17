#!/usr/bin/env bash
# ==============================================================================
# CyberArena - Жеке Қауіпсіз Кибер-Полигонды Басқару Скрипті
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}"
    echo "=========================================================="
    echo "   🛡️  CYBER ARENA - ҚАУІПСІЗ КИБЕР-ПОЛИГОН ПУЛЬТІ"
    echo "   Ноутбук қызбайды | 100% Оқшауланған | Толық бақылау"
    echo "=========================================================="
    echo -e "${NC}"
}

case "$1" in
    start)
        print_banner
        echo -e "${YELLOW}[*] Арена серверлері іске қосылуда...${NC}"
        docker-compose up -d --build
        echo ""
        echo -e "${GREEN}[✔] АРЕНА ДАЙЫН ЖӘНЕ ҚАУІПСІЗ ОҚШАУЛАНҒАН!${NC}"
        echo -e "----------------------------------------------------------"
        echo -e "🎭 0. CyberArena Portal (Who Am I UI):   ${BLUE}http://127.0.0.1:8000${NC}"
        echo -e "🛒 1. OWASP Juice Shop (Интернет-Дүкен):  ${BLUE}http://127.0.0.1:3000${NC}"
        echo -e "🎯 2. DVWA (Осал Сервер):                ${BLUE}http://127.0.0.1:8080${NC}"
        echo -e "📹 3. IP Camera (Бейнебақылау Камерасы):  ${BLUE}http://127.0.0.1:8081${NC}"
        echo -e "----------------------------------------------------------"
        echo -e "Тек веб-порталды жылдам қосу: ${YELLOW}./arena.sh portal${NC}"
        echo -e "Трафикті тыңдау үшін: ${YELLOW}./arena.sh sniff${NC}"
        echo -e "Сервер логтарын көру: ${YELLOW}./arena.sh logs${NC}"
        echo -e "Аренаны тоқтату үшін: ${RED}./arena.sh stop${NC}"
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
        docker-compose down
        pkill -f camera_server.py 2>/dev/null || true
        pkill -f "portal/server.py" 2>/dev/null || true
        echo -e "${GREEN}[✔] Барлық серверлер сөндірілді. Жад пен процессор босатылды!${NC}"
        ;;

    status)
        print_banner
        echo -e "${BLUE}[*] Қазіргі контейнерлердің күйі мен ресурстары:${NC}"
        docker ps --filter "name=arena_"
        echo ""
        echo -e "${BLUE}[*] Ресурс қолданылуы (Ноуттың жүктемесі):${NC}"
        docker stats --no-stream $(docker ps -q --filter "name=arena_") 2>/dev/null || echo "Арена іске қосылмаған."
        ;;

    logs)
        print_banner
        echo -e "${YELLOW}[*] Нақты уақыттағы сервер логтары (Blue Team қорғаныс режимі):${NC}"
        echo -e "Тоқтату үшін Ctrl + C басыңыз."
        docker-compose logs -f
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
        echo "  ./arena.sh start    - Барлық аренаны іске қосу (Docker)"
        echo "  ./arena.sh portal   - Тек CyberArena веб-порталын іске қосу (Python)"
        echo "  ./arena.sh stop     - Аренаны сөндіру (барлық ресурсты босату)"
        echo "  ./arena.sh status   - Ноутбуктің қызуы мен жадын тексеру"
        echo "  ./arena.sh sniff    - Трафикті нақты уақытта ұстап алу (Sniffing)"
        echo "  ./arena.sh logs     - Хакер не істеп жатқанын көретін логтар"
        echo ""
        ;;
esac
