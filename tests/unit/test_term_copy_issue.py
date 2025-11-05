#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to reproduce the term_copy error without running the full GUI.
This simulates what EigenLoadComponent does when it calls backend->get_setups().
"""

import sys
import os

# Add the EigenD modules to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tmp', 'stage', 'lib', 'python'))
sys.path.insert(0, os.path.dirname(__file__))

def test_term_copy_issue():
    """Test that reproduces the term_copy error in EigenLoadComponent."""
    
    print("🧪 Starting term_copy test...")
    print(f"Python version: {sys.version}")
    
    try:
        # Import the modules that EigenD uses
        print("🧪 Importing piw...")
        import piw
        print("✅ piw imported successfully")
        
        print("🧪 Importing pisession.agentd...")
        import pisession.agentd as agentd
        print("✅ agentd imported successfully")
        
        print("🧪 Calling agentd.find_all_setups() (what backend.get_setups() does)...")
        result = agentd.find_all_setups()
        print(f"✅ find_all_setups() completed successfully, result type: {type(result)}")
        
        print("🧪 Testing term conversion (what the PIP binding does)...")
        # This is what the C++ side tries to do - access the term structure
        print(f"Term type: {result.type()}")
        print(f"Term arity: {result.arity()}")
        
        if result.arity() > 0:
            print("🧪 Accessing first argument (simulating what EigenTreeItem does)...")
            first_arg = result.arg(0)
            print(f"✅ First argument accessed: {type(first_arg)}")
            
            if first_arg.arity() > 1:
                print("🧪 Accessing second argument (what itemOpennessChanged does: term_.arg(1))...")
                second_arg = first_arg.arg(1)
                print(f"✅ Second argument accessed: {type(second_arg)}")
                
                print("🧪 Testing term copy operation...")
                # This is where the crash happens - copying a term
                copied_term = piw.term_t(second_arg)  # Copy constructor
                print("✅ Term copy successful!")
                
        print("🎉 All tests passed! No term_copy error detected.")
        return True
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_term_creation():
    """Test basic term creation with different string types."""
    
    print("\n🧪 Testing simple term creation...")
    
    try:
        import piw
        
        # Test different string types
        test_strings = [
            "simple",
            "user 2",
            "pico 1",
            "with spaces",
            "user~test",
            "",
        ]
        
        for test_str in test_strings:
            print(f"🧪 Testing string: {test_str!r}")
            
            # Test raw string
            try:
                term1 = piw.term(piw.makestring(test_str, 0))
                print(f"✅ Raw string OK")
            except Exception as e:
                print(f"❌ Raw string failed: {e}")
                
            # Test encoded string
            try:
                encoded = test_str.encode('utf-8') if hasattr(test_str, 'encode') else test_str
                term2 = piw.term(piw.makestring(encoded, 0))
                print(f"✅ Encoded string OK")
            except Exception as e:
                print(f"❌ Encoded string failed: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Simple term creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_term_creation():
    """Test the Menu.term() method specifically."""
    
    print("\n🧪 Testing Menu.term() creation...")
    
    try:
        import pisession.agentd as agentd
        
        # Create a simple menu like find_user_setups does
        menu = agentd.Menu('Test Menu')
        
        # Add a test setup (similar to what find_user_setups does)
        menu.add_setup('', 'user 2', '/test/path', False, True)
        
        print("🧪 Calling menu.term()...")
        result = menu.term()
        print(f"✅ Menu.term() completed, type: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Menu term creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 EigenD term_copy reproduction test")
    print("=" * 50)
    
    # Run the tests
    success = True
    
    success &= test_simple_term_creation()
    success &= test_menu_term_creation() 
    success &= test_term_copy_issue()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)