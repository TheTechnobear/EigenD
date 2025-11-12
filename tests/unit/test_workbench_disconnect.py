"""
Tests for workbench disconnect functionality and find_item() behavior.

This test demonstrates that find_item() fails on deeply nested atoms
(like <console_mixer1>#3.1.1) even though they exist in the database
and have connections.

This causes disconnect() and connect_test() to fail when working with
expanded boxes that show internal pins.
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'pi'))
sys.path.insert(0, str(project_root / 'tmp/modules'))


@pytest.fixture
def eigend_database():
    """
    Create a node.Server instance connected to the current running setup.
    
    This requires eigend to be running with the test setup loaded.
    """
    from pi import node, paths
    
    paths.setup()
    db = node.Server('', None, None, False)
    db.start()
    
    yield db
    
    db.close()


class TestFindItemNestedAtoms:
    """
    Tests to demonstrate find_item() failure on nested atoms.
    
    Context:
    - Workbench shows expanded boxes with visual pins (e.g., #3.1.1)
    - These correspond to real atoms in eigend's database
    - Wire deletion tries to use find_item() on these nested IDs
    - find_item() returns None even though atoms exist
    
    Expected behavior: find_item() should work for all atom IDs
    Actual behavior: find_item() fails for deeply nested atoms
    """
    
    def test_find_agent_level_atom(self, eigend_database):
        """Agent-level atoms (like <console_mixer1>#) should be findable."""
        proxy = eigend_database.find_item('<console_mixer1>#')
        assert proxy is not None, "Agent-level atom should be found"
    
    def test_find_one_level_nested(self, eigend_database):
        """First-level children (like <console_mixer1>#3) may or may not work."""
        proxy = eigend_database.find_item('<console_mixer1>#3')
        # This might work or fail depending on implementation
        # Just document the behavior
        if proxy:
            print("✓ One-level nested atoms are findable")
        else:
            print("✗ One-level nested atoms NOT findable")
    
    def test_find_two_level_nested(self, eigend_database):
        """
        Two-level nested atoms (like <console_mixer1>#3.1) should be findable
        but find_item() likely returns None.
        """
        proxy = eigend_database.find_item('<console_mixer1>#3.1')
        
        # Check if atom exists via find_masters
        masters = eigend_database.find_masters('<console_mixer1>#3.1')
        
        if proxy is None and len(masters) > 0:
            pytest.fail(
                "find_item() returned None for <console_mixer1>#3.1 "
                f"but atom exists (has {len(masters)} masters). "
                "This breaks workbench operations!"
            )
        
        # If we get here, either proxy works or atom doesn't exist
        assert proxy is not None or len(masters) == 0
    
    def test_find_three_level_nested_KNOWN_TO_FAIL(self, eigend_database):
        """
        Three-level nested atoms (like <console_mixer1>#3.1.1) are actual
        input/output pins shown in expanded boxes.
        
        This is a KNOWN FAILURE that breaks wire deletion.
        """
        atom_id = '<console_mixer1>#3.1.1'
        
        # Try to find it
        proxy = eigend_database.find_item(atom_id)
        
        # Check if it actually exists
        masters = eigend_database.find_masters(atom_id)
        
        print(f"\n{'='*60}")
        print(f"Testing: {atom_id}")
        print(f"find_item() result: {proxy}")
        print(f"find_masters() result: {masters}")
        print(f"{'='*60}\n")
        
        # This WILL fail - documenting the bug
        if proxy is None and len(masters) > 0:
            pytest.fail(
                f"❌ KNOWN BUG: find_item() fails for {atom_id}\n"
                f"   - find_item() returned: None\n"
                f"   - But atom EXISTS with masters: {masters}\n"
                f"   - This causes disconnect() to fail\n"
                f"   - Solution: Use rpc.invoke_rpc() with to_usable_id() instead"
            )


class TestWorkbenchDisconnectRPC:
    """
    Tests the actual disconnect() implementation to show the failure.
    
    This requires:
    1. A wire to exist between <rig1>#2.1 and <console_mixer1>#3.1.1
    2. Workbench backend to be initialized
    """
    
    @pytest.mark.skip(reason="Requires full workbench environment")
    def test_disconnect_with_find_item(self, eigend_database):
        """
        This test shows that using find_item() for disconnect fails.
        
        When disconnect() uses:
            proxy = database.find_item(dstid)
            proxy.invoke_rpc('disconnect', term)
        
        It fails because proxy is None for nested atoms.
        """
        srcid = '<rig1>#2.1'
        dstid = '<console_mixer1>#3.1.1'
        
        # This is what the OLD disconnect() does
        proxy = eigend_database.find_item(dstid)
        
        assert proxy is None, (
            f"Expected find_item('{dstid}') to fail, "
            "but it returned a proxy. Test assumptions invalid."
        )
    
    @pytest.mark.skip(reason="Requires rpc module")
    def test_disconnect_with_rpc_invoke(self, eigend_database):
        """
        This test shows the CORRECT approach using rpc.invoke_rpc().
        
        When disconnect() uses:
            dst_qid = database.to_usable_id(dstid)
            rpc.invoke_rpc(dst_qid, 'disconnect', term)
        
        It works correctly even for nested atoms.
        """
        from pi import rpc, paths, logic
        
        srcid = '<rig1>#2.1'
        dstid = '<console_mixer1>#3.1.1'
        
        # Convert to qualified IDs
        dst_qid = eigend_database.to_usable_id(dstid)
        src_qid = eigend_database.to_usable_id(srcid)
        src_relative = paths.to_relative(src_qid, scope=paths.id2scope(dst_qid))
        
        # Build connection term
        term = logic.make_term('conn', None, None, src_relative, None, None)
        rendered_term = logic.render_term(term)
        
        print(f"\nDisconnect using rpc.invoke_rpc():")
        print(f"  dst_qid: {dst_qid}")
        print(f"  src_relative: {src_relative}")
        print(f"  term: {rendered_term}")
        
        # This should work
        try:
            rpc.invoke_rpc(dst_qid, 'disconnect', rendered_term)
            print("  ✓ SUCCESS - disconnect RPC completed")
        except Exception as e:
            pytest.fail(f"rpc.invoke_rpc() failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
