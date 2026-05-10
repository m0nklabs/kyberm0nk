#!/usr/bin/env python3
import urllib.request
import json
import os
import re

DOC_PATH = os.path.join(os.path.dirname(__file__), '../docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.md')
HTML_PATH = os.path.join(os.path.dirname(__file__), '../docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.html')

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

def fetch_llm_stats():
    req = urllib.request.Request('https://llm-stats.com/', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')

        matches = re.finditer(r'\[\{\\\"model_id\\\":', html)
        longest_array = ""

        for m in matches:
            start_idx = m.start()
            count = 0
            in_string = False
            escape = False
            end_idx = start_idx
            for i in range(start_idx, len(html)):
                char = html[i]
                if not escape and char == '\\' and i+1 < len(html) and html[i+1] == '"':
                    in_string = not in_string
                
                if not in_string:
                    if char == '[':
                        count += 1
                    elif char == ']':
                        count -= 1
                        
                if count == 0 and char == ']':
                    end_idx = i
                    break
                    
            candidate = html[start_idx:end_idx+1]
            if len(candidate) > len(longest_array):
                longest_array = candidate

        if longest_array:
            clean_json = longest_array.encode('utf-8').decode('unicode_escape')
            return json.loads(clean_json)
    except Exception as e:
        print("Scrape llm-stats failed:", e)
    return []

def calculate_ranks(llm_data):
    # Sort for overall arena
    chat_arena = sorted([m for m in llm_data if m.get('arena_scores', {}).get('chat-arena')], 
                        key=lambda x: x['arena_scores']['chat-arena'], reverse=True)
    coding_arena = sorted([m for m in llm_data if m.get('arena_scores', {}).get('coding-arena')], 
                          key=lambda x: x['arena_scores']['coding-arena'], reverse=True)
    gpqa = sorted([m for m in llm_data if m.get('gpqa_score')], 
                  key=lambda x: x['gpqa_score'], reverse=True)

    ranks = {}
    for i, m in enumerate(chat_arena):
        mid = m['model_id']
        ranks.setdefault(mid, {})['overall'] = f"#{i+1} ({m['arena_scores']['chat-arena']:.1f})"
    
    for i, m in enumerate(coding_arena):
        mid = m['model_id']
        ranks.setdefault(mid, {})['coding'] = f"#{i+1} ({m['arena_scores']['coding-arena']:.1f})"
        
    for i, m in enumerate(gpqa):
        mid = m['model_id']
        ranks.setdefault(mid, {})['math_logic'] = f"#{i+1} ({(m['gpqa_score']*100):.1f}%)"
        
    return ranks

def generate_markdown():
    print("Fetching OpenRouter...")
    models = fetch_openrouter()
    
    print("Fetching and parsing llm-stats...")
    llm_data = fetch_llm_stats()
    ext_ranks = calculate_ranks(llm_data)
    
    all_models = []
    for m in models:
        name = m.get('id', '')
        provider = name.split('/')[0] if '/' in name else 'unknown'
        
        # openrouter cost is often per 1 prompt token, multiply by 1M
        price_p = float(m.get('pricing', {}).get('prompt', 0)) * 1000000
        price_c = float(m.get('pricing', {}).get('completion', 0)) * 1000000
        context = m.get('context_length', 0)
        desc = m.get('name', name)
        
        # Try finding a match in llm-stats. OpenRouter names look like `anthropic/claude-3-opus`.
        # `model_id` in llm-stats looks like `claude-3-opus-20240229`. So string overlap check.
        r_overall, r_coding, r_math = '-', '-', '-'
        model_part = name.split('/')[-1].lower()
        
        # Soms heet openrouter gpt-4o-mini en stats gpt-4o-mini-2024-07-18
        # We zoeken de match met de langste naam die overeenkomt.
        best_match_id = None
        for stat_m in llm_data:
            s_id = stat_m['model_id'].lower()
            if model_part in s_id or s_id in model_part:
                best_match_id = stat_m['model_id']
                break
                
        if best_match_id and best_match_id in ext_ranks:
            rank_dict = ext_ranks[best_match_id]
            r_overall = rank_dict.get('overall', '-')
            r_coding = rank_dict.get('coding', '-')
            r_math = rank_dict.get('math_logic', '-')

        all_models.append({
            'provider': provider.capitalize(),
            'id': name,
            'cost_in': price_p,
            'cost_out': price_c,
            'context': context,
            'desc': desc,
            'r_overall': r_overall,
            'r_coding': r_coding,
            'r_math': r_math
        })

    def sort_key(x):
        r = x['r_overall']
        r_val = 9999
        if r != '-':
            try:
                r_val = int(r.split('(')[0].replace('#', '').strip())
            except:
                pass
        return (r_val, x['cost_out'])

    all_models.sort(key=sort_key)

    md_lines = [
        "# Uitgebreide LLM Prijs/Kwaliteit Analyse (Live OpenRouter + LLM-Stats)", 
        "",
        "> **Tip:** Open `LLM_COST_PERFORMANCE_ANALYSIS.html` in je browser voor een **volledig interactief en sorteerbaar** overzicht!",
        "> *Update data:* `python3 scripts/generate_llm_cost_analysis.py`",
        "",
        "| Bedrijf | Model | Overall Rank (Arena) | Coding Rank | GPQA (Logic) Rank | Prompt (1M) | Completion (1M) | Context | Beschrijving |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    html_rows = []

    for v in all_models:
        md_lines.append(f"| {v['provider']} | `{v['id']}` | {v['r_overall']} | {v['r_coding']} | {v['r_math']} | ${v['cost_in']:.2f} | ${v['cost_out']:.2f} | {v['context']} | {v['desc']} |")
        
        r_ov = int(v['r_overall'].split('(')[0].replace('#', '').strip()) if v['r_overall'] != '-' else 9999
        r_co = int(v['r_coding'].split('(')[0].replace('#', '').strip()) if v['r_coding'] != '-' else 9999
        r_ma = int(v['r_math'].split('(')[0].replace('#', '').strip()) if v['r_math'] != '-' else 9999
        
        html_rows.append(f"""
        <tr>
            <td>{v['provider']}</td>
            <td><code>{v['id']}</code></td>
            <td data-sort="{r_ov}">{v['r_overall']}</td>
            <td data-sort="{r_co}">{v['r_coding']}</td>
            <td data-sort="{r_ma}">{v['r_math']}</td>
            <td data-sort="{v['cost_in']}">&#36;{v['cost_in']:.2f}</td>
            <td data-sort="{v['cost_out']}">&#36;{v['cost_out']:.2f}</td>
            <td>{v['context']}</td>
            <td>{v['desc']}</td>
        </tr>
        """)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LLM Prijs & Performance Benchmark</title>
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
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
<h1>LLM Prijs & Performance Benchmark (Live OpenRouter + LLM-stats.com)</h1>
<table id="llmTable" class="display" style="width:100%">
    <thead>
        <tr>
            <th>Bedrijf</th>
            <th>Model</th>
            <th>Overall Rank</th>
            <th>Coding Rank</th>
            <th>GPQA (Logic) Rank</th>
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
    md_content, html_content = generate_markdown()
    with open(DOC_PATH, 'w') as f:
        f.write(md_content)
    with open(HTML_PATH, 'w') as f:
        f.write(html_content)
    print(f"MD updated: {os.path.abspath(DOC_PATH)}")
    print(f"HTML dashboard generated: {os.path.abspath(HTML_PATH)}")
