"""
Sistema de tiradas de dados para AD&D 2e
Dice rolling system for AD&D 2e
"""
import random
from typing import List, Tuple


class DiceRoller:
    """Manejador de tiradas de dados / Dice roller handler"""
    
    @staticmethod
    def roll(num_dice: int, dice_type: int, modifier: int = 0) -> Tuple[int, List[int]]:
        """
        Realiza una tirada de dados / Perform a dice roll
        
        Args:
            num_dice: Número de dados / Number of dice
            dice_type: Tipo de dado (4, 6, 8, 10, 12, 20, 100) / Dice type
            modifier: Modificador a aplicar / Modifier to apply
            
        Returns:
            Tuple con (resultado total, lista de tiradas individuales)
            Tuple with (total result, list of individual rolls)
        """
        if num_dice <= 0:
            raise ValueError("El número de dados debe ser positivo / Number of dice must be positive")
        
        if dice_type not in [4, 6, 8, 10, 12, 20, 100]:
            raise ValueError("Tipo de dado no válido / Invalid dice type")
        
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return total, rolls
    
    @staticmethod
    def roll_ability_scores() -> List[int]:
        """
        Genera puntuaciones de habilidad usando el método 3d6
        Generate ability scores using 3d6 method
        
        Returns:
            Lista de 6 puntuaciones / List of 6 scores
        """
        scores = []
        for _ in range(6):
            total, _ = DiceRoller.roll(3, 6)
            scores.append(total)
        return scores
    
    @staticmethod
    def roll_ability_scores_4d6_drop_lowest() -> List[int]:
        """
        Genera puntuaciones de habilidad usando 4d6, descartando el más bajo
        Generate ability scores using 4d6, drop lowest
        
        Returns:
            Lista de 6 puntuaciones / List of 6 scores
        """
        scores = []
        for _ in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort()
            total = sum(rolls[1:])  # Descartar el más bajo / Drop lowest
            scores.append(total)
        return scores
    
    @staticmethod
    def parse_dice_notation(notation: str) -> Tuple[int, int, int]:
        """
        Analiza notación de dados estándar (ej: "2d6+3", "1d20")
        Parse standard dice notation (e.g., "2d6+3", "1d20")
        
        Args:
            notation: Notación de dados / Dice notation
            
        Returns:
            Tuple con (num_dados, tipo_dado, modificador)
            Tuple with (num_dice, dice_type, modifier)
        """
        notation = notation.lower().strip()
        modifier = 0
        
        # Manejar modificadores / Handle modifiers
        if '+' in notation:
            parts = notation.split('+')
            notation = parts[0]
            modifier = int(parts[1])
        elif '-' in notation and notation.count('-') == 1:
            parts = notation.split('-')
            notation = parts[0]
            modifier = -int(parts[1])
        
        # Parsear dados / Parse dice
        if 'd' not in notation:
            raise ValueError("Formato inválido. Use NdX+M (ej: 2d6+3) / Invalid format. Use NdX+M (e.g., 2d6+3)")
        
        dice_parts = notation.split('d')
        num_dice = int(dice_parts[0]) if dice_parts[0] else 1
        dice_type = int(dice_parts[1])
        
        return num_dice, dice_type, modifier
    
    @staticmethod
    def roll_from_notation(notation: str) -> Tuple[int, List[int]]:
        """
        Realiza una tirada desde notación estándar
        Perform a roll from standard notation
        
        Args:
            notation: Notación de dados (ej: "2d6+3") / Dice notation (e.g., "2d6+3")
            
        Returns:
            Tuple con (resultado total, lista de tiradas)
            Tuple with (total result, list of rolls)
        """
        num_dice, dice_type, modifier = DiceRoller.parse_dice_notation(notation)
        return DiceRoller.roll(num_dice, dice_type, modifier)
