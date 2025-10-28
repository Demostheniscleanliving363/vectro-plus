#!/bin/bash
# Vectro+ 30-Second Teaser Demo
# Quick showcase for social media clips

set -e

# Colors
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear
echo -e "${BOLD}${MAGENTA}🚀 VECTRO+ SPEED DEMO${NC}"
echo ""

# Quick data
cat > /tmp/quick.jsonl << 'EOF'
{"id": "apple", "vector": [0.9, 0.1, 0.2]}
{"id": "orange", "vector": [0.85, 0.15, 0.25]}
{"id": "car", "vector": [0.1, 0.9, 0.8]}
{"id": "truck", "vector": [0.15, 0.88, 0.82]}
EOF

echo -e "${CYAN}→${NC} Compressing embeddings..."
cargo run --release -p vectro_cli -- compress /tmp/quick.jsonl /tmp/quick.bin 2>/dev/null
cargo run --release -p vectro_cli -- compress /tmp/quick.jsonl /tmp/quick_q.bin --quantize 2>/dev/null

SIZE1=$(stat -f%z /tmp/quick.bin 2>/dev/null || stat -c%s /tmp/quick.bin 2>/dev/null)
SIZE2=$(stat -f%z /tmp/quick_q.bin 2>/dev/null || stat -c%s /tmp/quick_q.bin 2>/dev/null)
SAVED=$((100 - (SIZE2 * 100 / SIZE1)))

echo -e "${GREEN}✓${NC} Regular: ${SIZE1}B → Quantized: ${SIZE2}B (${BOLD}${SAVED}% saved${NC})"
echo ""

echo -e "${CYAN}→${NC} Searching for 'apple'..."
cargo run --release -p vectro_cli -- search "0.9,0.1,0.2" --top-k 2 --dataset /tmp/quick.bin 2>/dev/null
echo ""

echo -e "${BOLD}${GREEN}⚡ Vectro+ • Rust • Fast • Efficient${NC}"
echo -e "${CYAN}github.com/yourorg/vectro-plus${NC}"

rm -f /tmp/quick*
