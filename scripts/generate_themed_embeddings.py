#!/usr/bin/env python3
"""
Generate themed sample embeddings for compelling Vectro+ demos.
Creates semantically meaningful vectors across different categories.
"""

import json
import random
import math
import argparse
from typing import List, Dict, Tuple

class SemanticEmbeddingGenerator:
    """Generates embeddings with semantic relationships."""
    
    def __init__(self, dim: int = 128, seed: int = 42):
        self.dim = dim
        random.seed(seed)
        
    def generate_cluster(self, center: List[float], noise: float = 0.1, count: int = 10) -> List[List[float]]:
        """Generate embeddings clustered around a center point."""
        embeddings = []
        for _ in range(count):
            vec = []
            for c in center:
                # Add gaussian noise
                val = c + random.gauss(0, noise)
                vec.append(max(-1.0, min(1.0, val)))  # Clamp to [-1, 1]
            embeddings.append(self._normalize(vec))
        return embeddings
    
    def _normalize(self, vec: List[float]) -> List[float]:
        """Normalize vector to unit length."""
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            return vec
        return [x / norm for x in vec]
    
    def _random_unit_vector(self) -> List[float]:
        """Generate a random unit vector."""
        vec = [random.gauss(0, 1) for _ in range(self.dim)]
        return self._normalize(vec)
    
    def generate_themed_dataset(self, theme: str = "products", count: int = 1000) -> List[Dict]:
        """Generate a themed dataset with semantic relationships."""
        if theme == "products":
            return self._generate_products(count)
        elif theme == "movies":
            return self._generate_movies(count)
        elif theme == "documents":
            return self._generate_documents(count)
        elif theme == "mixed":
            return self._generate_mixed(count)
        else:
            return self._generate_random(count)
    
    def _generate_products(self, count: int) -> List[Dict]:
        """Generate product embeddings with semantic categories."""
        products = []
        
        # Define category centers
        categories = {
            "electronics": self._random_unit_vector(),
            "clothing": self._random_unit_vector(),
            "food": self._random_unit_vector(),
            "books": self._random_unit_vector(),
            "toys": self._random_unit_vector(),
            "sports": self._random_unit_vector(),
        }
        
        product_names = {
            "electronics": ["laptop", "smartphone", "tablet", "headphones", "camera", "monitor"],
            "clothing": ["shirt", "pants", "dress", "jacket", "shoes", "hat"],
            "food": ["apple", "bread", "cheese", "pasta", "rice", "coffee"],
            "books": ["novel", "textbook", "magazine", "comic", "manual", "dictionary"],
            "toys": ["doll", "puzzle", "lego", "robot", "ball", "game"],
            "sports": ["basketball", "tennis_racket", "running_shoes", "yoga_mat", "dumbbell", "bike"],
        }
        
        items_per_category = count // len(categories)
        
        for cat_name, center in categories.items():
            vectors = self.generate_cluster(center, noise=0.15, count=items_per_category)
            names = product_names[cat_name]
            
            for i, vec in enumerate(vectors):
                name = names[i % len(names)]
                product_id = f"{cat_name}_{name}_{i:04d}"
                products.append({
                    "id": product_id,
                    "vector": vec
                })
        
        return products
    
    def _generate_movies(self, count: int) -> List[Dict]:
        """Generate movie embeddings with genre clusters."""
        movies = []
        
        genres = {
            "action": self._random_unit_vector(),
            "comedy": self._random_unit_vector(),
            "drama": self._random_unit_vector(),
            "scifi": self._random_unit_vector(),
            "horror": self._random_unit_vector(),
            "romance": self._random_unit_vector(),
        }
        
        items_per_genre = count // len(genres)
        
        for genre_name, center in genres.items():
            vectors = self.generate_cluster(center, noise=0.2, count=items_per_genre)
            
            for i, vec in enumerate(vectors):
                movie_id = f"movie_{genre_name}_{i:04d}"
                movies.append({
                    "id": movie_id,
                    "vector": vec
                })
        
        return movies
    
    def _generate_documents(self, count: int) -> List[Dict]:
        """Generate document embeddings with topic clusters."""
        documents = []
        
        topics = {
            "tech": self._random_unit_vector(),
            "business": self._random_unit_vector(),
            "science": self._random_unit_vector(),
            "health": self._random_unit_vector(),
            "politics": self._random_unit_vector(),
            "entertainment": self._random_unit_vector(),
        }
        
        items_per_topic = count // len(topics)
        
        for topic_name, center in topics.items():
            vectors = self.generate_cluster(center, noise=0.18, count=items_per_topic)
            
            for i, vec in enumerate(vectors):
                doc_id = f"doc_{topic_name}_{i:04d}"
                documents.append({
                    "id": doc_id,
                    "vector": vec
                })
        
        return documents
    
    def _generate_mixed(self, count: int) -> List[Dict]:
        """Generate mixed dataset with various themes."""
        products = self._generate_products(count // 3)
        movies = self._generate_movies(count // 3)
        docs = self._generate_documents(count // 3)
        return products + movies + docs
    
    def _generate_random(self, count: int) -> List[Dict]:
        """Generate completely random embeddings."""
        embeddings = []
        for i in range(count):
            vec = self._random_unit_vector()
            embeddings.append({
                "id": f"emb_{i:06d}",
                "vector": vec
            })
        return embeddings

def main():
    parser = argparse.ArgumentParser(
        description="Generate themed semantic embeddings for Vectro+ demos"
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=1000,
        help="Number of embeddings to generate (default: 1000)"
    )
    parser.add_argument(
        "--dim",
        type=int,
        default=128,
        help="Embedding dimension (default: 128)"
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="products",
        choices=["products", "movies", "documents", "mixed", "random"],
        help="Theme for generated embeddings (default: products)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    args = parser.parse_args()
    
    generator = SemanticEmbeddingGenerator(dim=args.dim, seed=args.seed)
    embeddings = generator.generate_themed_dataset(theme=args.theme, count=args.count)
    
    # Output as JSONL
    for emb in embeddings:
        print(json.dumps(emb))

if __name__ == "__main__":
    main()
