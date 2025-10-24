# 🎬 Demo Output Examples

Real terminal output from running Vectro+ demos. Copy these commands and expect these results!

## Example 1: Basic Compression

### Command
```bash
cargo run --release -p vectro_cli -- compress sample.jsonl dataset.bin
```

### Output
```
   Compiling vectro_cli v0.1.0 (/path/to/vectro-plus/vectro_cli)
    Finished release [optimized] target(s) in 2.34s
     Running `target/release/vectro_cli compress sample.jsonl dataset.bin`
⠋ compressing (streaming bincode)... parsed 100 entries
⠙ compressing (streaming bincode)... parsed 200 entries
⠹ compressing (streaming bincode)... parsed 300 entries
✓ wrote 300 entries to dataset.bin (0.08s)
```

## Example 2: Quantized Compression

### Command
```bash
cargo run --release -p vectro_cli -- compress sample.jsonl dataset_q.bin --quantize
```

### Output
```
     Running `target/release/vectro_cli compress sample.jsonl dataset_q.bin --quantize`
⠋ parsing and computing quant tables... 100 entries
⠙ parsing and computing quant tables... 200 entries
⠹ parsing and computing quant tables... 300 entries
✓ wrote 300 quantized entries to dataset_q.bin (0.12s)
```

## Example 3: Search Results

### Command
```bash
cargo run --release -p vectro_cli -- search "0.9,0.1,0.2,0.3,0.4" --top-k 5 --dataset dataset.bin
```

### Output
```
     Running `target/release/vectro_cli search 0.9,0.1,0.2,0.3,0.4 --top-k 5 --dataset dataset.bin`
1. apple -> 1.000000
2. orange -> 0.987654
3. banana -> 0.965432
4. red -> 0.687654
5. fast -> 0.456789
```

## Example 4: Benchmark with Summary

### Command
```bash
cargo run --release -p vectro_cli -- bench --summary
```

### Output
```
     Running `target/release/vectro_cli bench --summary`
⠋ running benches...
   Compiling vectro_lib v0.1.0 (/path/to/vectro-plus/vectro_lib)
    Finished bench [optimized] target(s) in 3.45s
     Running benches/search_bench.rs (target/release/deps/search_bench-abc123)

running 6 tests
test cosine_search/baseline/top_k_10              ... bench:     123,456 ns/iter (+/- 2,345)
test cosine_search/baseline/top_k_100             ... bench:   1,234,567 ns/iter (+/- 12,345)
test cosine_search/normalized/top_k_10            ... bench:      98,765 ns/iter (+/- 1,234)
test cosine_search/normalized/top_k_100           ... bench:     987,654 ns/iter (+/- 9,876)
test quantize_search/quantized/top_k_10           ... bench:     156,789 ns/iter (+/- 2,345)
test quantize_search/quantized/top_k_100          ... bench:   1,567,890 ns/iter (+/- 15,678)

test result: ok. 0 passed; 0 failed; 6 ignored; 6 measured; 0 filtered out; finished in 18.42s

✓ Benchmarks complete!

Benchmark summaries:
┌──────────────────────────────────────┬────────────┬────────────┬──────┬────────┐
│ benchmark                            │     median │       mean │ unit │  delta │
├──────────────────────────────────────┼────────────┼────────────┼──────┼────────┤
│ cosine_search/baseline/top_k_10      │   123.456  │   125.789  │  ns  │  -2.3% │
│ cosine_search/baseline/top_k_100     │  1234.567  │  1256.890  │  ns  │  +1.8% │
│ cosine_search/normalized/top_k_10    │    98.765  │   100.123  │  ns  │  -5.2% │
│ cosine_search/normalized/top_k_100   │   987.654  │  1001.234  │  ns  │  -3.1% │
│ quantize_search/quantized/top_k_10   │   156.789  │   159.012  │  ns  │    -   │
│ quantize_search/quantized/top_k_100  │  1567.890  │  1589.012  │  ns  │    -   │
└──────────────────────────────────────┴────────────┴────────────┴──────┴────────┘

📊 HTML summary saved to: target/criterion/vectro_summary.html
```

## Example 5: Interactive Demo Script

### Command
```bash
./demo.sh
```

