"""
🎲 AD&D 2e Dungeon Master Assistant - GUI
Interfaz gráfica profesional usando Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import sys
from pathlib import Path
from typing import Optional, List
import threading
import tempfile

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos del sistema
from core.dados import DiceRoller
from core.combate import CombatManager, MonsterDatabase, Combatant


class CharacterPanel(ttk.Frame):
    """Panel de gestión de personajes"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_character = None
        
        # Lista de personajes
        list_frame = ttk.LabelFrame(self, text="📋 Personajes Disponibles", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollable list
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.char_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set,
                                        font=('Consolas', 10), height=8)
        self.char_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.char_listbox.yview)
        
        self.char_listbox.bind('<Double-Button-1>', self.on_character_select)
        
        # Botón cargar
        ttk.Button(list_frame, text="🔄 Recargar Lista", 
                  command=self.load_character_list).pack(pady=5)
        
        # Panel de personaje actual
        current_frame = ttk.LabelFrame(self, text="👤 Personaje Activo", padding=10)
        current_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.char_info = tk.Text(current_frame, height=12, width=40, 
                                font=('Consolas', 9), wrap=tk.WORD, state=tk.DISABLED)
        self.char_info.pack(fill=tk.BOTH, expand=True)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(self, text="⚡ Acciones Rápidas", padding=10)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # HP buttons
        hp_frame = ttk.Frame(actions_frame)
        hp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(hp_frame, text="HP:").pack(side=tk.LEFT)
        
        for val in [-10, -5, -1, 1, 5, 10]:
            text = f"{val:+d}"
            ttk.Button(hp_frame, text=text, width=4,
                      command=lambda v=val: self.modify_hp(v)).pack(side=tk.LEFT, padx=1)
        
        # HP custom
        hp_custom = ttk.Frame(actions_frame)
        hp_custom.pack(fill=tk.X, pady=2)
        ttk.Label(hp_custom, text="HP =").pack(side=tk.LEFT)
        self.hp_entry = ttk.Entry(hp_custom, width=8)
        self.hp_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(hp_custom, text="✓", width=3,
                  command=self.set_hp).pack(side=tk.LEFT)
        
        # XP
        xp_frame = ttk.Frame(actions_frame)
        xp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(xp_frame, text="XP:").pack(side=tk.LEFT)
        self.xp_entry = ttk.Entry(xp_frame, width=10)
        self.xp_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(xp_frame, text="Añadir XP",
                  command=self.add_xp).pack(side=tk.LEFT)
        
        # Descanso
        ttk.Button(actions_frame, text="😴 Descanso Completo",
                  command=self.rest).pack(fill=tk.X, pady=2)
        
        # Guardar
        ttk.Button(actions_frame, text="💾 Guardar Cambios",
                  command=self.save_character).pack(fill=tk.X, pady=2)
        
        self.load_character_list()
    
    def load_character_list(self):
        """Carga lista de personajes"""
        self.char_listbox.delete(0, tk.END)
        
        char_dir = Path(__file__).parent
        for filepath in char_dir.glob("*_character.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                name = data.get('name', 'N/A')
                race = data.get('race', 'N/A')
                char_class = data.get('class', 'N/A')
                level = data.get('level', 1)
                hp = data.get('hp', {})
                hp_str = f"{hp.get('current', 0)}/{hp.get('max', 0)}"
                
                display = f"{name} [{race} {char_class} Nv.{level}] HP:{hp_str}"
                self.char_listbox.insert(tk.END, display)
                
            except Exception as e:
                self.char_listbox.insert(tk.END, f"Error: {filepath.name}")
    
    def on_character_select(self, event=None):
        """Carga personaje seleccionado"""
        selection = self.char_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        char_files = list(Path(__file__).parent.glob("*_character.json"))
        
        if idx < len(char_files):
            self.load_character(str(char_files[idx]))
    
    def load_character(self, filepath: str):
        """Carga un personaje"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.current_character = json.load(f)
            
            self.current_character['_filepath'] = filepath
            self.update_character_display()
            self.app.log(f"✅ Personaje cargado: {self.current_character.get('name')}")
            
            # Actualizar dice roller
            self.app.dice_roller.character = self.current_character
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando personaje: {e}")
    
    def update_character_display(self):
        """Actualiza la visualización del personaje"""
        if not self.current_character:
            self.char_info.config(state=tk.NORMAL)
            self.char_info.delete(1.0, tk.END)
            self.char_info.insert(1.0, "No hay personaje cargado")
            self.char_info.config(state=tk.DISABLED)
            return
        
        char = self.current_character
        hp = char.get('hp', {})
        attrs = char.get('attributes', {})
        equipped = char.get('equipped', {})
        
        info = f"""
╔══════════════════════════════════════╗
  {char.get('name', 'N/A'):^36}
╠══════════════════════════════════════╣
  {char.get('race', 'N/A')} • {char.get('class', 'N/A')} • Nv.{char.get('level', 1)}
  Alineamiento: {char.get('alignment', 'N/A')}
╠══════════════════════════════════════╣
  HP: {hp.get('current', 0)}/{hp.get('max', 0)}
  AC: {char.get('ac', 10)}
  THAC0: {char.get('thac0', 20)}
  XP: {char.get('experience', 0):,}
╠══════════════════════════════════════╣
  FUE: {attrs.get('FUE', 10):2d}  INT: {attrs.get('INT', 10):2d}  SAB: {attrs.get('SAB', 10):2d}
  DES: {attrs.get('DES', 10):2d}  CAR: {attrs.get('CAR', 10):2d}  CON: {attrs.get('CON', 10):2d}
╠══════════════════════════════════════╣
  Arma: {equipped.get('arma_principal', 'N/A')[:30]}
  Armadura: {equipped.get('armadura', 'N/A')[:30]}
╚══════════════════════════════════════╝
"""
        
        self.char_info.config(state=tk.NORMAL)
        self.char_info.delete(1.0, tk.END)
        self.char_info.insert(1.0, info)
        self.char_info.config(state=tk.DISABLED)
    
    def modify_hp(self, amount: int):
        """Modifica HP"""
        if not self.current_character:
            messagebox.showwarning("Advertencia", "No hay personaje cargado")
            return
        
        hp = self.current_character.get('hp', {})
        current = hp.get('current', 0)
        max_hp = hp.get('max', 0)
        
        new_hp = max(0, min(current + amount, max_hp))
        hp['current'] = new_hp
        
        self.update_character_display()
        self.app.log(f"HP modificado: {current} → {new_hp} ({amount:+d})")
        
        if new_hp == 0:
            messagebox.showwarning("¡Advertencia!", "¡Personaje inconsciente!")
    
    def set_hp(self):
        """Establece HP a valor específico"""
        if not self.current_character:
            return
        
        try:
            value = int(self.hp_entry.get())
            hp = self.current_character.get('hp', {})
            max_hp = hp.get('max', 0)
            
            hp['current'] = max(0, min(value, max_hp))
            self.update_character_display()
            self.hp_entry.delete(0, tk.END)
            self.app.log(f"HP establecido a: {hp['current']}/{max_hp}")
            
        except ValueError:
            messagebox.showerror("Error", "Valor inválido")
    
    def add_xp(self):
        """Añade XP"""
        if not self.current_character:
            return
        
        try:
            xp = int(self.xp_entry.get())
            current_xp = self.current_character.get('experience', 0)
            new_xp = current_xp + xp
            
            self.current_character['experience'] = new_xp
            self.update_character_display()
            self.xp_entry.delete(0, tk.END)
            self.app.log(f"XP añadido: +{xp:,} (Total: {new_xp:,})")
            
        except ValueError:
            messagebox.showerror("Error", "Valor inválido")
    
    def rest(self):
        """Descanso completo"""
        if not self.current_character:
            return
        
        hp = self.current_character.get('hp', {})
        old_hp = hp.get('current', 0)
        hp['current'] = hp.get('max', 0)
        
        self.update_character_display()
        self.app.log(f"😴 Descanso completo: HP {old_hp} → {hp['current']}")
    
    def save_character(self):
        """Guarda el personaje"""
        if not self.current_character:
            return
        
        try:
            filepath = self.current_character.get('_filepath')
            if not filepath:
                messagebox.showerror("Error", "No se encontró ruta del archivo")
                return
            
            # Remover campos temporales
            char_data = {k: v for k, v in self.current_character.items() 
                        if not k.startswith('_')}
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, indent=2, ensure_ascii=False)
            
            self.app.log(f"💾 Personaje guardado: {char_data.get('name')}")
            messagebox.showinfo("Éxito", "Personaje guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando: {e}")


class DicePanel(ttk.Frame):
    """Panel de dados"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Presets
        presets_frame = ttk.LabelFrame(self, text="🎲 Dados Rápidos", padding=10)
        presets_frame.pack(fill=tk.X, padx=5, pady=5)
        
        dice_types = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100']
        for i, dice in enumerate(dice_types):
            ttk.Button(presets_frame, text=dice, width=8,
                      command=lambda d=dice: self.roll_dice(f"1{d}")).grid(
                          row=i//4, column=i%4, padx=2, pady=2)
        
        # Custom roll
        custom_frame = ttk.LabelFrame(self, text="Tirada Personalizada", padding=10)
        custom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(custom_frame, text="Notación:").pack(side=tk.LEFT)
        self.dice_entry = ttk.Entry(custom_frame, width=15)
        self.dice_entry.pack(side=tk.LEFT, padx=5)
        self.dice_entry.bind('<Return>', lambda e: self.roll_custom())
        
        ttk.Button(custom_frame, text="🎲 Tirar",
                  command=self.roll_custom).pack(side=tk.LEFT)
        
        # Attack roll
        attack_frame = ttk.LabelFrame(self, text="⚔️ Tirada de Ataque", padding=10)
        attack_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # THAC0
        thac0_row = ttk.Frame(attack_frame)
        thac0_row.pack(fill=tk.X, pady=2)
        ttk.Label(thac0_row, text="THAC0:").pack(side=tk.LEFT)
        self.thac0_entry = ttk.Entry(thac0_row, width=8)
        self.thac0_entry.pack(side=tk.LEFT, padx=5)
        self.thac0_entry.insert(0, "20")
        
        # Bonuses
        bonus_row = ttk.Frame(attack_frame)
        bonus_row.pack(fill=tk.X, pady=2)
        ttk.Label(bonus_row, text="Bonus:").pack(side=tk.LEFT)
        self.attack_bonus_entry = ttk.Entry(bonus_row, width=8)
        self.attack_bonus_entry.pack(side=tk.LEFT, padx=5)
        self.attack_bonus_entry.insert(0, "0")
        
        ttk.Button(attack_frame, text="⚔️ Atacar",
                  command=self.roll_attack).pack(pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(self, text="📊 Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, 
                                                       font=('Consolas', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags para colores
        self.results_text.tag_config('critical', foreground='gold', font=('Consolas', 10, 'bold'))
        self.results_text.tag_config('fumble', foreground='red', font=('Consolas', 10, 'bold'))
        self.results_text.tag_config('success', foreground='green')
        self.results_text.tag_config('header', foreground='cyan', font=('Consolas', 10, 'bold'))
    
    def roll_dice(self, notation: str):
        """Tira dados"""
        try:
            result = self.app.dice_roller.roll(notation, 0, f"Tirada de {notation}")
            
            self.results_text.insert(tk.END, f"\n🎲 {notation}\n", 'header')
            self.results_text.insert(tk.END, f"Tiradas: {result['rolls']}\n")
            self.results_text.insert(tk.END, f"Total: {result['total']}\n", 'success')
            self.results_text.see(tk.END)
            
            self.app.log(f"🎲 {notation} = {result['total']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en tirada: {e}")
    
    def roll_custom(self):
        """Tira dados personalizados"""
        notation = self.dice_entry.get().strip()
        if notation:
            self.roll_dice(notation)
            self.dice_entry.delete(0, tk.END)
    
    def roll_attack(self):
        """Tirada de ataque"""
        try:
            thac0 = int(self.thac0_entry.get())
            bonus = int(self.attack_bonus_entry.get())
            
            result = self.app.dice_roller.roll("1d20", bonus, "Ataque")
            d20_roll = result['rolls'][0]
            total = result['total']
            ac_hit = thac0 - total
            
            self.results_text.insert(tk.END, f"\n⚔️ ATAQUE\n", 'header')
            self.results_text.insert(tk.END, f"d20: {d20_roll}\n")
            self.results_text.insert(tk.END, f"Bonus: {bonus:+d}\n")
            self.results_text.insert(tk.END, f"Total: {total}\n")
            
            if d20_roll == 20:
                self.results_text.insert(tk.END, "🎯 ¡CRÍTICO!\n", 'critical')
            elif d20_roll == 1:
                self.results_text.insert(tk.END, "💥 ¡PIFIA!\n", 'fumble')
            else:
                self.results_text.insert(tk.END, f"AC impactada: {ac_hit}\n", 'success')
            
            self.results_text.see(tk.END)
            self.app.log(f"⚔️ Ataque: d20={d20_roll}, Total={total}, AC={ac_hit}")
            
        except ValueError:
            messagebox.showerror("Error", "Valores inválidos")


class MonsterPanel(ttk.Frame):
    """Panel de monstruos"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.monster_db = MonsterDatabase()
        
        # Search
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_monsters())
        
        ttk.Button(search_frame, text="Buscar",
                  command=self.search_monsters).pack(side=tk.LEFT)
        
        # Filter by type
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Tipo:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar()
        types = ['Todos'] + sorted(set(m.get('type', 'Otro') 
                                      for m in self.monster_db.monsters.values()))
        self.type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var,
                                       values=types, width=18, state='readonly')
        self.type_combo.pack(side=tk.LEFT, padx=5)
        self.type_combo.current(0)
        self.type_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_by_type())
        
        # Monster list
        list_frame = ttk.LabelFrame(self, text="👹 Monstruos", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.monster_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set,
                                          font=('Consolas', 9))
        self.monster_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.monster_listbox.yview)
        
        self.monster_listbox.bind('<Double-Button-1>', self.show_monster_card)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📄 Ver Ficha",
                  command=self.show_monster_card).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="➕ Añadir al Combate",
                  command=self.add_to_combat).pack(side=tk.LEFT, padx=2)
        
        self.load_all_monsters()
    
    def load_all_monsters(self):
        """Carga todos los monstruos"""
        self.monster_listbox.delete(0, tk.END)
        
        for name, data in sorted(self.monster_db.monsters.items()):
            hd = data.get('hd', '1d8')
            ac = data.get('ac', 10)
            display = f"{name:30s} HD:{hd:8s} AC:{ac:2d}"
            self.monster_listbox.insert(tk.END, display)
    
    def search_monsters(self):
        """Busca monstruos"""
        query = self.search_entry.get().strip()
        if not query:
            self.load_all_monsters()
            return
        
        results = self.monster_db.search_monsters(query)
        
        self.monster_listbox.delete(0, tk.END)
        for name, data in results.items():
            hd = data.get('hd', '1d8')
            ac = data.get('ac', 10)
            display = f"{name:30s} HD:{hd:8s} AC:{ac:2d}"
            self.monster_listbox.insert(tk.END, display)
        
        self.app.log(f"🔍 Búsqueda '{query}': {len(results)} resultados")
    
    def filter_by_type(self):
        """Filtra por tipo"""
        type_selected = self.type_var.get()
        
        if type_selected == 'Todos':
            self.load_all_monsters()
            return
        
        results = self.monster_db.filter_by_type(type_selected)
        
        self.monster_listbox.delete(0, tk.END)
        for name, data in results.items():
            hd = data.get('hd', '1d8')
            ac = data.get('ac', 10)
            display = f"{name:30s} HD:{hd:8s} AC:{ac:2d}"
            self.monster_listbox.insert(tk.END, display)
        
        self.app.log(f"🔍 Filtro '{type_selected}': {len(results)} monstruos")
    
    def get_selected_monster_name(self) -> Optional[str]:
        """Obtiene nombre del monstruo seleccionado"""
        selection = self.monster_listbox.curselection()
        if not selection:
            return None
        
        text = self.monster_listbox.get(selection[0])
        # Extraer nombre (antes de HD:)
        name = text.split('HD:')[0].strip()
        return name
    
    def show_monster_card(self, event=None):
        """Muestra ficha del monstruo"""
        name = self.get_selected_monster_name()
        if not name:
            return
        
        # Crear ventana popup
        popup = tk.Toplevel(self)
        popup.title(f"Ficha de {name}")
        popup.geometry("500x600")
        
        # Text widget con scrollbar
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10),
                      yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        # Obtener datos del monstruo
        monster = self.monster_db.get_monster(name)
        if monster:
            card = f"""
╔══════════════════════════════════════════════════════╗
  {name:^50}
╠══════════════════════════════════════════════════════╣

TIPO: {monster.original_data.get('type', 'N/A')}
AMBIENTE: {monster.original_data.get('environment', 'N/A')}

ESTADÍSTICAS DE COMBATE:
  Clase de Armadura: {monster.ac}
  Dados de Golpe: {monster.hd}
  Puntos de Golpe: {monster.hp}
  THAC0: {monster.thac0}

ATAQUES:
  Número de Ataques: {monster.num_attacks}
  Daño: {', '.join(monster.attacks)}

CARACTERÍSTICAS:
  Movimiento: {monster.movement}
  Moral: {monster.morale}

HABILIDADES ESPECIALES:
{chr(10).join('  • ' + s for s in monster.special_abilities) if monster.special_abilities else '  Ninguna'}

INMUNIDADES:
{chr(10).join('  • ' + i for i in monster.immunities) if monster.immunities else '  Ninguna'}

VALOR EN XP: {monster.original_data.get('xp', 0):,}

╚══════════════════════════════════════════════════════╝
"""
            text.insert(1.0, card)
            text.config(state=tk.DISABLED)
        
        ttk.Button(popup, text="Cerrar", command=popup.destroy).pack(pady=5)
    
    def add_to_combat(self):
        """Añade monstruo al combate"""
        name = self.get_selected_monster_name()
        if not name:
            messagebox.showwarning("Advertencia", "Selecciona un monstruo primero")
            return
        
        if not self.app.combat_panel.combat_manager:
            response = messagebox.askyesno("Combate", 
                                          "No hay combate activo. ¿Iniciar uno?")
            if response:
                self.app.combat_panel.start_combat()
            else:
                return
        
        if self.app.combat_panel.combat_manager.add_monster(name):
            self.app.log(f"➕ {name} añadido al combate")
            self.app.combat_panel.update_combatants_list()
        else:
            messagebox.showerror("Error", f"No se pudo añadir {name}")


class CombatPanel(ttk.Frame):
    """Panel de combate"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.combat_manager: Optional[CombatManager] = None
        
        # Control buttons
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(ctrl_frame, text="⚔️ Iniciar Combate",
                  command=self.start_combat).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="🎲 Tirar Iniciativa",
                  command=self.roll_initiative).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="➡️ Siguiente Turno",
                  command=self.next_turn).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="❌ Terminar",
                  command=self.end_combat).pack(side=tk.LEFT, padx=2)
        
        # Combatants list
        list_frame = ttk.LabelFrame(self, text="👥 Combatientes", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for combatants
        columns = ('Nombre', 'HP', 'AC', 'THAC0', 'Iniciativa')
        self.combatants_tree = ttk.Treeview(list_frame, columns=columns,
                                            show='tree headings', height=10)
        
        for col in columns:
            self.combatants_tree.heading(col, text=col)
            self.combatants_tree.column(col, width=100)
        
        self.combatants_tree.pack(fill=tk.BOTH, expand=True)
        
        # Combat actions
        action_frame = ttk.LabelFrame(self, text="🎯 Acciones", padding=5)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="⚔️ Atacar",
                  command=self.attack_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="💊 Curar",
                  command=self.heal_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="🛡️ Salvación",
                  command=self.save_action).pack(side=tk.LEFT, padx=2)
        
        # Round info
        self.round_label = ttk.Label(self, text="Round: 0 | Turno: -",
                                    font=('Arial', 12, 'bold'))
        self.round_label.pack(pady=5)
    
    def start_combat(self):
        """Inicia combate"""
        self.combat_manager = CombatManager()
        
        # Añadir personaje si está cargado
        if self.app.char_panel.current_character:
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                            delete=False, encoding='utf-8') as f:
                char_data = {k: v for k, v in self.app.char_panel.current_character.items()
                           if not k.startswith('_')}
                json.dump(char_data, f, ensure_ascii=False, indent=2)
                temp_file = f.name
            
            if self.combat_manager.add_player(temp_file):
                self.app.log(f"✅ Personaje añadido al combate")
            
            # Limpiar
            try:
                os.unlink(temp_file)
            except:
                pass
        
        self.update_combatants_list()
        self.app.log("⚔️ Combate iniciado")
        messagebox.showinfo("Combate", "Combate iniciado. Añade enemigos y tira iniciativa.")
    
    def roll_initiative(self):
        """Tira iniciativa"""
        if not self.combat_manager:
            messagebox.showwarning("Advertencia", "No hay combate activo")
            return
        
        if len(self.combat_manager.combatants) < 2:
            messagebox.showwarning("Advertencia", "Se necesitan al menos 2 combatientes")
            return
        
        self.combat_manager.start_combat()
        self.update_combatants_list()
        self.update_round_label()
        self.app.log("🎲 Iniciativa tirada")
    
    def next_turn(self):
        """Siguiente turno"""
        if not self.combat_manager or self.combat_manager.round_number == 0:
            messagebox.showwarning("Advertencia", "Primero tira iniciativa")
            return
        
        # Verificar fin
        end_msg = self.combat_manager.check_combat_end()
        if end_msg:
            messagebox.showinfo("Combate Terminado", end_msg)
            self.app.log(end_msg)
            return
        
        self.combat_manager.next_turn()
        self.update_round_label()
        
        current = self.combat_manager.get_current_combatant()
        if current:
            self.app.log(f"🎯 Turno de: {current.name}")
    
    def end_combat(self):
        """Termina combate"""
        if not self.combat_manager:
            return
        
        # Actualizar HP del personaje
        if self.app.char_panel.current_character:
            for c in self.combat_manager.combatants:
                if c.is_player:
                    name = self.app.char_panel.current_character.get('name')
                    if c.name == name:
                        self.app.char_panel.current_character['hp']['current'] = c.hp
                        self.app.char_panel.update_character_display()
                        self.app.char_panel.save_character()
        
        self.combat_manager = None
        self.update_combatants_list()
        self.round_label.config(text="Round: 0 | Turno: -")
        self.app.log("❌ Combate terminado")
    
    def update_combatants_list(self):
        """Actualiza lista de combatientes"""
        # Limpiar
        for item in self.combatants_tree.get_children():
            self.combatants_tree.delete(item)
        
        if not self.combat_manager:
            return
        
        # Añadir combatientes
        for i, c in enumerate(self.combat_manager.combatants):
            if c.is_alive:
                icon = "👤" if c.is_player else "👹"
                hp_str = f"{c.hp}/{c.max_hp}"
                
                values = (c.name, hp_str, c.ac, c.thac0, c.initiative)
                
                # Resaltar turno actual
                tag = 'current' if (self.combat_manager.initiative_order and 
                                   self.combat_manager.current_turn_index < len(self.combat_manager.initiative_order) and
                                   self.combat_manager.initiative_order[self.combat_manager.current_turn_index] == c) else ''
                
                self.combatants_tree.insert('', tk.END, text=icon, values=values, tags=(tag,))
        
        # Estilo para turno actual
        self.combatants_tree.tag_configure('current', background='lightblue')
    
    def update_round_label(self):
        """Actualiza etiqueta de round"""
        if not self.combat_manager or self.combat_manager.round_number == 0:
            self.round_label.config(text="Round: 0 | Turno: -")
            return
        
        current = self.combat_manager.get_current_combatant()
        turn_name = current.name if current else "Fin"
        
        self.round_label.config(
            text=f"Round: {self.combat_manager.round_number} | Turno: {turn_name}")
    
    def attack_action(self):
        """Acción de ataque"""
        if not self.combat_manager or self.combat_manager.round_number == 0:
            messagebox.showwarning("Advertencia", "No hay combate activo")
            return
        
        current = self.combat_manager.get_current_combatant()
        if not current:
            messagebox.showwarning("Advertencia", "No hay combatiente activo")
            return
        
        # Seleccionar objetivo
        enemies = [c for c in self.combat_manager.combatants if c != current and c.is_alive]
        if not enemies:
            messagebox.showwarning("Advertencia", "No hay objetivos válidos")
            return
        
        # Diálogo de selección
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar Objetivo")
        dialog.geometry("300x400")
        
        ttk.Label(dialog, text="Selecciona objetivo:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=('Consolas', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for e in enemies:
            listbox.insert(tk.END, f"{e.name} (HP: {e.hp}/{e.max_hp}, AC: {e.ac})")
        
        def do_attack():
            selection = listbox.curselection()
            if not selection:
                return
            
            target = enemies[selection[0]]
            result = self.combat_manager.make_attack(current, target)
            
            self.app.log(result['message'])
            messagebox.showinfo("Resultado", result['message'])
            
            self.update_combatants_list()
            dialog.destroy()
        
        ttk.Button(dialog, text="⚔️ Atacar", command=do_attack).pack(pady=5)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).pack(pady=5)
    
    def heal_action(self):
        """Acción de curación"""
        if not self.combat_manager:
            return
        
        current = self.combat_manager.get_current_combatant()
        if not current:
            return
        
        # Diálogo para cantidad
        amount = tk.simpledialog.askinteger("Curación", 
                                           f"Cantidad de HP a curar para {current.name}:",
                                           minvalue=1, maxvalue=100)
        if amount:
            msg = current.heal(amount)
            self.app.log(msg)
            self.update_combatants_list()
    
    def save_action(self):
        """Tirada de salvación"""
        if not self.combat_manager:
            return
        
        current = self.combat_manager.get_current_combatant()
        if not current:
            return
        
        # Diálogo de tipo
        dialog = tk.Toplevel(self)
        dialog.title("Tirada de Salvación")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Tipo de salvación:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        save_types = [
            "Paralización, Veneno o Muerte por Magia",
            "Varita Mágica",
            "Petrificación o Transformación",
            "Soplo de Dragón",
            "Conjuro, Bastón o Vara"
        ]
        
        listbox = tk.Listbox(dialog, font=('Arial', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for st in save_types:
            listbox.insert(tk.END, st)
        
        def do_save():
            selection = listbox.curselection()
            if not selection:
                return
            
            save_type = save_types[selection[0]]
            result = self.combat_manager.make_saving_throw(current, save_type)
            
            self.app.log(result['message'])
            messagebox.showinfo("Resultado", result['message'])
            dialog.destroy()
        
        ttk.Button(dialog, text="🎲 Tirar", command=do_save).pack(pady=5)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).pack(pady=5)


class DMAssistantGUI:
    """Aplicación principal GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚔️ AD&D 2e DM Assistant")
        self.root.geometry("1400x900")
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dice roller
        self.dice_roller = DiceRoller()
        
        # Menu bar
        self.create_menu()
        
        # Main container
        main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Characters
        self.char_panel = CharacterPanel(main_container, self)
        main_container.add(self.char_panel, weight=1)
        
        # Center notebook
        center_notebook = ttk.Notebook(main_container)
        main_container.add(center_notebook, weight=3)
        
        # Tabs
        self.dice_panel = DicePanel(center_notebook, self)
        center_notebook.add(self.dice_panel, text="🎲 Dados")
        
        self.combat_panel = CombatPanel(center_notebook, self)
        center_notebook.add(self.combat_panel, text="⚔️ Combate")
        
        self.monster_panel = MonsterPanel(center_notebook, self)
        center_notebook.add(self.monster_panel, text="👹 Monstruos")
        
        # Right panel - Log
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        log_frame = ttk.LabelFrame(right_panel, text="📜 Registro de Actividad", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=40, 
                                                  font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(root, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Welcome message
        self.log("="*60)
        self.log("⚔️ AD&D 2e DM Assistant - Interfaz Gráfica")
        self.log("="*60)
        self.log("Bienvenido! Carga un personaje para comenzar.")
        self.log("")
    
    def create_menu(self):
        """Crea barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
    
    def log(self, message: str):
        """Añade mensaje al log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def show_about(self):
        """Muestra ventana Acerca de"""
        about_text = """
AD&D 2e DM Assistant
Versión 2.0

Sistema completo de gestión de partidas
para Advanced Dungeons & Dragons 2ª Edición.

Características:
• Gestión de personajes
• Sistema de dados completo
• Base de datos de 100+ monstruos
• Gestor de combate con iniciativa
• Auto-guardado de cambios

Desarrollado en Python con Tkinter
"""
        messagebox.showinfo("Acerca de", about_text)


def main():
    """Punto de entrada"""
    root = tk.Tk()
    app = DMAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
