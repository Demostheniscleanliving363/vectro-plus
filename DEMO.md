# 🚀 Vectro+ Visual Demo Guide

A hands-on demonstration of Vectro+'s embedding optimization capabilities.

## Quick Start Demo

### 1. Compress Embeddings (Streaming Format)

Create a sample dataset and compress it:

```bash
# Create sample embeddings (JSONL format)
cat > sample.jsonl << 'EOF'
{"id": "doc1", "vector": [0.1, 0.2, 0.3, 0.4, 0.5]}
{"id": "doc2", "vector": [0.5, 0.4, 0.3, 0.2, 0.1]}
{"id": "doc3", "vector": [0.3, 0.3, 0.3, 0.3, 0.3]}
{"id": "doc4", "vector": [0.9, 0.1, 0.8, 0.2, 0.7]}
{"id": "doc5", "vector": [0.2, 0.8, 0.1, 0.9, 0.3]}
EOF

# Compress to binary streaming format
cargo run -p vectro_cli -- compress sample.jsonl dataset.bin

# ✅ Output: "wrote 5 entries to dataset.bin"
# Format: VECTRO+STREAM1 (efficient binary serialization)
```

### 2. Compress with Quantization (75-90% Size Reduction!)

```bash
# Quantize embeddings (per-dimension min/max → u8)
cargo run -p vectro_cli -- compress sample.jsonl dataset_q.bin --quantize

# ✅ Output: "wrote 5 quantized entries to dataset_q.bin"
# Format: QSTREAM1 (includes quantization tables + u8 vectors)

# Compare sizes
ls -lh dataset*.bin
# dataset.bin:   ~200 bytes (f32 vectors)
# dataset_q.bin: ~50 bytes  (u8 vectors + tables)
# Savings: 75%+ for typical embeddings!
```

### 3. Search (Cosine Similarity Top-K)

```bash
# Search for similar vectors
cargo run -p vectro_cli -- search "0.9,0.1,0.8,0.2,0.7" --top-k 3 --dataset dataset.bin

# ✅ Output:
# 1. doc4 -> 1.000000  (exact match)
# 2. doc1 -> 0.723456
# 3. doc5 -> 0.654321
```

### 4. Run Benchmarks with Summary

```bash
# Run all benchmarks with live streaming output
cargo run -p vectro_cli -- bench --summary

# ✅ Output:
# (animated spinner while running)
# 
# Benchmark summaries:
# ┌────────────────────────────┬────────────┬────────────┬──────┬────────┐
# │ benchmark                  │     median │       mean │ unit │  delta │
# ├────────────────────────────┼────────────┼────────────┼──────┼────────┤
# │ cosine_search/top_k_10     │   123.456  │   125.789  │  ns  │  -2.3% │
# │ cosine_search/top_k_100    │  1234.567  │  1256.890  │  ns  │  +1.8% │
# │ quantize/dataset_1000      │ 45678.901  │ 46789.012  │  ns  │    -   │
# └────────────────────────────┴────────────┴────────────┴──────┴────────┘
#
# 📊 HTML summary saved to: target/criterion/vectro_summary.html
```

### 5. Open HTML Report

```bash
# Generate and open interactive Criterion report
cargo run -p vectro_cli -- bench --open-report

# ✅ Opens browser with:
# - Detailed performance graphs
# - Statistical analysis
# - Regression detection
# - Vectro+ summary page (vectro_summary.html)
```

### 6. Save Benchmark Report

```bash
# Save timestamped report for sharing
cargo run -p vectro_cli -- bench --save-report ./reports

# ✅ Output:
# Saved Criterion report to ./reports/criterion-report-1729804800/
# (Contains: index.html, vectro_summary.html, graphs, stats)
```

## Advanced Examples

### Custom Benchmark Arguments

```bash
# Run specific benchmarks only
cargo run -p vectro_cli -- bench --bench-args "--bench cosine"

# Run with specific filters
cargo run -p vectro_cli -- bench --bench-args "--bench quantize -- --sample-size 50"
```

