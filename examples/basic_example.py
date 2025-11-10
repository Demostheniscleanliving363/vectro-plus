#!/usr/bin/env python3
"""
Vectro+ Python API Basic Example

This example demonstrates the core functionality of the Vectro+ Python API:
- Creating embeddings
- Building search indices
- Performing similarity search
- Analyzing compression quality
"""

import numpy as np
import sys
import os
from pathlib import Path

# Add the python package to path for the example
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

try:
    import vectro_plus as vp
    print(f"✅ Vectro+ {vp.version()} loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import Vectro+: {e}")
    print("Please ensure the Python package is installed:")
    print("  pip install -e .")
    sys.exit(1)

def main():
    print("\n🚀 Vectro+ Python API Basic Example")
    print("="*50)
    
    # Step 1: Generate sample embeddings
    print("\n📊 Step 1: Creating sample embeddings")
    np.random.seed(42)
    
    n_vectors = 1000
    n_dimensions = 128
    
    # Create random embeddings (simulate real embeddings)
    vectors = np.random.randn(n_vectors, n_dimensions).astype(np.float32)
    
    # Normalize vectors for better similarity results
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    vectors = vectors / norms
    
    # Create IDs for the vectors
    ids = [f"document_{i:04d}" for i in range(n_vectors)]
    
    print(f"   Created {n_vectors} vectors with {n_dimensions} dimensions")
    
    # Step 2: Create search indices
    print("\n🔍 Step 2: Creating search indices")
    
    # Create regular search index
    print("   Creating regular search index...")
    search_index = vp.create_index(vectors, ids)
    print(f"   ✅ Regular index created: {search_index}")
    
    # Create quantized search index for compression
    print("   Creating quantized search index...")
    quantized_index = vp.create_quantized_index(vectors, ids)
    compression_ratio = quantized_index.compression_ratio()
    memory_mb = quantized_index.memory_usage_bytes() / (1024 * 1024)
    print(f"   ✅ Quantized index created: {quantized_index}")
    print(f"   📦 Compression ratio: {compression_ratio:.2f}x")
    print(f"   💾 Memory usage: {memory_mb:.1f} MB")
    
    # Step 3: Perform similarity search
    print("\n🔍 Step 3: Performing similarity search")
    
    # Create a query vector (use one of the original vectors for testing)
    query_idx = 42
    query_vector = vectors[query_idx].copy()
    print(f"   Using vector {query_idx} as query: {ids[query_idx]}")
    
    # Search with regular index
    print("\n   Regular index search:")
    reg_indices, reg_similarities = vp.search_similar(search_index, query_vector, top_k=5)
    
    for i, (idx, similarity) in enumerate(zip(reg_indices, reg_similarities)):
        print(f"   {i+1}. {ids[idx]} (similarity: {similarity:.6f})")
    
    # Search with quantized index
    print("\n   Quantized index search:")
    quant_indices, quant_similarities = vp.search_similar(quantized_index, query_vector, top_k=5)
    
    for i, (idx, similarity) in enumerate(zip(quant_indices, quant_similarities)):
        print(f"   {i+1}. {ids[idx]} (similarity: {similarity:.6f})")
    
    # Step 4: Batch search demonstration
    print("\n📦 Step 4: Batch search demonstration")
    
    # Use first 5 vectors as batch queries
    batch_queries = vectors[:5].copy()
    batch_results = vp.batch_search(quantized_index, batch_queries, top_k=3)
    
    print(f"   Processed {len(batch_results)} queries in batch:")
    
    for i, (indices, similarities) in enumerate(batch_results):
        top_result = ids[indices[0]]
        top_similarity = similarities[0]
        print(f"   Query {i}: Best match = {top_result} (similarity: {top_similarity:.6f})")
    
    # Step 5: Quality analysis
    print("\n📈 Step 5: Compression quality analysis")
    
    quality_report = vp.generate_quality_report(vectors, quantized_index, num_samples=500)
    
    print(f"   📊 Quality Report:")
    print(f"   • Average similarity: {quality_report['average_similarity']:.6f}")
    print(f"   • Compression ratio: {quality_report['compression_ratio']:.2f}x")
    print(f"   • Memory savings: {quality_report['memory_savings_percent']:.1f}%")
    print(f"   • Quality grade: {quality_report['quality_grade']}")
    print(f"   • Recommendation: {quality_report['recommendation']}")
    
    # Step 6: Performance benchmarking
    print("\n⚡ Step 6: Performance benchmarking")
    
    # Create some query vectors for benchmarking
    benchmark_queries = np.random.randn(20, n_dimensions).astype(np.float32)
    # Normalize
    norms = np.linalg.norm(benchmark_queries, axis=1, keepdims=True)
    norms[norms == 0] = 1
    benchmark_queries = benchmark_queries / norms
    
    # Benchmark regular index
    print("   Benchmarking regular index...")
    reg_benchmark = vp.benchmark_search_performance(
        search_index, benchmark_queries, top_k=10, num_runs=5
    )
    
    print(f"   • Average latency: {reg_benchmark['average_latency_ms']:.3f} ms")
    print(f"   • Queries per second: {reg_benchmark['queries_per_second']:.0f}")
    
    # Benchmark quantized index
    print("   Benchmarking quantized index...")
    quant_benchmark = vp.benchmark_search_performance(
        quantized_index, benchmark_queries, top_k=10, num_runs=5
    )
    
    print(f"   • Average latency: {quant_benchmark['average_latency_ms']:.3f} ms")
    print(f"   • Queries per second: {quant_benchmark['queries_per_second']:.0f}")
    
    # Summary
    print("\n🎉 Example completed successfully!")
    print("\nSummary:")
    print(f"• Processed {n_vectors} embeddings with {n_dimensions} dimensions")
    print(f"• Achieved {compression_ratio:.2f}x compression ratio")
    print(f"• Maintained {quality_report['average_similarity']:.4f} average similarity")
    print(f"• Performance: {reg_benchmark['queries_per_second']:.0f} queries/sec (regular)")
    print(f"• Performance: {quant_benchmark['queries_per_second']:.0f} queries/sec (quantized)")
    
    # Next steps
    print("\n📚 Next steps:")
    print("• Try different vector dimensions and dataset sizes")
    print("• Experiment with batch processing for large-scale operations")
    print("• Integrate Vectro+ into your ML pipeline")
    print("• Check out advanced_example.py for more features")


if __name__ == "__main__":
    main()