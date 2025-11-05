# Vectro+ Embedding Generators

High-performance Rust tools for generating sample embedding datasets for testing and demonstrations.

## Overview

This crate provides two binary tools for generating synthetic embedding data:

1. **`generate_embeddings`** - Generate simple random embeddings
2. **`generate_themed_embeddings`** - Generate semantically clustered embeddings around themes

## Installation

Build the generators with the main workspace:

```bash
cd /path/to/vectro-plus
cargo build --release --package generators
```

The binaries will be available at:
- `./target/release/generate_embeddings`
- `./target/release/generate_themed_embeddings`

## Usage

### Generate Random Embeddings

```bash
# Basic usage - 1000 embeddings, 128 dimensions
./target/release/generate_embeddings --count 1000 --dim 128 > data.jsonl

# With custom prefix and seed for reproducibility
./target/release/generate_embeddings \
  --count 5000 \
  --dim 256 \
  --prefix "test" \
  --seed 42 > test_data.jsonl
```

**Options:**
- `--count N` - Number of embeddings to generate (default: 1000)
- `--dim D` - Embedding dimension (default: 128)
- `--prefix P` - ID prefix (default: "emb")
- `--seed S` - Random seed for reproducibility (optional)

### Generate Themed Embeddings

```bash
# Generate product embeddings
./target/release/generate_themed_embeddings \
  --count 1000 \
  --dim 128 \
  --theme products \
  --seed 42 > products.jsonl

# Generate movie embeddings
./target/release/generate_themed_embeddings \
  --count 2000 \
  --dim 256 \
  --theme movies > movies.jsonl
```

**Options:**
- `--count N` - Number of embeddings to generate (default: 1000)
- `--dim D` - Embedding dimension (default: 128)
- `--theme T` - Theme to use (default: "products")
- `--seed S` - Random seed for reproducibility (default: 42)

**Available Themes:**

| Theme | Description | Categories |
|-------|-------------|------------|
| `products` | E-commerce products | electronics, clothing, food, books, toys, sports |
| `movies` | Movie database | action, comedy, drama, scifi, horror, romance |
| `documents` | Document corpus | tech, business, science, health, politics, entertainment |
| `mixed` | Combination of all themes | All of the above |
| `random` | Completely random | No clustering |

## Output Format

Both tools output JSON Lines (JSONL) format with one embedding per line:

```json
{"id":"electronics_laptop__0000","vector":[0.533,-0.088,0.369,...]}
{"id":"electronics_smartphone__0001","vector":[0.255,-0.096,0.088,...]}
```

## Examples

### Create a test dataset for benchmarking

```bash
# Generate 100K embeddings for performance testing
./target/release/generate_embeddings \
  --count 100000 \
  --dim 384 \
  --seed 12345 > benchmark.jsonl
```

### Create semantic search demo data

```bash
# Generate themed products for search demonstrations
./target/release/generate_themed_embeddings \
  --count 10000 \
  --dim 768 \
  --theme products \
  --seed 42 > demo_products.jsonl
```

### Test different clustering scenarios

```bash
# Random (no clustering)
./target/release/generate_themed_embeddings --theme random > random.jsonl

# Tight clusters (products)
./target/release/generate_themed_embeddings --theme products > products.jsonl

# Looser clusters (movies)
./target/release/generate_themed_embeddings --theme movies > movies.jsonl
```

## Integration with Vectro+

Use the generated data with vectro-plus CLI:

```bash
# Generate embeddings
./target/release/generate_themed_embeddings \
  --count 50000 \
  --dim 128 \
  --theme products > products.jsonl

# Build index
./target/release/vectro build \
  --input products.jsonl \
  --output products.bin \
  --dim 128

# Run queries
./target/release/vectro query \
  --index products.bin \
  --dim 128 \
  --k 10
```

## Performance

Both generators are highly optimized and use:
- ChaCha8 PRNG for fast, reproducible random generation
- Efficient vector normalization
- Minimal allocations
- Single-pass generation

**Benchmarks** (Apple M1 Pro):
- Simple embeddings: ~100K vectors/sec @ 128D
- Themed embeddings: ~80K vectors/sec @ 128D

## Algorithm Details

### Random Embeddings

1. Generate random values from normal distribution N(0,1)
2. Normalize to unit length (L2 norm = 1)

### Themed Embeddings

1. For each category/theme:
   - Generate a random center point
   - Create cluster around center with controlled noise
   - Normalize all vectors to unit length
2. Assign semantic IDs based on theme

The clustering uses Gaussian noise with configurable variance:
- Products: σ = 0.15 (tight clusters)
- Movies: σ = 0.20 (moderate clusters)
- Documents: σ = 0.18 (moderate clusters)

## Development

To modify the generators:

```bash
# Edit source files
vim generators/src/bin/generate_embeddings.rs
vim generators/src/bin/generate_themed_embeddings.rs
vim generators/src/lib.rs

# Build and test
cargo build --package generators
cargo test --package generators

# Run with cargo
cargo run --package generators --bin generate_embeddings -- --count 10
cargo run --package generators --bin generate_themed_embeddings -- --theme products --count 10
```

## License

Part of the Vectro+ project. See root LICENSE file.
