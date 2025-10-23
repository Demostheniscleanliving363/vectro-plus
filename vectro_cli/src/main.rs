use clap::{Parser, Subcommand};
use std::io::{BufRead, BufReader};

#[derive(Parser)]
#[command(name = "vectro")]
#[command(about = "Vectro+ — Rust embedding compressor & search tool", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Compress {
        input: String,
        output: String,
    },
    Search {
        query: String,
        #[arg(short, long, default_value_t = 10)]
        top_k: usize,
        /// Path to dataset (bincode). If omitted, uses built-in toy dataset.
        #[arg(long)]
        dataset: Option<String>,
    },
    Serve {
        #[arg(short, long, default_value_t = 8080)]
        port: u16,
    },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Compress { input, output } => {
            // Try to read input as JSONL first: each line {"id": "...", "vector": [..]}
            // Fallback to CSV with id, then floats
            let mut dataset = vectro_lib::EmbeddingDataset::new();

            // Try JSONL
            if let Ok(f) = std::fs::File::open(&input) {
                let reader = BufReader::new(f);
                let mut parsed = 0usize;
                for line in reader.lines().flatten() {
                    if let Ok(val) = serde_json::from_str::<serde_json::Value>(&line) {
                        if let (Some(id), Some(vec)) = (val.get("id"), val.get("vector")) {
                            if let (Some(id_str), Some(arr)) = (id.as_str(), vec.as_array()) {
                                let mut v = Vec::with_capacity(arr.len());
                                for x in arr {
                                    if let Some(flt) = x.as_f64() {
                                        v.push(flt as f32);
                                    }
                                }
                                dataset.add(vectro_lib::Embedding::new(id_str, v));
                                parsed += 1;
                            }
                        }
                    }
                }
                if parsed == 0 {
                    // try CSV
                    if let Ok(mut rdr) = csv::Reader::from_path(&input) {
                        for result in rdr.records() {
                            if let Ok(rec) = result {
                                if rec.len() >= 2 {
                                    let id = rec.get(0).unwrap_or("").to_string();
                                    let mut v = Vec::new();
                                    for i in 1..rec.len() {
                                        if let Ok(flt) = rec.get(i).unwrap_or("").parse::<f32>() {
                                            v.push(flt);
                                        }
                                    }
                                    dataset.add(vectro_lib::Embedding::new(id, v));
                                }
                            }
                        }
                    }
                }
            }

            // Save to output as bincode using vectro_lib save
            dataset.save(&output)?;
            println!("wrote {} embeddings to {}", dataset.len(), output);
        }
        Commands::Search { query, top_k, dataset } => {
            let vec: Vec<f32> = query
                .split(',')
                .filter_map(|s| s.trim().parse::<f32>().ok())
                .collect();

            // Load dataset if provided, else toy dataset
            let embeddings = if let Some(path) = dataset {
                match vectro_lib::EmbeddingDataset::load(&path) {
                    Ok(ds) => ds.embeddings,
                    Err(e) => {
                        eprintln!("failed to load dataset {}: {}", path, e);
                        vec![
                            vectro_lib::Embedding::new("one", vec![1.0, 0.0]),
                            vectro_lib::Embedding::new("two", vec![0.0, 1.0]),
                            vectro_lib::Embedding::new("three", vec![0.707, 0.707]),
                        ]
                    }
                }
            } else {
                vec![
                    vectro_lib::Embedding::new("one", vec![1.0, 0.0]),
                    vectro_lib::Embedding::new("two", vec![0.0, 1.0]),
                    vectro_lib::Embedding::new("three", vec![0.707, 0.707]),
                ]
            };

            // Build SearchIndex for faster repeated queries
            let idx = vectro_lib::search::SearchIndex::from_dataset(&embeddings);
            let results = idx.top_k(&vec, top_k);
            for (i, (id, score)) in results.into_iter().enumerate() {
                println!("{}. {} -> {:.6}", i + 1, id, score);
            }
        }
        Commands::Serve { port } => {
            println!("serve on port {} (not implemented)", port);
        }
    }

    Ok(())
}
