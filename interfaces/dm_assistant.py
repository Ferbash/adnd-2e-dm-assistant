"""
🎲 AD&D 2e Dungeon Master Assistant 🎲
Sistema integrado de gestión de partidas con interfaz de comandos
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import pickle
import subprocess

# Configurar UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos del sistema
from core.dados import DiceRoller
from core.combate import CombatManager, MonsterDatabase, Combatant
from core.biblio import RuleBook


class Character:
    """Representa un personaje cargado"""
    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_prompt_summary(self) -> str:
        """Genera resumen elegante para el prompt"""
        name = self.data.get('name', 'Desconocido')
        race = self.data.get('race', 'N/A')
        char_class = self.data.get('class', 'N/A')
        level = self.data.get('level', 1)
        hp = self.data.get('hp', {})
        hp_current = hp.get('current', 0)
        hp_max = hp.get('max', 0)
        
        # Calcular estado de salud
        hp_percent = (hp_current / hp_max * 100) if hp_max > 0 else 0
        if hp_percent >= 75:
            hp_status = "💚 Saludable"
        elif hp_percent >= 50:
            hp_status = "💛 Herido"
        elif hp_percent >= 25:
            hp_status = "🧡 Gravemente herido"
        else:
            hp_status = "❤️ Crítico"
        
        # Stats principales
        attrs = self.data.get('attributes', {})
        ac = self.data.get('ac', 10)
        thac0 = self.data.get('thac0', 20)
        
        # Arma equipada
        equipped = self.data.get('equipped', {})
        weapon = equipped.get('arma_principal', 'Desarmado')
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║  {name:^58}  ║
╠══════════════════════════════════════════════════════════════╣
║  {race} • {char_class} • Nivel {level}  {hp_status}                     ║
╠══════════════════════════════════════════════════════════════╣
║  HP: {hp_current}/{hp_max}  │  AC: {ac}  │  THAC0: {thac0}  │  Arma: {weapon[:15]}    ║
╠══════════════════════════════════════════════════════════════╣
║  FUE: {attrs.get('FUE', 10):2d}  │  INT: {attrs.get('INT', 10):2d}  │  SAB: {attrs.get('SAB', 10):2d}          ║
║  DES: {attrs.get('DES', 10):2d}  │  CAR: {attrs.get('CAR', 10):2d}  │  CON: {attrs.get('CON', 10):2d}          ║
╚══════════════════════════════════════════════════════════════╝
"""
        return summary.strip()
    
    def get_compact_summary(self) -> str:
        """Resumen compacto de una línea"""
        name = self.data.get('name', 'Desconocido')
        race = self.data.get('race', 'N/A')
        char_class = self.data.get('class', 'N/A')
        level = self.data.get('level', 1)
        hp = self.data.get('hp', {})
        hp_current = hp.get('current', 0)
        hp_max = hp.get('max', 0)
        
        return f"⚔️ {name} [{race} {char_class} Nv.{level}] HP:{hp_current}/{hp_max}"


class DMAssistant:
    """Asistente del Dungeon Master - Sistema principal"""
    
    def __init__(self):
        self.current_character: Optional[Character] = None
        self.dice_roller = DiceRoller()
        self.combat_manager: Optional[CombatManager] = None
        self.monster_db = MonsterDatabase()
        self.rulebook = RuleBook()
        self.running = True
        self.characters_dir = Path(__file__).parent.parent / "data"
        
    def show_banner(self):
        """Muestra banner de bienvenida"""
        banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🎲  AD&D 2e DUNGEON MASTER ASSISTANT  🎲                ║
