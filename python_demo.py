#!/usr/bin/env python3
"""
Vectro+ Python Bindings Demo
============================

This demo showcases the new Python bindings for Vectro+ v1.1,
demonstrating seamless integration with NumPy and comprehensive
vector processing capabilities.

Requirements:
- vectro_py compiled (run: python setup.py build_ext --inplace)
- numpy
- Optional: matplotlib for visualizations

Author: Wesley Scholl
Version: 1.1.0
"""

import numpy as np
import time
import random
from typing import List, Tuple

print("🐍 Vectro+ Python Bindings Demo v1.1.0")
print("=" * 50)

# Check if the bindings are available
try:
    import vectro_py
    print("✅ Vectro+ Python bindings loaded successfully!")
except ImportError as e:
    print("❌ Failed to import vectro_py bindings.")
    print("Please run: python setup.py build_ext --inplace")
    print(f"Error: {e}")
    exit(1)

def generate_semantic_embeddings() -> Tuple[np.ndarray, List[str]]:
    """Generate sample embeddings with semantic meaning."""
    np.random.seed(42)  # For reproducible demos
    
    categories = {
        "🍎 fruits": ["apple", "orange", "banana", "grape", "strawberry"],
        "🚗 vehicles": ["car", "truck", "bike", "plane", "train"],
        "🔴 colors": ["red", "blue", "green", "yellow", "purple"],
        "🐕 animals": ["dog", "cat", "bird", "fish", "rabbit"]
    }
    
    embeddings = []
    ids = []
    
    for category, items in categories.items():
        # Create a base vector for this category
        base_vector = np.random.randn(128).astype(np.float32)
        
        for item in items:
            # Add some variation to the base vector
            variation = np.random.normal(0, 0.3, 128).astype(np.float32)
            embedding = base_vector + variation
            
            # Normalize to unit length for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            embeddings.append(embedding)
            ids.append(f"{category.split()[-1]}_{item}")
    
    return np.array(embeddings), ids

def demo_basic_operations():
    """Demonstrate basic embedding operations."""
    print("\n📚 Step 1: Basic Operations")
    print("-" * 30)
    
    # Generate sample data
    vectors, ids = generate_semantic_embeddings()
    print(f"Generated {len(vectors)} semantic embeddings (128-dim)")
    
    # Create dataset
    print("Creating embedding dataset...")
    dataset = vectro_py.PyEmbeddingDataset()
    
    for vector, id_ in zip(vectors, ids):
        dataset.add_vector(id_, vector)
    
    print(f"✅ Dataset created with {len(dataset)} embeddings")
    return dataset, vectors, ids

def demo_search_indices(dataset, vectors):
    """Demonstrate search index creation and usage."""
    print("\n🔍 Step 2: Search Index Creation")
    print("-" * 35)
    
    # Create search indices
    print("Creating search index...")
    search_index = vectro_py.PySearchIndex.from_dataset(dataset)
    print("✅ Search index created")
    
    print("Creating quantized index...")
    quantized_index = vectro_py.PyQuantizedIndex.from_dataset(dataset)
    print("✅ Quantized index created")
    
    # Test search
    print("\nTesting similarity search...")
    query_vector = vectors[0]  # Use first vector as query
    
    indices, similarities = search_index.search_vector(query_vector, top_k=5)
    print(f"🎯 Top 5 similar vectors:")
    for i, (idx, sim) in enumerate(zip(indices, similarities)):
        print(f"   {i+1}. Index {idx}: {sim:.6f} similarity")
    
    return search_index, quantized_index

def demo_compression_analysis(vectors, quantized_index):
    """Demonstrate compression quality analysis."""
    print("\n📊 Step 3: Compression Analysis")
    print("-" * 35)
    
    print("Analyzing compression quality...")
    quality_metrics = vectro_py.analyze_compression_quality(
        vectors, quantized_index, num_samples=min(100, len(vectors))
    )
    
    print("📈 Quality Analysis Results:")
    for metric, value in quality_metrics.items():
        if 'similarity' in metric:
            print(f"   {metric}: {value:.4f}")
        elif 'ratio' in metric:
            print(f"   {metric}: {value:.2f}x")
        elif 'percent' in metric:
            print(f"   {metric}: {value:.1f}%")
        else:
            print(f"   {metric}: {value:.0f}")
    
    return quality_metrics

