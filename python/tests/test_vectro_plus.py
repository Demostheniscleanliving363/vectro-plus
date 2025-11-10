"""
Comprehensive test suite for Vectro+ Python API.

Tests cover all major functionality including vector compression,
search operations, quality analysis, and error handling.
"""

import unittest
import numpy as np
import sys
import os
from typing import List, Tuple, Dict, Any

# Add the python package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import vectro_plus as vp
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    print("Warning: Rust extension not available for testing")


class TestVectroPlusCore(unittest.TestCase):
    """Test core functionality of Vectro+ Python API."""
    
    def setUp(self):
        """Set up test data."""
        if not RUST_AVAILABLE:
            self.skipTest("Rust extension not available")
            
        # Create sample embeddings for testing
        np.random.seed(42)
        self.n_vectors = 100
        self.n_dims = 64
        self.vectors = np.random.randn(self.n_vectors, self.n_dims).astype(np.float32)
        self.ids = [f"test_vec_{i}" for i in range(self.n_vectors)]
        
        # Normalize vectors for better similarity results
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        self.vectors = self.vectors / norms
    
    def test_create_search_index(self):
        """Test creating a regular search index."""
        index = vp.create_index(self.vectors, self.ids)
        self.assertIsInstance(index, vp.SearchIndex)
        
    def test_create_quantized_index(self):
        """Test creating a quantized search index."""
        index = vp.create_quantized_index(self.vectors, self.ids)
        self.assertIsInstance(index, vp.QuantizedIndex)
        
        # Check compression ratio
        ratio = index.compression_ratio()
        self.assertGreater(ratio, 1.0)  # Should have some compression
        
    def test_search_vector(self):
        """Test searching with a single vector."""
        index = vp.create_index(self.vectors, self.ids)
        
        # Use one of the original vectors as query
        query = self.vectors[0].copy()
        indices, similarities = vp.search_similar(index, query, top_k=5)
        
        self.assertEqual(len(indices), 5)
        self.assertEqual(len(similarities), 5)
        
        # First result should be the exact match
        self.assertEqual(indices[0], 0)
        self.assertAlmostEqual(similarities[0], 1.0, places=5)
        
        # Similarities should be in descending order
        self.assertTrue(all(similarities[i] >= similarities[i+1] 
                          for i in range(len(similarities)-1)))
    
    def test_batch_search(self):
        """Test batch searching with multiple queries."""
        index = vp.create_index(self.vectors, self.ids)
        
        # Use first 5 vectors as queries
        queries = self.vectors[:5].copy()
        results = vp.batch_search(index, queries, top_k=3)
        
        self.assertEqual(len(results), 5)
        
        for i, (indices, similarities) in enumerate(results):
            self.assertEqual(len(indices), 3)
            self.assertEqual(len(similarities), 3)
            
            # First result should be the exact match
            self.assertEqual(indices[0], i)
            self.assertAlmostEqual(similarities[0], 1.0, places=5)
    
    def test_quantized_search_quality(self):
        """Test that quantized search maintains reasonable quality."""
        regular_index = vp.create_index(self.vectors, self.ids)
        quantized_index = vp.create_quantized_index(self.vectors, self.ids)
        
        # Use a few queries to compare results
        for i in range(5):
            query = self.vectors[i].copy()
            
            reg_indices, reg_similarities = vp.search_similar(regular_index, query, top_k=10)
            quant_indices, quant_similarities = vp.search_similar(quantized_index, query, top_k=10)
            
            # Should find the same top result
            self.assertEqual(reg_indices[0], quant_indices[0])
            
            # Quality should be reasonable (>90% of original)
            self.assertGreater(quant_similarities[0], reg_similarities[0] * 0.9)
    
    def test_compress_embeddings_convenience(self):
        """Test the convenience compress_embeddings function."""
        search_index, quantized_index = vp.compress_embeddings(self.vectors, self.ids)
        
        self.assertIsInstance(search_index, vp.SearchIndex)
        self.assertIsInstance(quantized_index, vp.QuantizedIndex)
        
        # Test search functionality
        query = self.vectors[0].copy()
        indices, similarities = search_index.search_vector(query, top_k=3)
        self.assertEqual(len(indices), 3)
        self.assertEqual(indices[0], 0)
        
        # Test quantized search
        q_indices, q_similarities = quantized_index.search_vector(query, top_k=3)
        self.assertEqual(len(q_indices), 3)
        self.assertEqual(q_indices[0], 0)