║                                                                ║
║              Sistema Integrado de Gestión de Partidas          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Escribe /help para ver todos los comandos disponibles
"""
        print(banner)
    
    def show_help(self):
        """Muestra ayuda de comandos"""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║                     COMANDOS DISPONIBLES                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  📋 GESTIÓN DE PERSONAJES                                      ║
║    /character <archivo>    - Cargar personaje                  ║
║    /char <archivo>         - Alias de /character               ║
║    /characters             - Listar personajes disponibles     ║
║    /sheet                  - Ver ficha completa del personaje  ║
║    /stats                  - Ver estadísticas básicas          ║
║    /unload                 - Descargar personaje actual        ║
║    /hp <cantidad>          - Modificar HP (+10, -5, =50)       ║
║    /rest                   - Descanso completo (recuperar HP)  ║
║    /xp <cantidad>          - Agregar experiencia               ║
║    /money <tipo> <cant>    - Modificar dinero (+100po, -50pa) ║
║    /equip <item>           - Equipar arma/armadura             ║
║    /save                   - Guardar cambios del personaje     ║
║                                                                ║
║  🎲 SISTEMA DE DADOS                                           ║
║    /dice [XdY+Z]          - Lanzar dados (ej: /dice 2d6+3)    ║
║    /roll [XdY+Z]          - Alias de /dice                     ║
║    /d20 [bonus]           - Tirar d20 con bonus opcional       ║
║    /attack                - Tirada de ataque (personaje)       ║
║    /damage                - Tirada de daño (personaje)         ║
║    /save <tipo>           - Tirada de salvación                ║
║    /check <atributo>      - Chequeo de atributo                ║
║                                                                ║
║  ⚔️  COMBATE                                                    ║
║    /combat start          - Iniciar nuevo combate              ║
║    /combat add <monstruo> - Agregar monstruo al combate        ║
║    /combat init           - Tirar iniciativa y comenzar        ║
║    /combat status         - Ver estado del combate             ║
║    /combat attack <N>     - Atacar al enemigo N                ║
║    /combat next           - Siguiente turno                    ║
║    /combat end            - Terminar combate                   ║
║                                                                ║
║  🐉 MONSTRUOS                                                   ║
║    /monster <nombre>      - Ver ficha de monstruo              ║
║    /monsters list         - Listar todos los monstruos         ║
║    /monsters search <q>   - Buscar monstruos                   ║
║    /monsters type <tipo>  - Filtrar por tipo                   ║
║    /monsters random       - Encuentro aleatorio                ║
║                                                                ║
║  📚 CONSULTA DE REGLAS                                          ║
║    /rules <búsqueda>      - Buscar regla (iniciativa, AC, etc)║
║    /spell <nombre>        - Buscar conjuro específico          ║
║    /class <nombre>        - Info de clase (guerrero, mago...) ║
║    /ability <atributo>    - Info de atributo (fuerza, des...) ║
║    /item <nombre>         - Buscar objeto mágico/equipo        ║
║                                                                ║
║  🔧 UTILIDADES                                                  ║
║    /create                - Crear nuevo personaje              ║
║    /edit                  - Editar personaje actual            ║
║    /levelup               - Subir nivel al personaje           ║
║    /help                  - Mostrar esta ayuda                 ║
║    /clear                 - Limpiar pantalla                   ║
║    /exit                  - Salir del asistente                ║
║    /quit                  - Alias de /exit                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
        try:
            print(help_text)
        except UnicodeEncodeError:
            # Fallback para terminales sin soporte UTF-8
            print(help_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
    
    def get_prompt(self) -> str:
        """Genera el prompt con info del personaje actual y combate"""
        prompt_parts = []
        
        # Info del personaje
        if self.current_character:
            char_summary = self.current_character.get_compact_summary()
            prompt_parts.append(char_summary)
        
        # Info del combate activo
        if self.combat_manager and self.combat_manager.round_number > 0:
            # Resumen compacto del combate
            current = self.combat_manager.get_current_combatant()
            distance_str = "MELÉ" if self.combat_manager.combat_distance <= 1 else f"{self.combat_manager.combat_distance}m"
            
            # Contar vivos
            players_alive = sum(1 for c in self.combat_manager.combatants if c.is_player and c.is_alive)
            enemies_alive = sum(1 for c in self.combat_manager.combatants if not c.is_player and c.is_alive)
            
            combat_info = f"⚔️ COMBATE Round {self.combat_manager.round_number} | Dist: {distance_str} | PJs: {players_alive} | Enemigos: {enemies_alive}"
            
            if current:
                turn_info = f"🎯 Turno: {current.name} (HP: {current.hp}/{current.max_hp})"
                prompt_parts.append(f"{combat_info}\n{turn_info}")
            else:
                prompt_parts.append(combat_info)
        
        if prompt_parts:
            return f"\n{chr(10).join(prompt_parts)}\n🎲 DM> "
        else:
            return "\n🎲 DM> "
    
    def list_characters(self):
        """Lista todos los personajes JSON disponibles"""
        json_files = list(self.characters_dir.glob("*_character.json"))
        
        if not json_files:
            print("\n⚠️ No se encontraron personajes guardados\n")
            return []
        
        print("\n" + "="*70)
        print("📋 PERSONAJES DISPONIBLES".center(70))
        print("="*70 + "\n")
        
        characters_info = []
        for i, filepath in enumerate(json_files, 1):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                
                name = char_data.get('name', 'Desconocido')
                race = char_data.get('race', 'N/A')
                char_class = char_data.get('class', 'N/A')
                level = char_data.get('level', 1)
                hp = char_data.get('hp', {})
                hp_current = hp.get('current', 0)
                hp_max = hp.get('max', 0)
                
                filename = filepath.name
                
                print(f"  [{i}] {name:25s} - {race} {char_class} Nv.{level}")
                print(f"      HP: {hp_current}/{hp_max}  |  Archivo: {filename}")
                print()
                
                characters_info.append({
                    'index': i,
                    'filepath': str(filepath),
                    'filename': filename,
                    'name': name
                })
            except Exception as e:
                print(f"  ❌ Error leyendo {filepath.name}: {e}\n")
        
        print("="*70 + "\n")
        return characters_info
    
    def load_character(self, filepath: str) -> bool:
        """Carga un personaje"""
        try:
            # Si es un número, buscar en la lista de personajes
            if filepath.isdigit():
                characters = list(self.characters_dir.glob("*_character.json"))
                idx = int(filepath) - 1
                if 0 <= idx < len(characters):
                    filepath = str(characters[idx])
                else:
                    print(f"❌ Índice {filepath} inválido")
                    return False
            
            if not filepath.endswith('.json'):
                # Buscar por nombre
                found = None
                for json_file in self.characters_dir.glob("*_character.json"):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('name', '').lower() == filepath.lower():
                            found = str(json_file)
                            break
                
                if found:
                    filepath = found
                else:
                    filepath += '.json'
            
            if not os.path.exists(filepath):
                print(f"❌ Archivo '{filepath}' no encontrado")
                print("\n💡 Usa /characters para ver personajes disponibles")
                return False
            
            self.current_character = Character(filepath)
            print("\n✅ Personaje cargado exitosamente!\n")
            print(self.current_character.get_prompt_summary())
            
            # Cargar en dice roller
            self.dice_roller.character = self.current_character.data
            
            return True
        except Exception as e:
            print(f"❌ Error cargando personaje: {e}")
            return False
    
    def unload_character(self):
        """Descarga el personaje actual"""
        if self.current_character:
            print(f"✅ Personaje '{self.current_character.data.get('name')}' descargado")
            self.current_character = None
            self.dice_roller.character = None
        else:
            print("⚠️ No hay personaje cargado")
    
    def show_sheet(self):
        """Muestra la ficha completa del personaje"""
        if not self.current_character:
            print("❌ No hay personaje cargado. Usa /character <archivo>")
            return
        
        char = self.current_character.data
        
        print("\n" + "="*70)
        print(f"FICHA DE PERSONAJE: {char.get('name', 'N/A')}".center(70))
        print("="*70)
        
        # Información básica
        print(f"\nRaza: {char.get('race', 'N/A')}")
        print(f"Clase: {char.get('class', 'N/A')}")
        print(f"Nivel: {char.get('level', 1)}")
        print(f"Alineamiento: {char.get('alignment', 'N/A')}")
        
        # Kit
        kit = char.get('kit')
        if kit:
            print(f"Kit: {kit.get('name', 'N/A')}")
        
        # Atributos
        print("\n📊 ATRIBUTOS:")
        attrs = char.get('attributes', {})
        for attr_name in ['FUE', 'DES', 'CON', 'INT', 'SAB', 'CAR']:
            value = attrs.get(attr_name, 10)
            print(f"  {attr_name}: {value}")
        
        # Combate
        print("\n⚔️ ESTADÍSTICAS DE COMBATE:")
        hp = char.get('hp', {})
        print(f"  Puntos de Golpe: {hp.get('current', 0)}/{hp.get('max', 0)}")
        print(f"  Clase de Armadura: {char.get('ac', 10)}")
        print(f"  THAC0: {char.get('thac0', 20)}")
        
        # Armas equipadas
        equipped = char.get('equipped', {})
        print("\n🗡️ EQUIPO:")
        if equipped.get('arma_principal'):
            print(f"  Arma Principal: {equipped['arma_principal']}")
        if equipped.get('armadura'):
            print(f"  Armadura: {equipped['armadura']}")
        if equipped.get('escudo'):
            print(f"  Escudo: {equipped['escudo']}")
        
        # Salvaciones
        print("\n🛡️ TIRADAS DE SALVACIÓN:")
        saves = char.get('saving_throws', {})
        for save_type, value in saves.items():
            print(f"  {save_type}: {value}")
        
        # Dinero
        print("\n💰 DINERO:")
        money = char.get('money', {})
        for coin, amount in money.items():
            if amount > 0:
                print(f"  {coin}: {amount}")
        
        print("\n" + "="*70 + "\n")
    
    def roll_dice(self, dice_string: str = None, bonus: int = 0):
        """Lanza dados"""
        if not dice_string:
            dice_string = input("Dados a lanzar (ej: 2d6+3): ").strip()
        
        try:
            result = self.dice_roller.roll(dice_string, bonus)
            print(f"\n🎲 {result['reason']}")
            print(f"   Tiradas: {result['rolls']}")
            print(f"   Total: {result['total']}")
            if result.get('critical'):
                print("   🎯 ¡CRÍTICO!")
            elif result.get('fumble'):
                print("   💥 ¡PIFIA!")
            print()
        except Exception as e:
            print(f"❌ Error en tirada: {e}")
    
    def character_attack(self):
        """Tirada de ataque del personaje"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            bonus = int(input("Bonus adicional (0 para ninguno): ").strip() or "0")
            self.dice_roller.attack_roll(bonus=bonus)
        except ValueError:
            print("❌ Bonus inválido")
    
    def character_damage(self):
        """Tirada de daño del personaje"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            bonus = int(input("Bonus adicional (0 para ninguno): ").strip() or "0")
            self.dice_roller.damage_roll(bonus=bonus)
        except ValueError:
            print("❌ Bonus inválido")
    
    def saving_throw(self, save_type: str = None):
        """Tirada de salvación"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        if not save_type:
            saves = self.current_character.data.get('saving_throws', {})
            print("\nTipos de salvación:")
            save_types = list(saves.keys())
            for i, st in enumerate(save_types, 1):
                print(f"  {i}. {st}")
            
            try:
                idx = int(input("Selecciona tipo (número): ").strip()) - 1
                if 0 <= idx < len(save_types):
                    save_type = save_types[idx]
            except ValueError:
                print("❌ Entrada inválida")
                return
        
        if save_type:
            self.dice_roller.saving_throw(save_type)
    
    def ability_check(self, attribute: str = None):
        """Chequeo de atributo"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        if not attribute:
            print("\nAtributos: FUE, DES, CON, INT, SAB, CAR")
            attribute = input("Atributo a chequear: ").strip().upper()
        
        self.dice_roller.ability_check(attribute)
    
    def quick_edit_hp(self, value_str: str):
        """Edición rápida de HP (+10, -5, =50)"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            hp_data = self.current_character.data['hp']
            current = hp_data['current']
            max_hp = hp_data['max']
            
            if value_str.startswith('+'):
                # Curar
                amount = int(value_str[1:])
                new_hp = min(current + amount, max_hp)
                hp_data['current'] = new_hp
                print(f"💚 {self.current_character.data['name']} se cura {amount} HP")
                print(f"   HP: {current} → {new_hp}/{max_hp}")
            
            elif value_str.startswith('-'):
                # Dañar
                amount = int(value_str[1:])
                new_hp = max(current - amount, 0)
                hp_data['current'] = new_hp
                print(f"💔 {self.current_character.data['name']} recibe {amount} de daño")
                print(f"   HP: {current} → {new_hp}/{max_hp}")
                
                if new_hp == 0:
                    print("   ⚠️ ¡PERSONAJE INCONSCIENTE!")
            
            elif value_str.startswith('='):
                # Establecer valor exacto
                new_hp = int(value_str[1:])
                new_hp = max(0, min(new_hp, max_hp))
                hp_data['current'] = new_hp
                print(f"💉 HP establecido a {new_hp}/{max_hp}")
            
            else:
                print("❌ Formato inválido. Usa +10, -5 o =50")
                return
            
            # Guardar cambios
            self.save_character()
            
        except (ValueError, KeyError) as e:
            print(f"❌ Error modificando HP: {e}")
    
    def rest_character(self):
        """Descanso completo - recupera todos los HP"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        hp_data = self.current_character.data['hp']
        old_hp = hp_data['current']
        hp_data['current'] = hp_data['max']
        
        print(f"😴 {self.current_character.data['name']} descansa y recupera toda su salud")
        print(f"   HP: {old_hp} → {hp_data['max']}/{hp_data['max']}")
        
        self.save_character()
    
    def add_experience(self, amount: int):
        """Agrega experiencia al personaje"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            current_xp = self.current_character.data.get('experience', 0)
            new_xp = current_xp + amount
            self.current_character.data['experience'] = new_xp
            
            print(f"⭐ {self.current_character.data['name']} gana {amount} XP")
            print(f"   XP Total: {current_xp:,} → {new_xp:,}")
            
            # Verificar si puede subir de nivel
            level = self.current_character.data.get('level', 1)
            char_class = self.current_character.data.get('class', '')
            
            # XP necesario para siguiente nivel (simplificado)
            xp_needed = level * 2000  # Aproximación
            if new_xp >= xp_needed:
                print(f"   🎉 ¡Suficiente XP para nivel {level + 1}!")
                print(f"   💡 Usa /levelup para subir de nivel")
            
            self.save_character()
            
        except Exception as e:
            print(f"❌ Error agregando XP: {e}")
    
    def save_character(self):
        """Guarda los cambios del personaje actual"""
        if not self.current_character:
            return
        
        try:
            with open(self.current_character.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_character.data, f, indent=2, ensure_ascii=False)
            print("💾 Cambios guardados")
        except Exception as e:
            print(f"❌ Error guardando: {e}")
    
    def modify_money(self, coin_type: str, amount_str: str):
        """Modifica el dinero del personaje"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            money = self.current_character.data.get('money', {})
            
            # Normalizar tipo de moneda
            coin_map = {
                'po': 'Piezas de Oro',
                'pp': 'Piezas de Platino',
                'pa': 'Piezas de Plata',
                'pe': 'Piezas de Electro',
                'pc': 'Piezas de Cobre',
                'oro': 'Piezas de Oro',
                'platino': 'Piezas de Platino',
                'plata': 'Piezas de Plata',
                'electro': 'Piezas de Electro',
                'cobre': 'Piezas de Cobre'
            }
            
            coin_type_lower = coin_type.lower()
            full_coin = coin_map.get(coin_type_lower)
            
            if not full_coin:
                print(f"❌ Tipo de moneda inválido: {coin_type}")
                print("   Tipos válidos: po, pp, pa, pe, pc")
                return
            
            current = money.get(full_coin, 0)
            
            if amount_str.startswith('+'):
                amount = int(amount_str[1:])
                new_amount = current + amount
                money[full_coin] = new_amount
                print(f"💰 +{amount} {coin_type.upper()}")
                print(f"   {full_coin}: {current} → {new_amount}")
            
            elif amount_str.startswith('-'):
                amount = int(amount_str[1:])
                new_amount = max(0, current - amount)
                money[full_coin] = new_amount
                print(f"💸 -{amount} {coin_type.upper()}")
                print(f"   {full_coin}: {current} → {new_amount}")
            
            elif amount_str.startswith('='):
                amount = int(amount_str[1:])
                money[full_coin] = amount
                print(f"💰 {full_coin} establecido a {amount}")
            
            else:
                print("❌ Formato inválido. Usa +100, -50 o =200")
                return
            
            self.save_character()
            
        except ValueError as e:
            print(f"❌ Cantidad inválida: {e}")
    
    def quick_equip(self, item_name: str):
        """Equipa un objeto rápidamente"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            equipment = self.current_character.data.get('equipment', {})
            equipped = self.current_character.data.get('equipped', {})
            
            # Buscar item en el inventario
            found_item = None
            for item_key in equipment.keys():
                if item_name.lower() in item_key.lower():
                    found_item = item_key
                    break
            
            if not found_item:
                print(f"❌ '{item_name}' no encontrado en el inventario")
                print("\n📦 Equipo disponible:")
                for item in equipment.keys():
                    print(f"   • {item}")
                return
            
            item_data = equipment[found_item]
            item_type = item_data.get('type', 'other')
            
            # Equipar según el tipo
            if item_type == 'weapon':
                equipped['arma_principal'] = found_item
                print(f"⚔️ {found_item} equipado como arma principal")
            
            elif item_type == 'armor':
                equipped['armadura'] = found_item
                print(f"🛡️ {found_item} equipado como armadura")
            
            elif item_type == 'shield':
                equipped['escudo'] = found_item
                print(f"🛡️ {found_item} equipado como escudo")
            
            else:
                print(f"⚠️ {found_item} no es equipable (tipo: {item_type})")
                return
            
            # Recalcular stats de combate
            self._recalculate_combat_stats()
            self.save_character()
            
        except Exception as e:
            print(f"❌ Error equipando: {e}")
    
    def _recalculate_combat_stats(self):
        """Recalcula AC, ataque y daño basados en equipo"""
        if not self.current_character:
            return
        
        char = self.current_character.data
        equipped = char.get('equipped', {})
        equipment = char.get('equipment', {})
        
        # Calcular AC base
        base_ac = 10
        
        # AC por armadura
        armor_name = equipped.get('armadura')
        if armor_name and armor_name in equipment:
            armor_ac = equipment[armor_name].get('ac', 10)
            base_ac = armor_ac
        
        # AC por escudo
        shield_name = equipped.get('escudo')
        if shield_name and shield_name in equipment:
            shield_bonus = equipment[shield_name].get('ac_bonus', 0)
            base_ac += shield_bonus
        
        # AC por DES
        dex = char.get('attributes', {}).get('DES', 10)
        dex_bonus = 0
        if dex >= 16:
            dex_bonus = -(dex - 15)  # -1 por cada punto sobre 15
        elif dex <= 6:
            dex_bonus = (7 - dex)  # +1 por cada punto bajo 7
        
        char['ac'] = base_ac + dex_bonus
        
        print(f"   AC recalculado: {char['ac']}")
    
    def show_monster(self, monster_name: str):
        """Muestra ficha de monstruo"""
        self.monster_db.print_monster_card(monster_name)
    
    def list_monsters(self):
        """Lista todos los monstruos"""
        monsters = self.monster_db.list_monsters()
        print(f"\n📋 MONSTRUOS DISPONIBLES ({len(monsters)} total):\n")
        for i, name in enumerate(monsters, 1):
            data = self.monster_db.monsters[name]
            print(f"  {i:3d}. {name:30s} - HD: {data['hd']:8s} AC: {data['ac']:2d} XP: {data['xp']:5d}")
        print()
    
    def search_monsters(self, query: str):
        """Busca monstruos"""
        results = self.monster_db.search_monsters(query)
        if results:
            print(f"\n🔍 Encontrados {len(results)} monstruos:\n")
            for name, data in sorted(results.items()):
                print(f"  • {name:30s} - HD: {data['hd']:8s} AC: {data['ac']:2d}")
            print()
        else:
            print("❌ No se encontraron monstruos")
    
    def combat_start(self):
        """Inicia un nuevo combate"""
        print("\n" + "="*70)
        print("⚔️ INICIANDO NUEVO COMBATE".center(70))
        print("="*70 + "\n")
        
        self.combat_manager = CombatManager()
        
        # Agregar personaje actual si está cargado
        if self.current_character:
            # Guardar personaje temporalmente
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(self.current_character.data, f, ensure_ascii=False, indent=2)
                temp_file = f.name
            
            # Agregar al combate
            if self.combat_manager.add_player(temp_file):
                print(f"✅ {self.current_character.data.get('name')} añadido al combate")
            
            # Limpiar archivo temporal
            import os
            try:
                os.unlink(temp_file)
            except:
                pass
        
        print("\n💡 Usa /combat add <monstruo> para agregar enemigos")
        print("💡 Usa /monsters list para ver monstruos disponibles")
        print("💡 Usa /combat init para tirar iniciativa y comenzar")
    
    def run_create_character(self):
        """Ejecuta el script de creación de personajes"""
        try:
            creator_path = Path(__file__).parent.parent / "core" / "character_creator.py"
            subprocess.run([sys.executable, str(creator_path)], check=True)
        except Exception as e:
            print(f"❌ Error ejecutando creador de personajes: {e}")
    
    def run_edit_character(self):
        """Ejecuta el script de edición"""
        if not self.current_character:
            print("❌ No hay personaje cargado")
            return
        
        try:
            # Recargar después de editar
            creator_path = Path(__file__).parent.parent / "core" / "character_creator.py"
            subprocess.run([sys.executable, str(creator_path)], check=True)
            self.load_character(self.current_character.filepath)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def process_command(self, command: str):
        """Procesa un comando"""
        command = command.strip()
        
        if not command:
            return
        
        # Comandos sin /
        if not command.startswith('/'):
            print("❌ Comando no reconocido. Usa /help para ver comandos disponibles")
            return
        
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Gestión de personajes
        if cmd in ['/character', '/char']:
            if args:
                self.load_character(args)
            else:
                print("❌ Uso: /character <archivo.json | número | nombre>")
                print("💡 Usa /characters para ver personajes disponibles")
        
        elif cmd == '/characters':
            chars = self.list_characters()
            if chars:
                print("💡 Usa /character <número> para cargar un personaje")
                print("   Ejemplo: /character 1")
        
        elif cmd == '/unload':
            self.unload_character()
        
        elif cmd == '/sheet':
            self.show_sheet()
        
        elif cmd == '/stats':
            if self.current_character:
                print(self.current_character.get_prompt_summary())
            else:
                print("❌ No hay personaje cargado")
        
        elif cmd == '/hp':
            if args:
                self.quick_edit_hp(args)
            else:
                print("❌ Uso: /hp +10  (curar 10)")
                print("        /hp -5   (dañar 5)")
                print("        /hp =50  (establecer a 50)")
        
        elif cmd == '/rest':
            self.rest_character()
        
        elif cmd == '/xp':
            if args:
                try:
                    amount = int(args)
                    self.add_experience(amount)
                except ValueError:
                    print("❌ Cantidad inválida")
            else:
                print("❌ Uso: /xp <cantidad>  (ej: /xp 1000)")
        
        elif cmd == '/money':
            if args:
                parts = args.split()
                if len(parts) == 2:
                    self.modify_money(parts[0], parts[1])
                else:
                    print("❌ Uso: /money <tipo> <cantidad>")
                    print("   Ejemplo: /money po +100")
                    print("   Tipos: po, pp, pa, pe, pc")
            else:
                print("❌ Uso: /money <tipo> <cantidad>")
        
        elif cmd == '/equip':
            if args:
                self.quick_equip(args)
            else:
                print("❌ Uso: /equip <nombre_item>")
        
        elif cmd == '/save':
            self.save_character()
        
        # Dados
        elif cmd in ['/dice', '/roll']:
            self.roll_dice(args if args else None)
        
        elif cmd == '/d20':
            bonus = int(args) if args else 0
            self.roll_dice("1d20", bonus)
        
        elif cmd == '/attack':
            self.character_attack()
        
        elif cmd == '/damage':
            self.character_damage()
        
        elif cmd == '/save':
            self.saving_throw(args if args else None)
        
        elif cmd == '/check':
            self.ability_check(args.upper() if args else None)
        
        # Combate
        elif cmd == '/combat':
            if not args:
                print("❌ Uso: /combat [start|add|init|status|attack|move|next|auto|end]")
                print("\nSubcomandos:")
                print("  start                    - Iniciar nuevo combate")
                print("  add <monstruo>           - Agregar monstruo al combate")
                print("  init                     - Tirar iniciativa y comenzar")
                print("  status                   - Ver estado del combate")
                print("  attack <objetivo>        - Atacar a un objetivo")
                print("  move <approach|retreat>  - Acercarse o retroceder")
                print("  next                     - Siguiente turno")
                print("  auto [min_hp]            - Combate automático (parar si HP <= min_hp)")
                print("  end                      - Terminar combate")
            else:
                subcmd_parts = args.split(maxsplit=1)
                subcmd = subcmd_parts[0].lower()
                subcmd_args = subcmd_parts[1] if len(subcmd_parts) > 1 else ""
                
                if subcmd == 'start':
                    self.combat_start()
                
                elif subcmd == 'add':
                    if not self.combat_manager:
                        print("❌ Inicia combate primero con /combat start")
                    elif not subcmd_args:
                        print("❌ Especifica el nombre del monstruo")
                        print("💡 Usa /monsters list para ver monstruos disponibles")
                    else:
                        # Buscar monstruo (acepta nombre parcial)
                        monsters = self.monster_db.search_monsters(subcmd_args)
                        if not monsters:
                            print(f"❌ Monstruo '{subcmd_args}' no encontrado")
                            print("💡 Usa /monsters search <nombre> para buscar")
                        elif len(monsters) == 1:
                            monster_name = list(monsters.keys())[0]
                            if self.combat_manager.add_monster(monster_name):
                                print(f"✅ {monster_name} añadido al combate")
                        else:
                            # Mostrar lista numerada para selección rápida
                            print(f"\n🔍 Se encontraron {len(monsters)} monstruos:\n")
                            monster_list = sorted(monsters.keys())
                            for i, name in enumerate(monster_list, 1):
                                data = monsters[name]
                                print(f"  {i:2d}. {name:30s} - HD: {data['hd']:8s} AC: {data['ac']:2d}")
                            
                            # Pedir selección
                            try:
                                choice = input(f"\n🎯 Selecciona un número (1-{len(monster_list)}) o ENTER para cancelar: ").strip()
                                if choice:
                                    idx = int(choice) - 1
                                    if 0 <= idx < len(monster_list):
                                        selected_monster = monster_list[idx]
                                        if self.combat_manager.add_monster(selected_monster):
                                            print(f"✅ {selected_monster} añadido al combate")
                                    else:
                                        print("❌ Número inválido")
                                else:
                                    print("⚠️ Cancelado")
                            except ValueError:
                                print("❌ Debes ingresar un número")
                
                elif subcmd == 'init':
                    if not self.combat_manager:
                        print("❌ No hay combate activo")
                    elif len(self.combat_manager.combatants) < 2:
                        print("❌ Se necesitan al menos 2 combatientes")
                        print(f"   Actuales: {len(self.combat_manager.combatants)}")
                    else:
                        self.combat_manager.start_combat()
                        print("\n✅ Iniciativa tirada y combate iniciado!")
                        self.combat_manager.show_combat_status()
                        
                        # Mostrar primer turno
                        current = self.combat_manager.get_current_combatant()
                        if current:
                            print(f"\n🎯 Turno de: {current.name}")
                            if current.is_player:
                                print("💡 Usa /combat attack <número> para atacar a un enemigo")
                            else:
                                print("💡 Usa /combat attack <número> para que el enemigo ataque al PJ")
                                print("   O usa /combat next si el enemigo no ataca este turno")
                
                elif subcmd == 'status':
                    if not self.combat_manager:
                        print("❌ No hay combate activo")
                    else:
                        self.combat_manager.show_combat_status()
                
                elif subcmd == 'attack':
                    if not self.combat_manager:
                        print("❌ No hay combate activo")
                    elif self.combat_manager.round_number < 1:
                        print("❌ Primero inicia el combate con /combat init")
                    else:
                        current = self.combat_manager.get_current_combatant()
                        if not current:
                            print("⚠️ Usa /combat next para avanzar al siguiente turno")
                        elif current.is_player:
                            # Turno del jugador - ataca a enemigos
                            enemies = [c for c in self.combat_manager.combatants 
                                     if not c.is_player and c.is_alive]
                            if not enemies:
                                print("⚠️ No hay enemigos vivos")
                            elif not subcmd_args:
                                # Sin argumento - mostrar lista
                                print("\n🎯 Objetivos disponibles:")
                                for i, e in enumerate(enemies, 1):
                                    print(f"  {i}. {e}")
                                print("\n💡 Usa /combat attack <número>")
                            else:
                                # Con argumento - atacar
                                try:
                                    idx = int(subcmd_args) - 1
                                    if 0 <= idx < len(enemies):
                                        result = self.combat_manager.make_attack(current, enemies[idx])
                                        print(f"\n{result['message']}")
                                    else:
                                        print(f"❌ Número inválido. Elige entre 1 y {len(enemies)}")
                                        for i, e in enumerate(enemies, 1):
                                            print(f"  {i}. {e}")
                                except ValueError:
                                    print("❌ Debes usar un número para el objetivo")
                        else:
                            # Turno del enemigo - ataca a jugadores
                            players = [c for c in self.combat_manager.combatants 
                                     if c.is_player and c.is_alive]
                            if not players:
                                print("⚠️ No hay jugadores vivos")
                            elif not subcmd_args:
                                # Sin argumento - mostrar lista
                                print(f"\n🎯 {current.name} puede atacar a:")
                                for i, p in enumerate(players, 1):
                                    print(f"  {i}. {p}")
                                print("\n💡 Usa /combat attack <número>")
                            else:
                                # Con argumento - atacar
                                try:
                                    idx = int(subcmd_args) - 1
                                    if 0 <= idx < len(players):
                                        result = self.combat_manager.make_attack(current, players[idx])
                                        print(f"\n{result['message']}")
                                    else:
                                        print(f"❌ Número inválido. Elige entre 1 y {len(players)}")
                                        for i, p in enumerate(players, 1):
                                            print(f"  {i}. {p}")
                                except ValueError:
                                    print("❌ Debes usar un número para el objetivo")
                
                elif subcmd == 'move':
                    if not self.combat_manager:
                        print("❌ No hay combate activo")
                    elif self.combat_manager.round_number < 1:
                        print("❌ Primero inicia el combate con /combat init")
                    else:
                        current = self.combat_manager.get_current_combatant()
                        if not current:
                            print("⚠️ Usa /combat next para avanzar al siguiente turno")
                        elif not subcmd_args:
                            print("❌ Especifica dirección: approach (acercarse) o retreat (retroceder)")
                            distance = self.combat_manager.combat_distance
                            if distance <= 1:
                                print(f"   Distancia actual: MELÉ")
                            else:
                                print(f"   Distancia actual: {distance}m")
                        else:
                            action = subcmd_args.lower()
                            if action in ['approach', 'acercarse', 'a']:
                                msg = self.combat_manager.move_combatant(current, 'approach')
                                print(f"\n{msg}")
                            elif action in ['retreat', 'retroceder', 'r']:
                                msg = self.combat_manager.move_combatant(current, 'retreat')
                                print(f"\n{msg}")
                            else:
                                print("❌ Dirección inválida. Usa 'approach' o 'retreat'")
                
                elif subcmd == 'auto':
                    if not self.combat_manager:
                        print("❌ No hay combate activo")
                    elif self.combat_manager.round_number < 1:
                        print("❌ Primero inicia el combate con /combat init")
                    else:
                        # Obtener HP mínimo
                        min_hp = 3
                        if subcmd_args:
                            try:
                                min_hp = int(subcmd_args)
                            except ValueError:
                                print(f"⚠️ Valor inválido, usando HP mínimo por defecto: {min_hp}")
                        
                        print(f"\n⚔️ COMBATE AUTOMÁTICO INICIADO")
                        print(f"   Se detendrá si algún jugador llega a {min_hp} HP o menos\n")
                        print("="*70)
                        
                        auto_rounds = 0
                        max_auto_rounds = 100  # Límite de seguridad
                        
                        while auto_rounds < max_auto_rounds:
                            # Verificar fin de combate
                            end_msg = self.combat_manager.check_combat_end()
                            if end_msg:
                                print(f"\n{end_msg}")
                                break
                            
                            # Verificar HP de jugadores
                            stop_combat = False
                            for combatant in self.combat_manager.combatants:
                                if combatant.is_player and combatant.is_alive:
                                    if combatant.hp <= min_hp:
                                        print(f"\n⚠️ COMBATE DETENIDO: {combatant.name} tiene {combatant.hp} HP (≤ {min_hp})")
                                        stop_combat = True
                                        break
                            
                            if stop_combat:
                                break
                            
                            # Obtener combatiente actual
                            current = self.combat_manager.get_current_combatant()
                            if not current:
                                self.combat_manager.next_turn()
                                continue
                            
                            print(f"\n🎯 Turno de: {current.name} (HP: {current.hp}/{current.max_hp})")
                            
                            # Determinar objetivo y atacar
                            if current.is_player:
                                # Jugador ataca a enemigos
                                enemies = [c for c in self.combat_manager.combatants 
                                         if not c.is_player and c.is_alive]
                                if enemies:
                                    # Atacar al primer enemigo vivo
                                    target = enemies[0]
                                    result = self.combat_manager.make_attack(current, target)
                                    print(f"   {result['message']}")
                            else:
                                # Enemigo ataca a jugadores
                                players = [c for c in self.combat_manager.combatants 
                                         if c.is_player and c.is_alive]
                                if players:
                                    # Atacar al jugador con menos HP
                                    target = min(players, key=lambda p: p.hp)
                                    result = self.combat_manager.make_attack(current, target)
                                    print(f"   {result['message']}")
                            
                            # Avanzar turno
                            self.combat_manager.next_turn()
                            auto_rounds += 1
                            
                            # Pequeña pausa visual cada round completo
                            if self.combat_manager.current_turn_index == 0 and auto_rounds > 0:
                                print("\n" + "-"*70)
                        
                        if auto_rounds >= max_auto_rounds:
                            print(f"\n⚠️ Límite de rounds alcanzado ({max_auto_rounds})")
                        
                        print("\n" + "="*70)
                        print("⚔️ COMBATE AUTOMÁTICO FINALIZADO")
                        print("="*70)
                        self.combat_manager.show_combat_status()
                        print("\n💡 Usa /combat end para terminar el combate")
                
                elif subcmd == 'next':
                    if not self.combat_manager:
                        print("❌ No hay combate activo")
                    elif self.combat_manager.round_number < 1:
                        print("❌ Primero inicia el combate con /combat init")
                    else:
                        # Verificar fin de combate
                        end_msg = self.combat_manager.check_combat_end()
                        if end_msg:
                            print(f"\n{end_msg}")
                            print("💡 Usa /combat end para terminar el combate")
                        else:
                            self.combat_manager.next_turn()
                            current = self.combat_manager.get_current_combatant()
                            if current:
                                print(f"\n🎯 Turno de: {current.name}")
                                if current.is_player:
                                    print("💡 Usa /combat attack <número> para atacar a un enemigo")
                                else:
                                    print("💡 Usa /combat attack <número> para que el enemigo ataque al PJ")
                                    print("   O usa /combat next si el enemigo no ataca este turno")
                            else:
                                print("⚠️ Round completado")
                
                elif subcmd == 'end':
                    if self.combat_manager:
                        print("\n" + "="*70)
                        print("⚔️ COMBATE FINALIZADO".center(70))
                        print("="*70)
                        
                        # Mostrar resumen
                        players_alive = sum(1 for c in self.combat_manager.combatants 
                                          if c.is_player and c.is_alive)
                        monsters_alive = sum(1 for c in self.combat_manager.combatants 
                                           if not c.is_player and c.is_alive)
                        
                        print(f"\nRounds: {self.combat_manager.round_number}")
                        print(f"Jugadores vivos: {players_alive}")
                        print(f"Enemigos vivos: {monsters_alive}")
                        
                        # Actualizar HP del personaje si está cargado
                        if self.current_character:
                            for c in self.combat_manager.combatants:
                                if c.is_player and c.name == self.current_character.data.get('name'):
                                    self.current_character.data['hp']['current'] = c.hp
                                    self.save_character()
                                    print(f"\n💾 HP de {c.name} actualizado: {c.hp}/{c.max_hp}")
                        
                        self.combat_manager = None
                        print("\n✅ Combate terminado")
                    else:
                        print("❌ No hay combate activo")
                
                else:
                    print(f"❌ Subcomando '{subcmd}' no reconocido")
                    print("💡 Usa /combat sin argumentos para ver opciones")
        
        # Monstruos
        elif cmd == '/monster':
            if args:
                self.show_monster(args)
            else:
                print("❌ Uso: /monster <nombre>")
        
        elif cmd == '/monsters':
            if not args:
                self.list_monsters()
            else:
                subcmd_parts = args.split(maxsplit=1)
                subcmd = subcmd_parts[0].lower()
                subcmd_args = subcmd_parts[1] if len(subcmd_parts) > 1 else ""
                
                if subcmd == 'list':
                    self.list_monsters()
                elif subcmd == 'search':
                    self.search_monsters(subcmd_args)
                elif subcmd == 'type':
                    results = self.monster_db.filter_by_type(subcmd_args)
                    if results:
                        print(f"\n🐉 Monstruos tipo '{subcmd_args}':\n")
                        for name in results:
                            print(f"  • {name}")
                        print()
                elif subcmd == 'random':
                    monster = self.monster_db.random_encounter()
                    if monster:
                        print(f"\n🎲 Encuentro aleatorio: {monster}")
                        self.show_monster(monster)
        
        # Utilidades
        elif cmd == '/create':
            self.run_create_character()
        
        elif cmd == '/edit':
            self.run_edit_character()
        
        elif cmd == '/levelup':
            if self.current_character:
                print("⚠️ Funcionalidad disponible en character_creator.py - opción de editar personaje")
            else:
                print("❌ No hay personaje cargado")
        
        elif cmd == '/help':
            self.show_help()
        
        elif cmd == '/clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_banner()
        
        elif cmd in ['/exit', '/quit']:
            print("\n¡Que tengas una gran aventura! 🎲\n")
            self.running = False
        
        else:
            print(f"❌ Comando '{cmd}' no reconocido. Usa /help para ver comandos disponibles")
    
    def search_rules(self, query: str):
        """Busca una regla en la biblioteca"""
        if not query:
            print("❌ Uso: /rules <búsqueda>")
            print("Ejemplos: /rules iniciativa, /rules THAC0, /rules salvación")
            return
        
        results = self.rulebook.search(query, 'rules')
        
        if not results:
            print(f"\n❌ No se encontraron reglas para '{query}'")
            return
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Mostrar resultados
        print(f"\n📚 Resultados para '{query}':")
        for i, result in enumerate(results[:5], 1):  # Top 5 resultados
            print(self.rulebook.format_result(result))
            if i < len(results[:5]):
                print()
        
        if len(results) > 5:
            print(f"\n... y {len(results) - 5} resultados más")
    
    def search_spell(self, query: str):
        """Busca un conjuro específico"""
        if not query:
            print("❌ Uso: /spell <nombre>")
            print("Ejemplos: /spell bola de fuego, /spell curar")
            return
        
        results = self.rulebook.search(query, 'spells')
        
        if not results:
            print(f"\n❌ No se encontró el conjuro '{query}'")
            return
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Mostrar solo el mejor resultado
        result = results[0]
        print(self.rulebook.format_result(result))
        
        if len(results) > 1:
            print(f"\n💡 También encontrados: {', '.join([r['name'] for r in results[1:6]])}")
    
    def search_class(self, query: str):
        """Busca información de una clase"""
        if not query:
            print("❌ Uso: /class <nombre>")
            print("Ejemplos: /class guerrero, /class mago, /class clérigo")
            return
        
        results = self.rulebook.search(query, 'classes')
        
        if not results:
            print(f"\n❌ No se encontró la clase '{query}'")
            return
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Mostrar resultado
        result = results[0]
        print(self.rulebook.format_result(result))
    
    def search_ability(self, query: str):
        """Busca información de un atributo"""
        if not query:
            print("❌ Uso: /ability <atributo>")
            print("Ejemplos: /ability fuerza, /ability destreza, /ability inteligencia")
            return
        
        results = self.rulebook.search(query, 'abilities')
        
        if not results:
            print(f"\n❌ No se encontró el atributo '{query}'")
            return
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Mostrar resultado
        result = results[0]
        print(self.rulebook.format_result(result))
    
    def search_item(self, query: str):
        """Busca objetos mágicos o equipo"""
        if not query:
            print("❌ Uso: /item <nombre>")
            print("Ejemplos: /item espada +1, /item poción, /item armadura")
            return
        
        # Buscar en objetos mágicos
        results = self.rulebook.search(query, 'magic_items')
        
        # Si no hay resultados, buscar en equipo
        if not results:
            results = self.rulebook.search(query, 'equipment')
        
        if not results:
            print(f"\n❌ No se encontró el objeto '{query}'")
            return
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Mostrar top 3 resultados
        for i, result in enumerate(results[:3], 1):
            print(self.rulebook.format_result(result))
            if i < len(results[:3]):
                print()
    
    def run(self):
        """Loop principal"""
        self.show_banner()
        
        while self.running:
            try:
                command = input(self.get_prompt()).strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print("\n\n¿Salir? (s/n): ", end='')
                if input().lower() == 's':
                    self.running = False
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 ¡Adiós!\n")


def main():
    """Punto de entrada principal"""
    assistant = DMAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