def demo_performance_benchmarking(search_index, vectors):
    """Demonstrate performance benchmarking."""
    print("\n⚡ Step 4: Performance Benchmarking")
    print("-" * 40)
    
    # Generate query vectors
    num_queries = min(50, len(vectors))
    query_vectors = vectors[:num_queries]
    
    print(f"Benchmarking search performance with {num_queries} queries...")
    benchmark_results = vectro_py.benchmark_search_performance(
        search_index, query_vectors, top_k=10, num_runs=3
    )
    
    print("🚀 Performance Results:")
    for metric, value in benchmark_results.items():
        if 'latency' in metric:
            print(f"   {metric}: {value:.3f} ms")
        elif 'queries_per_second' in metric:
            print(f"   {metric}: {value:.0f} QPS")
        else:
            print(f"   {metric}: {value:.0f}")
    
    return benchmark_results

def demo_advanced_features():
    """Demonstrate advanced features and edge cases."""
    print("\n🔬 Step 5: Advanced Features")
    print("-" * 32)
    
    # Test with larger dataset
    print("Generating larger dataset for stress testing...")
    large_vectors = np.random.randn(1000, 256).astype(np.float32)
    large_ids = [f"vector_{i}" for i in range(1000)]
    
    # Normalize vectors
    norms = np.linalg.norm(large_vectors, axis=1, keepdims=True)
    large_vectors = large_vectors / norms
    
    # Quick compression test
    print("Testing high-level compression API...")
    start_time = time.time()
    
    search_idx, quant_idx = vectro_py.compress_embeddings(large_vectors, ids=large_ids)
    
    compression_time = time.time() - start_time
    print(f"✅ Compressed 1000 vectors in {compression_time:.2f} seconds")
    
    # Test batch search
    print("Testing batch search performance...")
    query_batch = large_vectors[:10]
    
    start_time = time.time()
    batch_results = search_idx.batch_search(query_batch, top_k=5)
    batch_time = time.time() - start_time
    
    print(f"✅ Batch search (10 queries) completed in {batch_time*1000:.1f} ms")
    print(f"   Average per query: {batch_time*1000/10:.2f} ms")

def demo_semantic_search():
    """Demonstrate semantic search capabilities."""
    print("\n🧠 Step 6: Semantic Search Demo")
    print("-" * 38)
    
    # Create embeddings with clear semantic relationships
    vectors, ids = generate_semantic_embeddings()
    
    dataset = vectro_py.PyEmbeddingDataset()
    for vector, id_ in zip(vectors, ids):
        dataset.add_vector(id_, vector)
    
    search_index = vectro_py.PySearchIndex.from_dataset(dataset)
    
    # Find fruit-related embeddings
    print("🍎 Searching for fruit-like vectors...")
    fruit_query = vectors[0]  # First vector is a fruit
    indices, similarities = search_index.search_vector(fruit_query, top_k=3)
    
    print("   Results:")
    for i, (idx, sim) in enumerate(zip(indices, similarities)):
        id_name = ids[idx]
        print(f"   {i+1}. {id_name}: {sim:.4f}")
    
    return search_index

def print_summary(quality_metrics, benchmark_results):
    """Print a comprehensive summary."""
    print("\n" + "="*50)
    print("📋 DEMO SUMMARY")
    print("="*50)
    
    print("🎯 Key Achievements:")
    print(f"   • Python bindings working perfectly")
    print(f"   • Zero-copy NumPy integration")
    print(f"   • Compression ratio: {quality_metrics.get('compression_ratio', 'N/A'):.1f}x")
    print(f"   • Memory savings: {quality_metrics.get('memory_savings_percent', 'N/A'):.1f}%")
    print(f"   • Search latency: {benchmark_results.get('average_latency_ms', 'N/A'):.3f} ms")
    print(f"   • Query throughput: {benchmark_results.get('queries_per_second', 'N/A'):.0f} QPS")
    
    print("\n🐍 Python API Features:")
    print("   • PyEmbedding & PyEmbeddingDataset")
    print("   • PySearchIndex & PyQuantizedIndex")
    print("   • Quality analysis tools")
    print("   • Performance benchmarking")
    print("   • High-level convenience functions")
    
    print("\n🚀 Ready for Production:")
    print("   • ML pipeline integration")
    print("   • Real-time embedding search")
    print("   • Memory-efficient compression")
    print("   • Quality-aware optimization")

def main():
    """Run the complete demo."""
    print("Starting comprehensive Python bindings demo...\n")
    
    try:
        # Step-by-step demo
        dataset, vectors, ids = demo_basic_operations()
        search_index, quantized_index = demo_search_indices(dataset, vectors)
        quality_metrics = demo_compression_analysis(vectors, quantized_index)
        benchmark_results = demo_performance_benchmarking(search_index, vectors)
        demo_advanced_features()
        demo_semantic_search()
        
        # Final summary
        print_summary(quality_metrics, benchmark_results)
        
        print("\n✅ Demo completed successfully!")
        print("🎉 Vectro+ Python bindings are ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check your Python bindings installation.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)