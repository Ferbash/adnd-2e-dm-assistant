"""
Party Manager - Sistema de gestión de grupo estilo RPG clásico
Maneja hasta 5 personajes con interfaz tipo Final Fantasy
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import copy

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))


class CharacterCard(tk.Frame):
    """Tarjeta de personaje individual estilo RPG"""
    
    def __init__(self, parent, char_data=None, on_select=None, position=0):
        super().__init__(parent, relief=tk.RAISED, borderwidth=2)
        self.char_data = char_data
        self.on_select = on_select
        self.position = position
        self.selected = False
        
        self.configure(bg='#2c3e50', cursor='hand2')
        self.bind('<Button-1>', self._on_click)
        
        if char_data:
            self._create_widgets()
        else:
            self._create_empty()
    
    def _on_click(self, event=None):
        """Manejar click en la tarjeta"""
        if self.char_data and self.on_select:
            self.on_select(self.position)
    
    def _create_empty(self):
        """Crear tarjeta vacía"""
        label = tk.Label(
            self,
            text="[ VACÍO ]\n\nClick para\ncargar personaje",
            font=('Courier New', 10),
            bg='#2c3e50',
            fg='#7f8c8d',
            justify=tk.CENTER
        )
        label.pack(expand=True, fill=tk.BOTH, padx=10, pady=20)
        label.bind('<Button-1>', self._on_click)
    
    def _create_widgets(self):
        """Crear widgets con datos del personaje"""
        char = self.char_data
        
        # Nombre y clase
        name_label = tk.Label(
            self,
            text=char['name'].upper(),
            font=('Courier New', 11, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        name_label.pack(pady=(5, 0))
        name_label.bind('<Button-1>', self._on_click)
        
        class_level = f"{char['class']} Nv.{char['level']}"
        class_label = tk.Label(
            self,
            text=class_level,
            font=('Courier New', 9),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        class_label.pack()
        class_label.bind('<Button-1>', self._on_click)
        
        # Stats frame
        stats_frame = tk.Frame(self, bg='#34495e')
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        stats_frame.bind('<Button-1>', self._on_click)
        
        # HP
        hp = char.get('hp', {})
        hp_current = hp.get('current', 0) if isinstance(hp, dict) else hp
        hp_max = hp.get('max', 0) if isinstance(hp, dict) else hp
        hp_percent = (hp_current / hp_max * 100) if hp_max > 0 else 0
        
        hp_color = '#27ae60' if hp_percent > 50 else '#e67e22' if hp_percent > 25 else '#e74c3c'
        
        hp_label = tk.Label(
            stats_frame,
            text=f"HP {hp_current}/{hp_max}",
            font=('Courier New', 9, 'bold'),
            bg='#34495e',
            fg=hp_color
        )
        hp_label.pack(side=tk.LEFT, padx=5)
        hp_label.bind('<Button-1>', self._on_click)
        
        # AC
        ac = char.get('ac', 10)
        ac_label = tk.Label(
            stats_frame,
            text=f"AC {ac}",
            font=('Courier New', 9, 'bold'),
            bg='#34495e',
            fg='#3498db'
        )
        ac_label.pack(side=tk.RIGHT, padx=5)
        ac_label.bind('<Button-1>', self._on_click)
        
        # Equipo principal
        equipped = char.get('equipped', {})
        weapon = equipped.get('arma_principal', 'Desarmado')
        weapon_label = tk.Label(
            self,
            text=f"⚔ {weapon[:15]}",
            font=('Courier New', 8),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        weapon_label.pack()
        weapon_label.bind('<Button-1>', self._on_click)
        
        # XP
        xp_label = tk.Label(
            self,
            text=f"XP: {char.get('experience', 0):,}",
            font=('Courier New', 8),
            bg='#2c3e50',
            fg='#f39c12'
        )
        xp_label.pack(pady=(0, 5))
        xp_label.bind('<Button-1>', self._on_click)
    
    def set_selected(self, selected: bool):
        """Marcar como seleccionada"""
        self.selected = selected
        if selected:
            self.configure(bg='#e74c3c', borderwidth=3)
        else:
            self.configure(bg='#2c3e50', borderwidth=2)
        
        # Actualizar bg de todos los widgets hijos
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg='#e74c3c' if selected else widget.cget('bg'))
            elif isinstance(widget, tk.Frame):
                widget.configure(bg='#e74c3c' if selected else '#34495e')
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg='#e74c3c' if selected else '#34495e')
    
    def update_data(self, char_data):
        """Actualizar datos del personaje"""
        self.char_data = char_data
        for widget in self.winfo_children():
            widget.destroy()
        if char_data:
            self._create_widgets()
        else:
            self._create_empty()


class PartyManager(tk.Tk):
    """Gestor principal de party"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Party Manager - AD&D 2e")
        self.geometry("1400x900")
        self.configure(bg='#1a1a1a')
        
        # Datos
        self.party: List[Optional[Dict]] = [None] * 5
        self.selected_index: Optional[int] = None
        self.character_files: List[Optional[Path]] = [None] * 5
        
        # UI
        self.char_cards: List[CharacterCard] = []
        
        self._create_ui()
        self._update_display()
    
    def _create_ui(self):
        """Crear interfaz principal"""
        
        # Header
        header = tk.Frame(self, bg='#16a085', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="⚔ PARTY MANAGER ⚔",
            font=('Courier New', 24, 'bold'),
            bg='#16a085',
            fg='#ecf0f1'
        )
        title.pack(expand=True)
        
        # Main container
        main = tk.Frame(self, bg='#1a1a1a')
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Character cards (4 visible)
        left_frame = tk.Frame(main, bg='#1a1a1a')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        cards_label = tk.Label(
            left_frame,
            text="PERSONAJES DEL GRUPO",
            font=('Courier New', 12, 'bold'),
            bg='#1a1a1a',
            fg='#ecf0f1'
        )
        cards_label.pack(pady=5)
        
        # Grid de 4 personajes (2x2)
        cards_grid = tk.Frame(left_frame, bg='#1a1a1a')
        cards_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar grid
        for i in range(2):
            cards_grid.grid_rowconfigure(i, weight=1)
            cards_grid.grid_columnconfigure(i, weight=1)
        
        # Crear 4 tarjetas
        for i in range(4):
            row = i // 2
            col = i % 2
            card = CharacterCard(
                cards_grid,
                char_data=None,
                on_select=self._select_character,
                position=i
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.char_cards.append(card)
        
        # Quinta tarjeta (abajo, centrada)
        fifth_frame = tk.Frame(left_frame, bg='#1a1a1a')
        fifth_frame.pack(fill=tk.X, padx=5, pady=5)
        
        card5 = CharacterCard(
            fifth_frame,
            char_data=None,
            on_select=self._select_character,
            position=4
        )
        card5.pack(expand=True, fill=tk.BOTH, padx=200)
        self.char_cards.append(card5)
        
        # Right: Detail panel
        right_frame = tk.Frame(main, bg='#2c3e50', width=450)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        self._create_detail_panel(right_frame)
        
        # Bottom: Action buttons
        self._create_action_buttons()
    
    def _create_detail_panel(self, parent):
        """Crear panel de detalles del personaje seleccionado"""
        
        header = tk.Label(
            parent,
            text="DETALLES",
            font=('Courier New', 14, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Scroll
        scroll_frame = tk.Frame(parent, bg='#2c3e50')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(scroll_frame, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        self.detail_content = tk.Frame(canvas, bg='#2c3e50')
        
        canvas.create_window((0, 0), window=self.detail_content, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_content.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        self._show_no_selection()
    
    def _create_action_buttons(self):
        """Crear botones de acción"""
        
        button_frame = tk.Frame(self, bg='#34495e')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_style = {
            'font': ('Courier New', 10, 'bold'),
            'bg': '#16a085',
            'fg': '#ecf0f1',
            'activebackground': '#1abc9c',
            'cursor': 'hand2',
            'pady': 10,
            'padx': 15
        }
        
        # Cargar personaje
        tk.Button(
            button_frame,
            text="📂 CARGAR PERSONAJE",
            command=self._load_character,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Guardar cambios
        tk.Button(
            button_frame,
            text="💾 GUARDAR CAMBIOS",
            command=self._save_all,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Remover personaje
        tk.Button(
            button_frame,
            text="❌ REMOVER",
            command=self._remove_character,
            bg='#e74c3c',
            activebackground='#c0392b',
            **{k: v for k, v in btn_style.items() if k not in ['bg', 'activebackground']}
        ).pack(side=tk.LEFT, padx=5)
        
        # Exportar party
        tk.Button(
            button_frame,
            text="📤 EXPORTAR PARTY",
            command=self._export_party,
            **btn_style
        ).pack(side=tk.RIGHT, padx=5)
        
        # Importar party
        tk.Button(
            button_frame,
            text="📥 IMPORTAR PARTY",
            command=self._import_party,
            **btn_style
        ).pack(side=tk.RIGHT, padx=5)
    
    def _select_character(self, index: int):
        """Seleccionar personaje"""
        if self.party[index] is None:
            # Cargar nuevo personaje
            self.selected_index = index
            self._load_character()
        else:
            # Seleccionar existente
            if self.selected_index is not None:
                self.char_cards[self.selected_index].set_selected(False)
            
            self.selected_index = index
            self.char_cards[index].set_selected(True)
            self._show_character_details()
    
    def _load_character(self):
        """Cargar personaje desde archivo"""
        if self.selected_index is None:
            messagebox.showwarning("Advertencia", "Selecciona una casilla primero")
            return
        
        filepath = filedialog.askopenfilename(
            title="Cargar Personaje",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            self.party[self.selected_index] = char_data
            self.character_files[self.selected_index] = Path(filepath)
            
            self._update_display()
            self._show_character_details()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar personaje:\n{e}")
    
    def _remove_character(self):
        """Remover personaje seleccionado"""
        if self.selected_index is None:
            messagebox.showwarning("Advertencia", "Selecciona un personaje primero")
            return
        
        if self.party[self.selected_index] is None:
            return
        
        char_name = self.party[self.selected_index]['name']
        
        if messagebox.askyesno("Confirmar", f"¿Remover a {char_name} del grupo?"):
            self.party[self.selected_index] = None
            self.character_files[self.selected_index] = None
            self.char_cards[self.selected_index].set_selected(False)
            self.selected_index = None
            
            self._update_display()
            self._show_no_selection()
    
    def _update_display(self):
        """Actualizar visualización de todas las tarjetas"""
        for i, card in enumerate(self.char_cards):
            card.update_data(self.party[i])
            if i == self.selected_index and self.party[i] is not None:
                card.set_selected(True)
    
    def _show_no_selection(self):
        """Mostrar mensaje cuando no hay selección"""
        for widget in self.detail_content.winfo_children():
            widget.destroy()
        
        msg = tk.Label(
            self.detail_content,
            text="Selecciona un personaje\npara ver sus detalles",
            font=('Courier New', 12),
            bg='#2c3e50',
            fg='#7f8c8d',
            justify=tk.CENTER
        )
        msg.pack(expand=True, pady=50)
    
    def _show_character_details(self):
        """Mostrar detalles del personaje seleccionado"""
        for widget in self.detail_content.winfo_children():
            widget.destroy()
        
        if self.selected_index is None or self.party[self.selected_index] is None:
            self._show_no_selection()
            return
        
        char = self.party[self.selected_index]
        
        # Nombre
        name_label = tk.Label(
            self.detail_content,
            text=char['name'].upper(),
            font=('Courier New', 16, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        name_label.pack(pady=10)
        
        # Clase y nivel
        class_info = f"{char['class']} - Nivel {char['level']}"
        tk.Label(
            self.detail_content,
            text=class_info,
            font=('Courier New', 11),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack()
        
        tk.Label(
            self.detail_content,
            text=f"{char['race']} - {char.get('alignment', 'N/A')}",
            font=('Courier New', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack(pady=(0, 10))
        
        # Stats editables
        self._create_stat_section("ESTADÍSTICAS", char)
        self._create_abilities_section("ATRIBUTOS", char)
        self._create_equipment_section("EQUIPO", char)
        self._create_spells_section("CONJUROS", char)
    
    def _create_stat_section(self, title: str, char: Dict):
        """Crear sección de estadísticas editables"""
        section = tk.LabelFrame(
            self.detail_content,
            text=title,
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            labelanchor='n'
        )
        section.pack(fill=tk.X, padx=10, pady=5)
        
        # HP
        hp_frame = tk.Frame(section, bg='#34495e')
        hp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            hp_frame,
            text="HP:",
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#27ae60',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        hp = char.get('hp', {})
        hp_current = hp.get('current', 0) if isinstance(hp, dict) else hp
        hp_max = hp.get('max', 0) if isinstance(hp, dict) else hp
        
        hp_current_var = tk.StringVar(value=str(hp_current))
        hp_entry = tk.Entry(
            hp_frame,
            textvariable=hp_current_var,
            font=('Courier New', 10),
            width=5,
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#ecf0f1'
        )
        hp_entry.pack(side=tk.LEFT, padx=5)
        hp_entry.bind('<FocusOut>', lambda e: self._update_stat('hp', 'current', hp_current_var.get()))
        
        tk.Label(
            hp_frame,
            text=f"/ {hp_max}",
            font=('Courier New', 10),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT)
        
        # XP
        xp_frame = tk.Frame(section, bg='#34495e')
        xp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            xp_frame,
            text="Experiencia:",
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#f39c12',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        xp_var = tk.StringVar(value=str(char.get('experience', 0)))
        xp_entry = tk.Entry(
            xp_frame,
            textvariable=xp_var,
            font=('Courier New', 10),
            width=10,
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#ecf0f1'
        )
        xp_entry.pack(side=tk.LEFT, padx=5)
        xp_entry.bind('<FocusOut>', lambda e: self._update_stat('experience', None, xp_var.get()))
        
        # AC (solo lectura)
        ac_frame = tk.Frame(section, bg='#34495e')
        ac_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            ac_frame,
            text="AC:",
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#3498db',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            ac_frame,
            text=str(char.get('ac', 10)),
            font=('Courier New', 10),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
        
        # THAC0 (solo lectura)
        thac0_frame = tk.Frame(section, bg='#34495e')
        thac0_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            thac0_frame,
            text="THAC0:",
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#e74c3c',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            thac0_frame,
            text=str(char.get('thac0', 20)),
            font=('Courier New', 10),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_abilities_section(self, title: str, char: Dict):
        """Crear sección de atributos"""
        section = tk.LabelFrame(
            self.detail_content,
            text=title,
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            labelanchor='n'
        )
        section.pack(fill=tk.X, padx=10, pady=5)
        
        abilities = char.get('abilities', {})
        ability_names = {
            'strength': 'FUE',
            'dexterity': 'DES',
            'constitution': 'CON',
            'intelligence': 'INT',
            'wisdom': 'SAB',
            'charisma': 'CAR'
        }
        
        for ability, abbr in ability_names.items():
            value = abilities.get(ability, 10)
            
            frame = tk.Frame(section, bg='#34495e')
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(
                frame,
                text=f"{abbr}:",
                font=('Courier New', 9, 'bold'),
                bg='#34495e',
                fg='#bdc3c7',
                width=5,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=str(value),
                font=('Courier New', 9),
                bg='#34495e',
                fg='#ecf0f1',
                width=3
            ).pack(side=tk.LEFT, padx=5)
    
    def _create_equipment_section(self, title: str, char: Dict):
        """Crear sección de equipo"""
        section = tk.LabelFrame(
            self.detail_content,
            text=title,
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            labelanchor='n'
        )
        section.pack(fill=tk.X, padx=10, pady=5)
        
        equipped = char.get('equipped', {})
        equipment = char.get('equipment', {})
        
        # Arma principal
        weapon = equipped.get('arma_principal', 'Ninguna')
        tk.Label(
            section,
            text=f"⚔ Arma: {weapon}",
            font=('Courier New', 9),
            bg='#34495e',
            fg='#ecf0f1',
            anchor='w'
        ).pack(fill=tk.X, padx=10, pady=2)
        
        # Armadura
        armor = equipped.get('armadura', 'Ninguna')
        tk.Label(
            section,
            text=f"🛡 Armadura: {armor}",
            font=('Courier New', 9),
            bg='#34495e',
            fg='#ecf0f1',
            anchor='w'
        ).pack(fill=tk.X, padx=10, pady=2)
        
        # Escudo
        shield = equipped.get('escudo', 'Ninguno')
        tk.Label(
            section,
            text=f"🛡 Escudo: {shield}",
            font=('Courier New', 9),
            bg='#34495e',
            fg='#ecf0f1',
            anchor='w'
        ).pack(fill=tk.X, padx=10, pady=2)
        
        # Inventario
        items = [item for item in equipment.keys() if item not in [weapon, armor, shield]]
        if items:
            tk.Label(
                section,
                text=f"📦 Items: {len(items)}",
                font=('Courier New', 9),
                bg='#34495e',
                fg='#95a5a6',
                anchor='w'
            ).pack(fill=tk.X, padx=10, pady=2)
    
    def _create_spells_section(self, title: str, char: Dict):
        """Crear sección de conjuros"""
        spells = char.get('spells', {})
        
        if not spells:
            return
        
        section = tk.LabelFrame(
            self.detail_content,
            text=title,
            font=('Courier New', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            labelanchor='n'
        )
        section.pack(fill=tk.X, padx=10, pady=5)
        
        for level, spell_list in sorted(spells.items()):
            if spell_list:
                tk.Label(
                    section,
                    text=f"Nivel {level}: {len(spell_list)} conjuros",
                    font=('Courier New', 9),
                    bg='#34495e',
                    fg='#9b59b6',
                    anchor='w'
                ).pack(fill=tk.X, padx=10, pady=2)
    
    def _update_stat(self, stat: str, subkey: Optional[str], value: str):
        """Actualizar estadística del personaje"""
        if self.selected_index is None or self.party[self.selected_index] is None:
            return
        
        try:
            char = self.party[self.selected_index]
            
            if subkey:
                # Stat compuesto (ej: hp.current)
                if stat not in char:
                    char[stat] = {}
                char[stat][subkey] = int(value)
            else:
                # Stat simple (ej: experience)
                char[stat] = int(value)
            
            # Actualizar visualización
            self._update_display()
            
        except ValueError:
            messagebox.showerror("Error", "Valor numérico inválido")
    
    def _save_all(self):
        """Guardar todos los personajes a sus archivos"""
        saved = 0
        
        for i, char in enumerate(self.party):
            if char is not None and self.character_files[i] is not None:
                try:
                    with open(self.character_files[i], 'w', encoding='utf-8') as f:
                        json.dump(char, f, indent=2, ensure_ascii=False)
                    saved += 1
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error al guardar {char['name']}:\n{e}"
                    )
        
        if saved > 0:
            messagebox.showinfo("Éxito", f"Se guardaron {saved} personaje(s)")
        else:
            messagebox.showwarning("Advertencia", "No hay personajes para guardar")
    
    def _export_party(self):
        """Exportar configuración del party"""
        active_chars = [i for i, char in enumerate(self.party) if char is not None]
        
        if not active_chars:
            messagebox.showwarning("Advertencia", "No hay personajes en el party")
            return
        
        filepath = filedialog.asksavedfilename(
            title="Exportar Party",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if not filepath:
            return
        
        try:
            party_data = {
                'party': [],
                'files': []
            }
            
            for i in range(5):
                if self.party[i] is not None:
                    party_data['party'].append(self.party[i])
                    party_data['files'].append(str(self.character_files[i]) if self.character_files[i] else None)
                else:
                    party_data['party'].append(None)
                    party_data['files'].append(None)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(party_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", "Party exportado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar party:\n{e}")
    
    def _import_party(self):
        """Importar configuración del party"""
        filepath = filedialog.askopenfilename(
            title="Importar Party",
            filetypes=[("JSON files", "*.json")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                party_data = json.load(f)
            
            self.party = party_data['party']
            self.character_files = [
                Path(f) if f else None
                for f in party_data['files']
            ]
            
            self._update_display()
            self._show_no_selection()
            
            messagebox.showinfo("Éxito", "Party importado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar party:\n{e}")


def main():
    app = PartyManager()
    app.mainloop()


if __name__ == '__main__':
    main()
