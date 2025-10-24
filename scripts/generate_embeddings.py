#!/usr/bin/env python3
"""
Generate sample embeddings for Vectro+ demos and testing.
"""

import json
import random
import argparse
from typing import List

def generate_embedding(dim: int, seed: int = None) -> List[float]:
    """Generate a random normalized embedding vector."""
    if seed is not None:
        random.seed(seed)
    
    # Generate random vector
    vec = [random.gauss(0, 1) for _ in range(dim)]
    
    # Normalize to unit length
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    
    return vec

def generate_dataset(count: int, dim: int, prefix: str = "emb") -> None:
    """Generate and print a JSONL dataset."""
    for i in range(count):
        embedding = generate_embedding(dim, seed=i)
        obj = {
            "id": f"{prefix}_{i:06d}",
            "vector": embedding
        }
        print(json.dumps(obj))

def main():
    parser = argparse.ArgumentParser(
        description="Generate sample embeddings for Vectro+ testing"
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
        "--prefix",
        type=str,
        default="emb",
        help="ID prefix (default: emb)"
    )
    
    args = parser.parse_args()
    generate_dataset(args.count, args.dim, args.prefix)

if __name__ == "__main__":
    main()