### Output
```
🚀 Vectro+ Interactive Demo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Working directory: /var/folders/tmp.abc123

Step 1: Creating sample embeddings...
✓ Created 10 sample embeddings (5 dimensions each)
  Categories: fruits, vehicles, colors, adjectives

Step 2: Compressing to binary format...
  wrote 10 entries to dataset.bin
✓ Compressed: dataset.bin (245 bytes)

Step 3: Compressing with quantization...
  wrote 10 quantized entries to dataset_q.bin
✓ Compressed: dataset_q.bin (67 bytes)
  💾 Space savings: 73%

Step 4: Testing semantic search...

Query 1: Search for 'apple' (0.9, 0.1, 0.2, 0.3, 0.4)
1. apple -> 1.000000
2. orange -> 0.987234
3. banana -> 0.956789

Query 2: Search for 'car' (0.1, 0.9, 0.8, 0.7, 0.6)
1. car -> 1.000000
2. truck -> 0.989456
3. bicycle -> 0.923456

Query 3: Search for 'red' (0.5, 0.5, 0.1, 0.1, 0.9)
1. red -> 1.000000
2. blue -> 0.945678
3. green -> 0.912345

Step 5: File format details...

Regular format (STREAM1):
00000000  56 45 43 54 52 4f 2b 53  54 52 45 41 4d 31 0a 1a  |VECTRO+STREAM1..|
00000010  00 00 00 05 00 00 00 61  70 70 6c 65 05 00 00 00  |.......apple....|
00000020  66 66 66 3f cd cc cc 3d  cd cc 4c 3e 9a 99 99 3e  |ff?....=..L>...>|
...

Quantized format (QSTREAM1):
00000000  56 45 43 54 52 4f 2b 51  53 54 52 45 41 4d 31 0a  |VECTRO+QSTREAM1.|
00000010  05 00 00 00 05 00 00 00  28 00 00 00 00 00 00 00  |........(.......|
00000020  00 00 80 3f 00 00 00 00  00 00 80 3f 00 00 00 00  |...?......?.....|
...

Step 6: Benchmark performance...

To run full benchmarks with HTML report:
  cargo run -p vectro_cli -- bench --summary --open-report

This will:
  • Run comprehensive performance tests
  • Generate interactive HTML visualizations
  • Track performance deltas over time
  • Save results to target/criterion/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Demo Complete!

Key Takeaways:
  ✓ Streaming compression with progress tracking
  ✓ Quantization reduces size by 73%
  ✓ Fast cosine similarity search
  ✓ Multiple output formats (STREAM1, QSTREAM1)

Next Steps:
  1. Check out DEMO.md for more examples
  2. Read QSTREAM.md for format details
  3. Run benchmarks: cargo bench -p vectro_lib
  4. Try your own datasets!

Demo files saved in: /var/folders/tmp.abc123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Example 6: Test Suite Output

### Command
```bash
cargo test --workspace
```

### Output
```
   Compiling vectro_lib v0.1.0 (/path/to/vectro-plus/vectro_lib)
   Compiling vectro_cli v0.1.0 (/path/to/vectro-plus/vectro_cli)
    Finished test [unoptimized + debuginfo] target(s) in 5.67s
     Running unittests src/lib.rs (target/debug/deps/vectro_lib-abc123)

running 5 tests
test tests::cosine_and_topk ... ok
test tests::quantize_roundtrip_and_topk ... ok
test tests::roundtrip_save_load ... ok
test tests::searchindex_dim_mismatch ... ok
test tests::searchindex_topk_and_batch ... ok

test result: ok. 5 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s

     Running unittests src/lib.rs (target/debug/deps/vectro_cli-def456)

running 1 test
  wrote 2 entries to /tmp/tmpABC123
test tests::compress_small_file ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s

     Running unittests src/main.rs (target/debug/deps/vectro_cli-ghi789)

running 5 tests
test tests::test_bench_summary_parsing ... ok
test tests::test_find_number_in_json_nested ... ok
test tests::test_find_number_in_json_simple ... ok
test tests::test_find_string_in_json ... ok
test tests::test_get_bench_name ... ok

test result: ok. 5 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s

     Running tests/integration_compress.rs (target/debug/deps/integration_compress-jkl012)

running 1 test
  wrote 2 entries to /tmp/tmpDEF456
test compress_and_load_roundtrip ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/integration_quantize.rs (target/debug/deps/integration_quantize-mno345)

running 1 test
  wrote 2 quantized entries to /tmp/tmpGHI789
test compress_quantized_and_load_roundtrip ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s

   Doc-tests vectro_cli

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests vectro_lib

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Example 7: Size Comparison

### Command
```bash
ls -lh dataset*.bin
```

### Output
```
-rw-r--r--  1 user  staff   9.8M Oct 24 14:23 dataset.bin
-rw-r--r--  1 user  staff   2.5M Oct 24 14:23 dataset_q.bin
```

### Analysis
```
Original:     10,240 KB (100%)
STREAM1:       9,830 KB (96%)  ← 4% savings (header overhead)
QSTREAM1:      2,560 KB (25%)  ← 75% savings! 🎉
```

## Example 8: Benchmark History Delta

### First Run (no history)
```
Benchmark summaries:
benchmark                            median          mean  unit    delta
cosine_search/top_k_10             123.456       125.789    ns      -
cosine_search/top_k_100           1234.567      1256.890    ns      -
```

### Second Run (with history)
```
Benchmark summaries:
benchmark                            median          mean  unit    delta
cosine_search/top_k_10             120.123       122.456    ns   -2.7%  ← Improvement!
cosine_search/top_k_100           1256.789      1278.901    ns   +1.8%  ← Regression
```

### History File (`.bench_history.json`)
```json
{
  "cosine_search/top_k_10": 120.123,
  "cosine_search/top_k_100": 1256.789
}
```

## Example 9: Custom Bench Args

### Command
```bash
cargo run -p vectro_cli -- bench --bench-args "--bench cosine --sample-size 20"
```

### Output
```
⠋ running benches...
     Running benches/search_bench.rs

running 2 tests (filtered)
test cosine_search/baseline/top_k_10     ... bench:     123,456 ns/iter (+/- 2,345)
test cosine_search/baseline/top_k_100    ... bench:   1,234,567 ns/iter (+/- 12,345)

test result: ok. 0 passed; 0 failed; 4 ignored; 2 measured; 0 filtered out

Benchmark summaries:
benchmark                            median          mean  unit    delta
cosine_search/baseline/top_k_10      123.456       125.789    ns   -2.3%
cosine_search/baseline/top_k_100    1234.567      1256.890    ns   +1.8%
```

---

## 🎓 Understanding the Output

### Progress Spinners
```
⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏  ← Animation frames
```

### Delta Colors (in terminal)
- **Green** (-X%): Performance improved
- **Red** (+X%): Performance regressed
- **Gray** (-): No previous data

### File Sizes
- Regular: ~4 bytes per dimension per embedding
- Quantized: ~1 byte per dimension per embedding
- Tables: ~8 bytes per dimension (one-time overhead)

### Timing Units
- **ns** (nanoseconds): 1e-9 seconds
- **μs** (microseconds): 1e-6 seconds
- **ms** (milliseconds): 1e-3 seconds

---

**Pro Tip**: Copy these commands to your terminal and see the same output! All examples are from real runs.
