//! Vectro+ CLI - Command-line interface for embedding compression and search
//!
//! # Examples
//!
//! ```no_run
//! // Compress embeddings
//! // vectro compress input.jsonl output.bin
//!
//! // Search for similar vectors
//! // vectro search "1.0,2.0,3.0" --top-k 10 --dataset output.bin
//!
//! // Run benchmarks
//! // vectro bench --summary --open-report
//!
//! // Start web server
//! // vectro serve --port 8080
//! ```

use clap::{Parser, Subcommand};
use std::path::Path;
use vectro_cli::compress_stream;

use serde_json::Value;

mod server;

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
        #[arg(long, default_value_t = false)]
        /// Produce a quantized streaming dataset (per-dimension min/max -> u8).
        /// This reduces size and speeds up search at the cost of some accuracy.
        /// Use for large datasets where memory/storage is constrained.
        /// Default: false
        quantize: bool,
    },
    /// Run library benchmarks (uses the `vectro_lib` bench harness).
    /// Streams benchmark output and shows a spinner while running.
    Bench {
        /// Save the Criterion HTML report to this path (directory). If omitted, report will remain under target/criterion.
        #[arg(long)]
        save_report: Option<String>,
        /// Open the HTML report after generation (macOS `open` is used).
        #[arg(long, default_value_t = false)]
        open_report: bool,
        /// Print a short JSON summary (median, mean) from Criterion's JSON output.
        #[arg(long, default_value_t = true)]
        summary: bool,
        /// Directory to copy the report into when using --save-report (default: current dir)
        #[arg(long)]
        report_dir: Option<String>,
        /// Extra arguments to pass to cargo bench (e.g., "--bench cosine_bench")
        #[arg(long)]
        bench_args: Option<String>,
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
        Commands::Compress { input, output, quantize } => {
            let _ = crate::compress_stream(&input, &output, quantize)?;
        }
        Commands::Bench { save_report, open_report, summary, report_dir: _, bench_args } => {
            // Run cargo bench for vectro_lib and stream output. Show a spinner while running.
            use indicatif::{ProgressBar, ProgressStyle};
            use std::process::{Command, Stdio};
            use std::io::{BufRead, BufReader};
            use std::thread;
            use std::fs;
            use std::path::PathBuf;

            let pb = ProgressBar::new_spinner();
            pb.set_style(ProgressStyle::with_template("{spinner} {msg}").unwrap());
            pb.enable_steady_tick(std::time::Duration::from_millis(80));
            pb.set_message("running benches...");

            let mut cmd = Command::new("cargo");
            cmd.arg("bench").arg("-p").arg("vectro_lib");
            
            // Add extra bench args if provided
            if let Some(extra) = bench_args {
                for arg in extra.split_whitespace() {
                    cmd.arg(arg);
                }
            }
            
            cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

            let mut child = cmd.spawn().expect("failed to spawn cargo bench");

            // stream stdout
            if let Some(out) = child.stdout.take() {
                let pb_out = pb.clone();
                thread::spawn(move || {
                    let reader = BufReader::new(out);
                    for line in reader.lines().flatten() {
                        pb_out.println(line);
                    }
                });
            }

            // stream stderr
            if let Some(err) = child.stderr.take() {
                let pb_err = pb.clone();
                thread::spawn(move || {
                    let reader = BufReader::new(err);
                    for line in reader.lines().flatten() {
                        pb_err.println(line);
                    }
                });
            }

            let status = child.wait().expect("bench wait failed");
            pb.finish_and_clear();
            if !status.success() {
                eprintln!("bench failed: {:?}\n(bench output above)", status);
            } else {
                // After success, optionally locate Criterion report and copy/open it
                let crit_dir = PathBuf::from("target/criterion");
                if crit_dir.exists() {
                    if summary {
                        // parse JSON summaries in target/criterion/*/new/*.json and present a clean table
                        if let Ok(entries) = fs::read_dir(&crit_dir) {
                            let mut rows: Vec<(String, Option<f64>, Option<f64>, Option<String>)> = Vec::new();
                            for e in entries.flatten() {
                                let p = e.path();
                                if p.is_dir() {
                                    let new_dir = p.join("new");
                                    if new_dir.exists() {
                                        if let Ok(it) = fs::read_dir(&new_dir) {
                                            for j in it.flatten() {
                                                let jp = j.path();
                                                if jp.extension().map(|s| s == "json").unwrap_or(false) {
                                                    if let Ok(txt) = fs::read_to_string(&jp) {
                                                        if let Ok(json) = serde_json::from_str::<Value>(&txt) {
                                                            let med = get_estimate(&json, "median");
                                                            let mean = get_estimate(&json, "mean");
                                                            let unit = find_string_in_json(&json, "unit");
                                                            // Use benchmark name if available, fallback to filename
                                                            let name = get_bench_name(&json)
                                                                .unwrap_or_else(|| jp.file_stem()
                                                                    .and_then(|s| s.to_str())
                                                                    .unwrap_or("unknown")
                                                                    .to_string());
                                                            rows.push((name, med, mean, unit));
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            if !rows.is_empty() {
                                // try to load previous history for deltas
                                let history_path = PathBuf::from(".bench_history.json");
                                let mut history: std::collections::HashMap<String, f64> = std::collections::HashMap::new();
                                if let Ok(txt) = std::fs::read_to_string(&history_path) {
                                    if let Ok(hm) = serde_json::from_str::<std::collections::HashMap<String, f64>>(&txt) {
                                        history = hm;
                                    }
                                }

                                // print pretty table
                                println!("\nBenchmark summaries:");
                                // header (include delta vs previous run)
                                println!("\x1b[1m{:<60} {:>12} {:>12} {:>8} {:>8}\x1b[0m", "benchmark", "median", "mean", "unit", "delta");
                                for (f, med, mean, unit) in &rows {
                                    let med_s = med.map(|v| format!("{:.6}", v)).unwrap_or_else(|| "-".to_string());
                                    let mean_s = mean.map(|v| format!("{:.6}", v)).unwrap_or_else(|| "-".to_string());
                                    let unit_s = unit.clone().unwrap_or_else(|| "".to_string());
                                    // compute delta vs previous median
                                    let delta_s = if let Some(prev) = history.get(f) {
                                        if let Some(curr) = med {
                                            if *prev != 0.0 {
                                                let pct = (*curr - *prev) / *prev * 100.0;
                                                format!("{:+.2}%", pct)
                                            } else { "n/a".to_string() }
                                        } else { "-".to_string() }
                                    } else { "-".to_string() };
                                    println!("{:<60} {:>12} {:>12} {:>8} {:>8}", f, med_s, mean_s, unit_s, delta_s);
                                }

                                // update history with latest medians
                                let mut new_hist: std::collections::HashMap<String, f64> = std::collections::HashMap::new();
                                for (f, med, _mean, _unit) in &rows {
                                    if let Some(m) = med { new_hist.insert(f.clone(), *m); }
                                }
                                if let Ok(out) = serde_json::to_string_pretty(&new_hist) {
                                    let _ = std::fs::write(&history_path, out);
                                }

                                // Generate HTML summary in criterion dir
                                let html_summary = generate_html_summary(&rows, &history);
                                let summary_path = crit_dir.join("vectro_summary.html");
                                if let Err(e) = fs::write(&summary_path, html_summary) {
                                    eprintln!("Warning: couldn't write HTML summary: {}", e);
                                } else {
                                    println!("\n📊 HTML summary saved to: {}", summary_path.display());
                                }
                            }
                        }
                    }

                    if let Some(dest) = save_report {
                        let dest_dir = PathBuf::from(dest);
                        let ts = match std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH) {
                            Ok(d) => format!("{}", d.as_secs()),
                            Err(_) => "ts".to_string(),
                        };
                        let target_copy = dest_dir.join(format!("criterion-report-{}", ts));
                        let _ = fs::create_dir_all(&target_copy);
                        let _ = copy_dir_all(&crit_dir, &target_copy);
                        println!("Saved Criterion report to {}", target_copy.display());
                        if open_report {
                            let opener = if cfg!(target_os = "macos") { "open" } else { "xdg-open" };
                            let _ = Command::new(opener).arg(target_copy.join("index.html")).spawn();
                        }
                    } else if open_report {
                        // try to find an index.html anywhere under crit_dir
                        let mut index_opt: Option<PathBuf> = None;
                        // simple recursive search
                        let mut stack: Vec<PathBuf> = vec![crit_dir.clone()];
                        while let Some(p) = stack.pop() {
                            if let Ok(entries) = std::fs::read_dir(&p) {
                                for en in entries.flatten() {
                                    let pp = en.path();
                                    if pp.is_dir() { stack.push(pp); }
                                    else if pp.file_name().and_then(|s| s.to_str()) == Some("index.html") {
                                        index_opt = Some(pp);
                                        break;
                                    }
                                }
                            }
                            if index_opt.is_some() { break; }
                        }
                        if let Some(idx) = index_opt {
                            let opener = if cfg!(target_os = "macos") { "open" } else { "xdg-open" };
                            let _ = Command::new(opener).arg(idx).spawn();
                        }
                    }
                }
            }
        }
        Commands::Search { query, top_k, dataset } => {
            let vec: Vec<f32> = query
                .split(',')
                .filter_map(|s| s.trim().parse::<f32>().ok())
                .collect();

            // Load dataset if provided. If not provided and ./dataset.bin exists, use it.
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
            } else if Path::new("./dataset.bin").exists() {
                match vectro_lib::EmbeddingDataset::load("./dataset.bin") {
                    Ok(ds) => ds.embeddings,
                    Err(e) => {
                        eprintln!("failed to load ./dataset.bin: {}", e);
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
            tokio::runtime::Runtime::new()?.block_on(async {
                server::serve(port).await
            })?;
        }
    }

    Ok(())
}

/// Recursively search a serde_json::Value for the first numeric value keyed by `key` and return it as f64.
fn find_number_in_json(v: &Value, key: &str) -> Option<f64> {
    match v {
        Value::Object(map) => {
            if let Some(val) = map.get(key) {
                if let Some(n) = val.as_f64() { return Some(n); }
            }
            for (_k, vv) in map.iter() {
                if let Some(n) = find_number_in_json(vv, key) { return Some(n); }
            }
            None
        }
        Value::Array(arr) => {
            for item in arr { if let Some(n) = find_number_in_json(item, key) { return Some(n); } }
            None
        }
        _ => None,
    }
}

/// Recursively find a string field in JSON by key
fn find_string_in_json(v: &Value, key: &str) -> Option<String> {
    match v {
        Value::Object(map) => {
            if let Some(val) = map.get(key) {
                if let Some(s) = val.as_str() { return Some(s.to_string()); }
            }
            for (_k, vv) in map.iter() {
                if let Some(s) = find_string_in_json(vv, key) { return Some(s); }
            }
            None
        }
        Value::Array(arr) => {
            for item in arr { if let Some(s) = find_string_in_json(item, key) { return Some(s); } }
            None
        }
        _ => None,
    }
}

/// Attempt to find an estimate value which may be nested in several known fields
fn get_estimate(v: &Value, key: &str) -> Option<f64> {
    // common shapes: { "estimates": { "median": {"point_estimate": 0.1 } } } or direct
    if let Some(direct) = find_number_in_json(v, key) { return Some(direct); }
    // try path: estimates -> key -> point_estimate
    if let Value::Object(map) = v {
        if let Some(est) = map.get("estimates") {
            if let Value::Object(est_map) = est {
                if let Some(kv) = est_map.get(key) {
                    if let Value::Object(kmap) = kv {
                        if let Some(pe) = kmap.get("point_estimate") {
                            return pe.as_f64();
                        }
                    }
                }
            }
        }
    }
    None
}

/// Extract a short benchmark name from Criterion JSON (tries "group_id", "function_id", or fallback)
fn get_bench_name(v: &Value) -> Option<String> {
    // Try common Criterion fields
    if let Some(name) = find_string_in_json(v, "group_id") {
        return Some(name);
    }
    if let Some(name) = find_string_in_json(v, "function_id") {
        return Some(name);
    }
    if let Some(name) = find_string_in_json(v, "title") {
        return Some(name);
    }
    None
}

/// Generate a compact HTML summary from benchmark results
fn generate_html_summary(rows: &[(String, Option<f64>, Option<f64>, Option<String>)], history: &std::collections::HashMap<String, f64>) -> String {
    let mut html = String::from(r#"<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vectro+ Benchmark Summary</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; 
               padding: 2rem; max-width: 1200px; margin: 0 auto; background: #f5f5f5; }
        h1 { color: #333; border-bottom: 3px solid #4a90e2; padding-bottom: 0.5rem; }
        .timestamp { color: #666; font-size: 0.9rem; margin-bottom: 2rem; }
        table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #4a90e2; color: white; font-weight: 600; }
        tr:hover { background: #f9f9f9; }
        .number { text-align: right; font-family: 'Monaco', 'Courier New', monospace; }
        .delta-positive { color: #d32f2f; }
        .delta-negative { color: #388e3c; }
        .delta-neutral { color: #666; }
        .footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #666; font-size: 0.85rem; }
        .link { color: #4a90e2; text-decoration: none; }
        .link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🚀 Vectro+ Benchmark Results</h1>
    <div class="timestamp">Generated: "#);
    
    html.push_str(&format!("{}</div>\n", chrono::Local::now().format("%Y-%m-%d %H:%M:%S")));
    html.push_str("    <table>\n        <thead>\n            <tr>\n");
    html.push_str("                <th>Benchmark</th><th class=\"number\">Median</th><th class=\"number\">Mean</th><th>Unit</th><th class=\"number\">Δ vs Previous</th>\n");
    html.push_str("            </tr>\n        </thead>\n        <tbody>\n");
    
    for (name, med, mean, unit) in rows {
        let med_str = med.map(|v| format!("{:.6}", v)).unwrap_or_else(|| "-".to_string());
        let mean_str = mean.map(|v| format!("{:.6}", v)).unwrap_or_else(|| "-".to_string());
        let unit_str = unit.clone().unwrap_or_else(|| "".to_string());
        
        let (delta_str, delta_class) = if let Some(prev) = history.get(name) {
            if let Some(curr) = med {
                if *prev != 0.0 {
                    let pct = (*curr - *prev) / *prev * 100.0;
                    let class = if pct > 0.5 { "delta-positive" } else if pct < -0.5 { "delta-negative" } else { "delta-neutral" };
                    (format!("{:+.2}%", pct), class)
                } else {
                    ("n/a".to_string(), "delta-neutral")
                }
            } else {
                ("-".to_string(), "delta-neutral")
            }
        } else {
            ("-".to_string(), "delta-neutral")
        };
        
        html.push_str(&format!("            <tr>\n                <td>{}</td><td class=\"number\">{}</td><td class=\"number\">{}</td><td>{}</td><td class=\"number {}\">  {}</td>\n            </tr>\n",
            name, med_str, mean_str, unit_str, delta_class, delta_str));
    }
    
    html.push_str(r#"        </tbody>
    </table>
    <div class="footer">
        Generated by <a href="https://github.com/yourorg/vectro-plus" class="link">Vectro+</a> — 
        <a href="./report/index.html" class="link">View Full Criterion Report</a>
    </div>
</body>
</html>"#);
    
    html
}
// Simple recursive directory copy used to copy Criterion reports
fn copy_dir_all(src: &std::path::Path, dst: &std::path::Path) -> std::io::Result<()> {
    std::fs::create_dir_all(dst)?;
    for entry in std::fs::read_dir(src)? {
        let entry = entry?;
        let file_type = entry.file_type()?;
        let from = entry.path();
        let to = dst.join(entry.file_name());
        if file_type.is_dir() {
            copy_dir_all(&from, &to)?;
        } else {
            std::fs::copy(&from, &to)?;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_find_number_in_json_simple() {
        let v = json!({"median": 0.123, "mean": 0.2});
        assert_eq!(find_number_in_json(&v, "median"), Some(0.123));
        assert_eq!(find_number_in_json(&v, "mean"), Some(0.2));
    }

    #[test]
    fn test_find_number_in_json_nested() {
        let v = json!({"estimates": {"median": {"point_estimate": 0.5}, "mean": {"point_estimate": 0.6}}});
        assert_eq!(get_estimate(&v, "median"), Some(0.5));
        assert_eq!(get_estimate(&v, "mean"), Some(0.6));
    }

    #[test]
    fn test_find_string_in_json() {
        let v = json!({"unit": "ns", "nested": {"unit": "ms"}});
        assert_eq!(find_string_in_json(&v, "unit"), Some("ns".to_string()));
        let v2 = json!({"outer": {"inner": {"unit": "us"}}});
        assert_eq!(find_string_in_json(&v2, "unit"), Some("us".to_string()));
    }

    #[test]
    fn test_get_bench_name() {
        let v1 = json!({"group_id": "search/cosine", "function_id": "top_k"});
        assert_eq!(get_bench_name(&v1), Some("search/cosine".to_string()));
        
        let v2 = json!({"function_id": "quantize_dataset", "title": "Quantization Bench"});
        assert_eq!(get_bench_name(&v2), Some("quantize_dataset".to_string()));
        
        let v3 = json!({"title": "Simple Bench"});
        assert_eq!(get_bench_name(&v3), Some("Simple Bench".to_string()));
    }

    #[test]
    fn test_bench_summary_parsing() {
        use std::fs;
        use tempfile::TempDir;

        // Create fake Criterion-like JSON output
        let tmp = TempDir::new().unwrap();
        let crit_dir = tmp.path().join("criterion");
        let bench_dir = crit_dir.join("cosine_search").join("new");
        fs::create_dir_all(&bench_dir).unwrap();

        let fake_json = json!({
            "group_id": "cosine_search",
            "function_id": "top_k_100",
            "estimates": {
                "median": {"point_estimate": 123.456},
                "mean": {"point_estimate": 125.789}
            },
            "unit": "ns"
        });

        fs::write(bench_dir.join("estimates.json"), serde_json::to_string_pretty(&fake_json).unwrap()).unwrap();

        // Parse the fake structure
        let mut found = false;
        if let Ok(entries) = fs::read_dir(&crit_dir) {
            for e in entries.flatten() {
                let p = e.path();
                if p.is_dir() {
                    let new_dir = p.join("new");
                    if new_dir.exists() {
                        if let Ok(it) = fs::read_dir(&new_dir) {
                            for j in it.flatten() {
                                let jp = j.path();
                                if jp.extension().map(|s| s == "json").unwrap_or(false) {
                                    if let Ok(txt) = fs::read_to_string(&jp) {
                                        if let Ok(json) = serde_json::from_str::<Value>(&txt) {
                                            let med = get_estimate(&json, "median");
                                            let mean = get_estimate(&json, "mean");
                                            let unit = find_string_in_json(&json, "unit");
                                            let name = get_bench_name(&json);

                                            assert_eq!(med, Some(123.456));
                                            assert_eq!(mean, Some(125.789));
                                            assert_eq!(unit, Some("ns".to_string()));
                                            assert_eq!(name, Some("cosine_search".to_string()));
                                            found = true;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        assert!(found, "Should have parsed the fake Criterion JSON");
    }
}
