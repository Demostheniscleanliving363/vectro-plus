# 🎨 Vectro+ Visual Guide

An illustrated walkthrough of Vectro+'s features with real examples and output.

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Vectro+ System                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  Input Data  │      │   CLI Tool   │                   │
│  │   (JSONL)    │─────▶│  vectro_cli  │                   │
│  └──────────────┘      └──────┬───────┘                   │
│                               │                             │
│                               ▼                             │
│                    ┌─────────────────────┐                 │
│                    │   compress_stream   │                 │
│                    │  (parallel pipeline)│                 │
│                    └──────────┬──────────┘                 │
│                               │                             │
│              ┌────────────────┴────────────────┐           │
│              ▼                                 ▼           │
│    ┌──────────────────┐            ┌──────────────────┐   │
│    │  STREAM1 Format  │            │ QSTREAM1 Format  │   │
│    │   (f32 binary)   │            │ (u8 quantized)   │   │
│    └────────┬─────────┘            └────────┬─────────┘   │
│             │                                │             │
│             └────────────┬───────────────────┘             │
│                          ▼                                 │
│                 ┌──────────────────┐                       │
│                 │  SearchIndex /   │                       │
│                 │ QuantizedIndex   │                       │
│                 └──────────────────┘                       │
│                          │                                 │
│                          ▼                                 │
│                 ┌──────────────────┐                       │
│                 │  Top-K Search    │                       │
│                 │ (cosine similarity)                      │
│                 └──────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow: Compress Pipeline

```
Input File (JSONL)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│              Reader Thread                          │
│  • Parse JSON lines                                 │
│  • Create Embedding objects                         │
│  • Feed to channel (bounded 1024)                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Crossbeam Channel   │
         │    (Embedding)        │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │Worker 1 │  │Worker 2 │  │Worker N │
    │serialize│  │serialize│  │serialize│
    │bincode  │  │bincode  │  │bincode  │
    └────┬────┘  └────┬────┘  └────┬────┘
         │            │            │
         └────────────┼────────────┘
                     ▼
         ┌───────────────────────┐
         │   Crossbeam Channel   │
         │     (Vec<u8>)         │
         └───────────┬───────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              Writer Thread                          │
│  • Write header (STREAM1 or QSTREAM1)               │
│  • Write length-prefixed records                    │
│  • Flush to disk                                    │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
              Output File (.bin)
```

## 📦 Binary Format Comparison

### STREAM1 (Regular)
```
Offset  Hex                                     ASCII
──────────────────────────────────────────────────────────
0x0000  56 45 43 54 52 4f 2b 53 54 52 45 41  VECTRO+STREA
0x000c  4d 31 0a                              M1.
        ├─── Header (15 bytes) ───┘
        
0x000f  0a 00 00 00                           ....
        └─ Record 1 length (10 bytes) ─┘
        
0x0013  [bincode serialized Embedding]
        └─ { id: "doc1", vector: [0.1, 0.2, ...] }

0x001d  0b 00 00 00                           ....
        └─ Record 2 length (11 bytes) ─┘
        
0x0021  [bincode serialized Embedding]
        ...
```

### QSTREAM1 (Quantized)
```
Offset  Hex                                     ASCII
──────────────────────────────────────────────────────────
0x0000  56 45 43 54 52 4f 2b 51 53 54 52 45  VECTRO+QSTRE
0x000c  41 4d 31 0a                           AM1.
        ├─── Header (16 bytes) ───┘

0x0010  05 00 00 00                           ....
        └─ Table count (5 dimensions) ─┘

0x0014  05 00 00 00                           ....
        └─ Dim (repeated) ─┘

0x0018  28 00 00 00                           (...
        └─ Tables blob length (40 bytes) ─┘

0x001c  [bincode(Vec<QuantTable>)]
        └─ [{ min: 0.0, max: 1.0 }, { min: -0.5, max: 0.5 }, ...]

0x0044  08 00 00 00                           ....
        └─ Record 1 length (8 bytes) ─┘

0x0048  [bincode((id: String, qvec: Vec<u8>))]
        └─ ("doc1", [230, 45, 67, 189, 12])
        ...
```

## 🎯 Search Workflow

