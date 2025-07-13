import os
import ast
import json
from typing import Dict, List, Set

class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.call_graph = {}

    def visit_FunctionDef(self, node):
        prev_function = self.current_function
        self.current_function = node.name
        if node.name not in self.call_graph:
            self.call_graph[node.name] = set()
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.call_graph[self.current_function].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.call_graph[self.current_function].add(node.func.attr)
        self.generic_visit(node)

def extract_call_graph_from_file(filepath: str) -> Dict[str, Set[str]]:
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)
    visitor = CallGraphVisitor()
    visitor.visit(tree)
    return visitor.call_graph

def merge_call_graphs(graphs: List[Dict[str, Set[str]]]) -> Dict[str, Set[str]]:
    merged = {}
    for graph in graphs:
        for func, calls in graph.items():
            if func not in merged:
                merged[func] = set()
            merged[func].update(calls)
    return merged

def extract_call_graph_from_dir(directory: str) -> Dict[str, List[str]]:
    all_graphs = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                all_graphs.append(extract_call_graph_from_file(filepath))
    merged = merge_call_graphs(all_graphs)
    # Convert sets to lists for JSON serialization
    return {k: list(v) for k, v in merged.items()}

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate call graph (trace data) from Python code.')
    parser.add_argument('code_dir', help='Directory containing Python code')
    parser.add_argument('--output', default='trace_data.json', help='Output JSON file')
    args = parser.parse_args()

    call_graph = extract_call_graph_from_dir(args.code_dir)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(call_graph, f, indent=2, ensure_ascii=False)
    print(f"Generated call graph for {len(call_graph)} functions. Output written to {args.output}")

if __name__ == '__main__':
    main()