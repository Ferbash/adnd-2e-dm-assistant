"""
🎲 AD&D 2e Character Creator - Launcher
Creador de personajes
"""

import sys
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.character_creator import main

if __name__ == "__main__":
    main()
