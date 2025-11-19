"""
Sistema de creación de personajes para AD&D 2e
Character creation system for AD&D 2e
"""
from typing import Dict, List, Optional
from dice_roller import DiceRoller


# Razas disponibles / Available races
RACES = {
    "Humano": {
        "name": "Humano / Human",
        "ability_adjustments": {},
        "classes": ["Guerrero", "Mago", "Clérigo", "Ladrón", "Paladín", "Ranger", "Druida", "Bardo"]
    },
    "Elfo": {
        "name": "Elfo / Elf",
        "ability_adjustments": {"Destreza": 1, "Constitución": -1},
        "classes": ["Guerrero", "Mago", "Ladrón", "Ranger"]
    },
    "Enano": {
        "name": "Enano / Dwarf",
        "ability_adjustments": {"Constitución": 1, "Carisma": -1},
        "classes": ["Guerrero", "Clérigo", "Ladrón"]
    },
    "Halfling": {
        "name": "Halfling",
        "ability_adjustments": {"Destreza": 1, "Fuerza": -1},
        "classes": ["Guerrero", "Ladrón", "Clérigo"]
    },
    "Semielfo": {
        "name": "Semielfo / Half-Elf",
        "ability_adjustments": {},
        "classes": ["Guerrero", "Mago", "Clérigo", "Ladrón", "Ranger", "Druida", "Bardo"]
    }
}

# Clases de personaje / Character classes
CLASSES = {
    "Guerrero": {
        "name": "Guerrero / Fighter",
        "hit_die": 10,
        "prime_requisite": ["Fuerza"]
    },
    "Mago": {
        "name": "Mago / Wizard",
        "hit_die": 4,
        "prime_requisite": ["Inteligencia"]
    },
    "Clérigo": {
        "name": "Clérigo / Cleric",
        "hit_die": 8,
        "prime_requisite": ["Sabiduría"]
    },
    "Ladrón": {
        "name": "Ladrón / Thief",
        "hit_die": 6,
        "prime_requisite": ["Destreza"]
    },
    "Paladín": {
        "name": "Paladín / Paladin",
        "hit_die": 10,
        "prime_requisite": ["Fuerza", "Carisma"]
    },
    "Ranger": {
        "name": "Ranger",
        "hit_die": 10,
        "prime_requisite": ["Fuerza", "Destreza", "Sabiduría"]
    },
    "Druida": {
        "name": "Druida / Druid",
        "hit_die": 8,
        "prime_requisite": ["Sabiduría", "Carisma"]
    },
    "Bardo": {
        "name": "Bardo / Bard",
        "hit_die": 6,
        "prime_requisite": ["Destreza", "Carisma"]
    }
}


