"""
Test rápido de integración biblio.py en dm_assistant.py
"""

from biblio import RuleBook

# Crear instancia
rulebook = RuleBook()

# Test de búsquedas
print("="*70)
print("TEST 1: Buscar 'THAC0'")
print("="*70)
results = rulebook.search("THAC0", "rules")
if results:
    results.sort(key=lambda x: x['relevance'], reverse=True)
    print(rulebook.format_result(results[0]))

print("\n" + "="*70)
print("TEST 2: Buscar conjuro 'misiles mágicos'")
print("="*70)
results = rulebook.search("misiles mágicos", "spells")
if results:
    results.sort(key=lambda x: x['relevance'], reverse=True)
    print(rulebook.format_result(results[0]))

print("\n" + "="*70)
print("TEST 3: Buscar clase 'mago'")
print("="*70)
results = rulebook.search("mago", "classes")
if results:
    results.sort(key=lambda x: x['relevance'], reverse=True)
    print(rulebook.format_result(results[0]))

print("\n" + "="*70)
print("TEST 4: Buscar objeto 'espada +1'")
print("="*70)
results = rulebook.search("espada +1", "magic_items")
if not results:
    results = rulebook.search("espada +1", "equipment")
if results:
    results.sort(key=lambda x: x['relevance'], reverse=True)
    print(rulebook.format_result(results[0]))

print("\n✅ Todos los tests completados")
