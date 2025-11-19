"""
Sistema de referencia de reglas para AD&D 2e
Rules reference system for AD&D 2e
"""
from typing import Dict, List, Optional


# Base de datos de reglas / Rules database
RULES_DATABASE = {
    "combate": {
        "nombre": "Combate / Combat",
        "reglas": [
            {
                "titulo": "Iniciativa / Initiative",
                "descripcion": "Cada bando tira 1d10. El resultado más bajo actúa primero. En caso de empate, las acciones son simultáneas. / Each side rolls 1d10. Lowest roll acts first. Ties are simultaneous."
            },
            {
                "titulo": "Tirada de Ataque / Attack Roll",
                "descripcion": "Tira 1d20 + modificadores. Compara con THAC0 del atacante menos CA del defensor. Si es igual o mayor, impacta. / Roll 1d20 + modifiers. Compare to attacker's THAC0 minus defender's AC. Equal or higher hits."
            },
            {
                "titulo": "Daño / Damage",
                "descripcion": "Tira el dado de daño del arma + modificadores de Fuerza. Resta de los HP del objetivo. / Roll weapon damage die + Strength modifiers. Subtract from target's HP."
            },
            {
                "titulo": "Ataque de Oportunidad / Attack of Opportunity",
                "descripcion": "Los enemigos pueden atacar cuando te retiras del combate cuerpo a cuerpo. / Enemies can attack when you withdraw from melee combat."
            }
        ]
    },
    "tiradas_salvacion": {
        "nombre": "Tiradas de Salvación / Saving Throws",
        "reglas": [
            {
                "titulo": "Tipos de Salvación / Save Types",
                "descripcion": "Hay 5 categorías: Vara/Bastón/Cetro, Petrificación/Polimorfismo, Aliento de Dragón, Conjuros, y Muerte/Veneno. / There are 5 categories: Rod/Staff/Wand, Petrification/Polymorph, Breath Weapon, Spell, and Death Magic/Poison."
            },
            {
                "titulo": "Cómo usar / How to use",
                "descripcion": "Tira 1d20. Si el resultado es igual o superior al número objetivo de salvación, tienes éxito. / Roll 1d20. If equal to or higher than the save target number, you succeed."
            }
        ]
    },
    "habilidades": {
        "nombre": "Habilidades / Abilities",
        "reglas": [
            {
                "titulo": "Fuerza / Strength",
                "descripcion": "Afecta al combate cuerpo a cuerpo, daño y peso que puedes cargar. / Affects melee combat, damage, and encumbrance."
            },
            {
                "titulo": "Destreza / Dexterity",
                "descripcion": "Afecta a CA, ataque a distancia e iniciativa. / Affects AC, ranged attacks, and initiative."
            },
            {
                "titulo": "Constitución / Constitution",
                "descripcion": "Afecta a puntos de golpe y resistencia. / Affects hit points and endurance."
            },
            {
                "titulo": "Inteligencia / Intelligence",
                "descripcion": "Afecta a número de conjuros y nivel máximo de conjuros para magos. / Affects spell numbers and max spell level for wizards."
            },
            {
                "titulo": "Sabiduría / Wisdom",
                "descripcion": "Afecta a tiradas de salvación contra magia mental y conjuros de sacerdotes. / Affects saves vs mental magic and priest spells."
            },
            {
                "titulo": "Carisma / Charisma",
                "descripcion": "Afecta a reacciones de PNJs y número máximo de seguidores. / Affects NPC reactions and max number of henchmen."
            }
        ]
    },
    "magia": {
        "nombre": "Magia / Magic",
        "reglas": [
            {
                "titulo": "Memorización / Memorization",
                "descripcion": "Los conjuradores deben memorizar conjuros antes de lanzarlos. Requiere descanso. / Spellcasters must memorize spells before casting. Requires rest."
            },
            {
                "titulo": "Componentes / Components",
                "descripcion": "Los conjuros pueden requerir componentes verbales (V), somáticos (S) y/o materiales (M). / Spells may require verbal (V), somatic (S), and/or material (M) components."
            },
            {
                "titulo": "Interrupción / Interruption",
                "descripcion": "Si recibes daño mientras lanzas un conjuro, debes hacer una salvación de Concentración o perder el conjuro. / If damaged while casting, must make Concentration save or lose the spell."
            },
            {
                "titulo": "Niveles de Conjuro / Spell Levels",
                "descripcion": "Los conjuros van del nivel 1 al 9. Niveles de personaje más altos permiten acceder a conjuros más poderosos. / Spells range from level 1-9. Higher character levels grant access to more powerful spells."
            }
        ]
    },
    "experiencia": {
        "nombre": "Experiencia / Experience",
        "reglas": [
            {
                "titulo": "Ganar XP / Gaining XP",
                "descripcion": "Se gana XP por derrotar monstruos, completar objetivos y tesoros recuperados. / XP is gained from defeating monsters, completing objectives, and treasure recovered."
            },
            {
                "titulo": "Subida de Nivel / Level Up",
                "descripcion": "Al alcanzar suficiente XP, subes de nivel. Tira dados de golpe y gana nuevas habilidades. / Upon reaching enough XP, you level up. Roll hit dice and gain new abilities."
            }
        ]
    },
    "movimiento": {
        "nombre": "Movimiento / Movement",
        "reglas": [
            {
                "titulo": "Velocidad Base / Base Movement",
                "descripcion": "La mayoría de razas tienen 12\" de movimiento (120 pies/turno). / Most races have 12\" movement (120 feet/turn)."
            },
            {
                "titulo": "Combate / Combat",
                "descripcion": "En combate, puedes moverte tu velocidad completa o atacar, no ambos en la misma ronda. / In combat, you can move your full rate or attack, not both in the same round."
            }
        ]
    }
}


