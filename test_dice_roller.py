"""
Tests para el sistema de tiradas de dados
Tests for the dice rolling system
"""
import unittest
from dice_roller import DiceRoller


class TestDiceRoller(unittest.TestCase):
    """Pruebas para DiceRoller / Tests for DiceRoller"""
    
    def test_basic_roll(self):
        """Prueba tirada básica / Test basic roll"""
        total, rolls = DiceRoller.roll(2, 6)
        self.assertEqual(len(rolls), 2)
        self.assertTrue(all(1 <= r <= 6 for r in rolls))
        self.assertEqual(total, sum(rolls))
    
    def test_roll_with_modifier(self):
        """Prueba tirada con modificador / Test roll with modifier"""
        total, rolls = DiceRoller.roll(1, 20, modifier=5)
        self.assertEqual(len(rolls), 1)
        self.assertTrue(1 <= rolls[0] <= 20)
        self.assertEqual(total, rolls[0] + 5)
    
    def test_roll_with_negative_modifier(self):
        """Prueba tirada con modificador negativo / Test roll with negative modifier"""
        total, rolls = DiceRoller.roll(1, 6, modifier=-2)
        self.assertEqual(total, rolls[0] - 2)
    
    def test_invalid_num_dice(self):
        """Prueba número de dados inválido / Test invalid number of dice"""
        with self.assertRaises(ValueError):
            DiceRoller.roll(0, 6)
        with self.assertRaises(ValueError):
            DiceRoller.roll(-1, 6)
    
    def test_invalid_dice_type(self):
        """Prueba tipo de dado inválido / Test invalid dice type"""
        with self.assertRaises(ValueError):
            DiceRoller.roll(1, 7)
        with self.assertRaises(ValueError):
            DiceRoller.roll(1, 3)
    
    def test_all_dice_types(self):
        """Prueba todos los tipos de dados / Test all dice types"""
        valid_dice = [4, 6, 8, 10, 12, 20, 100]
        for dice_type in valid_dice:
            total, rolls = DiceRoller.roll(1, dice_type)
            self.assertEqual(len(rolls), 1)
            self.assertTrue(1 <= rolls[0] <= dice_type)
    
    def test_ability_scores(self):
        """Prueba generación de puntuaciones de habilidad / Test ability score generation"""
        scores = DiceRoller.roll_ability_scores()
        self.assertEqual(len(scores), 6)
        for score in scores:
            self.assertTrue(3 <= score <= 18)
    
    def test_ability_scores_4d6_drop_lowest(self):
        """Prueba 4d6 descartando el más bajo / Test 4d6 drop lowest"""
        scores = DiceRoller.roll_ability_scores_4d6_drop_lowest()
        self.assertEqual(len(scores), 6)
        for score in scores:
            self.assertTrue(3 <= score <= 18)
    
    def test_parse_dice_notation_basic(self):
        """Prueba parseo de notación básica / Test basic notation parsing"""
        num, dtype, mod = DiceRoller.parse_dice_notation("2d6")
        self.assertEqual(num, 2)
        self.assertEqual(dtype, 6)
        self.assertEqual(mod, 0)
    
    def test_parse_dice_notation_with_positive_modifier(self):
        """Prueba parseo con modificador positivo / Test parsing with positive modifier"""
        num, dtype, mod = DiceRoller.parse_dice_notation("2d6+3")
        self.assertEqual(num, 2)
        self.assertEqual(dtype, 6)
        self.assertEqual(mod, 3)
    
    def test_parse_dice_notation_with_negative_modifier(self):
        """Prueba parseo con modificador negativo / Test parsing with negative modifier"""
        num, dtype, mod = DiceRoller.parse_dice_notation("1d20-2")
        self.assertEqual(num, 1)
        self.assertEqual(dtype, 20)
        self.assertEqual(mod, -2)
    
    def test_parse_dice_notation_single_die(self):
        """Prueba parseo de un solo dado / Test parsing single die"""
        num, dtype, mod = DiceRoller.parse_dice_notation("d20")
        self.assertEqual(num, 1)
        self.assertEqual(dtype, 20)
        self.assertEqual(mod, 0)
    
    def test_parse_dice_notation_case_insensitive(self):
        """Prueba parseo insensible a mayúsculas / Test case-insensitive parsing"""
        num1, dtype1, mod1 = DiceRoller.parse_dice_notation("2D6")
        num2, dtype2, mod2 = DiceRoller.parse_dice_notation("2d6")
        self.assertEqual((num1, dtype1, mod1), (num2, dtype2, mod2))
    
    def test_parse_dice_notation_with_spaces(self):
        """Prueba parseo con espacios / Test parsing with spaces"""
        num, dtype, mod = DiceRoller.parse_dice_notation(" 2d6+3 ")
        self.assertEqual(num, 2)
        self.assertEqual(dtype, 6)
        self.assertEqual(mod, 3)
    
    def test_parse_dice_notation_invalid(self):
        """Prueba parseo de notación inválida / Test parsing invalid notation"""
        with self.assertRaises(ValueError):
            DiceRoller.parse_dice_notation("invalid")
        with self.assertRaises(ValueError):
            DiceRoller.parse_dice_notation("2x6")
    
    def test_roll_from_notation(self):
        """Prueba tirada desde notación / Test roll from notation"""
        total, rolls = DiceRoller.roll_from_notation("2d6+3")
        self.assertEqual(len(rolls), 2)
        self.assertTrue(all(1 <= r <= 6 for r in rolls))
        self.assertEqual(total, sum(rolls) + 3)
    
    def test_roll_from_notation_d20(self):
        """Prueba tirada de d20 desde notación / Test d20 roll from notation"""
        total, rolls = DiceRoller.roll_from_notation("1d20")
        self.assertEqual(len(rolls), 1)
        self.assertTrue(1 <= rolls[0] <= 20)
        self.assertEqual(total, rolls[0])
    
    def test_multiple_rolls_consistency(self):
        """Prueba consistencia de múltiples tiradas / Test consistency of multiple rolls"""
        for _ in range(100):
            total, rolls = DiceRoller.roll(3, 6)
            self.assertEqual(len(rolls), 3)
            self.assertEqual(total, sum(rolls))
            self.assertTrue(all(1 <= r <= 6 for r in rolls))


if __name__ == '__main__':
    unittest.main()
