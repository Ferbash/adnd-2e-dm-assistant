#!/usr/bin/env python3
"""
Asistente para Dungeon Master de AD&D 2e
AD&D 2e Dungeon Master Assistant

Un completo asistente que permite:
- Consultar reglas
- Crear personajes
- Hacer tiradas de dados
- Gestionar recursos

A complete assistant that allows:
- Query rules
- Create characters
- Make dice rolls
- Manage resources
"""
import sys
from typing import List, Optional
from dice_roller import DiceRoller
from character import Character, create_character_interactive, RACES, CLASSES
from rules import RulesReference


class DMAssistant:
    """Asistente principal del DM / Main DM Assistant"""
    
    def __init__(self):
        self.characters: List[Character] = []
        self.active_character: Optional[Character] = None
    
    def show_menu(self):
        """Muestra el menú principal / Show main menu"""
        print("\n" + "="*60)
        print("  ASISTENTE DE DUNGEON MASTER AD&D 2e")
        print("  AD&D 2e DUNGEON MASTER ASSISTANT")
        print("="*60)
        print("\n1. Consultar Reglas / Query Rules")
        print("2. Crear Personaje / Create Character")
        print("3. Ver Personajes / View Characters")
        print("4. Gestionar Personaje / Manage Character")
        print("5. Hacer Tirada de Dados / Make Dice Roll")
        print("6. Búsqueda de Reglas / Search Rules")
        print("7. Ver Todas las Reglas / View All Rules")
        print("0. Salir / Exit")
        print()
    
    def handle_rules_query(self):
        """Maneja consultas de reglas / Handle rule queries"""
        print("\n=== CATEGORÍAS DE REGLAS / RULE CATEGORIES ===\n")
        categories = {
            "1": ("combate", "Combate / Combat"),
            "2": ("tiradas_salvacion", "Tiradas de Salvación / Saving Throws"),
            "3": ("habilidades", "Habilidades / Abilities"),
            "4": ("magia", "Magia / Magic"),
            "5": ("experiencia", "Experiencia / Experience"),
            "6": ("movimiento", "Movimiento / Movement")
        }
        
        for key, (_, name) in categories.items():
            print(f"{key}. {name}")
        
        choice = input("\nSelecciona categoría (0 para volver): ").strip()
        
        if choice == "0":
            return
        
        if choice in categories:
            category_key, _ = categories[choice]
            RulesReference.display_category(category_key)
            input("\nPresiona Enter para continuar...")
        else:
            print("Opción inválida / Invalid option")
    
    def handle_character_creation(self):
        """Maneja la creación de personajes / Handle character creation"""
        character = create_character_interactive()
        self.characters.append(character)
        
        if not self.active_character:
            self.active_character = character
            print(f"\n{character.name} es ahora el personaje activo / is now the active character")
        
        input("\nPresiona Enter para continuar...")
    
    def handle_view_characters(self):
        """Muestra todos los personajes / Display all characters"""
        if not self.characters:
            print("\nNo hay personajes creados / No characters created")
            input("\nPresiona Enter para continuar...")
            return
        
        print("\n=== PERSONAJES / CHARACTERS ===\n")
        for i, char in enumerate(self.characters, 1):
            active = " [ACTIVO/ACTIVE]" if char == self.active_character else ""
            print(f"{i}. {char.name} - {char.race} {char.char_class} (Nivel {char.level}){active}")
        
        print("\n0. Ver detalles de un personaje / View character details")
        print("1. Cambiar personaje activo / Change active character")
        
        choice = input("\nSelecciona opción (Enter para volver): ").strip()
        
        if choice == "0":
            char_num = input("Número de personaje / Character number: ").strip()
            try:
                idx = int(char_num) - 1
                if 0 <= idx < len(self.characters):
                    print("\n" + str(self.characters[idx]))
                else:
                    print("Número inválido / Invalid number")
            except ValueError:
                print("Entrada inválida / Invalid input")
            input("\nPresiona Enter para continuar...")
        elif choice == "1":
            char_num = input("Número de personaje / Character number: ").strip()
            try:
                idx = int(char_num) - 1
                if 0 <= idx < len(self.characters):
                    self.active_character = self.characters[idx]
                    print(f"\n{self.active_character.name} es ahora el personaje activo / is now the active character")
                else:
                    print("Número inválido / Invalid number")
            except ValueError:
                print("Entrada inválida / Invalid input")
            input("\nPresiona Enter para continuar...")
    
    def handle_character_management(self):
        """Gestiona recursos de personajes / Manage character resources"""
        if not self.active_character:
            print("\nNo hay personaje activo. Crea o selecciona un personaje primero.")
            print("No active character. Create or select a character first.")
            input("\nPresiona Enter para continuar...")
            return
        
        char = self.active_character
        
        print(f"\n=== Gestionando: {char.name} ===")
        print(f"HP: {char.current_hp}/{char.max_hp}")
        print(f"Oro / Gold: {char.resources['Oro']}")
        print(f"Items: {len(char.resources['Items'])}")
        
        print("\n1. Modificar HP")
        print("2. Modificar Oro / Gold")
        print("3. Añadir Item / Add Item")
        print("4. Eliminar Item / Remove Item")
        print("5. Ver Items / View Items")
        print("0. Volver / Back")
        
        choice = input("\nSelecciona opción: ").strip()
        
        if choice == "1":
            try:
                amount = int(input("Cantidad de HP (+/-): "))
                char.modify_resource("HP", amount)
                print(f"HP actualizado: {char.current_hp}/{char.max_hp}")
            except ValueError:
                print("Cantidad inválida / Invalid amount")
        
        elif choice == "2":
            try:
                amount = int(input("Cantidad de Oro (+/-): "))
                char.modify_resource("Oro", amount)
                print(f"Oro actualizado / Gold updated: {char.resources['Oro']}")
            except ValueError:
                print("Cantidad inválida / Invalid amount")
        
        elif choice == "3":
            item = input("Nombre del item: ").strip()
            if item:
                char.add_item(item)
                print(f"Item '{item}' añadido / added")
        
        elif choice == "4":
            item = input("Nombre del item: ").strip()
            if char.remove_item(item):
                print(f"Item '{item}' eliminado / removed")
            else:
                print(f"Item '{item}' no encontrado / not found")
        
        elif choice == "5":
            if char.resources['Items']:
                print("\nItems:")
                for i, item in enumerate(char.resources['Items'], 1):
                    print(f"{i}. {item}")
            else:
                print("\nNo hay items / No items")
        
        input("\nPresiona Enter para continuar...")
    
    def handle_dice_roll(self):
        """Maneja tiradas de dados / Handle dice rolls"""
        print("\n=== TIRADA DE DADOS / DICE ROLL ===")
        print("\nFormatos válidos / Valid formats:")
        print("  - NdX (ej/e.g.: 2d6, 1d20)")
        print("  - NdX+M (ej/e.g.: 2d6+3)")
        print("  - NdX-M (ej/e.g.: 1d20-2)")
        print("\nTipos de dados / Dice types: d4, d6, d8, d10, d12, d20, d100")
        
        notation = input("\nNotación de dados (o Enter para volver): ").strip()
        
        if not notation:
            return
        
        try:
            total, rolls = DiceRoller.roll_from_notation(notation)
            print(f"\n{notation}:")
            print(f"Tiradas individuales / Individual rolls: {rolls}")
            print(f"Resultado total / Total result: {total}")
        except (ValueError, IndexError) as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def handle_search_rules(self):
        """Maneja búsqueda de reglas / Handle rules search"""
        RulesReference.interactive_search()
    
    def handle_view_all_rules(self):
        """Muestra todas las reglas / Display all rules"""
        RulesReference.display_all_rules()
        input("\nPresiona Enter para continuar...")
    
    def run(self):
        """Ejecuta el asistente / Run the assistant"""
        print("\n¡Bienvenido al Asistente de DM de AD&D 2e!")
        print("Welcome to the AD&D 2e DM Assistant!")
        
        while True:
            self.show_menu()
            choice = input("Selecciona opción / Select option: ").strip()
            
            if choice == "0":
                print("\n¡Hasta luego! / Goodbye!")
                break
            elif choice == "1":
                self.handle_rules_query()
            elif choice == "2":
                self.handle_character_creation()
            elif choice == "3":
                self.handle_view_characters()
            elif choice == "4":
                self.handle_character_management()
            elif choice == "5":
                self.handle_dice_roll()
            elif choice == "6":
                self.handle_search_rules()
            elif choice == "7":
                self.handle_view_all_rules()
            else:
                print("\nOpción inválida / Invalid option")
                input("Presiona Enter para continuar...")


def main():
    """Punto de entrada principal / Main entry point"""
    assistant = DMAssistant()
    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego! / Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
