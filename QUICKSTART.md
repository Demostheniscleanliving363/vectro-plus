# ⚡ Vectro+ Quick Start

Get up and running with Vectro+ in 5 minutes!

## 🚀 Installation

```bash
git clone https://github.com/yourorg/vectro-plus
cd vectro-plus
cargo build --release
```

The binary will be at `target/release/vectro_cli`

## 📖 5-Minute Tutorial

### Step 1: Run the Interactive Demo

```bash
./demo.sh
```

This will show you:
- ✅ Sample data creation
- ✅ Compression (regular + quantized)
- ✅ Size comparison (75% savings!)
- ✅ Semantic search examples
- ✅ Binary format inspection

### Step 2: Try Your Own Data

Create a JSONL file with embeddings:

```json
{"id": "doc1", "vector": [0.1, 0.2, 0.3, 0.4, 0.5]}
{"id": "doc2", "vector": [0.5, 0.4, 0.3, 0.2, 0.1]}
```

Or generate programmatically:

```bash
python scripts/generate_embeddings.py --count 1000 --dim 128 > my_embeddings.jsonl
```

### Step 3: Compress

```bash
# Regular compression
cargo run --release -p vectro_cli -- compress my_embeddings.jsonl dataset.bin

# Quantized (75%+ smaller)
cargo run --release -p vectro_cli -- compress my_embeddings.jsonl dataset_q.bin --quantize
```

### Step 4: Search

```bash
# Find top-10 similar vectors
cargo run --release -p vectro_cli -- search "0.1,0.2,0.3,0.4,0.5" --top-k 10 --dataset dataset.bin
```

### Step 5: Benchmark

```bash
# Run benchmarks with visual summary
cargo run --release -p vectro_cli -- bench --summary --open-report
```

This will:
- Run comprehensive performance tests
- Generate HTML report with graphs
- Track performance deltas over time
- Open results in your browser

## 📚 What to Read Next

1. **[DEMO.md](./DEMO.md)** - Comprehensive examples and workflows
2. **[VISUAL_GUIDE.md](./VISUAL_GUIDE.md)** - Architecture, formats, and diagrams
3. **[QSTREAM.md](./QSTREAM.md)** - Binary format specification
4. **[README.md](./README.md)** - Full feature overview

## 🎯 Common Commands

```bash
# Compress with progress
cargo run -p vectro_cli -- compress input.jsonl output.bin

# Compress + quantize
cargo run -p vectro_cli -- compress input.jsonl output.bin --quantize

# Search
cargo run -p vectro_cli -- search "0.1,0.2,0.3" --top-k 5 --dataset output.bin

# Benchmark (summary only)
cargo run -p vectro_cli -- bench --summary

# Benchmark (open HTML)
cargo run -p vectro_cli -- bench --open-report

# Benchmark (save report)
cargo run -p vectro_cli -- bench --save-report ./reports --summary

# Benchmark (specific tests)
cargo run -p vectro_cli -- bench --bench-args "--bench cosine"

# Run unit tests
cargo test --workspace

# Run specific integration test
cargo test -p vectro_cli --test integration_quantize
```

## 🔧 Build Options

```bash
# Development build (fast compile, slow runtime)
cargo build

# Release build (slow compile, fast runtime)
cargo build --release

# Run without building
cargo run -p vectro_cli -- <command>

# Run with release optimizations
cargo run --release -p vectro_cli -- <command>
```

## 💡 Tips

1. **Always use `--release` for large datasets** - 10-100x faster!
2. **Start with regular compression** to verify correctness
3. **Use quantization for production** - massive space savings
4. **Run benchmarks twice** - first run establishes baseline
5. **Check HTML summary** - easier to read than terminal output

## 🆘 Troubleshooting

**Problem**: Command not found  
**Solution**: Use `cargo run -p vectro_cli --` instead of `vectro`

**Problem**: Slow compression  
**Solution**: Use `--release` flag: `cargo run --release -p vectro_cli --`

**Problem**: Out of memory during quantization  
**Solution**: Quantization loads full dataset; split large files first

**Problem**: Tests fail  
**Solution**: Run `cargo clean && cargo test --workspace`

**Problem**: Benchmarks show all dashes for deltas  
**Solution**: Run benchmarks twice to establish baseline

## 📊 Expected Performance

On M1 Max (10-core):

| Dataset | Compress | Quantize | Search (k=10) |
|---------|----------|----------|---------------|
| 10K × 128d | 180ms | 220ms | 45μs |
| 100K × 768d | 3.2s | 4.1s | 123μs |

Your mileage may vary based on:
- CPU cores (parallel workers scale)
- Disk speed (compression I/O bound)
- Vector dimensions (affects compute)

## 🎓 Learning Path

1. ✅ **Run `./demo.sh`** - See it in action
2. ✅ **Try your data** - Compress and search
3. ✅ **Run benchmarks** - Understand performance
4. ✅ **Read VISUAL_GUIDE.md** - Deep dive into architecture
5. ✅ **Explore the code** - Understand implementation
6. ✅ **Extend it** - Add your own features!

## 🤝 Getting Help

- 📖 Check the documentation files
- 🐛 Open an issue on GitHub
- 💬 Ask questions in discussions
- 🔍 Search existing issues

## ⚡ Quick Reference Card

```
COMMANDS
  compress <in> <out>         Compress JSONL to binary
  compress --quantize         Compress with quantization
  search <vec>                Find similar vectors
  bench                       Run performance tests
  serve                       Start HTTP server (TODO)

FLAGS
  --quantize                  Enable u8 quantization
  --top-k <N>                 Return top N results
  --dataset <file>            Binary dataset file
  --summary                   Show benchmark summary
  --open-report               Open HTML in browser
  --save-report <dir>         Save report to directory
  --bench-args <args>         Pass args to cargo bench

FORMATS
  STREAM1                     f32 binary (header + records)
  QSTREAM1                    u8 quantized (tables + records)

FILES
  .bench_history.json         Benchmark delta tracking
  target/criterion/           Benchmark reports
  vectro_summary.html         Custom HTML summary
```

---

**Ready?** Run `./demo.sh` to get started! 🎉
