use clap::{Parser, Subcommand};

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
            println!("compressing {} -> {}", input, output);
            // TODO: call vectro_lib compress functions
        }
        Commands::Search { query, top_k } => {
            // For now, expect query to be a comma-separated list of floats
            let vec: Vec<f32> = query
                .split(',')
                .filter_map(|s| s.trim().parse::<f32>().ok())
                .collect();

            // Load a dataset file if present at ./dataset.bin, else create a toy dataset
            let dataset = if let Ok(ds) = vectro_lib::EmbeddingDataset::load("dataset.bin") {
                ds.embeddings
            } else {
                eprintln!("warning: dataset.bin not found, using toy dataset");
                vec![
                    vectro_lib::Embedding::new("one", vec![1.0, 0.0]),
                    vectro_lib::Embedding::new("two", vec![0.0, 1.0]),
                    vectro_lib::Embedding::new("three", vec![0.707, 0.707]),
                ]
            };

            let results = vectro_lib::search::top_k(&dataset, &vec, top_k);
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
