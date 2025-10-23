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
            println!("search '{}' top_k={} (not implemented)", query, top_k);
        }
        Commands::Serve { port } => {
            println!("serve on port {} (not implemented)", port);
        }
    }

    Ok(())
}