```
Query Vector: [0.9, 0.1, 0.8, 0.2, 0.7]
      │
      ▼
┌──────────────────────────────────┐
│   Load Dataset from disk         │
│   • Detect format (STREAM/QSTREAM)│
│   • Parse embeddings              │
│   • Dequantize if needed          │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   Build SearchIndex              │
│   • Store vectors & IDs          │
│   • Precompute norms (optional)  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   Compute Cosine Similarities    │
│   • dot(query, vec_i) / norms    │
│   • Parallel with rayon          │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   Select Top-K                   │
│   • Partial sort by score        │
│   • Return (id, score) pairs     │
└──────────────┬───────────────────┘
               │
               ▼
         Result Set
     ┌──────────────┐
     │ 1. doc4 → 1.00│
     │ 2. doc1 → 0.72│
     │ 3. doc5 → 0.65│
     └──────────────┘
```

## 📈 Benchmark Report Structure

```
target/
└── criterion/
    ├── vectro_summary.html          ← 🎨 Our custom summary
    ├── report/
    │   └── index.html               ← Criterion main report
    │
    ├── cosine_search/
    │   ├── top_k_10/
    │   │   ├── new/
    │   │   │   ├── estimates.json   ← Parsed for summary
    │   │   │   ├── raw.csv
    │   │   │   └── tukey.json
    │   │   └── report/
    │   │       └── index.html
    │   │
    │   └── top_k_100/
    │       └── ...
    │
    └── quantize_dataset/
        └── ...
```

## 🎨 CLI Output Examples

### 1. Compress (Regular)

```bash
$ vectro compress large.jsonl dataset.bin

⠋ compressing (streaming bincode)... parsed 10000 entries
⠙ compressing (streaming bincode)... parsed 20000 entries
⠹ compressing (streaming bincode)... parsed 30000 entries
⠸ compressing (streaming bincode)... parsed 40000 entries
⠼ compressing (streaming bincode)... parsed 50000 entries
✓ wrote 50000 entries to dataset.bin (1.8s)
```

### 2. Compress (Quantized)

```bash
$ vectro compress large.jsonl dataset_q.bin --quantize

⠋ parsing and computing quant tables... 10000 entries
⠙ parsing and computing quant tables... 20000 entries
⠹ writing quantized records... 10000/50000
⠸ writing quantized records... 20000/50000
⠼ writing quantized records... 30000/50000
⠴ writing quantized records... 40000/50000
✓ wrote 50000 quantized entries to dataset_q.bin (2.3s)
```

### 3. Search Results

```bash
$ vectro search "0.9,0.1,0.8,0.2,0.7" --top-k 5 --dataset dataset.bin

Top 5 results:
1. fast → 0.998234
2. car → 0.956789
3. truck → 0.934567
4. bicycle → 0.876543
5. red → 0.543210
```

### 4. Benchmark Summary

```bash
$ vectro bench --summary

⠋ running benches...
(Criterion output streams here...)

Benchmark summaries:
┌─────────────────────────────────┬────────────┬────────────┬──────┬────────┐
│ benchmark                       │     median │       mean │ unit │  delta │
├─────────────────────────────────┼────────────┼────────────┼──────┼────────┤
│ cosine_search/top_k_10          │   123.456  │   125.789  │  ns  │  -2.3% │ ← Improvement!
│ cosine_search/top_k_100         │  1234.567  │  1256.890  │  ns  │  +1.8% │ ← Regression
│ quantize/dataset_1000           │ 45678.901  │ 46789.012  │  ns  │    -   │ ← First run
│ quantize_search/top_k_10        │   156.789  │   159.012  │  ns  │  -5.4% │ ← Improvement!
└─────────────────────────────────┴────────────┴────────────┴──────┴────────┘

📊 HTML summary saved to: target/criterion/vectro_summary.html
```

## 🌈 HTML Summary Preview

```html
🚀 Vectro+ Benchmark Results
Generated: 2025-10-24 14:23:45

┌─────────────────────────────────────────────────────────────────────┐
│ Benchmark                    Median      Mean    Unit  Δ vs Previous│
├─────────────────────────────────────────────────────────────────────┤
│ cosine_search/top_k_10      123.456   125.789     ns      -2.3%     │ (green)
│ cosine_search/top_k_100    1234.567  1256.890     ns      +1.8%     │ (red)
│ quantize/dataset_1000     45678.901 46789.012     ns        -       │
└─────────────────────────────────────────────────────────────────────┘

Generated by Vectro+ — View Full Criterion Report
```

