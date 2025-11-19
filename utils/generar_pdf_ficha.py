"""
Generador de PDF de personaje AD&D 2e usando la ficha oficial como fondo
"""

import fitz  # PyMuPDF
import json
import sys
from pathlib import Path

class CharacterSheetGenerator:
    """Genera PDF de personaje usando la ficha oficial AD&D 2e como plantilla"""
    
    def __init__(self, template_pdf="AD&D_2e_Character_Record_Sheet.pdf"):
        self.template_pdf = template_pdf
        
    def generate_sheet(self, character_data, output_filename="personaje_ficha.pdf"):
        """Genera la ficha de personaje rellenando la plantilla"""
        
        # Abrir la plantilla
        doc = fitz.open(self.template_pdf)
        page = doc[0]  # Primera página
        
        # Configuración de fuente
        fontsize = 10
        font = "helv"  # Helvetica
        
        # ===== INFORMACIÓN BÁSICA =====
        # Character name (arriba a la izquierda)
        page.insert_text((260, 72), character_data.get('name', ''), 
                        fontsize=11, fontname=font)
        
        # Player name (arriba a la derecha)
        page.insert_text((830, 72), character_data.get('player', 'Jugador'), 
                        fontsize=10, fontname=font)
        
        # Race
        page.insert_text((160, 145), character_data.get('race', ''), 
                        fontsize=10, fontname=font)
        
        # Class/Kit
        page.insert_text((400, 145), character_data.get('class', ''), 
                        fontsize=10, fontname=font)
        
        # Level
        page.insert_text((1030, 145), str(character_data.get('level', 1)), 
                        fontsize=10, fontname=font)
        
        # Alignment
        page.insert_text((110, 185), character_data.get('alignment', 'Neutral'), 
                        fontsize=9, fontname=font)
        
        # Sex, Age, Height, Weight
        page.insert_text((290, 185), character_data.get('sex', 'M'), 
                        fontsize=9, fontname=font)
        page.insert_text((360, 185), str(character_data.get('age', 25)), 
                        fontsize=9, fontname=font)
        page.insert_text((450, 185), character_data.get('height', '1.75m'), 
                        fontsize=9, fontname=font)
        page.insert_text((550, 185), character_data.get('weight', '75kg'), 
                        fontsize=9, fontname=font)
        
        # ===== ATRIBUTOS (columna izquierda) =====
        # Posiciones basadas en la ficha real
        attrs = character_data.get('attributes', {})
        attr_positions = {
            'STR': (145, 530),   # Strength
            'DEX': (145, 615),   # Dexterity
            'CON': (145, 700),   # Constitution
            'INT': (145, 770),   # Intelligence
            'WIS': (145, 840),   # Wisdom (SAB)
            'CHA': (145, 910),   # Charisma
        }
        
        # Mapeo de nombres en español a inglés
        attr_map = {
            'FUE': 'STR',
            'DES': 'DEX',
            'CON': 'CON',
            'INT': 'INT',
            'SAB': 'WIS',
            'CAR': 'CHA'
        }
        
        for esp_name, eng_name in attr_map.items():
            if esp_name in attrs and eng_name in attr_positions:
                x, y = attr_positions[eng_name]
                page.insert_text((x, y), str(attrs[esp_name]), 
                               fontsize=16, fontname=font, color=(1, 0, 0))  # Rojo para destacar
        
        # ===== COMBATE =====
        # HP (Hit Points) - arriba a la derecha
        hp_current = character_data.get('hp_current', 0)
        hp_max = character_data.get('hp_max', 0)
        page.insert_text((950, 340), f"{hp_current}/{hp_max}", 
                        fontsize=11, fontname=font)
        
        # AC (Armor Class)
        page.insert_text((950, 375), str(character_data.get('ac', 10)), 
                        fontsize=11, fontname=font)
        
        # THAC0
        page.insert_text((950, 410), str(character_data.get('thac0', 20)), 
                        fontsize=11, fontname=font)
        
        # ===== TIRADAS DE SALVACIÓN =====
        saves = character_data.get('saving_throws', {})
        save_positions = {
            'paralisis': (950, 530),
            'varitas': (950, 565),
            'petrificacion': (950, 600),
            'aliento': (950, 635),
            'conjuros': (950, 670),
        }
        
        for save_name, (x, y) in save_positions.items():
            if save_name in saves:
                page.insert_text((x, y), str(saves[save_name]), 
                               fontsize=10, fontname=font)
        
        # ===== ARMAS EQUIPADAS =====
        equipped = character_data.get('equipped', {})
        y_pos = 530
        
        if equipped.get('arma_principal'):
            weapon = equipped['arma_principal']
            page.insert_text((350, y_pos), weapon.get('nombre', ''), 
                           fontsize=9, fontname=font)
            page.insert_text((550, y_pos), f"+{weapon.get('ataque', 0)}", 
                           fontsize=9, fontname=font)
            page.insert_text((620, y_pos), weapon.get('daño', ''), 
                           fontsize=9, fontname=font)
            y_pos += 35
        
        if equipped.get('arma_secundaria'):
            weapon = equipped['arma_secundaria']
            page.insert_text((350, y_pos), weapon.get('nombre', ''), 
                           fontsize=9, fontname=font)
            page.insert_text((550, y_pos), f"+{weapon.get('ataque', 0)}", 
                           fontsize=9, fontname=font)
            page.insert_text((620, y_pos), weapon.get('daño', ''), 
                           fontsize=9, fontname=font)
        
        # ===== ARMADURA Y ESCUDO =====
        if equipped.get('armadura'):
            armor = equipped['armadura']
            page.insert_text((350, 680), f"{armor.get('nombre', '')} (CA {armor.get('ca', 10)})", 
                           fontsize=8, fontname=font)
        
        if equipped.get('escudo'):
            shield = equipped['escudo']
            page.insert_text((350, 700), f"{shield.get('nombre', '')} ({shield.get('ca_bonus', -1):+d})", 
                           fontsize=8, fontname=font)
        
        # ===== EQUIPO (segunda página) =====
        if len(doc) > 1:
            page2 = doc[1]
            
            # Pericias
            proficiencies = character_data.get('proficiencies', {})
            y_pos = 100
            
            # Pericias de armas
            if proficiencies.get('armas'):
                page2.insert_text((50, y_pos), "=== PERICIAS DE ARMAS ===", 
                                fontsize=10, fontname=font, color=(0.2, 0.2, 0.2))
                y_pos += 20
                for prof in proficiencies['armas']:
                    page2.insert_text((60, y_pos), f"• {prof}", 
                                    fontsize=9, fontname=font)
                    y_pos += 15
                y_pos += 10
            
            # Pericias de no-armas
            if proficiencies.get('no_armas'):
                page2.insert_text((50, y_pos), "=== PERICIAS DE NO-ARMAS ===", 
                                fontsize=10, fontname=font, color=(0.2, 0.2, 0.2))
                y_pos += 20
                for prof in proficiencies['no_armas']:
                    page2.insert_text((60, y_pos), f"• {prof}", 
                                    fontsize=9, fontname=font)
                    y_pos += 15
                y_pos += 20
            
            # Equipo
            equipment = character_data.get('equipment', [])
            if equipment:
                page2.insert_text((50, y_pos), "=== EQUIPO ===", 
                                fontsize=10, fontname=font, color=(0.2, 0.2, 0.2))
                y_pos += 20
                for item in equipment[:20]:  # Máximo 20 items
                    page2.insert_text((60, y_pos), f"• {item}", 
                                    fontsize=9, fontname=font)
                    y_pos += 15
            
            # Hechizos conocidos
            known_spells = character_data.get('known_spells', [])
            if known_spells:
                y_pos = 100
                x_pos = 320
                page2.insert_text((x_pos, y_pos), "=== HECHIZOS CONOCIDOS ===", 
                                fontsize=10, fontname=font, color=(0.2, 0.2, 0.2))
                y_pos += 20
                for spell in known_spells[:15]:
                    page2.insert_text((x_pos + 10, y_pos), f"• {spell}", 
                                    fontsize=9, fontname=font)
                    y_pos += 15
        
        # Guardar el PDF
        output_path = Path(output_filename)
        doc.save(output_path)
        doc.close()
        
        print(f"✓ Ficha de personaje generada: {output_path}")
        return output_path


