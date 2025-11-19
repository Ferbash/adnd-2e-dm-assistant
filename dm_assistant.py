"""
🎲 AD&D 2e Dungeon Master Assistant - Launcher
Punto de entrada principal del sistema
"""

import sys
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interfaces.dm_assistant import main

if __name__ == "__main__":
    main()
