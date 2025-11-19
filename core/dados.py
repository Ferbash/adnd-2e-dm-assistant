"""
Sistema de lanzamiento de dados para AD&D 2e
Incluye todas las tiradas comunes del juego con bonificadores
"""

import random
import json
from pathlib import Path


class DiceRoller:
    """Lanzador de dados con soporte para personajes"""
    
    def __init__(self):
        self.character = None
        self.last_roll = None
    
    def load_character(self, filename):
        """Carga un personaje desde JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.character = data
            print(f"✓ Personaje cargado: {data.get('name', 'Desconocido')}")
            print(f"  Clase: {data.get('class', '?')} Nivel {data.get('level', 1)}")
            return True
        except Exception as e:
            print(f"❌ Error cargando personaje: {e}")
            return False
    
    def roll(self, dice_string, bonus=0, reason=""):
        """
        Lanza dados en formato XdY+Z
        Ejemplos: 1d20, 2d6, 3d8+5
        """
        try:
            # Parsear dice_string
            parts = dice_string.lower().replace(' ', '').split('d')
            num_dice = int(parts[0]) if parts[0] else 1
            
            # Separar dado y bonus
            if '+' in parts[1]:
                die_parts = parts[1].split('+')
                die_size = int(die_parts[0])
                bonus += int(die_parts[1])
            elif '-' in parts[1]:
                die_parts = parts[1].split('-')
                die_size = int(die_parts[0])
                bonus -= int(die_parts[1])
            else:
                die_size = int(parts[1])
            
            # Lanzar dados
            rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            total = sum(rolls) + bonus
            
            # Verificar crítico/pifia
            critical = (die_size == 20 and num_dice == 1 and rolls[0] == 20)
            fumble = (die_size == 20 and num_dice == 1 and rolls[0] == 1)
            
            # Guardar resultado
            self.last_roll = {
                'dice': dice_string,
                'rolls': rolls,
                'bonus': bonus,
                'total': total,
                'reason': reason,
                'critical': critical,
                'fumble': fumble
            }
            
            # Mostrar resultado
            rolls_str = ' + '.join(map(str, rolls))
            bonus_str = f" {bonus:+d}" if bonus != 0 else ""
            reason_str = f" ({reason})" if reason else ""
            
            print(f"\n🎲 {dice_string}{bonus_str}{reason_str}")
            print(f"   Tiradas: [{rolls_str}]{bonus_str} = {total}")
            
            # Destacar críticos y pifia en d20
            if critical:
                print("   ⭐ ¡CRÍTICO! ⭐")
            elif fumble:
                print("   💀 ¡PIFIA! 💀")
            
            return self.last_roll
            
        except Exception as e:
            print(f"❌ Error en tirada: {e}")
            print("Formato: XdY+Z (ej: 1d20, 2d6+3)")
            return None
    
    def d20(self, bonus=0, reason=""):
        """Tirada de d20 (la más común)"""
        result = self.roll("1d20", bonus, reason)
        return result['total'] if result else None
    
    def d100(self, reason=""):
        """Tirada percentil (d100)"""
        result = self.roll("1d100", 0, reason)
        return result['total'] if result else None
    
    def ability_check(self, ability_name):
        """Tirada de atributo (tirar bajo el valor)"""
        if not self.character:
            print("❌ Debes cargar un personaje primero")
            return None
        
        attrs = self.character.get('attributes', {})
        ability_value = attrs.get(ability_name.upper())
        
        if ability_value is None:
            print(f"❌ Atributo '{ability_name}' no encontrado")
            return None
        
        roll = self.d20(0, f"Chequeo de {ability_name}")
        
        if roll <= ability_value:
            print(f"   ✓ ÉXITO (necesitabas {ability_value} o menos)")
            return True
        else:
            print(f"   ✗ FALLO (necesitabas {ability_value} o menos)")
            return False
    
    def saving_throw(self, save_type):
        """Tirada de salvación"""
        if not self.character:
            print("❌ Debes cargar un personaje primero")
            return None
        
        saves = self.character.get('saving_throws', {})
        save_value = saves.get(save_type.lower())
        
        if save_value is None:
            print(f"❌ Salvación '{save_type}' no encontrada")
            print(f"Tipos válidos: {', '.join(saves.keys())}")
            return None
        
        roll = self.d20(0, f"TS de {save_type.capitalize()}")
        
        if roll >= save_value:
            print(f"   ✓ SALVACIÓN EXITOSA (necesitabas {save_value}+)")
            return True
        else:
            print(f"   ✗ SALVACIÓN FALLIDA (necesitabas {save_value}+)")
            return False
    
    def attack_roll(self, weapon_name=None, bonus=0):
        """Tirada de ataque"""
        if not self.character:
            print("❌ Debes cargar un personaje primero")
            return None
        
        thac0 = self.character.get('thac0', 20)
        
        # Buscar arma equipada (nuevo formato: equipped tiene nombres, equipment tiene datos)
        equipped = self.character.get('equipped', {})
        equipment = self.character.get('equipment', {})
        weapon_data = None
        weapon_str = ""
        
        if weapon_name:
            # Buscar por nombre en el inventario
            for item_name, item_data in equipment.items():
                if weapon_name.lower() in item_name.lower() and item_data.get('type') == 'weapon':
                    weapon_data = item_data
                    weapon_str = f" con {item_name}"
                    break
        else:
            # Usar arma principal equipada
            arma_principal = equipped.get('arma_principal')
            if arma_principal and arma_principal in equipment:
                weapon_data = equipment[arma_principal]
                weapon_str = f" con {arma_principal}"
        
        # Bonus de FUE para ataques cuerpo a cuerpo
        str_val = self.character.get('attributes', {}).get('FUE', 10)
        str_bonus = self._get_str_attack_bonus(str_val)
        
        total_bonus = bonus + str_bonus
        
        roll = self.d20(total_bonus, f"Ataque{weapon_str}")
        
        # Calcular CA golpeada
        ac_hit = thac0 - roll
        
        print(f"   THAC0: {thac0} | Bonus FUE: {str_bonus:+d} | Total: {total_bonus:+d}")
        print(f"   ⚔️  Golpeas CA {ac_hit} o mejor")
        
        return {
            'roll': roll,
            'ac_hit': ac_hit,
            'weapon': weapon_data,
            'bonus': total_bonus
        }
    
    def _get_str_attack_bonus(self, strength):
        """Bonus de ataque por FUE según AD&D 2e"""
        if strength >= 18: return 1
        elif strength >= 17: return 1
        elif strength >= 16: return 0
        elif strength <= 5: return -2
        elif strength <= 7: return -1
        return 0
    
    def damage_roll(self, weapon_name=None, bonus=0):
        """Tirada de daño"""
        if not self.character:
            print("❌ Debes cargar un personaje primero")
            return None
        
        # Buscar arma equipada (nuevo formato)
        equipped = self.character.get('equipped', {})
        equipment = self.character.get('equipment', {})
        weapon_data = None
        weapon_str = "Desarmado"
        damage_dice = "1d2"  # Daño desarmado por defecto
        
        if weapon_name:
            # Buscar por nombre
            for item_name, item_data in equipment.items():
                if weapon_name.lower() in item_name.lower() and item_data.get('type') == 'weapon':
                    weapon_data = item_data
                    weapon_str = item_name
                    damage_dice = item_data.get('damage', '1d6')
                    break
        else:
            # Usar arma principal equipada
            arma_principal = equipped.get('arma_principal')
            if arma_principal and arma_principal in equipment:
                weapon_data = equipment[arma_principal]
                weapon_str = arma_principal
                damage_dice = weapon_data.get('damage', '1d6')
        
        # Bonus de FUE para daño cuerpo a cuerpo
        str_val = self.character.get('attributes', {}).get('FUE', 10)
        str_bonus = self._get_str_damage_bonus(str_val)
        
        total_bonus = bonus + str_bonus
        
        # Extraer dados base (sin modificadores del string)
        base_dice = damage_dice.split('+')[0].split('-')[0]
        
        total = self.roll(base_dice, total_bonus, f"Daño de {weapon_str}")
        
        return total
    
    def _get_str_damage_bonus(self, strength):
        """Bonus de daño por FUE según AD&D 2e"""
        if strength >= 18: return 2
        elif strength >= 16: return 1
        elif strength <= 5: return -2
        elif strength <= 7: return -1
        return 0
    
    def initiative(self):
        """Tirada de iniciativa (d10 en AD&D 2e)"""
        if self.character:
            dex = self.character.get('attributes', {}).get('DES', 10)
            # Bonus de DES a iniciativa (opcional)
            bonus = (dex - 10) // 4  # Pequeño bonus por DES alta
            return self.roll("1d10", -bonus, "Iniciativa")  # Negativo porque menor es mejor
        else:
            return self.roll("1d10", 0, "Iniciativa")
    
    def surprise(self):
        """Tirada de sorpresa (d6, sorpresa en 1-2)"""
        roll = self.roll("1d6", 0, "Sorpresa")
        if roll <= 2:
            print("   ⚡ ¡SORPRENDIDO!")
            return True
        else:
            print("   👀 No sorprendido")
            return False
    
    def turn_undead(self):
        """Tirada para expulsar no-muertos (d20)"""
        if not self.character:
            print("❌ Debes cargar un personaje primero")
            return None
        
        char_class = self.character.get('class', '')
        if char_class not in ['Clérigo', 'Paladín']:
            print(f"❌ {char_class} no puede expulsar no-muertos")
            return None
        
        level = self.character.get('level', 1)
        roll = self.d20(0, "Expulsar no-muertos")
        
        print(f"   Nivel del clérigo: {level}")
        print("   Consulta la tabla de expulsión para ver el resultado")
        
        return roll
    
    def thief_skill(self, skill_name, base_chance):
        """Tirada de habilidad de ladrón (d100)"""
        if not self.character:
            print("❌ Debes cargar un personaje primero")
            return None
        
        char_class = self.character.get('class', '')
        if 'Ladrón' not in char_class and 'Bardo' not in char_class:
            print(f"❌ {char_class} no tiene habilidades de ladrón")
            return None
        
        roll = self.d100(f"Habilidad: {skill_name}")
        
        if roll <= base_chance:
            print(f"   ✓ ÉXITO (necesitabas {base_chance}% o menos)")
            return True
        else:
            print(f"   ✗ FALLO (necesitabas {base_chance}% o menos)")
            return False
    
    def show_character_stats(self):
        """Muestra las estadísticas del personaje cargado"""
        if not self.character:
            print("❌ No hay personaje cargado")
            return
        
        print("\n" + "="*60)
        print(f"📊 ESTADÍSTICAS DE {self.character.get('name', 'PERSONAJE')}")
        print("="*60)
        
        # Atributos
        print("\nATRIBUTOS:")
        attrs = self.character.get('attributes', {})
        for attr, val in attrs.items():
            print(f"  {attr}: {val}")
        
        # Combate
        print(f"\nCOMBATE:")
        print(f"  PG: {self.character.get('hp_current', 0)}/{self.character.get('hp_max', 0)}")
        print(f"  CA: {self.character.get('ac', 10)}")
        print(f"  THAC0: {self.character.get('thac0', 20)}")
        
        # Salvaciones
        print(f"\nTIRADAS DE SALVACIÓN:")
        saves = self.character.get('saving_throws', {})
        for save, val in saves.items():
            print(f"  {save.capitalize()}: {val}+")
        
        # Armas equipadas
        equipped = self.character.get('equipped', {})
        if equipped.get('arma_principal'):
            print(f"\nARMAS EQUIPADAS:")
            wp = equipped['arma_principal']
            print(f"  Principal: {wp['nombre']} (Ataque: {wp['ataque']:+d}, Daño: {wp['daño']})")
            if equipped.get('arma_secundaria'):
                ws = equipped['arma_secundaria']
                print(f"  Secundaria: {ws['nombre']} (Ataque: {ws['ataque']:+d}, Daño: {ws['daño']})")
        
        print("="*60)


def main():
    """Menú interactivo del lanzador de dados"""
    roller = DiceRoller()
    
    print("\n" + "="*60)
    print("🎲 LANZADOR DE DADOS AD&D 2e")
    print("="*60)
    
    while True:
        print("\n" + "-"*60)
        print("MENÚ PRINCIPAL")
        print("-"*60)
        print("  [1] Cargar personaje")
        print("  [2] Tirada libre (XdY+Z)")
        print("  [3] Modo tiradas rápidas")
        print("  [4] d20 con bonus")
        print("  [5] d100 (percentil)")
        print("  [6] Chequeo de atributo")
        print("  [7] Tirada de salvación")
        print("  [8] Tirada de ataque")
        print("  [9] Tirada de daño")
        print("  [10] Iniciativa")
        print("  [11] Sorpresa")
        print("  [12] Expulsar no-muertos")
        print("  [13] Habilidad de ladrón")
        print("  [14] Ver estadísticas del personaje")
        print("  [0] Salir")
        
        choice = input("\nElige opción: ").strip()
        
        if choice == '0':
            print("\n¡Que la suerte te acompañe!")
            break
        
        elif choice == '1':
            # Buscar archivos JSON
            json_files = list(Path('.').glob('*_character.json'))
            if not json_files:
                print("\n❌ No hay personajes guardados")
            else:
                print("\n--- PERSONAJES DISPONIBLES ---")
                for i, f in enumerate(json_files, 1):
                    print(f"  [{i}] {f.stem.replace('_character', '')}")
                
                try:
                    idx = int(input("\nElige personaje: ").strip()) - 1
                    if 0 <= idx < len(json_files):
                        roller.load_character(json_files[idx])
                except (ValueError, IndexError):
                    print("❌ Opción inválida")
        
        elif choice == '2':
            dice = input("Dados (ej: 2d6+3): ").strip()
            reason = input("Razón (opcional): ").strip()
            roller.roll(dice, 0, reason)
        
        elif choice == '3':
            # Modo tiradas rápidas
            print("\n" + "="*60)
            print("⚡ MODO TIRADAS RÁPIDAS")
            print("="*60)
            print("Escribe la tirada directamente (ej: 2d6, 1d20+3)")
            print("Comandos especiales:")
            print("  d20, d12, d10, d8, d6, d4, d100 - Tirada simple")
            print("  ataque, daño, ini, salvacion - Tiradas de personaje")
            print("  stats - Ver estadísticas del personaje")
            print("  'salir' o 'q' para volver al menú")
            print("-"*60)
            
            while True:
                cmd = input("\n🎲 > ").strip().lower()
                
                if cmd in ['salir', 'q', 'exit', '']:
                    break
                
                # Comandos rápidos de dados simples
                elif cmd == 'd20':
                    roller.d20(0, "")
                elif cmd == 'd12':
                    roller.roll("1d12", 0, "")
                elif cmd == 'd10':
                    roller.roll("1d10", 0, "")
                elif cmd == 'd8':
                    roller.roll("1d8", 0, "")
                elif cmd == 'd6':
                    roller.roll("1d6", 0, "")
                elif cmd == 'd4':
                    roller.roll("1d4", 0, "")
                elif cmd == 'd100':
                    roller.d100("")
                
                # Comandos de personaje
                elif cmd in ['ataque', 'attack', 'att']:
                    roller.attack_roll()
                elif cmd in ['daño', 'dano', 'damage', 'dmg']:
                    roller.damage_roll()
                elif cmd in ['ini', 'initiative', 'iniciativa']:
                    roller.initiative()
                elif cmd in ['salvacion', 'save', 'ts']:
                    if roller.character:
                        saves = roller.character.get('saving_throws', {})
                        print(f"Tipos: {', '.join(saves.keys())}")
                        save_type = input("¿Cuál? ").strip()
                        roller.saving_throw(save_type)
                    else:
                        print("❌ Carga un personaje primero")
                elif cmd == 'stats':
                    roller.show_character_stats()
                
                # Tirada libre en formato XdY+Z
                elif 'd' in cmd:
                    roller.roll(cmd, 0, "")
                
                else:
                    print("❌ Comando no reconocido. Usa formato XdY+Z o comandos: d20, d6, ataque, etc.")
        
        elif choice == '4':
            try:
                bonus = int(input("Bonus (ej: +2, -1, 0): ").strip() or "0")
                reason = input("Razón (opcional): ").strip()
                roller.d20(bonus, reason)
            except ValueError:
                print("❌ Bonus inválido")
        
        elif choice == '5':
            reason = input("Razón (opcional): ").strip()
            roller.d100(reason)
        
        elif choice == '6':
            if not roller.character:
                print("❌ Debes cargar un personaje primero")
            else:
                print("\nAtributos: FUE, DES, CON, INT, SAB, CAR")
                attr = input("Atributo a chequear: ").strip()
                roller.ability_check(attr)
        
        elif choice == '7':
            if not roller.character:
                print("❌ Debes cargar un personaje primero")
            else:
                saves = roller.character.get('saving_throws', {})
                print(f"\nTipos: {', '.join(saves.keys())}")
                save = input("Tipo de salvación: ").strip()
                roller.saving_throw(save)
        
        elif choice == '8':
            if not roller.character:
                print("❌ Debes cargar un personaje primero")
            else:
                try:
                    bonus = int(input("Bonus adicional (0 para ninguno): ").strip() or "0")
                    roller.attack_roll(bonus=bonus)
                except ValueError:
                    print("❌ Bonus inválido")
        
        elif choice == '9':
            if not roller.character:
                print("❌ Debes cargar un personaje primero")
            else:
                try:
                    bonus = int(input("Bonus adicional (0 para ninguno): ").strip() or "0")
                    roller.damage_roll(bonus=bonus)
                except ValueError:
                    print("❌ Bonus inválido")
        
        elif choice == '10':
            roller.initiative()
        
        elif choice == '11':
            roller.surprise()
        
        elif choice == '12':
            roller.turn_undead()
        
        elif choice == '13':
            if not roller.character:
                print("❌ Debes cargar un personaje primero")
            else:
                skill = input("Nombre de la habilidad: ").strip()
                try:
                    chance = int(input("% de éxito base: ").strip())
                    roller.thief_skill(skill, chance)
                except ValueError:
                    print("❌ Porcentaje inválido")
        
        elif choice == '14':
            roller.show_character_stats()


if __name__ == "__main__":
    main()
