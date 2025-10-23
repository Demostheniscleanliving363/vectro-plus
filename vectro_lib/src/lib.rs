use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::{Read, Write};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Embedding {
    pub id: String,
    pub vector: Vec<f32>,
}

impl Embedding {
    pub fn new(id: impl Into<String>, vector: Vec<f32>) -> Self {
        Self {
            id: id.into(),
            vector,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EmbeddingDataset {
    pub embeddings: Vec<Embedding>,
}

impl EmbeddingDataset {
    pub fn new() -> Self {
        Self { embeddings: vec![] }
    }

    pub fn add(&mut self, e: Embedding) {
        self.embeddings.push(e);
    }

    pub fn len(&self) -> usize {
        self.embeddings.len()
    }

    pub fn save(&self, path: &str) -> anyhow::Result<()> {
        let mut f = File::create(path)?;
        let data = bincode::serialize(self)?;
        f.write_all(&data)?;
        Ok(())
    }

    pub fn load(path: &str) -> anyhow::Result<Self> {
        let mut f = File::open(path)?;
        let mut buf = Vec::new();
        f.read_to_end(&mut buf)?;
        let ds: EmbeddingDataset = bincode::deserialize(&buf)?;
        Ok(ds)
    }
}

/// Search utilities
pub mod search {
    use crate::Embedding;
    use rayon::prelude::*;

    /// Compute dot product between two same-length slices
    fn dot(a: &[f32], b: &[f32]) -> f32 {
        a.iter().zip(b.iter()).map(|(x, y)| x * y).sum()
    }

    /// Compute L2 norm of a vector
    fn norm(a: &[f32]) -> f32 {
        a.iter().map(|x| x * x).sum::<f32>().sqrt()
    }

    /// Cosine similarity between two vectors (returns -1..1)
    pub fn cosine(a: &[f32], b: &[f32]) -> f32 {
        if a.len() != b.len() {
            return -1.0;
        }
        let denom = norm(a) * norm(b);
        if denom == 0.0 {
            return -1.0;
        }
        dot(a, b) / denom
    }

    /// Naive top-k nearest neighbors by cosine similarity.
    /// Returns a Vec of (id, score) sorted by descending score.
    pub fn top_k<'a>(
        dataset: &'a [Embedding],
        query: &[f32],
        k: usize,
    ) -> Vec<(&'a str, f32)> {
        let mut scores: Vec<(&str, f32)> = dataset
            .par_iter()
            .map(|e| (e.id.as_str(), cosine(&e.vector, query)))
            .collect();

        // sort descending by score
        scores.par_sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        scores.into_iter().take(k).collect()
    }

    /// A simple search index that caches normalized vectors for fast cosine scoring.
    /// It owns a normalized copy of all vectors and the ids.
    pub struct SearchIndex {
        ids: Vec<String>,
        normalized: Vec<Vec<f32>>,
        dim: usize,
    }

    impl SearchIndex {
        /// Build an index from an embedding slice by normalizing each vector.
        pub fn from_dataset(dataset: &[Embedding]) -> Self {
            let mut ids = Vec::with_capacity(dataset.len());
            let mut normalized = Vec::with_capacity(dataset.len());
            let mut dim = 0usize;

            for e in dataset {
                if dim == 0 {
                    dim = e.vector.len();
                }
                ids.push(e.id.clone());
                // normalize; handle zero-norm vectors
                let n = norm(&e.vector);
                if n == 0.0 {
                    normalized.push(vec![0.0; e.vector.len()]);
                } else {
                    normalized.push(e.vector.iter().map(|v| v / n).collect());
                }
            }

            Self { ids, normalized, dim }
        }

        /// Single query top-k using the cached normalized vectors. Query will be normalized.
        pub fn top_k(&self, query: &[f32], k: usize) -> Vec<(&str, f32)> {
            if query.len() != self.dim {
                return vec![];
            }
            let qnorm = norm(query);
            if qnorm == 0.0 {
                return vec![];
            }
            let q: Vec<f32> = query.iter().map(|v| v / qnorm).collect();

            let mut scores: Vec<(&str, f32)> = self
                .normalized
                .par_iter()
                .zip(self.ids.par_iter())
                .map(|(vec, id)| (id.as_str(), dot(vec, &q)))
                .collect();

            scores.par_sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            scores.into_iter().take(k).collect()
        }

        /// Batch top-k: accept multiple queries and return a Vec per query.
        pub fn batch_top_k(&self, queries: &[Vec<f32>], k: usize) -> Vec<Vec<(&str, f32)>> {
            // Parallelize across queries
            queries
                .par_iter()
                .map(|q| self.top_k(q, k))
                .collect()
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn roundtrip_save_load() {
        let mut ds = EmbeddingDataset::new();
        ds.add(Embedding::new("one", vec![0.1, 0.2]));
        ds.add(Embedding::new("two", vec![1.0, 2.0]));

        let tmp = NamedTempFile::new().expect("create temp file");
        let path = tmp.path().to_str().unwrap().to_string();
        ds.save(&path).expect("save");

        let loaded = EmbeddingDataset::load(&path).expect("load");
        assert_eq!(loaded.len(), 2);
        assert_eq!(loaded.embeddings[0].id, "one");
    }

    #[test]
    fn cosine_and_topk() {
        use crate::search;

        let a = Embedding::new("a", vec![1.0, 0.0]);
        let b = Embedding::new("b", vec![0.0, 1.0]);
        let c = Embedding::new("c", vec![0.707, 0.707]);

        let ds = vec![a.clone(), b.clone(), c.clone()];

        // a vs c ~ 0.707
        let sim_ac = search::cosine(&a.vector, &c.vector);
        assert!(sim_ac > 0.7 && sim_ac < 0.72);

        let top2 = search::top_k(&ds, &a.vector, 2);
        assert_eq!(top2.len(), 2);
        // first should be 'a' itself with score 1.0
        assert_eq!(top2[0].0, "a");
        assert!((top2[0].1 - 1.0).abs() < 1e-6);
    }

    #[test]
    fn searchindex_topk_and_batch() {
        use crate::search::SearchIndex;

        let a = Embedding::new("a", vec![1.0, 0.0]);
        let b = Embedding::new("b", vec![0.0, 1.0]);
        let c = Embedding::new("c", vec![0.707, 0.707]);
        let ds = vec![a.clone(), b.clone(), c.clone()];

        let idx = SearchIndex::from_dataset(&ds);

        let q1 = vec![1.0, 0.0];
        let q2 = vec![0.0, 1.0];

        let single = idx.top_k(&q1, 2);
        let batch = idx.batch_top_k(&vec![q1.clone(), q2.clone()], 2);

        assert_eq!(single.len(), 2);
        assert_eq!(batch.len(), 2);
        assert_eq!(single[0].0, batch[0][0].0);
        assert!((single[0].1 - batch[0][0].1).abs() < 1e-6);
    }

    #[test]
    fn searchindex_dim_mismatch() {
        use crate::search::SearchIndex;

        let a = Embedding::new("a", vec![1.0, 0.0]);
        let ds = vec![a.clone()];
        let idx = SearchIndex::from_dataset(&ds);

        let q = vec![1.0, 0.0, 0.0];
        let res = idx.top_k(&q, 1);
        assert!(res.is_empty());
    }
}
