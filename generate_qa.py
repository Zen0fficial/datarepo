import os
import ast
import json
from typing import List, Dict

def extract_qa_from_file(filepath: str) -> List[Dict]:
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)
    qas = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            question = f"What does the function '{node.name}' do?"
            answer = ast.get_docstring(node) or "No docstring available."
            qas.append({
                'type': 'function',
                'name': node.name,
                'question': question,
                'answer': answer,
                'file': filepath,
                'lineno': node.lineno
            })
        elif isinstance(node, ast.ClassDef):
            question = f"What is the purpose of the class '{node.name}'?"
            answer = ast.get_docstring(node) or "No docstring available."
            qas.append({
                'type': 'class',
                'name': node.name,
                'question': question,
                'answer': answer,
                'file': filepath,
                'lineno': node.lineno
            })
    return qas

def extract_qa_from_dir(directory: str) -> List[Dict]:
    all_qas = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                all_qas.extend(extract_qa_from_file(filepath))
    return all_qas

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate Q&A pairs from Python code.')
    parser.add_argument('code_dir', help='Directory containing Python code')
    parser.add_argument('--output', default='qa_pairs.json', help='Output JSON file')
    args = parser.parse_args()

    qas = extract_qa_from_dir(args.code_dir)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(qas, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(qas)} Q&A pairs. Output written to {args.output}")

if __name__ == '__main__':
    main()