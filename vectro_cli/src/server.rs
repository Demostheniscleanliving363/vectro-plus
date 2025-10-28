use axum::{
    extract::{Json, Query, State},
    http::StatusCode,
    response::Html,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::cors::{Any, CorsLayer};
use vectro_lib::{Embedding, EmbeddingDataset, search::SearchIndex};

// Shared application state
#[derive(Clone)]
pub struct AppState {
    index: Arc<RwLock<Option<SearchIndex>>>,
    embeddings: Arc<RwLock<Vec<Embedding>>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            index: Arc::new(RwLock::new(None)),
            embeddings: Arc::new(RwLock::new(Vec::new())),
        }
    }
}

// API request/response types
#[derive(Debug, Deserialize)]
pub struct SearchRequest {
    pub query: Vec<f32>,
    #[serde(default = "default_top_k")]
    pub k: usize,
}

fn default_top_k() -> usize {
    10
}

#[derive(Debug, Serialize)]
pub struct SearchResult {
    pub id: String,
    pub score: f32,
}

#[derive(Debug, Serialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub query_time_ms: f64,
}

#[derive(Debug, Deserialize)]
pub struct UploadRequest {
    pub embeddings: Vec<Embedding>,
}

#[derive(Debug, Serialize)]
pub struct StatsResponse {
    pub count: usize,
    pub dimensions: Option<usize>,
    pub index_loaded: bool,
}

#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub version: String,
}

// Route handlers
async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    })
}

async fn stats(State(state): State<AppState>) -> Json<StatsResponse> {
    let embeddings = state.embeddings.read().await;
    let index = state.index.read().await;
    
    let dimensions = embeddings.first().map(|e| e.vector.len());
    
    Json(StatsResponse {
        count: embeddings.len(),
        dimensions,
        index_loaded: index.is_some(),
    })
}

async fn upload_embeddings(
    State(state): State<AppState>,
    Json(payload): Json<UploadRequest>,
) -> Result<Json<StatsResponse>, (StatusCode, String)> {
    if payload.embeddings.is_empty() {
        return Err((StatusCode::BAD_REQUEST, "No embeddings provided".to_string()));
    }
    
    // Validate dimensions are consistent
    let first_dim = payload.embeddings[0].vector.len();
    for emb in &payload.embeddings {
        if emb.vector.len() != first_dim {
            return Err((
                StatusCode::BAD_REQUEST,
                "Inconsistent embedding dimensions".to_string(),
            ));
        }
    }
    
    // Update embeddings
    let mut embeddings = state.embeddings.write().await;
    *embeddings = payload.embeddings;
    
    // Rebuild index
    let new_index = SearchIndex::from_dataset(&embeddings);
    let mut index = state.index.write().await;
    *index = Some(new_index);
    
    let count = embeddings.len();
    drop(embeddings);
    drop(index);
    
    Ok(Json(StatsResponse {
        count,
        dimensions: Some(first_dim),
        index_loaded: true,
    }))
}

async fn search(
    State(state): State<AppState>,
    Json(payload): Json<SearchRequest>,
) -> Result<Json<SearchResponse>, (StatusCode, String)> {
    let index = state.index.read().await;
    
    if index.is_none() {
        return Err((StatusCode::NOT_FOUND, "No index loaded. Upload embeddings first.".to_string()));
    }
    
    let start = std::time::Instant::now();
    
    let idx = index.as_ref().unwrap();
    let results = idx.top_k(&payload.query, payload.k);
    
    let elapsed = start.elapsed().as_secs_f64() * 1000.0;
    
    let search_results: Vec<SearchResult> = results
        .into_iter()
        .map(|(id, score)| SearchResult {
            id: id.to_string(),
            score,
        })
        .collect();
    
    Ok(Json(SearchResponse {
        results: search_results,
        query_time_ms: elapsed,
    }))
}

async fn load_dataset_endpoint(
    State(state): State<AppState>,
    Query(params): Query<std::collections::HashMap<String, String>>,
) -> Result<Json<StatsResponse>, (StatusCode, String)> {
    let path = params.get("path").ok_or((
        StatusCode::BAD_REQUEST,
        "Missing 'path' query parameter".to_string(),
    ))?;
    
    let dataset = EmbeddingDataset::load(path).map_err(|e| {
        (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to load dataset: {}", e))
    })?;
    
    let embeddings_vec = dataset.embeddings;
    let count = embeddings_vec.len();
    let dimensions = embeddings_vec.first().map(|e| e.vector.len());
    
    // Update state
    let new_index = SearchIndex::from_dataset(&embeddings_vec);
    let mut embeddings = state.embeddings.write().await;
    *embeddings = embeddings_vec;
    
    let mut index = state.index.write().await;
    *index = Some(new_index);
    
    Ok(Json(StatsResponse {
        count,
        dimensions,
        index_loaded: true,
    }))
}

async fn index_page() -> Html<String> {
    Html(include_str!("../static/index.html").to_string())
}

pub async fn serve(port: u16) -> anyhow::Result<()> {
    let state = AppState::new();
    
    // Configure CORS
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);
    
    let app = Router::new()
        .route("/", get(index_page))
        .route("/health", get(health))
        .route("/api/stats", get(stats))
        .route("/api/search", post(search))
        .route("/api/upload", post(upload_embeddings))
        .route("/api/load", get(load_dataset_endpoint))
        .layer(cors)
        .with_state(state);
    
    let addr = format!("0.0.0.0:{}", port);
    println!("🚀 Vectro+ server starting on http://localhost:{}", port);
    println!("📊 Dashboard: http://localhost:{}", port);
    println!("🔍 API endpoints:");
    println!("   GET  /health");
    println!("   GET  /api/stats");
    println!("   POST /api/search");
    println!("   POST /api/upload");
    println!("   GET  /api/load?path=<path>");
    
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;
    
    Ok(())
}
