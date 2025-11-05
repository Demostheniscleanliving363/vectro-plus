# Embedding Data Generators

This directory contains Python scripts for generating sample embedding datasets. These are being maintained for backward compatibility, but Rust equivalents are now available as part of the `vectro_cli` binary.

## Python Generators (Legacy)

### generate_embeddings.py
Generate simple random embeddings for testing.

```bash
python3 scripts/generate_embeddings.py --count 1000 --dim 128 --prefix emb > data.jsonl
```

### generate_themed_embeddings.py
Generate themed embeddings with semantic clustering.

```bash
python3 scripts/generate_themed_embeddings.py --count 1000 --dim 128 --theme products > products.jsonl
```

## Rust Generators (Recommended)

The same functionality is now available as Rust binaries in `vectro_cli`. These are faster, have no Python dependencies, and are the recommended approach.

### Generate simple embeddings

```bash
cargo run --release --bin generate_embeddings -- --count 1000 --dim 128 --prefix emb > data.jsonl
```

### Generate themed embeddings

```bash
cargo run --release --bin generate_themed_embeddings -- --count 1000 --dim 128 --theme products > products.jsonl
```

Available themes:
- `products` - Electronics, clothing, food, books, toys, sports
- `movies` - Action, comedy, drama, sci-fi, horror, romance
- `documents` - Tech, business, science, health, politics, entertainment
- `mixed` - Combination of all themes
- `random` - Completely random embeddings

## Installation

The Rust binaries are built automatically when you build the project:

```bash
cargo build --release
```

Then you can run them directly:

```bash
./target/release/generate_embeddings --help
./target/release/generate_themed_embeddings --help
```

## Migration

To migrate from Python to Rust generators, simply replace:

```bash
# Old
python3 scripts/generate_themed_embeddings.py --count 1000 --theme products

# New
cargo run --release --bin generate_themed_embeddings -- --count 1000 --theme products
```

The output format is identical, so existing workflows will continue to work.
