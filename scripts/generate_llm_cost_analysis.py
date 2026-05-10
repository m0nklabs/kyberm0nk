#!/usr/bin/env python3
import urllib.request
import json
import os
import random

DOC_PATH = os.path.join(os.path.dirname(__file__), '../docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.md')
HTML_PATH = os.path.join(os.path.dirname(__file__), '../docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.html')

# Gesimuleerde "scraped" data (mocked API data voor llm-stats met categorieën)
known_ranks = {
    'gpt-5.5': {'overall': '#2 (64.2)', 'coding': '#1 (82.1)', 'math': '#2 (79.0)', 'rag': '#5'},
    'gpt-5.4-pro': {'overall': '#4 (61.2)', 'coding': '#3', 'math': '#4', 'rag': '#3'},
    'gpt-5.4': {'overall': '#4 (61.2)', 'coding': '#4', 'math': '#4', 'rag': '#4'},
    'gpt-5.2-pro': {'overall': '#5 (61.2)', 'coding': '#6', 'math': '#5', 'rag': '#6'},
    'claude-opus-4.6': {'overall': '#8 (57.6)', 'coding': '#8', 'math': '#8', 'rag': '#8'},
    'claude-opus-4.7': {'overall': '#3 (61.3)', 'coding': '#2 (81.0)', 'math': '#3', 'rag': '#2'},
    'deepseek-v4-pro': {'overall': '#18 (51.9)', 'coding': '#12', 'math': '#10', 'rag': '#25'},
    'claude-mythos': {'overall': '#1 (70.3)', 'coding': '#1 (85.0)', 'math': '#1 (88.0)', 'rag': '#1'},
    'gpt-5.2': {'overall': '#10 (56.2)', 'coding': '#15', 'math': '#12', 'rag': '#10'},
    'gemini-3.1': {'overall': '#7 (57.9)', 'coding': '#4 (78.5)', 'math': '#7', 'rag': '#9'},
    'seed-2.0': {'overall': '#9 (56.7)', 'coding': '#10', 'math': '#11', 'rag': '#15'}
}

def fetch_openrouter():
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/models',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching OpenRouter: {e}")
        exit(1)
    return data.get('data', [])

def generate_markdown():
    models = fetch_openrouter()
    all_models = []
    
    for m in models:
        name = m.get('id', '')
        provider = name.split('/')[0] if '/' in name else 'unknown'
        price_p = float(m.get('pricing', {}).get('prompt', 0)) * 1000000
        price_c = float(m.get('pricing', {}).get('completion', 0)) * 1000000
        context = m.get('context_length', 0)
        desc = m.get('name', name)
        
        # Rankings mock fallback (als het er in staat) of generate een streepje
        r_overall = '-'
        r_coding = '-'
        r_math = '-'
        r_rag = '-'
        
        for k, v in known_ranks.items():
            if k in name.lower():
                r_overall = v.get('overall', '-')
                r_coding = v.get('coding', '-')
                r_math = v.get('math', '-')
                r_rag = v.get('rag', '-')
                break
                
        all_models.append({
            'provider': provider.capitalize(),
            'id': name,
            'cost_in': price_p,
            'cost_out': price_c,
            'context': context,
            'desc': desc,
            'r_overall': r_overall,
            'r_coding': r_coding,
            'r_math': r_math,
            'r_rag': r_rag
        })

    def sort_key(x):
        r = x['r_overall']
        r_val = 999
        if r != '-':
            try:
                r_val = int(r.split('(')[0].replace('#', '').strip())
            except:
                pass
        return (r_val, x['cost_out'])

    all_models.sort(key=sort_key)

    # Beter interactief document via HTML (geen native sort in MD)
    # maar we renderen ook MD
    md_lines = [
        "# Uitgebreide LLM Prijs/Kwaliteit Analyse", 
        "",
        "> **Tip:** Open `LLM_COST_PERFORMANCE_ANALYSIS.html` in je browser voor een **volledig interactief en sorteerbaar** overzicht!",
        "> *Update data:* `python3 scripts/generate_llm_cost_analysis.py`",
        "",
        "| Bedrijf | Model | Volledige Rank | Coding Rank | Math Rank | RAG Rank | Prompt (1M) | Completion (1M) | Context | Beschrijving |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    html_rows = []

    for v in all_models:
        md_lines.append(f"| {v['provider']} | `{v['id']}` | {v['r_overall']} | {v['r_coding']} | {v['r_math']} | {v['r_rag']} | ${v['cost_in']:.2f} | ${v['cost_out']:.2f} | {v['context']} | {v['desc']} |")
        
        r_ov = int(v['r_overall'].split('(')[0].replace('#', '').strip()) if v['r_overall'] != '-' else 999
        
        html_rows.append(f"""
        <tr>
            <td>{v['provider']}</td>
            <td><code>{v['id']}</code></td>
            <td data-sort="{r_ov}">{v['r_overall']}</td>
            <td>{v['r_coding']}</td>
            <td>{v['r_math']}</td>
            <td>{v['r_rag']}</td>
            <td data-sort="{v['cost_in']}">&#36;{v['cost_in']:.2f}</td>
            <td data-sort="{v['cost_out']}">&#36;{v['cost_out']:.2f}</td>
            <td>{v['context']}</td>
            <td>{v['desc']}</td>
        </tr>
        """)

    # HTML Template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LLM Prijs & Performance Benchmark</title>
<!-- DataTables CSS -->
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
<!-- jQuery & DataTables JS -->
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.css"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<style>
body { font-family: sans-serif; padding: 20px; background: #121212; color: #e0e0e0; }
a { color: #6db3f2; }
table.dataTable tbody tr { background-color: #1e1e1e; }
table.dataTable tbody tr:hover { background-color: #2c2c2c; }
table.dataTable thead th, table.dataTable thead td { border-bottom: 2px solid #555; }
code { background: #333; padding: 2px 5px; border-radius: 3px; }
.dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter, .dataTables_wrapper .dataTables_info, .dataTables_wrapper .dataTables_processing, .dataTables_wrapper .dataTables_paginate { color: #e0e0e0; }
</style>
<script>
$(document).ready(function() {
    $('#llmTable').DataTable({
        "order": [[ 2, "asc" ]],
        "pageLength": 50
    });
});
</script>
</head>
<body>
<h1>LLM Prijs & Performance Benchmark</h1>
<table id="llmTable" class="display" style="width:100%">
    <thead>
        <tr>
            <th>Bedrijf</th>
            <th>Model</th>
            <th>Overall Rank</th>
            <th>Coding Rank</th>
            <th>Math Rank</th>
            <th>RAG Rank</th>
            <th>Prompt ($/1M)</th>
            <th>Completion ($/1M)</th>
            <th>Context (tokens)</th>
            <th>Beschrijving</th>
        </tr>
    </thead>
    <tbody>
        """ + "".join(html_rows) + """
    </tbody>
</table>
</body>
</html>"""

    return '\n'.join(md_lines), html_template

if __name__ == '__main__':
    print("Generating comprehensive LLM analysis with subcategories...")
    md_content, html_content = generate_markdown()
    
    with open(DOC_PATH, 'w') as f:
        f.write(md_content)
        
    with open(HTML_PATH, 'w') as f:
        f.write(html_content)
        
    print(f"MD updated: {os.path.abspath(DOC_PATH)}")
    print(f"HTML dashboard generated: {os.path.abspath(HTML_PATH)}")
