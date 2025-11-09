#!/usr/bin/env python3
"""
Extract and analyze connections from EigenD setup file.
Shows agent loading order and connection dependencies.
"""

import sys
import os

# Add EigenD modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pi import state, paths, logic
import piw
import picross

def pathextend(path, i):
    if not path: return "%u" % i
    return "%s.%u" % (path, i)

def find_connections(node, path=''):
    """Recursively find all 'master' properties (connections) in tree"""
    connections = []
    
    # Check if this node has 'master' property
    data_str = str(node.get_data())
    if 'master' in data_str or 'conn(' in data_str:
        connections.append((path, data_str))
    
    # Recurse children
    i = node.enum_children(0)
    while i != 0:
        child = node.get_child(i)
        connections.extend(find_connections(child, pathextend(path, i)))
        i = node.enum_children(i)
    
    return connections

def analyze_setup(setup_file):
    """Analyze setup file for loading order and connections"""
    
    print(f"Analyzing setup: {setup_file}\n")
    
    # Open database
    db = state.open_database(setup_file, False)
    snap = db.get_trunk()
    
    agent_count = snap.agent_count()
    print(f"Setup version: {snap.version()}")
    print(f"Total agents: {agent_count}\n")
    
    print("=" * 80)
    print("AGENT LOADING ORDER (from database)")
    print("=" * 80)
    
    agents = []
    for i in range(agent_count):
        agent = snap.get_agent_index(i)
        addr = agent.get_address()
        agent_type = agent.get_type()
        checkpoint = agent.get_checkpoint()
        
        agents.append({
            'index': i,
            'address': addr,
            'type': agent_type,
            'checkpoint': checkpoint,
            'agent_obj': agent
        })
        
        type_str = "persistent" if agent_type == 0 else "transient"
        print(f"{i:3d}. {addr:40s} [{type_str}] (v{checkpoint})")
    
    print("\n" + "=" * 80)
    print("CONNECTIONS FOUND")
    print("=" * 80)
    
    all_connections = []
    
    for agent_info in agents:
        agent = agent_info['agent_obj']
        addr = agent_info['address']
        idx = agent_info['index']
        
        root = agent.get_root()
        connections = find_connections(root)
        
        if connections:
            print(f"\nAgent {idx}: {addr}")
            for path, data in connections:
                print(f"  Path {path}: {data}")
                
                # Try to parse connection terms
                if 'conn(' in data:
                    all_connections.append({
                        'source_idx': idx,
                        'source': addr,
                        'path': path,
                        'data': data
                    })
    
    print("\n" + "=" * 80)
    print("POTENTIAL FORWARD REFERENCES")
    print("=" * 80)
    print("(Connections to agents that load later)\n")
    
    # Build agent name to index map
    name_to_idx = {a['address']: a['index'] for a in agents}
    
    forward_refs = []
    
    for conn in all_connections:
        src_idx = conn['source_idx']
        src_name = conn['source']
        data = conn['data']
        
        # Try to extract target agent names from connection data
        # Connection format: conn(index, flags, target_id, ...)
        if 'conn(' in data:
            # Simple parsing - look for agent names
            for target_name in name_to_idx.keys():
                if target_name in data and target_name != src_name:
                    target_idx = name_to_idx[target_name]
                    if target_idx > src_idx:
                        forward_refs.append({
                            'source_idx': src_idx,
                            'source': src_name,
                            'target_idx': target_idx,
                            'target': target_name,
                            'diff': target_idx - src_idx
                        })
    
    if forward_refs:
        forward_refs.sort(key=lambda x: x['diff'], reverse=True)
        
        for ref in forward_refs:
            print(f"Agent {ref['source_idx']:3d} ({ref['source']}) → "
                  f"Agent {ref['target_idx']:3d} ({ref['target']}) "
                  f"[+{ref['diff']} ahead]")
    else:
        print("No obvious forward references found.")
        print("(Note: Simple text search used - may miss encoded references)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total agents: {agent_count}")
    print(f"Total connections found: {len(all_connections)}")
    print(f"Forward references: {len(forward_refs)}")
    
    if forward_refs:
        max_ref = forward_refs[0]
        print(f"\nWorst forward reference:")
        print(f"  Agent {max_ref['source_idx']} → Agent {max_ref['target_idx']} "
              f"(+{max_ref['diff']} positions ahead)")
        print(f"  {max_ref['source']} → {max_ref['target']}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_setup.py <setup_file>")
        print("\nExample:")
        print("  python3 analyze_setup.py ~/Setups/my_setup")
        sys.exit(1)
    
    picross.pic_init_time()
    
    setup_file = sys.argv[1]
    if not os.path.exists(setup_file):
        print(f"Error: Setup file not found: {setup_file}")
        sys.exit(1)
    
    try:
        analyze_setup(setup_file)
    except Exception as e:
        print(f"Error analyzing setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
