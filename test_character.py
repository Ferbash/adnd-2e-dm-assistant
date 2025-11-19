"""
Tests para el sistema de creación de personajes
Tests for the character creation system
"""
import unittest
from character import Character, RACES, CLASSES


class TestCharacter(unittest.TestCase):
    """Pruebas para Character / Tests for Character"""
    
    def test_character_creation_basic(self):
        """Prueba creación básica de personaje / Test basic character creation"""
        char = Character("Thorin", "Enano", "Guerrero")
        self.assertEqual(char.name, "Thorin")
        self.assertEqual(char.race, "Enano")
        self.assertEqual(char.char_class, "Guerrero")
        self.assertEqual(char.level, 1)
    
    def test_character_has_abilities(self):
        """Prueba que el personaje tiene habilidades / Test character has abilities"""
        char = Character("Test", "Humano", "Guerrero")
        required_abilities = ["Fuerza", "Destreza", "Constitución", 
                             "Inteligencia", "Sabiduría", "Carisma"]
        for ability in required_abilities:
            self.assertIn(ability, char.abilities)
            self.assertTrue(3 <= char.abilities[ability] <= 18)
    
    def test_character_with_custom_abilities(self):
        """Prueba personaje con habilidades personalizadas / Test character with custom abilities"""
        abilities = {
            "Fuerza": 18,
            "Destreza": 16,
            "Constitución": 14,
            "Inteligencia": 12,
            "Sabiduría": 10,
            "Carisma": 8
        }
        char = Character("Custom", "Humano", "Guerrero", ability_scores=abilities)
        for ability, value in abilities.items():
            self.assertEqual(char.abilities[ability], value)
    
    def test_racial_adjustments_dwarf(self):
        """Prueba ajustes raciales de enano / Test dwarf racial adjustments"""
        abilities = {
            "Fuerza": 10,
            "Destreza": 10,
            "Constitución": 10,
            "Inteligencia": 10,
            "Sabiduría": 10,
            "Carisma": 10
        }
        char = Character("Dwarf", "Enano", "Guerrero", ability_scores=abilities)
        # Enano: +1 CON, -1 CHA
        self.assertEqual(char.abilities["Constitución"], 11)
        self.assertEqual(char.abilities["Carisma"], 9)
    
    def test_racial_adjustments_elf(self):
        """Prueba ajustes raciales de elfo / Test elf racial adjustments"""
        abilities = {
            "Fuerza": 10,
            "Destreza": 10,
            "Constitución": 10,
            "Inteligencia": 10,
            "Sabiduría": 10,
            "Carisma": 10
        }
        char = Character("Elf", "Elfo", "Guerrero", ability_scores=abilities)
        # Elfo: +1 DEX, -1 CON
        self.assertEqual(char.abilities["Destreza"], 11)
        self.assertEqual(char.abilities["Constitución"], 9)
    
    def test_racial_adjustments_halfling(self):
        """Prueba ajustes raciales de halfling / Test halfling racial adjustments"""
        abilities = {
            "Fuerza": 10,
            "Destreza": 10,
            "Constitución": 10,
            "Inteligencia": 10,
            "Sabiduría": 10,
            "Carisma": 10
        }
        char = Character("Hobbit", "Halfling", "Ladrón", ability_scores=abilities)
        # Halfling: +1 DEX, -1 STR
        self.assertEqual(char.abilities["Destreza"], 11)
        self.assertEqual(char.abilities["Fuerza"], 9)
    
    def test_hit_points_fighter(self):
        """Prueba puntos de golpe de guerrero / Test fighter hit points"""
        char = Character("Fighter", "Humano", "Guerrero")
        # Guerrero tiene d10, nivel 1 obtiene máximo
        self.assertGreaterEqual(char.max_hp, 1)
        self.assertEqual(char.current_hp, char.max_hp)
    
    def test_hit_points_wizard(self):
        """Prueba puntos de golpe de mago / Test wizard hit points"""
        char = Character("Wizard", "Humano", "Mago")
        # Mago tiene d4
        self.assertGreaterEqual(char.max_hp, 1)
        self.assertEqual(char.current_hp, char.max_hp)
    
    def test_ability_modifier_low(self):
        """Prueba modificador de habilidad baja / Test low ability modifier"""
        char = Character("Test", "Humano", "Guerrero")
        # 3 o menos = -3
        self.assertEqual(self.get_ability_modifier_for_score(3), -3)
        # 4-5 = -2
        self.assertEqual(self.get_ability_modifier_for_score(5), -2)
        # 6-8 = -1
        self.assertEqual(self.get_ability_modifier_for_score(8), -1)
    
    def test_ability_modifier_average(self):
        """Prueba modificador de habilidad promedio / Test average ability modifier"""
        char = Character("Test", "Humano", "Guerrero")
        # 9-12 = 0
        self.assertEqual(self.get_ability_modifier_for_score(10), 0)
        self.assertEqual(self.get_ability_modifier_for_score(12), 0)
    
    def test_ability_modifier_high(self):
        """Prueba modificador de habilidad alta / Test high ability modifier"""
        char = Character("Test", "Humano", "Guerrero")
        # 13-15 = +1
        self.assertEqual(self.get_ability_modifier_for_score(15), 1)
        # 16-17 = +2
        self.assertEqual(self.get_ability_modifier_for_score(17), 2)
        # 18+ = +3
        self.assertEqual(self.get_ability_modifier_for_score(18), 3)
    
    def get_ability_modifier_for_score(self, score):
        """Helper para probar modificadores / Helper to test modifiers"""
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
        else:
            return 3
    
    def test_modify_hp(self):
        """Prueba modificación de HP / Test HP modification"""
        char = Character("Test", "Humano", "Guerrero")
        initial_hp = char.current_hp
        
        # Restar HP / Subtract HP
        char.modify_resource("HP", -5)
        self.assertEqual(char.current_hp, initial_hp - 5)
        
        # Añadir HP / Add HP
        char.modify_resource("HP", 3)
        self.assertEqual(char.current_hp, initial_hp - 2)
        
        # No puede exceder máximo / Cannot exceed max
        char.modify_resource("HP", 100)
        self.assertEqual(char.current_hp, char.max_hp)
        
        # No puede ser negativo / Cannot be negative
        char.modify_resource("HP", -1000)
        self.assertEqual(char.current_hp, 0)
    
    def test_modify_gold(self):
        """Prueba modificación de oro / Test gold modification"""
        char = Character("Test", "Humano", "Guerrero")
        
        # Añadir oro / Add gold
        char.modify_resource("Oro", 100)
        self.assertEqual(char.resources["Oro"], 100)
        
        # Restar oro / Subtract gold
        char.modify_resource("Oro", -30)
        self.assertEqual(char.resources["Oro"], 70)
        
        # No puede ser negativo / Cannot be negative
        char.modify_resource("Oro", -100)
        self.assertEqual(char.resources["Oro"], 0)
    
    def test_add_item(self):
        """Prueba añadir objeto / Test add item"""
        char = Character("Test", "Humano", "Guerrero")
        self.assertEqual(len(char.resources["Items"]), 0)
        
        char.add_item("Espada larga")
        self.assertEqual(len(char.resources["Items"]), 1)
        self.assertIn("Espada larga", char.resources["Items"])
        
        char.add_item("Poción de curación")
        self.assertEqual(len(char.resources["Items"]), 2)
    
    def test_remove_item(self):
        """Prueba eliminar objeto / Test remove item"""
        char = Character("Test", "Humano", "Guerrero")
        char.add_item("Espada")
        char.add_item("Escudo")
        
        # Eliminar objeto existente / Remove existing item
        result = char.remove_item("Espada")
        self.assertTrue(result)
        self.assertNotIn("Espada", char.resources["Items"])
        self.assertEqual(len(char.resources["Items"]), 1)
        
        # Intentar eliminar objeto no existente / Try to remove non-existent item
        result = char.remove_item("Espada")
        self.assertFalse(result)
        self.assertEqual(len(char.resources["Items"]), 1)
    
    def test_to_dict(self):
        """Prueba conversión a diccionario / Test conversion to dictionary"""
        char = Character("Test", "Humano", "Guerrero")
        char_dict = char.to_dict()
        
        self.assertEqual(char_dict["nombre"], "Test")
        self.assertEqual(char_dict["raza"], "Humano")
        self.assertEqual(char_dict["clase"], "Guerrero")
        self.assertEqual(char_dict["nivel"], 1)
        self.assertIn("habilidades", char_dict)
        self.assertIn("hp_actual", char_dict)
        self.assertIn("hp_maximo", char_dict)
        self.assertIn("recursos", char_dict)
    
    def test_str_representation(self):
        """Prueba representación en cadena / Test string representation"""
        char = Character("Gandalf", "Humano", "Mago")
        char_str = str(char)
        
        self.assertIn("Gandalf", char_str)
        self.assertIn("Humano", char_str)
        self.assertIn("Mago", char_str)
        self.assertIn("Fuerza", char_str)
        self.assertIn("Hit Points", char_str)
    
    def test_races_database(self):
        """Prueba base de datos de razas / Test races database"""
        self.assertIn("Humano", RACES)
        self.assertIn("Elfo", RACES)
        self.assertIn("Enano", RACES)
        self.assertIn("Halfling", RACES)
        
        for race_data in RACES.values():
            self.assertIn("name", race_data)
            self.assertIn("ability_adjustments", race_data)
            self.assertIn("classes", race_data)
    
    def test_classes_database(self):
        """Prueba base de datos de clases / Test classes database"""
        self.assertIn("Guerrero", CLASSES)
        self.assertIn("Mago", CLASSES)
        self.assertIn("Clérigo", CLASSES)
        self.assertIn("Ladrón", CLASSES)
        
        for class_data in CLASSES.values():
            self.assertIn("name", class_data)
            self.assertIn("hit_die", class_data)
            self.assertIn("prime_requisite", class_data)


if __name__ == '__main__':
    unittest.main()
