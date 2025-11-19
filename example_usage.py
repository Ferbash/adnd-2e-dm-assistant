#!/usr/bin/env python3
"""
Ejemplo de uso del Asistente AD&D 2e
Example usage of the AD&D 2e Assistant

Este script demuestra las capacidades principales del asistente.
This script demonstrates the main capabilities of the assistant.
"""

from dice_roller import DiceRoller
from character import Character
from rules import RulesReference


def main():
    print("\n" + "="*70)
    print("  DEMOSTRACIÓN DEL ASISTENTE AD&D 2e")
    print("  AD&D 2e ASSISTANT DEMONSTRATION")
    print("="*70)
    
    # 1. Tiradas de dados / Dice Rolling
    print("\n### 1. TIRADAS DE DADOS / DICE ROLLING ###\n")
    
    print("Ataque con espada larga / Longsword attack: 1d20+2")
    total, rolls = DiceRoller.roll_from_notation("1d20+2")
    print(f"  Resultado: {total} (tirada: {rolls[0]})")
    
    print("\nDaño de hacha / Battleaxe damage: 1d8+3")
    total, rolls = DiceRoller.roll_from_notation("1d8+3")
    print(f"  Resultado: {total} (tirada: {rolls[0]})")
    
    print("\nBola de fuego / Fireball: 8d6")
    total, rolls = DiceRoller.roll_from_notation("8d6")
    print(f"  Resultado: {total} (tiradas: {rolls})")
    
    # 2. Creación de personajes / Character Creation
    print("\n\n### 2. CREACIÓN DE PERSONAJES / CHARACTER CREATION ###\n")
    
    # Crear un guerrero enano / Create a dwarf fighter
    print("Creando un Guerrero Enano / Creating a Dwarf Fighter...")
    dwarf = Character("Bruenor Battlehammer", "Enano", "Guerrero", ability_scores={
        "Fuerza": 17,
        "Destreza": 12,
        "Constitución": 16,
        "Inteligencia": 10,
        "Sabiduría": 13,
        "Carisma": 9
    })
    print(dwarf)
    
    # Crear un mago elfo / Create an elf wizard
    print("\n" + "-"*70)
    print("\nCreando un Mago Elfo / Creating an Elf Wizard...")
    elf = Character("Elminster", "Elfo", "Mago", ability_scores={
        "Fuerza": 10,
        "Destreza": 14,
        "Constitución": 12,
        "Inteligencia": 18,
        "Sabiduría": 15,
        "Carisma": 14
    })
    print(elf)
    
    # 3. Gestión de recursos / Resource Management
    print("\n\n### 3. GESTIÓN DE RECURSOS / RESOURCE MANAGEMENT ###\n")
    
    print(f"Bruenor encuentra un tesoro / Bruenor finds treasure...")
    dwarf.modify_resource("Oro", 500)
    dwarf.add_item("Hacha de guerra +1")
    dwarf.add_item("Armadura de placas")
    dwarf.add_item("Poción de curación superior")
    print(f"  Oro: {dwarf.resources['Oro']} monedas de oro")
    print(f"  Items: {', '.join(dwarf.resources['Items'])}")
    
    print(f"\nElminster sufre daño en combate / Elminster takes damage in combat...")
    print(f"  HP antes / HP before: {elf.current_hp}/{elf.max_hp}")
    elf.modify_resource("HP", -8)
    print(f"  HP después / HP after: {elf.current_hp}/{elf.max_hp}")
    
    print(f"\nElminster bebe una poción / Elminster drinks a potion...")
    healing = DiceRoller.roll_from_notation("2d4+2")[0]
    elf.modify_resource("HP", healing)
    print(f"  Curación / Healing: +{healing} HP")
    print(f"  HP final / Final HP: {elf.current_hp}/{elf.max_hp}")
    
    # 4. Consulta de reglas / Rules Query
    print("\n\n### 4. CONSULTA DE REGLAS / RULES QUERY ###\n")
    
    print("Buscando 'combate' / Searching for 'combat'...")
    results = RulesReference.search_rules("combate")
    print(f"  Encontrados {len(results)} resultados / Found {len(results)} results\n")
    for i, result in enumerate(results[:3], 1):  # Mostrar primeros 3 / Show first 3
        print(f"  {i}. [{result['categoria']}] {result['titulo']}")
        print(f"     {result['descripcion'][:80]}...")
        print()
    
    # 5. Ejemplo de combate / Combat Example
    print("\n### 5. EJEMPLO DE COMBATE / COMBAT EXAMPLE ###\n")
    
    print("Bruenor ataca a un orco / Bruenor attacks an orc...")
    print("  Roll de iniciativa / Initiative roll: 1d10")
    initiative = DiceRoller.roll(1, 10)[0]
    print(f"    Resultado: {initiative}")
    
    print("\n  Ataque / Attack roll: 1d20+4 (Fuerza +2, Maestría +2)")
    attack_roll = DiceRoller.roll_from_notation("1d20+4")[0]
    print(f"    Resultado: {attack_roll}")
    
    if attack_roll >= 15:  # THAC0 simplificado / Simplified THAC0
        print("    ¡Impacto! / Hit!")
        damage = DiceRoller.roll_from_notation("1d10+3")[0]  # Hacha de guerra +1 + Fuerza
        print(f"  Daño / Damage: {damage} HP")
    else:
        print("    ¡Fallo! / Miss!")
    
    # Resumen final / Final Summary
    print("\n" + "="*70)
    print("  RESUMEN / SUMMARY")
    print("="*70)
    print(f"\n  Personajes creados / Characters created: 2")
    print(f"  Tiradas realizadas / Rolls made: múltiples / multiple")
    print(f"  Reglas consultadas / Rules queried: sí / yes")
    print(f"  Sistema funcionando / System working: ✓")
    print("\n  ¡Asistente AD&D 2e listo para jugar!")
    print("  AD&D 2e Assistant ready to play!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
