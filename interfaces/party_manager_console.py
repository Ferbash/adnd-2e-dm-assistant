"""
Party Manager - Sistema de gestión de grupo estilo RPG clásico (Consola)
Maneja hasta 5 personajes con interfaz tipo Final Fantasy en terminal
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Colors:
    """Colores ANSI para terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colores de texto
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Colores brillantes
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Fondos
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class PartyManagerConsole:
    """Gestor de party en consola"""
    
    def __init__(self):
        self.party: List[Optional[Dict]] = [None] * 5
        self.character_files: List[Optional[Path]] = [None] * 5
        self.selected_index: Optional[int] = None
        
        # Habilitar colores en Windows
        if sys.platform == 'win32':
            os.system('color')
    
    def clear_screen(self):
        """Limpiar pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Imprimir header del programa"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═' * 80}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'⚔ PARTY MANAGER - AD&D 2e ⚔':^80}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═' * 80}{Colors.RESET}\n")
    
    def print_party_grid(self):
        """Imprimir grid de personajes (4 visibles en cuadrícula)"""
        print(f"{Colors.YELLOW}{Colors.BOLD}╔════════════════════════════════════╦════════════════════════════════════╗{Colors.RESET}")
        
        # Primera fila (pos 0 y 1)
        for i in range(0, 2):
            if i == 0:
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}", end="")
            self._print_character_card(i)
            print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}", end="")
            if i == 1:
                print()
        
        print(f"{Colors.YELLOW}{Colors.BOLD}╠════════════════════════════════════╬════════════════════════════════════╣{Colors.RESET}")
        
        # Segunda fila (pos 2 y 3)
        for i in range(2, 4):
            if i == 2:
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}", end="")
            self._print_character_card(i)
            print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}", end="")
            if i == 3:
                print()
        
        print(f"{Colors.YELLOW}{Colors.BOLD}╚════════════════════════════════════╩════════════════════════════════════╝{Colors.RESET}")
        
        # Quinta posición (centrada abajo)
        print(f"\n{Colors.YELLOW}{Colors.BOLD}{'╔════════════════════════════════════╗':^80}{Colors.RESET}")
        print(f"{Colors.YELLOW}{Colors.BOLD}{'║':^42}{Colors.RESET}", end="")
        self._print_character_card(4)
        print(f"{Colors.YELLOW}{Colors.BOLD}{'║':^38}{Colors.RESET}")
        print(f"{Colors.YELLOW}{Colors.BOLD}{'╚════════════════════════════════════╝':^80}{Colors.RESET}\n")
    
    def _print_character_card(self, index: int):
        """Imprimir tarjeta de personaje"""
        char = self.party[index]
        is_selected = index == self.selected_index
        
        if char is None:
            # Tarjeta vacía
            slot_text = f" [{index + 1}] VACÍO "
            if is_selected:
                print(f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}{slot_text:^34}{Colors.RESET}", end="")
            else:
                print(f"{Colors.BRIGHT_BLACK}{slot_text:^34}{Colors.RESET}", end="")
        else:
            # Tarjeta con personaje
            name = char['name'][:16].upper()
            char_class = char['class'][:12]
            level = char['level']
            
            hp = char.get('hp', {})
            hp_current = hp.get('current', 0) if isinstance(hp, dict) else hp
            hp_max = hp.get('max', 0) if isinstance(hp, dict) else hp
            hp_percent = (hp_current / hp_max * 100) if hp_max > 0 else 0
            
            # Color de HP
            if hp_percent > 50:
                hp_color = Colors.GREEN
            elif hp_percent > 25:
                hp_color = Colors.YELLOW
            else:
                hp_color = Colors.RED
            
            ac = char.get('ac', 10)
            equipped = char.get('equipped', {})
            weapon = equipped.get('arma_principal', 'Desarmado')[:12]
            
            # Construir líneas
            line1 = f" [{index + 1}] {name}"
            line2 = f" {char_class} Nv.{level}"
            line3 = f" HP {hp_current}/{hp_max} | AC {ac}"
            line4 = f" ⚔ {weapon}"
            
            if is_selected:
                print(f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}{line1:^34}{Colors.RESET}")
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}{Colors.BG_RED}{Colors.WHITE}{line2:^34}{Colors.RESET}{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}")
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}{Colors.BG_RED}{hp_color}{Colors.BOLD}{line3:^34}{Colors.RESET}{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}")
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}{Colors.BG_RED}{Colors.WHITE}{line4:^34}{Colors.RESET}", end="")
            else:
                print(f"{Colors.CYAN}{Colors.BOLD}{line1:^34}{Colors.RESET}")
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}{Colors.WHITE}{line2:^34}{Colors.RESET}{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}")
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}{hp_color}{Colors.BOLD}{line3:^34}{Colors.RESET}{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}")
                print(f"{Colors.YELLOW}{Colors.BOLD}║{Colors.RESET}{Colors.BRIGHT_BLACK}{line4:^34}{Colors.RESET}", end="")
    
    def print_menu(self):
        """Imprimir menú principal"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}╔══════════════════════════ MENÚ ══════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.GREEN}1-5{Colors.RESET} Seleccionar personaje  {Colors.GREEN}L{Colors.RESET} Cargar personaje      {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.GREEN}V{Colors.RESET}   Ver detalles          {Colors.GREEN}E{Colors.RESET} Editar HP/XP           {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.GREEN}R{Colors.RESET}   Remover personaje     {Colors.GREEN}G{Colors.RESET} Guardar cambios        {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.GREEN}X{Colors.RESET}   Exportar party        {Colors.GREEN}I{Colors.RESET} Importar party         {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.GREEN}Q{Colors.RESET}   Salir                                                {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    
    def show_character_details(self):
        """Mostrar detalles del personaje seleccionado"""
        if self.selected_index is None or self.party[self.selected_index] is None:
            print(f"{Colors.RED}No hay personaje seleccionado{Colors.RESET}")
            return
        
        char = self.party[self.selected_index]
        
        self.clear_screen()
        self.print_header()
        
        print(f"{Colors.CYAN}{Colors.BOLD}╔════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}{Colors.YELLOW}{Colors.BOLD}{char['name'].upper():^76}{Colors.RESET}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╠════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        # Clase, raza, nivel
        info = f"{char['race']} - {char['class']} - Nivel {char['level']} - {char.get('alignment', 'N/A')}"
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {info:74} {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╠════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        # Estadísticas
        hp = char.get('hp', {})
        hp_current = hp.get('current', 0) if isinstance(hp, dict) else hp
        hp_max = hp.get('max', 0) if isinstance(hp, dict) else hp
        
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.GREEN}{Colors.BOLD}HP:{Colors.RESET} {hp_current}/{hp_max:20}  {Colors.BLUE}{Colors.BOLD}AC:{Colors.RESET} {char.get('ac', 10):5}  {Colors.RED}{Colors.BOLD}THAC0:{Colors.RESET} {char.get('thac0', 20):20} {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.YELLOW}{Colors.BOLD}XP:{Colors.RESET} {char.get('experience', 0):,}{' ' * 60}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}"[:80])
        print(f"{Colors.CYAN}{Colors.BOLD}╠════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        # Atributos
        abilities = char.get('abilities', {})
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.BOLD}ATRIBUTOS:{Colors.RESET}{' ' * 64}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        
        ability_names = [
            ('strength', 'FUE'),
            ('dexterity', 'DES'),
            ('constitution', 'CON'),
            ('intelligence', 'INT'),
            ('wisdom', 'SAB'),
            ('charisma', 'CAR')
        ]
        
        for i in range(0, 6, 3):
            line = f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} "
            for j in range(3):
                if i + j < len(ability_names):
                    ability, abbr = ability_names[i + j]
                    value = abilities.get(ability, 10)
                    line += f"{Colors.BRIGHT_CYAN}{abbr}:{Colors.RESET} {value:2}  "
            line += " " * (76 - len(line.replace(Colors.CYAN, '').replace(Colors.BOLD, '').replace(Colors.RESET, '').replace(Colors.BRIGHT_CYAN, '')))
            print(f"{line}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        
        print(f"{Colors.CYAN}{Colors.BOLD}╠════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        # Equipo
        equipped = char.get('equipped', {})
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.BOLD}EQUIPO:{Colors.RESET}{' ' * 67}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}   ⚔ Arma: {equipped.get('arma_principal', 'Ninguna'):60} {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}   🛡 Armadura: {equipped.get('armadura', 'Ninguna'):56} {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}   🛡 Escudo: {equipped.get('escudo', 'Ninguno'):58} {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        
        # Inventario
        equipment = char.get('equipment', {})
        items = [item for item in equipment.keys() if item not in equipped.values()]
        print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}   📦 Inventario: {len(items)} items{' ' * 52}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        
        print(f"{Colors.CYAN}{Colors.BOLD}╠════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        # Conjuros
        spells = char.get('spells', {})
        if spells:
            print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.BOLD}CONJUROS:{Colors.RESET}{' ' * 65}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
            for level in sorted(spells.keys()):
                spell_list = spells[level]
                if spell_list:
                    print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}   {Colors.MAGENTA}Nivel {level}:{Colors.RESET} {len(spell_list)} conjuros{' ' * 50}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}╠════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        # Tiradas de salvación
        saves = char.get('saving_throws', {})
        if saves:
            print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.BOLD}TIRADAS DE SALVACIÓN:{Colors.RESET}{' ' * 53}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
            for save_type, value in saves.items():
                print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}   {save_type}: {value}{' ' * (70 - len(save_type) - len(str(value)))}{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
        
        print(f"{Colors.CYAN}{Colors.BOLD}╚════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}")
        
        input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def load_character(self):
        """Cargar personaje desde archivo"""
        if self.selected_index is None:
            print(f"{Colors.RED}Selecciona un slot primero (1-5){Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            return
        
        filepath = input(f"\n{Colors.GREEN}Ruta del archivo JSON: {Colors.RESET}").strip('"')
        
        if not filepath or not os.path.exists(filepath):
            print(f"{Colors.RED}Archivo no encontrado{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            self.party[self.selected_index] = char_data
            self.character_files[self.selected_index] = Path(filepath)
            
            print(f"{Colors.GREEN}✓ {char_data['name']} cargado en slot {self.selected_index + 1}{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}Error al cargar personaje: {e}{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def edit_character(self):
        """Editar HP y XP del personaje"""
        if self.selected_index is None or self.party[self.selected_index] is None:
            print(f"{Colors.RED}Selecciona un personaje primero{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            return
        
        char = self.party[self.selected_index]
        
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Editando: {char['name']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}(Dejar vacío para no cambiar){Colors.RESET}\n")
        
        # HP
        hp = char.get('hp', {})
        hp_current = hp.get('current', 0) if isinstance(hp, dict) else hp
        hp_max = hp.get('max', 0) if isinstance(hp, dict) else hp
        
        print(f"HP actual: {hp_current}/{hp_max}")
        new_hp = input(f"{Colors.GREEN}Nuevo HP actual: {Colors.RESET}").strip()
        
        if new_hp:
            try:
                hp_value = int(new_hp)
                if isinstance(char.get('hp'), dict):
                    char['hp']['current'] = hp_value
                else:
                    char['hp'] = {'current': hp_value, 'max': hp_max}
                print(f"{Colors.GREEN}✓ HP actualizado{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Valor inválido{Colors.RESET}")
        
        # XP
        current_xp = char.get('experience', 0)
        print(f"\nXP actual: {current_xp:,}")
        new_xp = input(f"{Colors.GREEN}Nuevo XP: {Colors.RESET}").strip()
        
        if new_xp:
            try:
                char['experience'] = int(new_xp)
                print(f"{Colors.GREEN}✓ XP actualizado{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Valor inválido{Colors.RESET}")
        
        input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def remove_character(self):
        """Remover personaje del slot"""
        if self.selected_index is None or self.party[self.selected_index] is None:
            print(f"{Colors.RED}No hay personaje seleccionado para remover{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            return
        
        char_name = self.party[self.selected_index]['name']
        confirm = input(f"\n{Colors.RED}¿Remover a {char_name}? (s/n): {Colors.RESET}").strip().lower()
        
        if confirm == 's':
            self.party[self.selected_index] = None
            self.character_files[self.selected_index] = None
            print(f"{Colors.GREEN}✓ Personaje removido{Colors.RESET}")
            self.selected_index = None
        
        input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def save_all(self):
        """Guardar todos los personajes"""
        saved = 0
        
        for i, char in enumerate(self.party):
            if char is not None and self.character_files[i] is not None:
                try:
                    with open(self.character_files[i], 'w', encoding='utf-8') as f:
                        json.dump(char, f, indent=2, ensure_ascii=False)
                    print(f"{Colors.GREEN}✓ {char['name']} guardado{Colors.RESET}")
                    saved += 1
                except Exception as e:
                    print(f"{Colors.RED}✗ Error al guardar {char['name']}: {e}{Colors.RESET}")
        
        if saved == 0:
            print(f"{Colors.YELLOW}No hay personajes para guardar{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Se guardaron {saved} personaje(s){Colors.RESET}")
        
        input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def export_party(self):
        """Exportar configuración del party"""
        active = sum(1 for char in self.party if char is not None)
        
        if active == 0:
            print(f"{Colors.RED}No hay personajes en el party{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            return
        
        filepath = input(f"\n{Colors.GREEN}Nombre del archivo (sin extensión): {Colors.RESET}").strip()
        
        if not filepath:
            return
        
        filepath = f"{filepath}.json"
        
        try:
            party_data = {
                'party': self.party,
                'files': [str(f) if f else None for f in self.character_files]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(party_data, f, indent=2, ensure_ascii=False)
            
            print(f"{Colors.GREEN}✓ Party exportado a {filepath}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error al exportar: {e}{Colors.RESET}")
        
        input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def import_party(self):
        """Importar configuración del party"""
        filepath = input(f"\n{Colors.GREEN}Ruta del archivo JSON: {Colors.RESET}").strip('"')
        
        if not filepath or not os.path.exists(filepath):
            print(f"{Colors.RED}Archivo no encontrado{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                party_data = json.load(f)
            
            self.party = party_data['party']
            self.character_files = [Path(f) if f else None for f in party_data['files']]
            self.selected_index = None
            
            active = sum(1 for char in self.party if char is not None)
            print(f"{Colors.GREEN}✓ Party importado ({active} personajes){Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error al importar: {e}{Colors.RESET}")
        
        input(f"\n{Colors.BRIGHT_BLACK}Presiona ENTER para continuar...{Colors.RESET}")
    
    def run(self):
        """Loop principal"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_party_grid()
            self.print_menu()
            
            if self.selected_index is not None:
                if self.party[self.selected_index]:
                    print(f"{Colors.BRIGHT_GREEN}► Seleccionado: Slot {self.selected_index + 1} - {self.party[self.selected_index]['name']}{Colors.RESET}")
                else:
                    print(f"{Colors.BRIGHT_YELLOW}► Seleccionado: Slot {self.selected_index + 1} (vacío){Colors.RESET}")
            
            choice = input(f"\n{Colors.CYAN}Opción: {Colors.RESET}").strip().upper()
            
            if choice in ['1', '2', '3', '4', '5']:
                self.selected_index = int(choice) - 1
            elif choice == 'L':
                self.load_character()
            elif choice == 'V':
                self.show_character_details()
            elif choice == 'E':
                self.edit_character()
            elif choice == 'R':
                self.remove_character()
            elif choice == 'G':
                self.save_all()
            elif choice == 'X':
                self.export_party()
            elif choice == 'I':
                self.import_party()
            elif choice == 'Q':
                print(f"\n{Colors.CYAN}¡Hasta luego!{Colors.RESET}\n")
                break


def main():
    manager = PartyManagerConsole()
    manager.run()


if __name__ == '__main__':
    main()
