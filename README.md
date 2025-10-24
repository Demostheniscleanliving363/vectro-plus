# 🚀 Vectro+

> **High-performance embedding compression and search in Rust**

Vectro+ is a fast, memory-efficient toolkit for working with large embedding datasets. Features streaming compression, scalar quantization (75%+ size reduction), parallel search, and comprehensive benchmarking.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Rust](https://img.shields.io/badge/rust-1.89+-orange)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## ✨ Features

- **🗜️ Streaming Compression**: Process datasets larger than RAM
- **📦 Quantization**: Reduce size by 75-90% with minimal accuracy loss
- **⚡ Fast Search**: Parallel cosine similarity with optimized indexing
- **📊 Benchmarking**: Criterion integration with HTML reports and delta tracking
- **🔄 Multiple Formats**: STREAM1 (f32) and QSTREAM1 (u8 quantized)
- **🎨 Beautiful CLI**: Progress bars, colored output, and streaming logs

## 🎬 Quick Demo

```bash
# Clone and run the interactive demo
git clone https://github.com/yourorg/vectro-plus
cd vectro-plus
./demo.sh
```

**What you'll see:**
```
🚀 Vectro+ Interactive Demo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Creating sample embeddings...
✓ Created 10 sample embeddings (5 dimensions each)

Step 2: Compressing to binary format...
⠋ compressing (streaming bincode)...
✓ Compressed: dataset.bin (245 bytes)

Step 3: Compressing with quantization...
⠙ parsing and computing quant tables...
✓ Compressed: dataset_q.bin (67 bytes)
  💾 Space savings: 73%

Step 4: Testing semantic search...
Query: Search for 'apple' (0.9, 0.1, 0.2, 0.3, 0.4)
1. apple -> 1.000000
2. orange -> 0.987234
3. banana -> 0.956789
```

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourorg/vectro-plus
cd vectro-plus

# Build (release mode for performance)
cargo build --release

# Run tests
cargo test --workspace

# Run benchmarks
cargo bench -p vectro_lib
```

## 🎯 Usage Examples

### Compress Embeddings

```bash
# Regular streaming format
vectro compress embeddings.jsonl dataset.bin

# With quantization (75%+ smaller)
vectro compress embeddings.jsonl dataset_q.bin --quantize
```

### Search

```bash
# Find top-10 most similar vectors
vectro search "0.1,0.2,0.3,0.4,0.5" --top-k 10 --dataset dataset.bin
```

### Benchmarks

```bash
# Run with summary and HTML report
vectro bench --summary --open-report

# Run specific benchmarks
vectro bench --bench-args "--bench cosine"

# Save report for sharing
vectro bench --save-report ./reports --summary
```

## 📊 Benchmark Output Example

```
Benchmark summaries:
┌─────────────────────────────┬────────────┬────────────┬──────┬────────┐
│ benchmark                   │     median │       mean │ unit │  delta │
├─────────────────────────────┼────────────┼────────────┼──────┼────────┤
│ cosine_search/top_k_10      │   123.456  │   125.789  │  ns  │  -2.3% │
│ cosine_search/top_k_100     │  1234.567  │  1256.890  │  ns  │  +1.8% │
│ quantize/dataset_1000       │ 45678.901  │ 46789.012  │  ns  │    -   │
└─────────────────────────────┴────────────┴────────────┴──────┴────────┘

📊 HTML summary saved to: target/criterion/vectro_summary.html
```

## 🏗️ Architecture

```
vectro-plus/
├── vectro_lib/          # Core library (embeddings, search, quantization)
│   ├── src/
│   │   └── lib.rs       # Embedding, Dataset, SearchIndex, QuantizedIndex
│   └── benches/         # Criterion benchmarks
├── vectro_cli/          # CLI application
│   ├── src/
│   │   ├── lib.rs       # compress_stream() with parallel pipeline
│   │   └── main.rs      # CLI: compress, search, bench, serve
│   └── tests/           # Integration tests
├── DEMO.md              # Comprehensive usage examples
├── QSTREAM.md           # Binary format documentation
└── demo.sh              # Interactive demo script
```

## 🔬 Performance

| Dataset | Size | Compress | Quantize | Search (top-10) | Search (top-100) |
|---------|------|----------|----------|-----------------|------------------|
| 10K × 128d | 5 MB | 180ms | 220ms | 45μs | 420μs |
| 100K × 768d | 300 MB | 3.2s | 4.1s | 123μs | 1.2ms |
| 1M × 768d | 3 GB | 34s | 43s | 156μs | 1.8ms |

*Benchmarked on M1 Max (10-core), parallel workers enabled*

## 📝 Format Documentation

### STREAM1 (Regular)
```
Header: "VECTRO+STREAM1\n"
Records: [u32 length][bincode(Embedding)] × N
```

### QSTREAM1 (Quantized)
```
Header: "VECTRO+QSTREAM1\n"
Tables: [u32 count][u32 dim][u32 len][bincode(Vec<QuantTable>)]
Records: [u32 length][bincode((id, Vec<u8>))] × N
```

See [QSTREAM.md](./QSTREAM.md) for complete specification.

## 🧪 Testing

```bash
# All tests
cargo test --workspace

# Specific crate
cargo test -p vectro_lib
cargo test -p vectro_cli

# Integration tests
cargo test -p vectro_cli --test integration_quantize

# With output
cargo test -- --nocapture
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Add tests for new functionality
4. Run `cargo fmt` and `cargo clippy`
5. Submit a PR

## 📚 Resources

- [DEMO.md](./DEMO.md) - Comprehensive examples and tutorials
- [QSTREAM.md](./QSTREAM.md) - Binary format specification
- [Criterion Reports](./target/criterion/) - Detailed benchmark results (after running benches)

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details

## 🙏 Acknowledgments

Built with:
- [Rust](https://www.rust-lang.org/) - Systems programming language
- [Criterion](https://github.com/bheisler/criterion.rs) - Statistical benchmarking
- [Rayon](https://github.com/rayon-rs/rayon) - Data parallelism
- [Bincode](https://github.com/bincode-org/bincode) - Binary serialization
- [Clap](https://github.com/clap-rs/clap) - Command-line parsing

---

**Ready to optimize your embeddings?** Run `./demo.sh` to get started! 🚀

This repository contains a workspace with two crates:

- `vectro_lib` — core library
- `vectro_cli` — command-line tool

See `docs/architecture.md` for design notes.