class Character:
    """Representa un personaje de AD&D 2e / Represents an AD&D 2e character"""
    
    def __init__(self, name: str, race: str, char_class: str, 
                 ability_scores: Optional[Dict[str, int]] = None):
        """
        Inicializa un nuevo personaje / Initialize a new character
        
        Args:
            name: Nombre del personaje / Character name
            race: Raza del personaje / Character race
            char_class: Clase del personaje / Character class
            ability_scores: Puntuaciones de habilidad opcionales / Optional ability scores
        """
        self.name = name
        self.race = race
        self.char_class = char_class
        self.level = 1
        
        # Puntuaciones de habilidad / Ability scores
        if ability_scores:
            self.abilities = ability_scores
        else:
            self.abilities = self._generate_abilities()
        
        # Aplicar ajustes raciales / Apply racial adjustments
        self._apply_racial_adjustments()
        
        # Puntos de golpe / Hit points
        self.max_hp = self._roll_hit_points()
        self.current_hp = self.max_hp
        
        # Recursos / Resources
        self.resources = {
            "Oro": 0,
            "Items": [],
            "Conjuros preparados": [] if char_class in ["Mago", "Clérigo", "Druida"] else None
        }
    
    def _generate_abilities(self) -> Dict[str, int]:
        """Genera puntuaciones de habilidad / Generate ability scores"""
        scores = DiceRoller.roll_ability_scores_4d6_drop_lowest()
        return {
            "Fuerza": scores[0],
            "Destreza": scores[1],
            "Constitución": scores[2],
            "Inteligencia": scores[3],
            "Sabiduría": scores[4],
            "Carisma": scores[5]
        }
    
    def _apply_racial_adjustments(self):
        """Aplica ajustes raciales a las habilidades / Apply racial adjustments to abilities"""
        if self.race in RACES:
            adjustments = RACES[self.race]["ability_adjustments"]
            for ability, adjustment in adjustments.items():
                if ability in self.abilities:
                    self.abilities[ability] += adjustment
    
    def _roll_hit_points(self) -> int:
        """Calcula puntos de golpe iniciales / Calculate initial hit points"""
        if self.char_class in CLASSES:
            hit_die = CLASSES[self.char_class]["hit_die"]
            # Primer nivel obtiene máximo / First level gets maximum
            base_hp = hit_die
            # Añadir bono de Constitución / Add Constitution bonus
            con_bonus = self.get_ability_modifier("Constitución")
            return max(1, base_hp + con_bonus)
        return 1
    
    def get_ability_modifier(self, ability: str) -> int:
        """
        Calcula el modificador de habilidad / Calculate ability modifier
        
        Args:
            ability: Nombre de la habilidad / Ability name
            
        Returns:
            Modificador de habilidad / Ability modifier
        """
        score = self.abilities.get(ability, 10)
        
        # Tabla de modificadores de AD&D 2e (simplificada)
        # AD&D 2e modifier table (simplified)
        if score <= 3:
            return -3
        elif score <= 5:
            return -2
        elif score <= 8:
            return -1
        elif score <= 12:
            return 0
        elif score <= 15:
            return 1
        elif score <= 17:
            return 2
        else:  # 18+
            return 3
    
    def modify_resource(self, resource_type: str, amount: int):
        """
        Modifica un recurso del personaje / Modify a character resource
        
        Args:
            resource_type: Tipo de recurso / Resource type
            amount: Cantidad a modificar / Amount to modify
        """
        if resource_type == "HP":
            self.current_hp = max(0, min(self.max_hp, self.current_hp + amount))
        elif resource_type == "Oro":
            self.resources["Oro"] = max(0, self.resources["Oro"] + amount)
    
    def add_item(self, item: str):
        """Añade un objeto al inventario / Add an item to inventory"""
        self.resources["Items"].append(item)
    
    def remove_item(self, item: str) -> bool:
        """
        Elimina un objeto del inventario / Remove an item from inventory
        
        Returns:
            True si se eliminó, False si no se encontró
            True if removed, False if not found
        """
        if item in self.resources["Items"]:
            self.resources["Items"].remove(item)
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convierte el personaje a diccionario / Convert character to dictionary"""
        return {
            "nombre": self.name,
            "raza": self.race,
            "clase": self.char_class,
            "nivel": self.level,
            "habilidades": self.abilities,
            "hp_actual": self.current_hp,
            "hp_maximo": self.max_hp,
            "recursos": self.resources
        }
    
    def __str__(self) -> str:
        """Representación en cadena del personaje / String representation of character"""
        lines = [
            f"=== {self.name} ===",
            f"Raza: {self.race} | Clase: {self.char_class} | Nivel: {self.level}",
            "",
            "Habilidades / Abilities:",
            f"  Fuerza (STR): {self.abilities['Fuerza']}",
            f"  Destreza (DEX): {self.abilities['Destreza']}",
            f"  Constitución (CON): {self.abilities['Constitución']}",
            f"  Inteligencia (INT): {self.abilities['Inteligencia']}",
            f"  Sabiduría (WIS): {self.abilities['Sabiduría']}",
            f"  Carisma (CHA): {self.abilities['Carisma']}",
            "",
            f"Puntos de Golpe / Hit Points: {self.current_hp}/{self.max_hp}",
            f"Oro / Gold: {self.resources['Oro']}",
            f"Items: {', '.join(self.resources['Items']) if self.resources['Items'] else 'Ninguno'}"
        ]
        return "\n".join(lines)


def create_character_interactive() -> Character:
    """
    Crea un personaje de forma interactiva / Create a character interactively
    
    Returns:
        Personaje creado / Created character
    """
    print("\n=== Creación de Personaje AD&D 2e ===")
    print("=== AD&D 2e Character Creation ===\n")
    
    # Nombre / Name
    name = input("Nombre del personaje / Character name: ").strip()
    if not name:
        name = "Aventurero"
    
    # Raza / Race
    print("\nRazas disponibles / Available races:")
    for i, (race_key, race_data) in enumerate(RACES.items(), 1):
        print(f"{i}. {race_data['name']}")
    
    while True:
        try:
            race_choice = int(input("\nSelecciona raza / Select race (número): "))
            if 1 <= race_choice <= len(RACES):
                race = list(RACES.keys())[race_choice - 1]
                break
            else:
                print("Opción inválida / Invalid option")
        except ValueError:
            print("Por favor ingresa un número / Please enter a number")
    
    # Clase / Class
    available_classes = RACES[race]["classes"]
    print(f"\nClases disponibles para {race} / Available classes for {race}:")
    for i, class_name in enumerate(available_classes, 1):
        class_data = CLASSES[class_name]
        print(f"{i}. {class_data['name']} (DG: d{class_data['hit_die']})")
    
    while True:
        try:
            class_choice = int(input("\nSelecciona clase / Select class (número): "))
            if 1 <= class_choice <= len(available_classes):
                char_class = available_classes[class_choice - 1]
                break
            else:
                print("Opción inválida / Invalid option")
        except ValueError:
            print("Por favor ingresa un número / Please enter a number")
    
    # Crear personaje / Create character
    print("\nGenerando puntuaciones de habilidad (4d6, descartando el más bajo)...")
    print("Generating ability scores (4d6, drop lowest)...")
    character = Character(name, race, char_class)
    
    print("\n¡Personaje creado! / Character created!")
    print(character)
    
    return character
