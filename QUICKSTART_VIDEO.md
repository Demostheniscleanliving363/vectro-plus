# 🎬 Quick Start: Video Demo

Want to see Vectro+ in action? Here's how to run the demo:

## Option 1: Enhanced Interactive Demo (Recommended)
```bash
./demo_enhanced.sh
```

This script demonstrates:
- ✨ Streaming compression with progress indicators
- 🗜️ Quantization (75% size reduction)
- 🔍 Semantic search across themed data
- 🌐 Web UI with real-time search
- 📊 Beautiful terminal output

**Perfect for:** Screen recording, presentations, video demos

## Option 2: Simple Demo
```bash
./demo.sh
```

Classic demo with all core features.

## Option 3: Web UI Only
```bash
# Generate sample data
python3 scripts/generate_themed_embeddings.py --count 1000 --theme products > products.jsonl

# Compress it
cargo run --release -p vectro_cli -- compress products.jsonl products.bin

# Start server
cargo run --release -p vectro_cli -- serve --port 8080

# Open browser to http://localhost:8080
```

## 📹 Recording a Video Demo?

See **[VIDEO_DEMO.md](./VIDEO_DEMO.md)** for:
- Complete recording guide (5-7 min demo)
- Script with timestamps
- Visual tips and best practices
- Post-production editing guide

## 🎨 Sample Datasets

Generate realistic themed embeddings:

```bash
# Products (electronics, clothing, food, etc.)
python3 scripts/generate_themed_embeddings.py --count 5000 --dim 384 --theme products > products.jsonl

# Movies (by genre)
python3 scripts/generate_themed_embeddings.py --count 5000 --dim 384 --theme movies > movies.jsonl

# Documents (by topic)
python3 scripts/generate_themed_embeddings.py --count 5000 --dim 384 --theme documents > docs.jsonl

# Mixed dataset
python3 scripts/generate_themed_embeddings.py --count 10000 --dim 768 --theme mixed > mixed.jsonl
```

## 🚀 Web Server Features

The new web interface includes:

### 📊 Real-time Dashboard
- Live embedding count
- Dimension info
- Index status

### 🔍 Interactive Search
- Visual query input
- Top-K results
- Similarity scores
- Query time metrics

### 📤 Dataset Management
- Upload embeddings via UI
- Load from file
- REST API for automation

### API Endpoints

```bash
# Health check
curl http://localhost:8080/health

# Get stats
curl http://localhost:8080/api/stats

# Search (POST JSON)
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": [0.1, 0.2, 0.3, ...], "k": 10}'

# Upload embeddings
curl -X POST http://localhost:8080/api/upload \
  -H "Content-Type: application/json" \
  -d '{"embeddings": [{"id": "doc1", "vector": [...]}, ...]}'

# Load dataset
curl "http://localhost:8080/api/load?path=./dataset.bin"
```

## 💡 Demo Tips

### For Best Visual Impact:
1. Use themed data (products, movies) for semantic meaning
2. Show compression ratio with `ls -lh`
3. Highlight query speed (< 1ms)
4. Demonstrate the web UI for interactivity

### Terminal Setup:
```bash
# Increase font size
# Set color scheme to dark theme
# Use larger terminal window (1280x720 or 1920x1080)
```

### Talking Points:
- **Streaming compression** - No memory limits
- **Quantization** - 75% smaller with minimal accuracy loss
- **Fast search** - Microsecond query times
- **Beautiful UI** - Production-ready web interface
- **Rust** - Safety and performance

## 🎯 Demo Flow (3 minutes)

```bash
# 1. Generate data (10 seconds)
python3 scripts/generate_themed_embeddings.py --count 1000 --theme products > data.jsonl

# 2. Compress (15 seconds)
cargo run --release -p vectro_cli -- compress data.jsonl data.bin
cargo run --release -p vectro_cli -- compress data.jsonl data_q.bin --quantize
ls -lh data*.bin  # Show size comparison

# 3. Search (30 seconds)
cargo run --release -p vectro_cli -- search "0.1,0.2,..." --top-k 5 --dataset data.bin

# 4. Web UI (2 minutes)
cargo run --release -p vectro_cli -- serve --port 8080
# Open browser, load dataset, run searches
```

## 🎥 Example Video Structure

1. **Intro (15s)**: "Vectro+ - High-performance embedding search in Rust"
2. **Data (20s)**: Show generating themed embeddings
3. **Compression (30s)**: Regular + quantized, show size reduction
4. **Search (45s)**: CLI search with multiple queries
5. **Web UI (90s)**: Load data, interactive search, show metrics
6. **Outro (20s)**: Key benefits, GitHub link

**Total: ~3-4 minutes** (perfect for social media, demos, presentations)

---

**Ready to demo?** Pick an option above and get started! 🚀

For more details, see:
- [README.md](./README.md) - Full documentation
- [DEMO.md](./DEMO.md) - Comprehensive examples
- [VIDEO_DEMO.md](./VIDEO_DEMO.md) - Complete recording guide
