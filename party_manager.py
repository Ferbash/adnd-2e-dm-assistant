"""
🎲 AD&D 2e Party Manager - Launcher (Consola)
Gestor de grupo de personajes
"""

import sys
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interfaces.party_manager_console import main

if __name__ == "__main__":
    main()
