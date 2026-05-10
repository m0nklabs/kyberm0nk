#!/usr/bin/env python3
import urllib.request
import json
import collections
import os

DOC_PATH = os.path.join(os.path.dirname(__file__), '../docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.md')

# Bekende LLM-Stats ranks
known_ranks = {
    'gpt-5.5': '#2 (64.2)',
    'gpt-5.4-pro': '#4 (61.2)',
    'gpt-5.4': '#4 (61.2)',
    'gpt-5.2-pro': '#5 (61.2)',
    'claude-opus-4.6': '#8 (57.6)',
    'claude-opus-4.7': '#3 (61.3)',
    'deepseek-v4-pro': '#18 (51.9)',
    'claude-mythos': '#1 (70.3)',
    'gpt-5.2': '#10 (56.2)',
    'gemini-3.1': '#7 (57.9)',
    'seed-2.0': '#9 (56.7)'
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
    providers = collections.defaultdict(list)
    
    for m in models:
        name = m.get('id', '')
        provider = name.split('/')[0] if '/' in name else 'unknown'
        price_p = float(m.get('pricing', {}).get('prompt', 0)) * 1000000
        price_c = float(m.get('pricing', {}).get('completion', 0)) * 1000000
        context = m.get('context_length', 0)
        desc = m.get('name', name)
        
        # Bepaal rank indien we m kennen
        rank = '-'
        for k, v in known_ranks.items():
            if k in name.lower():
                rank = v
                break
                
        providers[provider].append({
            'id': name,
            'cost_in': price_p,
            'cost_out': price_c,
            'context': context,
            'desc': desc,
            'rank': rank
        })

    # Top 20 providers gebaseerd op hoeveelheid modellen
    top_providers = sorted(providers.keys(), key=lambda k: len(providers[k]), reverse=True)
    selected_providers = top_providers[:20]

    md_lines = [
        "# Uitgebreide LLM Prijs/Kwaliteit Analyse (20 Bedrijven)", 
        "",
        "> **Let op:** Dit document kan automatisch ge-update worden met live data via `scripts/generate_llm_cost_analysis.py`.",
        ""
    ]

    for p in selected_providers:
        md_lines.append(f"## {p.capitalize()}")
        md_lines.append("| Rank/Score | Model | Live Prijs (1M In / Out) | Context | Beschrijving |")
        md_lines.append("|---|---|---|---|---|")
        
        variants = sorted(providers[p], key=lambda x: x['cost_out'], reverse=True)
        # Max 10 laten zien, of meer als gewenst
        for v in variants[:10]:
            md_lines.append(f"| {v['rank']} | `{v['id']}` | ${v['cost_in']:.2f} / ${v['cost_out']:.2f} | {v['context']} | {v['desc']} |")
        md_lines.append("")

    return '\n'.join(md_lines)

if __name__ == '__main__':
    print("Generating comprehensive LLM analysis...")
    md_content = generate_markdown()
    
    # Save the file
    with open(DOC_PATH, 'w') as f:
        f.write(md_content)
        
    print(f"Document updated successfully at: {os.path.abspath(DOC_PATH)}")