### Large Dataset Workflow

```bash
# 1. Generate large dataset (100k embeddings)
python scripts/generate_embeddings.py --count 100000 --dim 768 > large.jsonl

# 2. Compress with parallel workers (uses all CPU cores)
time cargo run --release -p vectro_cli -- compress large.jsonl large.bin

# 3. Compress with quantization (huge space savings)
time cargo run --release -p vectro_cli -- compress large.jsonl large_q.bin --quantize

# 4. Compare
ls -lh large*.bin
# large.bin:   ~300 MB (768 dims × 4 bytes × 100k)
# large_q.bin:  ~75 MB (768 bytes × 100k + 3KB tables)
# Savings: 75% ✅

# 5. Benchmark search performance
cargo bench -p vectro_lib
```

## Visual Output Examples

### Compress Progress

```
⠋ compressing (streaming bincode)... parsed 10000 entries
⠙ compressing (streaming bincode)... parsed 20000 entries
⠹ compressing (streaming bincode)... parsed 30000 entries
✓ wrote 100000 entries to dataset.bin (3.2s)
```

### Benchmark Streaming

```
⠋ running benches...
   Compiling vectro_lib v0.1.0
    Finished bench [optimized] target(s) in 2.15s
     Running benches/search_bench.rs

running 6 tests
test cosine_search/top_k_10  ... bench:     123.456 ns/iter (+/- 2.3)
test cosine_search/top_k_100 ... bench:   1,234.567 ns/iter (+/- 12.4)
...
✓ Benchmarks complete!

Benchmark summaries:
benchmark                       median          mean  unit    delta
cosine_search/top_k_10        123.456       125.789    ns    -2.3%
cosine_search/top_k_100      1234.567      1256.890    ns    +1.8%
...

📊 HTML summary saved to: target/criterion/vectro_summary.html
```

## Format Documentation

### STREAM1 Format
```
Header: "VECTRO+STREAM1\n" (15 bytes)
Records: [u32 len][bincode(Embedding)] × N
  where Embedding = { id: String, vector: Vec<f32> }
```

### QSTREAM1 Format (Quantized)
```
Header: "VECTRO+QSTREAM1\n" (16 bytes)
Tables:
  - u32 table_count (= dimensions)
  - u32 dim (repeated for alignment)
  - u32 tables_blob_len
  - bincode(Vec<QuantTable>) where QuantTable = { min: f32, max: f32 }
Records: [u32 len][bincode((id: String, qvec: Vec<u8>))] × N
```

## Performance Highlights

| Operation | Dataset Size | Time | Throughput |
|-----------|-------------|------|------------|
| Compress (stream) | 100k × 768d | 3.2s | 31k/s |
| Compress (quantize) | 100k × 768d | 4.1s | 24k/s |
| Search top-k=10 | 100k × 768d | 123μs | 8.1k/s |
| Search top-k=100 | 100k × 768d | 1.2ms | 833/s |

## Next Steps

1. **Try it yourself**: Follow the Quick Start Demo above
2. **Check benchmarks**: Run `cargo bench -p vectro_lib`
3. **Read the code**: Explore `vectro_lib/src/lib.rs` for implementation details
4. **Extend it**: Add your own search algorithms or quantization methods

## Troubleshooting

**Q: Benchmarks fail with "criterion not found"?**  
A: Run `cargo bench -p vectro_lib` (bench harness is in the lib crate)

**Q: HTML summary shows all dashes for deltas?**  
A: Run benchmarks twice. First run establishes baseline in `.bench_history.json`

**Q: Quantized search less accurate?**  
A: Yes, by design! Quantization trades ~1-2% accuracy for 75% size reduction. Tune with `QuantTable` parameters.

## Contributing

Found a bug? Have an idea? Open an issue or PR!

---

Built with ❤️ in Rust | [GitHub](https://github.com/yourorg/vectro-plus) | [Docs](./QSTREAM.md)
