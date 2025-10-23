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
}