## 📊 Size Comparison Example

```
Original Dataset (100K × 768d):
┌────────────────────────────────────────────┐
│████████████████████████████████████  300MB│
└────────────────────────────────────────────┘

After STREAM1 Compression:
┌────────────────────────────────────────────┐
│██████████████████████████████████    295MB│ (-1.7%)
└────────────────────────────────────────────┘
(Minimal savings - mainly header overhead)

After QSTREAM1 Quantization:
┌──────────────┐
│████████  75MB│ (-75%)
└──────────────┘
(Massive savings! Each dim: 4 bytes → 1 byte)
```

## ⚡ Performance Metrics

### Throughput (embeddings/sec)

```
Compress (STREAM1):    31,250/s  ████████████████████
Compress (QSTREAM1):   24,390/s  ███████████████
Search (k=10):          8,130/s  ████████
Search (k=100):           833/s  █
```

### Latency (microseconds)

```
cosine (single):        1.2μs  █
top_k (k=10):         123.0μs  █████████████
top_k (k=100):       1234.0μs  ████████████████████████████████████████
```

## 🎓 Tutorial: End-to-End Workflow

```bash
# 1. Generate test data
python scripts/generate_embeddings.py --count 10000 --dim 256 > test.jsonl

# 2. Compress (regular)
vectro compress test.jsonl test.bin
# Output: ✓ wrote 10000 entries to test.bin (0.3s)

# 3. Compress (quantized)
vectro compress test.jsonl test_q.bin --quantize
# Output: ✓ wrote 10000 quantized entries to test_q.bin (0.4s)

# 4. Compare sizes
ls -lh test*.bin
# test.bin:   9.8M
# test_q.bin: 2.5M  (75% smaller!)

# 5. Test search accuracy
vectro search "$(head -1 test.jsonl | jq -r '.vector | join(",")')" \
    --top-k 5 --dataset test.bin

# 6. Compare with quantized
vectro search "$(head -1 test.jsonl | jq -r '.vector | join(",")')" \
    --top-k 5 --dataset test_q.bin

# 7. Benchmark both
cargo bench -p vectro_lib

# 8. Generate reports
vectro bench --summary --save-report ./benchmark-results --open-report
```

## 🎯 Use Cases

### 1. Semantic Search Engine
```
Large document corpus (1M+ docs)
  ↓ embed with sentence-transformers
  ↓ compress with vectro (quantized)
  ↓ fast similarity search
Result: 75% smaller index, <1ms query time
```

### 2. Recommendation System
```
User/item embeddings (100K+ entities)
  ↓ periodic recompression
  ↓ in-memory search index
  ↓ batch recommendations
Result: Fits in RAM, fast batch queries
```

### 3. ML Model Checkpoints
```
Embedding layer weights
  ↓ quantize for deployment
  ↓ stream from disk as needed
  ↓ reduced model size
Result: 4× smaller models, faster loading
```

## 🔧 Troubleshooting

### Problem: Quantized search less accurate

**Diagnosis:**
```bash
# Check quantization error
vectro compress data.jsonl data_q.bin --quantize --verbose
# Look for "quantization RMSE: 0.023" in output
```

**Solution:**
- Acceptable error: <3% RMSE
- High error: Increase precision (future feature)
- Or use regular STREAM1 format

### Problem: Out of memory

**Diagnosis:**
```bash
# Monitor memory during compress
/usr/bin/time -l vectro compress huge.jsonl huge.bin
```

**Solution:**
```bash
# Use streaming mode (default)
# Processes in chunks, constant memory
vectro compress huge.jsonl huge.bin

# For quantized: two-pass required (loads full dataset)
# Split input and merge outputs:
split -l 100000 huge.jsonl chunk_
for f in chunk_*; do
    vectro compress "$f" "${f}.bin" --quantize
done
```

---

**Need more help?** Check [DEMO.md](./DEMO.md) for complete examples!
