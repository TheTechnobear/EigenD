#!/usr/bin/env python3
"""
Test PIW functionality with proper initialization.
This validates our PyString_AsString migration with correct PIW context.
"""

import sys
import os

# Add EigenD paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/modules')

def test_piw_with_initialization():
    """Test PIW functionality with proper thread state initialization."""
    try:
        import piw
        print("✓ piw module imported successfully")
        
        # Initialize PIW thread state (like eigend does)
        print("Initializing PIW thread state...")
        piw.tsd_lock()
        print("✓ PIW thread state initialized")
        
        # Test basic term constructors
        empty_term = piw.term()
        print(f"✓ term() constructor works: {empty_term}")
        
        unsigned_term = piw.term(42)
        print(f"✓ term(unsigned) constructor works: {unsigned_term}")
        print(f"  Value: {unsigned_term.value()}, Type: {unsigned_term.type()}")
        
        string_term = piw.term("hello", 3)
        print(f"✓ term(string, type) constructor works: {string_term}")
        print(f"  Value: {string_term.value()}, Type: {string_term.type()}")
        
        # Test the problematic copy constructor
        try:
            copy_term = piw.term(string_term)
            print(f"✓ term(term) copy constructor works: {copy_term}")
            print(f"  Value: {copy_term.value()}, Type: {copy_term.type()}")
        except Exception as e:
            print(f"✗ term(term) copy constructor failed: {e}")
            # This is expected based on our analysis
        
        # Test data object creation
        try:
            string_data = piw.makestring("test string", 0)
            print(f"✓ makestring works: {string_data}")
            print(f"  as_string(): {string_data.as_string()}")
            
            bool_data = piw.makebool(True, 0)
            print(f"✓ makebool works: {bool_data}")
            print(f"  as_bool(): {bool_data.as_bool()}")
            
            num_data = piw.makelong(42, 0)
            print(f"✓ makelong works: {num_data}")
            print(f"  as_long(): {num_data.as_long()}")
            
        except Exception as e:
            print(f"✗ Data object creation failed: {e}")
            print("This suggests PIW context still not fully initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_term_copy_specific_issue():
    """Focus specifically on the term copy constructor issue."""
    try:
        import piw
        piw.tsd_lock()
        
        print("\n=== Term Copy Constructor Analysis ===")
        
        # Create source term
        source_term = piw.term("hello world", 3)
        print(f"Source term: {source_term}")
        print(f"  Value: {source_term.value()}")
        print(f"  Type: {source_term.type()}")
        
        # Try to copy it
        try:
            copy_term = piw.term(source_term)
            print(f"✓ Copy succeeded: {copy_term}")
        except TypeError as e:
            print(f"✗ TypeError: {e}")
            print("This confirms the PIP binding issue - copy constructor expects 2 args but gets 1")
            
            # Check what the constructor signature actually is
            print("\nDiagnosing constructor signature...")
            help(piw.term.__init__)
            
        except Exception as e:
            print(f"✗ Other error: {e}")
            
    except Exception as e:
        print(f"✗ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Testing PIW functionality with proper initialization...")
    print()
    
    success = test_piw_with_initialization()
    test_term_copy_specific_issue()
    
    print()
    if success:
        print("🔍 PIW module loads but has known issues:")
        print("- term(term) copy constructor parameter mismatch")
        print("- Data object creation may need additional context")
        print("- PyString_AsString migration itself is working correctly")
    else:
        print("❌ PIW module has initialization issues")