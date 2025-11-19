"""
Demo rápida del sistema de consulta de reglas integrado
Ejecuta búsquedas automáticas para mostrar funcionalidad
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from biblio import RuleBook

def demo():
    print("="*70)
    print("🎲 DEMO DEL SISTEMA DE CONSULTA DE REGLAS AD&D 2e 🎲")
    print("="*70)
    
    rulebook = RuleBook()
    
    demos = [
        ("REGLAS DE COMBATE", "iniciativa", "rules"),
        ("CONJURO OFENSIVO", "bola de fuego", "spells"),
        ("CONJURO DE CURACIÓN", "curar heridas", "spells"),
        ("CLASE GUERRERO", "guerrero", "classes"),
        ("CLASE MAGO", "mago", "classes"),
        ("ATRIBUTO FUERZA", "fuerza", "abilities"),
        ("ATRIBUTO DESTREZA", "destreza", "abilities"),
        ("OBJETO MÁGICO", "espada +1", "magic_items"),
        ("ARMA", "espada larga", "equipment"),
        ("ARMADURA", "armadura de placas", "equipment"),
    ]
    
    for title, query, category in demos:
        print(f"\n{'='*70}")
        print(f"🔍 {title}: '{query}'")
        print(f"{'='*70}")
        
        results = rulebook.search(query, category)
        
        if results:
            results.sort(key=lambda x: x['relevance'], reverse=True)
            print(rulebook.format_result(results[0]))
            
            if len(results) > 1:
                print(f"\n💡 También: {', '.join([r['name'] for r in results[1:4]])}")
        else:
            print(f"❌ No encontrado")
        
        input("\n[Presiona ENTER para continuar...]")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETADA")
    print("="*70)
    print("\n📖 Para usar en dm_assistant.py:")
    print("  python dm_assistant.py")
    print("\nComandos disponibles:")
    print("  /rules <búsqueda>   - Buscar reglas")
    print("  /spell <nombre>     - Buscar conjuros")
    print("  /class <nombre>     - Info de clases")
    print("  /ability <atributo> - Info de atributos")
    print("  /item <nombre>      - Buscar objetos")
    print("\n🎲 ¡Buenas aventuras! 🎲\n")

if __name__ == '__main__':
    demo()
