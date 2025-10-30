#!/bin/bash
# Vectro+ Interactive Demo Script
# Run this to see all features in action!

set -e

echo "🚀 Vectro+ Interactive Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directory of this script (repo root for vectro-plus)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Create temp directory
DEMO_DIR=$(mktemp -d)
cd "$DEMO_DIR"
echo -e "${BLUE}📁 Working directory: $DEMO_DIR${NC}"
echo ""

# Step 1: Create sample data
echo -e "${YELLOW}Step 1: Creating sample embeddings...${NC}"
cat > sample.jsonl << 'EOF'
{"id": "apple", "vector": [0.9, 0.1, 0.2, 0.3, 0.4]}
{"id": "orange", "vector": [0.8, 0.2, 0.3, 0.2, 0.3]}
{"id": "banana", "vector": [0.7, 0.3, 0.4, 0.1, 0.2]}
{"id": "car", "vector": [0.1, 0.9, 0.8, 0.7, 0.6]}
{"id": "truck", "vector": [0.2, 0.8, 0.9, 0.6, 0.5]}
{"id": "bicycle", "vector": [0.3, 0.7, 0.6, 0.8, 0.4]}
{"id": "red", "vector": [0.5, 0.5, 0.1, 0.1, 0.9]}
{"id": "blue", "vector": [0.4, 0.6, 0.2, 0.1, 0.8]}
{"id": "green", "vector": [0.6, 0.4, 0.3, 0.2, 0.7]}
{"id": "fast", "vector": [0.2, 0.8, 0.9, 0.8, 0.7]}
EOF

echo -e "${GREEN}✓${NC} Created 10 sample embeddings (5 dimensions each)"
echo "  Categories: fruits, vehicles, colors, adjectives"
echo ""
sleep 1

# Step 2: Regular compression
echo -e "${YELLOW}Step 2: Compressing to binary format...${NC}"
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- compress sample.jsonl dataset.bin
REGULAR_SIZE=$(stat -f%z dataset.bin 2>/dev/null || stat -c%s dataset.bin)
echo -e "${GREEN}✓${NC} Compressed: dataset.bin (${REGULAR_SIZE} bytes)"
echo ""
sleep 1

# Step 3: Quantized compression
echo -e "${YELLOW}Step 3: Compressing with quantization...${NC}"
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- compress sample.jsonl dataset_q.bin --quantize
QUANTIZED_SIZE=$(stat -f%z dataset_q.bin 2>/dev/null || stat -c%s dataset_q.bin)
SAVINGS=$((100 - (QUANTIZED_SIZE * 100 / REGULAR_SIZE)))
echo -e "${GREEN}✓${NC} Compressed: dataset_q.bin (${QUANTIZED_SIZE} bytes)"
echo -e "  💾 Space savings: ${SAVINGS}%"
echo ""
sleep 1

# Step 4: Search demo
echo -e "${YELLOW}Step 4: Testing semantic search...${NC}"
echo ""
echo "Query 1: Search for 'apple' (0.9, 0.1, 0.2, 0.3, 0.4)"
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- search "0.9,0.1,0.2,0.3,0.4" --top-k 3 --dataset dataset.bin
echo ""
sleep 1

echo "Query 2: Search for 'car' (0.1, 0.9, 0.8, 0.7, 0.6)"
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- search "0.1,0.9,0.8,0.7,0.6" --top-k 3 --dataset dataset.bin
echo ""
sleep 1

echo "Query 3: Search for 'red' (0.5, 0.5, 0.1, 0.1, 0.9)"
cargo run --manifest-path "$SCRIPT_DIR/Cargo.toml" --release -p vectro_cli -- search "0.5,0.5,0.1,0.1,0.9" --top-k 3 --dataset dataset.bin
echo ""
sleep 1

# Step 5: Format comparison
echo -e "${YELLOW}Step 5: File format details...${NC}"
echo ""
echo "Regular format (STREAM1):"
hexdump -C dataset.bin | head -n 3
echo "..."
echo ""
echo "Quantized format (QSTREAM1):"
hexdump -C dataset_q.bin | head -n 3
echo "..."
echo ""
sleep 1

# Step 6: Benchmark teaser
echo -e "${YELLOW}Step 6: Benchmark performance...${NC}"
echo ""
echo "To run full benchmarks with HTML report:"
echo -e "${BLUE}  cargo run -p vectro_cli -- bench --summary --open-report${NC}"
echo ""
echo "This will:"
echo "  • Run comprehensive performance tests"
echo "  • Generate interactive HTML visualizations"
echo "  • Track performance deltas over time"
echo "  • Save results to target/criterion/"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Demo Complete!${NC}"
echo ""
echo "Key Takeaways:"
echo "  ✓ Streaming compression with progress tracking"
echo "  ✓ Quantization reduces size by ${SAVINGS}%"
echo "  ✓ Fast cosine similarity search"
echo "  ✓ Multiple output formats (STREAM1, QSTREAM1)"
echo ""
echo "Next Steps:"
echo "  1. Check out DEMO.md for more examples"
echo "  2. Read QSTREAM.md for format details"
echo "  3. Run benchmarks: cargo bench -p vectro_lib"
echo "  4. Try your own datasets!"
echo ""
echo -e "${BLUE}Demo files saved in: $DEMO_DIR${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