class TestQualityAnalysis(unittest.TestCase):
    """Test quality analysis functionality."""
    
    def setUp(self):
        """Set up test data."""
        if not RUST_AVAILABLE:
            self.skipTest("Rust extension not available")
            
        np.random.seed(42)
        self.vectors = np.random.randn(50, 32).astype(np.float32)
        # Normalize for consistent results
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.vectors = self.vectors / norms
        
        self.quantized_index = vp.create_quantized_index(self.vectors)
    
    def test_analyze_compression_quality(self):
        """Test compression quality analysis."""
        quality = vp.analyze_compression_quality(self.vectors, self.quantized_index)
        
        # Check that all expected keys are present
        expected_keys = {
            "average_similarity", "max_similarity", "min_similarity",
            "compression_ratio", "memory_savings_percent", "samples_analyzed"
        }
        self.assertTrue(expected_keys.issubset(quality.keys()))
        
        # Check reasonable values
        self.assertGreater(quality["average_similarity"], 0.5)
        self.assertLessEqual(quality["max_similarity"], 1.0)
        self.assertGreater(quality["compression_ratio"], 1.0)
        self.assertGreater(quality["memory_savings_percent"], 0)
    
    def test_generate_quality_report(self):
        """Test comprehensive quality report generation."""
        report = vp.generate_quality_report(self.vectors, self.quantized_index)
        
        # Check that it includes all basic metrics plus extras
        expected_keys = {
            "average_similarity", "compression_ratio", "quality_grade",
            "recommendation", "memory_usage_mb", "original_size_estimate_mb"
        }
        self.assertTrue(expected_keys.issubset(report.keys()))
        
        # Check quality grade is valid
        self.assertIn(report["quality_grade"], ["A+", "A", "B", "C", "D"])
        
        # Check recommendation is a string
        self.assertIsInstance(report["recommendation"], str)
        self.assertGreater(len(report["recommendation"]), 10)  # Should be descriptive
    
    def test_benchmark_search_performance(self):
        """Test search performance benchmarking."""
        index = vp.create_index(self.vectors)
        
        # Create some query vectors
        queries = np.random.randn(10, 32).astype(np.float32)
        
        # Run benchmark
        benchmark = vp.benchmark_search_performance(index, queries, top_k=5, num_runs=3)
        
        expected_keys = {
            "average_latency_ms", "queries_per_second", 
            "successful_queries", "total_runs"
        }
        self.assertTrue(expected_keys.issubset(benchmark.keys()))
        
        # Check reasonable performance values
        self.assertGreater(benchmark["average_latency_ms"], 0)
        self.assertGreater(benchmark["queries_per_second"], 0)
        self.assertEqual(benchmark["total_runs"], 30)  # 10 queries * 3 runs


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test data."""
        if not RUST_AVAILABLE:
            self.skipTest("Rust extension not available")
    
    def test_empty_vectors(self):
        """Test handling of empty vector arrays."""
        empty_vectors = np.array([], dtype=np.float32).reshape(0, 10)
        
        with self.assertRaises(Exception):  # Should raise some kind of error
            vp.create_index(empty_vectors)
    
    def test_mismatched_dimensions(self):
        """Test handling of dimension mismatches."""
        vectors = np.random.randn(10, 32).astype(np.float32)
        index = vp.create_index(vectors)
        
        # Try to search with wrong dimension query
        wrong_query = np.random.randn(64).astype(np.float32)  # Different dimension
        
        with self.assertRaises(Exception):
            vp.search_similar(index, wrong_query, top_k=5)
    
    def test_invalid_top_k(self):
        """Test handling of invalid top_k values."""
        vectors = np.random.randn(10, 32).astype(np.float32)
        index = vp.create_index(vectors)
        query = np.random.randn(32).astype(np.float32)
        
        # Test top_k = 0
        with self.assertRaises(Exception):
            vp.search_similar(index, query, top_k=0)
    
    def test_non_float32_input(self):
        """Test automatic conversion of non-float32 inputs."""
        # Use float64 vectors
        vectors_f64 = np.random.randn(10, 32).astype(np.float64)
        
        # Should work with automatic conversion
        index = vp.create_index(vectors_f64)
        self.assertIsInstance(index, vp.SearchIndex)
        
        # Test with integer input
        vectors_int = (np.random.randn(10, 32) * 100).astype(np.int32)
        index = vp.create_index(vectors_int)
        self.assertIsInstance(index, vp.SearchIndex)


class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        """Set up test data.""" 
        if not RUST_AVAILABLE:
            self.skipTest("Rust extension not available")
    
    def test_load_embeddings_from_array(self):
        """Test loading embeddings from numpy array."""
        vectors = np.random.randn(20, 16).astype(np.float32)
        ids = [f"id_{i}" for i in range(20)]
        
        dataset = vp.load_embeddings_from_array(vectors, ids)
        self.assertIsInstance(dataset, vp.EmbeddingDataset)
        self.assertEqual(len(dataset), 20)
    
    def test_package_info(self):
        """Test package information functions."""
        # Test info function
        info = vp.info()
        self.assertIsInstance(info, dict)
        self.assertIn("version", info)
        self.assertIn("author", info)
        self.assertIn("rust_available", info)
        
        # Test version function
        version = vp.version()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)
    
    def test_config_usage(self):
        """Test configuration object."""
        config = vp.VectroConfig(
            compression_method="quantized",
            quantization_bits=8,
            memory_map=True
        )
        
        self.assertEqual(config.compression_method, "quantized")
        self.assertEqual(config.quantization_bits, 8)
        self.assertTrue(config.memory_map)
        
        # Test using config with index creation
        vectors = np.random.randn(10, 16).astype(np.float32)
        index = vp.create_index(vectors, config=config)
        self.assertIsInstance(index, vp.SearchIndex)


class TestIntegrationWorkflow(unittest.TestCase):
    """Test complete workflows and integration scenarios."""
    
    def setUp(self):
        """Set up test data."""
        if not RUST_AVAILABLE:
            self.skipTest("Rust extension not available")
            
        np.random.seed(123)
        self.vectors = np.random.randn(100, 128).astype(np.float32)
        
        # Normalize vectors
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.vectors = self.vectors / norms
        
        self.ids = [f"doc_{i:04d}" for i in range(100)]
    
    def test_complete_compression_workflow(self):
        """Test a complete compression and search workflow."""
        # Step 1: Compress embeddings
        search_index, quantized_index = vp.compress_embeddings(self.vectors, self.ids)
        
        # Step 2: Analyze quality
        quality_report = vp.generate_quality_report(self.vectors, quantized_index)
        self.assertIn(quality_report["quality_grade"], ["A+", "A", "B", "C", "D"])
        
        # Step 3: Benchmark performance
        queries = self.vectors[:10].copy()  # Use some vectors as queries
        benchmark = vp.benchmark_search_performance(search_index, queries, top_k=10)
        self.assertGreater(benchmark["queries_per_second"], 0)
        
        # Step 4: Search for similar vectors
        query = self.vectors[50].copy()
        
        # Regular search
        reg_indices, reg_similarities = vp.search_similar(search_index, query, top_k=5)
        
        # Quantized search
        quant_indices, quant_similarities = vp.search_similar(quantized_index, query, top_k=5)
        
        # Both should find the same top result
        self.assertEqual(reg_indices[0], quant_indices[0])
        self.assertEqual(reg_indices[0], 50)  # Should be the exact match
        
        # Quality should be maintained
        self.assertGreater(quant_similarities[0], 0.95)
    
    def test_batch_processing_workflow(self):
        """Test batch processing capabilities."""
        # Create index
        index = vp.create_quantized_index(self.vectors, self.ids)
        
        # Prepare batch queries
        batch_queries = self.vectors[::10].copy()  # Every 10th vector
        
        # Batch search
        batch_results = vp.batch_search(index, batch_queries, top_k=3)
        
        self.assertEqual(len(batch_results), 10)  # Should have 10 results
        
        # Each query should find itself as the top result
        expected_indices = list(range(0, 100, 10))
        for i, (indices, similarities) in enumerate(batch_results):
            self.assertEqual(indices[0], expected_indices[i])
            self.assertGreater(similarities[0], 0.95)
    
    def test_large_dataset_handling(self):
        """Test handling of larger datasets."""
        # Create a moderately large dataset
        large_vectors = np.random.randn(1000, 64).astype(np.float32)
        
        # Normalize
        norms = np.linalg.norm(large_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        large_vectors = large_vectors / norms
        
        # Create quantized index for memory efficiency
        quantized_index = vp.create_quantized_index(large_vectors)
        
        # Check compression
        self.assertGreater(quantized_index.compression_ratio(), 1.5)
        
        # Test search performance
        query = large_vectors[500].copy()
        indices, similarities = vp.search_similar(quantized_index, query, top_k=20)
        
        self.assertEqual(len(indices), 20)
        self.assertEqual(indices[0], 500)  # Should find exact match
        self.assertGreater(similarities[0], 0.95)


if __name__ == "__main__":
    # Check if Rust extension is available
    if not RUST_AVAILABLE:
        print("Warning: Rust extension not available. Some tests will be skipped.")
        print("To run full tests, ensure the Rust extension is properly compiled.")
    
    # Run all tests
    unittest.main(verbosity=2)