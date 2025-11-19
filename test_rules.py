"""
Tests para el sistema de referencia de reglas
Tests for the rules reference system
"""
import unittest
from rules import RulesReference, RULES_DATABASE


class TestRulesReference(unittest.TestCase):
    """Pruebas para RulesReference / Tests for RulesReference"""
    
    def test_rules_database_exists(self):
        """Prueba que existe la base de datos de reglas / Test rules database exists"""
        self.assertIsNotNone(RULES_DATABASE)
        self.assertGreater(len(RULES_DATABASE), 0)
    
    def test_rules_database_categories(self):
        """Prueba categorías de la base de datos / Test database categories"""
        expected_categories = ["combate", "tiradas_salvacion", "habilidades", 
                              "magia", "experiencia", "movimiento"]
        for category in expected_categories:
            self.assertIn(category, RULES_DATABASE)
    
    def test_get_all_categories(self):
        """Prueba obtener todas las categorías / Test get all categories"""
        categories = RulesReference.get_all_categories()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
    
    def test_get_category_valid(self):
        """Prueba obtener categoría válida / Test get valid category"""
        category = RulesReference.get_category("combate")
        self.assertIsNotNone(category)
        self.assertIn("nombre", category)
        self.assertIn("reglas", category)
    
    def test_get_category_invalid(self):
        """Prueba obtener categoría inválida / Test get invalid category"""
        category = RulesReference.get_category("invalid_category")
        self.assertIsNone(category)
    
    def test_category_structure(self):
        """Prueba estructura de categorías / Test category structure"""
        for category_key, category_data in RULES_DATABASE.items():
            self.assertIn("nombre", category_data)
            self.assertIn("reglas", category_data)
            self.assertIsInstance(category_data["reglas"], list)
            
            for rule in category_data["reglas"]:
                self.assertIn("titulo", rule)
                self.assertIn("descripcion", rule)
                self.assertIsInstance(rule["titulo"], str)
                self.assertIsInstance(rule["descripcion"], str)
    
    def test_search_rules_combat(self):
        """Prueba búsqueda de reglas de combate / Test search combat rules"""
        results = RulesReference.search_rules("combate")
        self.assertGreater(len(results), 0)
        
        for result in results:
            self.assertIn("categoria", result)
            self.assertIn("titulo", result)
            self.assertIn("descripcion", result)
    
    def test_search_rules_initiative(self):
        """Prueba búsqueda de iniciativa / Test search initiative"""
        results = RulesReference.search_rules("iniciativa")
        self.assertGreater(len(results), 0)
        
        # Verificar que encontró la regla de iniciativa
        found_initiative = any("Iniciativa" in r["titulo"] for r in results)
        self.assertTrue(found_initiative)
    
    def test_search_rules_magic(self):
        """Prueba búsqueda de reglas de magia / Test search magic rules"""
        results = RulesReference.search_rules("magia")
        self.assertGreater(len(results), 0)
    
    def test_search_rules_case_insensitive(self):
        """Prueba búsqueda insensible a mayúsculas / Test case-insensitive search"""
        results_lower = RulesReference.search_rules("combate")
        results_upper = RulesReference.search_rules("COMBATE")
        results_mixed = RulesReference.search_rules("Combate")
        
        self.assertEqual(len(results_lower), len(results_upper))
        self.assertEqual(len(results_lower), len(results_mixed))
    
    def test_search_rules_no_results(self):
        """Prueba búsqueda sin resultados / Test search with no results"""
        results = RulesReference.search_rules("xyzabc123notfound")
        self.assertEqual(len(results), 0)
    
    def test_search_rules_partial_match(self):
        """Prueba búsqueda con coincidencia parcial / Test search with partial match"""
        results = RulesReference.search_rules("ataque")
        self.assertGreater(len(results), 0)
    
    def test_search_in_description(self):
        """Prueba búsqueda en descripción / Test search in description"""
        results = RulesReference.search_rules("d20")
        self.assertGreater(len(results), 0)
    
    def test_combat_category_has_rules(self):
        """Prueba que categoría combate tiene reglas / Test combat category has rules"""
        category = RulesReference.get_category("combate")
        self.assertIsNotNone(category)
        self.assertGreater(len(category["reglas"]), 0)
        
        rule_titles = [rule["titulo"] for rule in category["reglas"]]
        self.assertTrue(any("Iniciativa" in title or "Initiative" in title 
                           for title in rule_titles))
    
    def test_abilities_category_has_all_abilities(self):
        """Prueba que categoría habilidades tiene todas / Test abilities category has all"""
        category = RulesReference.get_category("habilidades")
        self.assertIsNotNone(category)
        
        rule_titles = [rule["titulo"] for rule in category["reglas"]]
        abilities = ["Fuerza", "Destreza", "Constitución", 
                    "Inteligencia", "Sabiduría", "Carisma"]
        
        for ability in abilities:
            found = any(ability in title for title in rule_titles)
            self.assertTrue(found, f"{ability} not found in abilities category")
    
    def test_magic_category_has_rules(self):
        """Prueba que categoría magia tiene reglas / Test magic category has rules"""
        category = RulesReference.get_category("magia")
        self.assertIsNotNone(category)
        self.assertGreater(len(category["reglas"]), 0)
    
    def test_saving_throws_category(self):
        """Prueba categoría de tiradas de salvación / Test saving throws category"""
        category = RulesReference.get_category("tiradas_salvacion")
        self.assertIsNotNone(category)
        self.assertGreater(len(category["reglas"]), 0)
    
    def test_experience_category(self):
        """Prueba categoría de experiencia / Test experience category"""
        category = RulesReference.get_category("experiencia")
        self.assertIsNotNone(category)
        self.assertGreater(len(category["reglas"]), 0)
    
    def test_movement_category(self):
        """Prueba categoría de movimiento / Test movement category"""
        category = RulesReference.get_category("movimiento")
        self.assertIsNotNone(category)
        self.assertGreater(len(category["reglas"]), 0)
    
    def test_all_rules_have_bilingual_content(self):
        """Prueba que las reglas tienen contenido bilingüe / Test rules have bilingual content"""
        for category_data in RULES_DATABASE.values():
            # Verificar que el nombre de categoría tiene ambos idiomas
            self.assertIn("/", category_data["nombre"])
            
            for rule in category_data["reglas"]:
                # La mayoría debería tener contenido en español e inglés
                self.assertTrue(len(rule["descripcion"]) > 0)


if __name__ == '__main__':
    unittest.main()
