#!/usr/bin/env python3
"""
Standalone test for hierarchical semantic chunking.
Tests the new implementation that preserves tree structure.
"""

import json
import sys
import importlib.util
from pathlib import Path

# Import semantic module directly from file
semantic_path = Path(__file__).parent / "rest" / "agent" / "chunk" / "semantic.py"
spec = importlib.util.spec_from_file_location("semantic", semantic_path)
semantic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(semantic)

# Test data covering all edge cases

# Edge Case 1: Tiny span (easily fits in any chunk)
TINY_SPAN = {
    "span_id": "tiny_123",
    "func_full_name": "tiny_operation",
    "log_0": {"message": "Quick operation"}
}

# Edge Case 2: Small nested span
SMALL_SPAN = {
    "span_id": "small_456",
    "func_full_name": "small_operation",
    "log_0": {"message": "Starting small operation"},
    "log_1": {"message": "Step 1 complete"},
    "child_span": {
        "span_id": "child_789",
        "func_full_name": "child_op",
        "log_0": {"message": "Child running"}
    }
}

# Edge Case 3: Medium span with moderate nesting
MEDIUM_SPAN = {
    "span_id": "medium_abc",
    "func_full_name": "medium_operation",
    "log_0": {"message": "Starting medium operation"},
    "log_1": {"message": "Phase 1: Initialization"},
    "log_2": {"message": "Phase 2: Validation"},
    "validation_span": {
        "span_id": "val_def",
        "func_full_name": "validate",
        "log_0": {"message": "Validating input schema"},
        "log_1": {"message": "Checking data integrity"},
        "log_2": {"message": "Validation passed"}
    },
    "log_3": {"message": "Phase 3: Processing"},
    "process_span": {
        "span_id": "proc_ghi",
        "func_full_name": "process",
        "log_0": {"message": "Processing started"},
        "log_1": {"message": "Processing complete"}
    },
    "log_4": {"message": "Operation completed"}
}

# Edge Case 4: Large span with many logs (exceeds chunk size)
LARGE_SPAN_MANY_LOGS = {
    "span_id": "large_jkl",
    "func_full_name": "large_operation",
    **{f"log_{i}": {"message": f"Log entry {i}: This is a detailed log message with additional context and information that makes it larger"} for i in range(20)}
}

# Edge Case 5: Deep nesting (3+ levels)
DEEP_NESTED_SPAN = {
    "span_id": "root_mno",
    "func_full_name": "root_operation",
    "log_0": {"message": "Root level operation started"},
    "level_1_span": {
        "span_id": "level1_pqr",
        "func_full_name": "level_1_operation",
        "log_0": {"message": "Level 1 operation"},
        "level_2_span": {
            "span_id": "level2_stu",
            "func_full_name": "level_2_operation",
            "log_0": {"message": "Level 2 operation"},
            "level_3_span": {
                "span_id": "level3_vwx",
                "func_full_name": "level_3_operation",
                "log_0": {"message": "Level 3 operation - deepest level"}
            }
        }
    }
}

# Edge Case 6: Span with multiple children at same level
MULTIPLE_CHILDREN_SPAN = {
    "span_id": "parent_yz1",
    "func_full_name": "parent_operation",
    "log_0": {"message": "Parent operation with multiple children"},
    "child_1": {
        "span_id": "child_a1",
        "func_full_name": "child_operation_1",
        "log_0": {"message": "Child 1 executing"}
    },
    "child_2": {
        "span_id": "child_b2",
        "func_full_name": "child_operation_2",
        "log_0": {"message": "Child 2 executing"}
    },
    "child_3": {
        "span_id": "child_c3",
        "func_full_name": "child_operation_3",
        "log_0": {"message": "Child 3 executing"}
    },
    "child_4": {
        "span_id": "child_d4",
        "func_full_name": "child_operation_4",
        "log_0": {"message": "Child 4 executing"}
    }
}

# Edge Case 7: Span with nested children that have their own nested children
COMPLEX_NESTED_SPAN = {
    "span_id": "complex_root",
    "func_full_name": "complex_operation",
    "log_0": {"message": "Complex operation started"},
    "log_1": {"message": "Initializing subsystems"},
    "subsystem_a": {
        "span_id": "subsys_a",
        "func_full_name": "subsystem_a_init",
        "log_0": {"message": "Subsystem A initializing"},
        "component_a1": {
            "span_id": "comp_a1",
            "func_full_name": "component_a1",
            "log_0": {"message": "Component A1 starting"},
            "log_1": {"message": "Component A1 ready"}
        },
        "component_a2": {
            "span_id": "comp_a2",
            "func_full_name": "component_a2",
            "log_0": {"message": "Component A2 starting"},
            "log_1": {"message": "Component A2 ready"}
        }
    },
    "subsystem_b": {
        "span_id": "subsys_b",
        "func_full_name": "subsystem_b_init",
        "log_0": {"message": "Subsystem B initializing"},
        "component_b1": {
            "span_id": "comp_b1",
            "func_full_name": "component_b1",
            "log_0": {"message": "Component B1 starting"}
        }
    },
    "log_2": {"message": "All subsystems initialized"}
}