class RulesReference:
    """Manejador de referencia de reglas / Rules reference handler"""
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """
        Obtiene todas las categorías de reglas / Get all rule categories
        
        Returns:
            Lista de categorías / List of categories
        """
        return [data["nombre"] for data in RULES_DATABASE.values()]
    
    @staticmethod
    def get_category(category_key: str) -> Optional[Dict]:
        """
        Obtiene una categoría específica / Get a specific category
        
        Args:
            category_key: Clave de la categoría / Category key
            
        Returns:
            Datos de la categoría o None / Category data or None
        """
        return RULES_DATABASE.get(category_key)
    
    @staticmethod
    def search_rules(query: str) -> List[Dict]:
        """
        Busca reglas por palabra clave / Search rules by keyword
        
        Args:
            query: Término de búsqueda / Search term
            
        Returns:
            Lista de reglas coincidentes / List of matching rules
        """
        query = query.lower()
        results = []
        
        for category_key, category_data in RULES_DATABASE.items():
            for rule in category_data["reglas"]:
                if (query in rule["titulo"].lower() or 
                    query in rule["descripcion"].lower() or
                    query in category_data["nombre"].lower()):
                    results.append({
                        "categoria": category_data["nombre"],
                        "titulo": rule["titulo"],
                        "descripcion": rule["descripcion"]
                    })
        
        return results
    
    @staticmethod
    def display_category(category_key: str):
        """
        Muestra una categoría de reglas / Display a rule category
        
        Args:
            category_key: Clave de la categoría / Category key
        """
        category = RulesReference.get_category(category_key)
        if not category:
            print(f"Categoría no encontrada / Category not found: {category_key}")
            return
        
        print(f"\n=== {category['nombre']} ===\n")
        for rule in category["reglas"]:
            print(f"• {rule['titulo']}")
            print(f"  {rule['descripcion']}\n")
    
    @staticmethod
    def display_all_rules():
        """Muestra todas las reglas / Display all rules"""
        print("\n=== REGLAS DE AD&D 2e / AD&D 2e RULES ===\n")
        
        for category_key in RULES_DATABASE.keys():
            RulesReference.display_category(category_key)
    
    @staticmethod
    def interactive_search():
        """Búsqueda interactiva de reglas / Interactive rule search"""
        print("\n=== Búsqueda de Reglas / Rules Search ===")
        print("Introduce una palabra clave o 'salir' para terminar")
        print("Enter a keyword or 'exit' to quit\n")
        
        while True:
            query = input("Buscar / Search: ").strip()
            
            if query.lower() in ['salir', 'exit', 'quit', '']:
                break
            
            results = RulesReference.search_rules(query)
            
            if results:
                print(f"\n{len(results)} resultado(s) encontrado(s) / result(s) found:\n")
                for result in results:
                    print(f"[{result['categoria']}]")
                    print(f"• {result['titulo']}")
                    print(f"  {result['descripcion']}\n")
            else:
                print("No se encontraron resultados / No results found\n")
