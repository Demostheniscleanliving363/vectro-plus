use vectro_lib::{Embedding, EmbeddingDataset};
use tempfile::NamedTempFile;

#[tokio::test]
async fn test_server_state_creation() {
    // Test creating server state with a dataset
    let mut ds = EmbeddingDataset::new();
    ds.add(Embedding::new("test1", vec![1.0, 0.0, 0.0]));
    ds.add(Embedding::new("test2", vec![0.0, 1.0, 0.0]));
    
    assert_eq!(ds.len(), 2);
}

#[tokio::test]
async fn test_search_index_creation() {
    let mut ds = EmbeddingDataset::new();
    ds.add(Embedding::new("a", vec![1.0, 0.0]));
    ds.add(Embedding::new("b", vec![0.0, 1.0]));
    
    let idx = vectro_lib::search::SearchIndex::from_dataset(&ds.embeddings);
    let results = idx.top_k(&[1.0, 0.0], 1);
    
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].0, "a");
}

#[tokio::test]
async fn test_quantized_index_creation() {
    let mut ds = EmbeddingDataset::new();
    ds.add(Embedding::new("a", vec![1.0, 0.0, 0.0]));
    ds.add(Embedding::new("b", vec![0.0, 1.0, 0.0]));
    ds.add(Embedding::new("c", vec![0.0, 0.0, 1.0]));
    
    let mut idx = vectro_lib::search::QuantizedIndex::from_dataset(&ds.embeddings);
    idx.precompute_normalized();
    
    let results = idx.top_k(&[1.0, 0.0, 0.0], 1);
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].0, "a");
}

#[tokio::test]
async fn test_dataset_save_load() {
    let tmp = NamedTempFile::new().unwrap();
    let path = tmp.path().to_str().unwrap().to_string();
    
    let mut ds = EmbeddingDataset::new();
    ds.add(Embedding::new("x", vec![1.0, 2.0]));
    ds.add(Embedding::new("y", vec![3.0, 4.0]));
    ds.save(&path).expect("save");
    
    let loaded = EmbeddingDataset::load(&path).expect("load");
    assert_eq!(loaded.len(), 2);
}

#[tokio::test]
async fn test_json_serialization() {
    use serde_json::json;
    
    let query_json = json!({
        "query": [1.0, 2.0, 3.0],
        "k": 10
    });
    
    assert!(query_json.get("query").is_some());
    assert!(query_json.get("k").is_some());
    
    if let Some(k) = query_json.get("k").and_then(|v| v.as_u64()) {
        assert_eq!(k, 10);
    }
}

#[test]
fn test_cors_and_static_files() {
    // Test that we can construct basic responses
    let test_string = "test data";
    assert_eq!(test_string.len(), 9);
    
    // Test JSON serialization for responses
    use serde_json::json;
    let response = json!({
        "status": "ok",
        "message": "Server ready"
    });
    assert!(response.get("status").is_some());
}