# Main comprehensive test trace
COMPREHENSIVE_TRACE = {
    "span_id": "main_comprehensive",
    "func_full_name": "main_operation",
    "log_0": {"message": "=" * 50},
    "log_1": {"message": "COMPREHENSIVE SEMANTIC CHUNKING TEST"},
    "log_2": {"message": "=" * 50},
    "log_3": {"message": "Testing all edge cases for hierarchical chunking"},
    "log_4": {"message": "Phase 1: Small operations"},
    
    # Tiny operation
    "tiny_op_1": {
        "span_id": "tiny_001",
        "func_full_name": "tiny_quick_check",
        "log_0": {"message": "Quick check passed"}
    },
    
    "log_5": {"message": "Phase 2: Validation with moderate nesting"},
    
    # Medium nested validation
    "validation_check": {
        "span_id": "val_002",
        "func_full_name": "validation_check",
        "log_0": {"message": "Starting validation"},
        "log_1": {"message": "Checking schema..."},
        "log_2": {"message": "Checking data integrity..."},
        "nested_validator": {
            "span_id": "nested_val_003",
            "func_full_name": "nested_validator",
            "log_0": {"message": "Running nested validation"},
            "log_1": {"message": "Validation passed"}
        },
        "log_3": {"message": "All validations completed"}
    },
    
    "log_6": {"message": "Phase 3: Heavy processing with many logs"},
    
    # Large operation with many logs
    "heavy_processor": {
        "span_id": "heavy_004",
        "func_full_name": "heavy_processor",
        **{f"log_{i}": {"message": f"Processing item {i} - Status: {'OK' if i % 3 != 0 else 'WARNING'}"} for i in range(15)}
    },
    
    "log_7": {"message": "Phase 4: Parallel operations (multiple children)"},
    
    # Multiple parallel children
    "parallel_executor": {
        "span_id": "parallel_005",
        "func_full_name": "parallel_executor",
        "log_0": {"message": "Starting parallel execution"},
        "worker_1": {
            "span_id": "worker_001",
            "func_full_name": "worker_process",
            "log_0": {"message": "Worker 1 processing..."},
            "log_1": {"message": "Worker 1 complete"}
        },
        "worker_2": {
            "span_id": "worker_002",
            "func_full_name": "worker_process",
            "log_0": {"message": "Worker 2 processing..."},
            "log_1": {"message": "Worker 2 complete"}
        },
        "worker_3": {
            "span_id": "worker_003",
            "func_full_name": "worker_process",
            "log_0": {"message": "Worker 3 processing..."},
            "log_1": {"message": "Worker 3 failed - retrying..."},
            "log_2": {"message": "Worker 3 retry successful"}
        }
    },
    
    "log_8": {"message": "Phase 5: Deep nesting test"},
    
    # Deep nesting
    "deep_operation": {
        "span_id": "deep_006",
        "func_full_name": "deep_operation",
        "log_0": {"message": "Level 1"},
        "level_2": {
            "span_id": "deep_007",
            "func_full_name": "level_2_op",
            "log_0": {"message": "Level 2"},
            "level_3": {
                "span_id": "deep_008",
                "func_full_name": "level_3_op",
                "log_0": {"message": "Level 3 - deepest operation"}
            }
        }
    },
    
    "log_9": {"message": "=" * 50},
    "log_10": {"message": "TEST SUMMARY"},
    "log_11": {"message": "All phases completed successfully"},
    "log_12": {"message": "=" * 50}
}


def test_edge_case(name, test_data, chunk_size):
    """Test a specific edge case and output in simple format."""
    trace_json = json.dumps(test_data, indent=2)
    
    # Print test case name
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print('='*80)
    
    # Print original context
    print("\nORIGINAL CONTEXT:")
    print(trace_json)
    
    # Generate chunks
    chunks = list(semantic.semantic_chunk(trace_json, chunk_size=chunk_size, min_chunk_size=200))
    
    # Print chunked context
    print(f"\nCHUNKED CONTEXT ({len(chunks)} chunks):")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(chunk)
    
    print()
    
    return chunks


def test_hierarchical_chunking():
    """Test the new hierarchical chunking implementation with all edge cases."""
    
    # Test 1: Tiny span
    test_edge_case(
        "Tiny Span (< 100 chars)",
        TINY_SPAN,
        chunk_size=5000
    )
    
    # Test 2: Small nested span
    test_edge_case(
        "Small Nested Span",
        SMALL_SPAN,
        chunk_size=5000
    )
    
    # Test 3: Medium span with moderate nesting
    test_edge_case(
        "Medium Span with Moderate Nesting",
        MEDIUM_SPAN,
        chunk_size=800
    )
    
    # Test 4: Large span with many logs
    test_edge_case(
        "Large Span with 20+ Logs",
        LARGE_SPAN_MANY_LOGS,
        chunk_size=1000
    )
    
    # Test 5: Deep nesting (3+ levels)
    test_edge_case(
        "Deep Nesting (3+ levels)",
        DEEP_NESTED_SPAN,
        chunk_size=1000
    )
    
    # Test 6: Multiple children at same level
    test_edge_case(
        "Multiple Children (4 siblings)",
        MULTIPLE_CHILDREN_SPAN,
        chunk_size=600
    )
    
    # Test 7: Complex nested structure
    test_edge_case(
        "Complex Nested (subsystems with components)",
        COMPLEX_NESTED_SPAN,
        chunk_size=800
    )
    
    # Test 8: Comprehensive trace (all edge cases combined)
    test_edge_case(
        "Comprehensive Trace (all patterns combined)",
        COMPREHENSIVE_TRACE,
        chunk_size=1000
    )


if __name__ == "__main__":
    try:
        test_hierarchical_chunking()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

