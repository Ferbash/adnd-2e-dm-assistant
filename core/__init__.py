"""
Core - Módulos fundamentales del sistema AD&D 2e
"""

from .dados import DiceRoller
from .combate import CombatManager, MonsterDatabase, Combatant
from .biblio import RuleBook

__all__ = [
    'DiceRoller',
    'CombatManager',
    'MonsterDatabase',
    'Combatant',
    'RuleBook'
]