def main():
    """Función principal para generar PDF desde JSON o archivo de personaje"""
    
    if len(sys.argv) < 2:
        print("Uso: python generar_pdf_ficha.py <archivo_personaje.json>")
        print("   o: python generar_pdf_ficha.py <nombre_personaje.pkl>")
        return
    
    input_file = sys.argv[1]
    
    # Determinar si es JSON o pickle
    if input_file.endswith('.json'):
        with open(input_file, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
    elif input_file.endswith('.pkl'):
        import pickle
        with open(input_file, 'rb') as f:
            character_obj = pickle.load(f)
            # Convertir objeto Character a diccionario
            character_data = {
                'name': character_obj.name,
                'race': character_obj.race,
                'class': character_obj.character_class,
                'level': character_obj.level,
                'attributes': character_obj.attributes,
                'hp_current': character_obj.hit_points_current,
                'hp_max': character_obj.hit_points_max,
                'ac': character_obj.armor_class,
                'thac0': character_obj.thac0,
                'saving_throws': character_obj.saving_throws,
                'proficiencies': character_obj.proficiencies,
                'equipment': character_obj.equipment,
                'equipped': character_obj.equipped,
                'known_spells': character_obj.known_spells,
                'player': 'Jugador',
                'alignment': 'Neutral',
                'sex': 'M',
                'age': 25,
                'height': '1.75m',
                'weight': '75kg'
            }
    else:
        print("❌ Formato no soportado. Use .json o .pkl")
        return
    
    # Generar ficha
    generator = CharacterSheetGenerator()
    output_name = f"{character_data.get('name', 'personaje')}_ficha.pdf"
    generator.generate_sheet(character_data, output_name)


if __name__ == "__main__":
    main()
