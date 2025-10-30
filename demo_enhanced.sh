#!/bin/bash
# Vectro+ Enhanced Video Demo Script
# Perfect for recording a compelling demo video

set -e

# Colors and formatting
BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directory of this script (repo root for vectro-plus)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Animation helpers
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    while ps -p $pid > /dev/null 2>&1; do
        local temp=${spinstr#?}
        printf " ${CYAN}%c${NC}  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

print_header() {
    echo ""
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_step() {
    echo ""
    echo -e "${BOLD}${BLUE}▶ $1${NC}"
    echo -e "${DIM}$2${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_data() {
    echo -e "${CYAN}→${NC} $1"
}

pause_for_demo() {
    sleep 1.5
}

# Clear screen for clean video start
clear

print_header "🚀 VECTRO+ INTERACTIVE DEMO"
echo -e "${BOLD}High-Performance Embedding Compression & Search in Rust${NC}"
echo -e "${DIM}Demonstrating streaming compression, quantization, and semantic search${NC}"
pause_for_demo

# Setup
DEMO_DIR=$(mktemp -d)
cd "$DEMO_DIR"
print_info "Demo workspace: ${CYAN}$DEMO_DIR${NC}"
pause_for_demo

# ============================================================================
# PART 1: DATA GENERATION
# ============================================================================

print_step "STEP 1: Creating Sample Embeddings" \
           "Generating realistic embedding vectors for semantic concepts"

cat > sample_semantic.jsonl << 'EOF'
{"id": "🍎 apple", "vector": [0.92, 0.15, 0.18, 0.12, 0.25, 0.08, 0.14, 0.22]}
{"id": "🍊 orange", "vector": [0.88, 0.20, 0.22, 0.15, 0.28, 0.10, 0.16, 0.25]}
{"id": "🍌 banana", "vector": [0.85, 0.25, 0.20, 0.18, 0.22, 0.12, 0.15, 0.20]}
{"id": "🍇 grape", "vector": [0.80, 0.22, 0.25, 0.20, 0.30, 0.15, 0.18, 0.28]}
{"id": "🚗 car", "vector": [0.12, 0.88, 0.82, 0.75, 0.68, 0.15, 0.20, 0.10]}
{"id": "🚙 truck", "vector": [0.15, 0.85, 0.88, 0.72, 0.65, 0.18, 0.22, 0.12]}
{"id": "🚲 bicycle", "vector": [0.22, 0.78, 0.70, 0.82, 0.58, 0.25, 0.30, 0.20]}
{"id": "🏍️  motorcycle", "vector": [0.18, 0.82, 0.75, 0.85, 0.62, 0.22, 0.28, 0.15]}
{"id": "🔴 red", "vector": [0.50, 0.48, 0.15, 0.12, 0.92, 0.88, 0.20, 0.15]}
{"id": "🔵 blue", "vector": [0.45, 0.52, 0.18, 0.15, 0.15, 0.12, 0.88, 0.92]}
{"id": "🟢 green", "vector": [0.55, 0.45, 0.20, 0.18, 0.28, 0.32, 0.85, 0.25]}
{"id": "🟡 yellow", "vector": [0.52, 0.50, 0.22, 0.20, 0.85, 0.78, 0.30, 0.28]}
{"id": "⚡ fast", "vector": [0.18, 0.85, 0.92, 0.88, 0.75, 0.15, 0.22, 0.18]}
{"id": "🐌 slow", "vector": [0.75, 0.25, 0.15, 0.12, 0.20, 0.82, 0.78, 0.85]}
{"id": "🔥 hot", "vector": [0.88, 0.15, 0.12, 0.10, 0.92, 0.85, 0.18, 0.15]}
{"id": "❄️  cold", "vector": [0.15, 0.82, 0.78, 0.75, 0.12, 0.18, 0.88, 0.92]}
EOF

SAMPLE_COUNT=$(wc -l < sample_semantic.jsonl | tr -d ' ')
print_success "Created ${BOLD}${SAMPLE_COUNT}${NC} semantic embeddings"
print_data "Categories: fruits 🍎, vehicles 🚗, colors 🔴, properties ⚡"
print_data "Dimensions: ${BOLD}8${NC} (each embedding)"
pause_for_demo

# ============================================================================
# PART 2: COMPRESSION
# ============================================================================

print_step "STEP 2: Streaming Compression" \
           "Converting JSONL to efficient binary format (STREAM1)"

echo -e "${CYAN}⠋${NC} Compressing..."
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- compress sample_semantic.jsonl dataset.bin

REGULAR_SIZE=$(stat -f%z dataset.bin 2>/dev/null || stat -c%s dataset.bin 2>/dev/null)
print_success "Created ${BOLD}dataset.bin${NC}"
print_data "Format: ${BOLD}VECTRO+STREAM1${NC} (32-bit floats)"
print_data "Size: ${BOLD}${REGULAR_SIZE}${NC} bytes"
pause_for_demo

# ============================================================================
# PART 3: QUANTIZATION
# ============================================================================

print_step "STEP 3: Quantization (Size Reduction)" \
           "Converting floats to 8-bit with per-dimension scaling"

echo -e "${CYAN}⠋${NC} Quantizing..."
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- compress sample_semantic.jsonl dataset_q.bin --quantize

QUANTIZED_SIZE=$(stat -f%z dataset_q.bin 2>/dev/null || stat -c%s dataset_q.bin 2>/dev/null)
SAVINGS=$((100 - (QUANTIZED_SIZE * 100 / REGULAR_SIZE)))

print_success "Created ${BOLD}dataset_q.bin${NC}"
print_data "Format: ${BOLD}QSTREAM1${NC} (8-bit quantized)"
print_data "Size: ${BOLD}${QUANTIZED_SIZE}${NC} bytes"
echo ""
echo -e "${BOLD}${GREEN}💾 Space Savings: ${SAVINGS}%${NC}"
echo -e "${DIM}   Original: ${REGULAR_SIZE} bytes → Quantized: ${QUANTIZED_SIZE} bytes${NC}"
pause_for_demo

# ============================================================================
# PART 4: SEMANTIC SEARCH
# ============================================================================

print_step "STEP 4: Semantic Search Demo" \
           "Finding similar embeddings using cosine similarity"

echo -e "${BOLD}Query 1:${NC} Searching for fruits 🍎 (similar to apple)"
print_data "Vector: [0.92, 0.15, 0.18, 0.12, 0.25, 0.08, 0.14, 0.22]"
echo ""
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- search "0.92,0.15,0.18,0.12,0.25,0.08,0.14,0.22" --top-k 4 --dataset dataset.bin | while read line; do
    echo -e "  ${GREEN}→${NC} $line"
done
pause_for_demo

echo ""
echo -e "${BOLD}Query 2:${NC} Searching for vehicles 🚗 (similar to car)"
print_data "Vector: [0.12, 0.88, 0.82, 0.75, 0.68, 0.15, 0.20, 0.10]"
echo ""
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- search "0.12,0.88,0.82,0.75,0.68,0.15,0.20,0.10" --top-k 4 --dataset dataset.bin | while read line; do
    echo -e "  ${GREEN}→${NC} $line"
done
pause_for_demo

echo ""
echo -e "${BOLD}Query 3:${NC} Searching for warm colors 🔴 (similar to red)"
print_data "Vector: [0.50, 0.48, 0.15, 0.12, 0.92, 0.88, 0.20, 0.15]"
echo ""
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- search "0.50,0.48,0.15,0.12,0.92,0.88,0.20,0.15" --top-k 3 --dataset dataset.bin | while read line; do
    echo -e "  ${GREEN}→${NC} $line"
done
pause_for_demo

# ============================================================================
# PART 5: WEB UI DEMO
# ============================================================================

print_step "STEP 5: Interactive Web UI" \
           "Launching web server with real-time search dashboard"

print_info "Starting Vectro+ server on ${BOLD}http://localhost:8080${NC}"
echo ""
echo -e "${CYAN}→${NC} Load the dataset in your browser:"
echo -e "   ${DIM}1. Open http://localhost:8080${NC}"
echo -e "   ${DIM}2. Click 'Upload' tab${NC}"
echo -e "   ${DIM}3. Enter path: ${BOLD}$DEMO_DIR/dataset.bin${NC}"
echo -e "   ${DIM}4. Click 'Load Dataset'${NC}"
echo -e "   ${DIM}5. Switch to 'Search' tab and try queries!${NC}"
echo ""
print_info "The server provides:"
echo -e "   ${GREEN}•${NC} Real-time semantic search"
echo -e "   ${GREEN}•${NC} Performance metrics"
echo -e "   ${GREEN}•${NC} Beautiful web interface"
echo -e "   ${GREEN}•${NC} REST API for integrations"
echo ""
print_data "Press ${BOLD}Ctrl+C${NC} to stop the server"
echo ""

# Start server
cd "$DEMO_DIR"
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- serve --port 8080

# ============================================================================
# CLEANUP (won't reach here due to Ctrl+C, but good practice)
# ============================================================================

print_header "✅ DEMO COMPLETE"
echo -e "${GREEN}Thank you for watching!${NC}"
echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo -e "  ${CYAN}•${NC} Explore the codebase: ${DIM}github.com/yourorg/vectro-plus${NC}"
echo -e "  ${CYAN}•${NC} Read the docs: ${DIM}DEMO.md, QSTREAM.md${NC}"
echo -e "  ${CYAN}•${NC} Run benchmarks: ${DIM}cargo bench -p vectro_lib${NC}"
echo -e "  ${CYAN}•${NC} Try your own datasets!"
echo ""
echo -e "${DIM}Demo files saved in: $DEMO_DIR${NC}"
