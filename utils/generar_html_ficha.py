"""
Generador de ficha de personaje AD&D 2e en HTML
Crea una ficha visual completa con todos los datos del personaje
"""

import json
import sys
from pathlib import Path


def generate_html_sheet(character_data, output_filename="personaje_ficha.html"):
    """Genera una ficha de personaje en HTML con estilo AD&D 2e"""
    
    # Obtener datos del personaje
    name = character_data.get('name', 'Sin Nombre')
    race = character_data.get('race', '')
    char_class = character_data.get('class', '')
    level = character_data.get('level', 1)
    attrs = character_data.get('attributes', {})
    hp_current = character_data.get('hp_current', 0)
    hp_max = character_data.get('hp_max', 0)
    ac = character_data.get('ac', 10)
    thac0 = character_data.get('thac0', 20)
    saves = character_data.get('saving_throws', {})
    profs = character_data.get('proficiencies', {})
    equipment = character_data.get('equipment', [])
    equipped = character_data.get('equipped', {})
    money = character_data.get('money', {})
    spells = character_data.get('known_spells', [])
    
    # Calcular modificadores de atributos
    def get_modifier(score):
        return (score - 10) // 2
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ficha de {name}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:wght@400;600&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            font-family: 'Crimson Text', serif;
            padding: 20px;
            color: #2c2c2c;
        }}
        
        .character-sheet {{
            max-width: 1200px;
            margin: 0 auto;
            background: linear-gradient(to bottom, #f4e8d0 0%, #ede0c8 100%);
            border: 8px solid #2c1810;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 0 100px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 4px double #8b0000;
            padding-bottom: 20px;
            margin-bottom: 25px;
            background: linear-gradient(to right, #8b0000, #b22222, #8b0000);
            color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 5px 15px rgba(139, 0, 0, 0.4);
        }}
        
        .character-name {{
            font-family: 'Cinzel', serif;
            font-size: 48px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}
        
        .character-title {{
            font-size: 24px;
            font-weight: 600;
            color: #ffd700;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .info-bar {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background: rgba(139, 0, 0, 0.1);
            border: 2px solid #8b0000;
            border-radius: 5px;
        }}
        
        .info-item {{
            text-align: center;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #8b0000;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .info-value {{
            font-size: 22px;
            font-weight: 700;
            color: #2c1810;
            margin-top: 5px;
        }}
        
        .main-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .section {{
            background: white;
            border: 3px solid #2c1810;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .section-title {{
            font-family: 'Cinzel', serif;
            font-size: 20px;
            font-weight: 700;
            color: #8b0000;
            border-bottom: 2px solid #8b0000;
            padding-bottom: 8px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .attribute {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: linear-gradient(to right, #f9f5f0, #fff);
            border-left: 4px solid #8b0000;
            border-radius: 4px;
        }}
        
        .attr-name {{
            font-weight: 700;
            color: #8b0000;
            font-size: 16px;
            letter-spacing: 1px;
        }}
        
        .attr-value {{
            font-size: 28px;
            font-weight: 700;
            color: #2c1810;
            text-align: center;
            min-width: 50px;
        }}
        
        .attr-modifier {{
            font-size: 16px;
            color: #666;
            font-weight: 600;
        }}
        
        .combat-stat {{
            background: linear-gradient(135deg, #8b0000, #b22222);
            color: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .combat-label {{
            font-size: 14px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .combat-value {{
            font-size: 36px;
            font-weight: 700;
            margin-top: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .saves-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        
        .save-item {{
            padding: 10px;
            background: #f9f5f0;
            border: 2px solid #8b0000;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .save-name {{
            font-weight: 600;
            color: #2c1810;
            text-transform: capitalize;
        }}
        
        .save-value {{
            font-size: 20px;
            font-weight: 700;
            color: #8b0000;
        }}
        
        .weapon-item {{
            background: #f9f5f0;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #b22222;
            border-radius: 4px;
        }}
        
        .weapon-name {{
            font-weight: 700;
            font-size: 16px;
            color: #2c1810;
            margin-bottom: 5px;
        }}
        
        .weapon-stats {{
            display: flex;
            gap: 15px;
            font-size: 14px;
            color: #666;
        }}
        
        .weapon-stat {{
            font-weight: 600;
        }}
        
        .equipment-list {{
            list-style: none;
            padding: 0;
        }}
        
        .equipment-item {{
            padding: 8px 12px;
            margin: 5px 0;
            background: #f9f5f0;
            border-left: 3px solid #8b0000;
            border-radius: 3px;
            font-size: 14px;
        }}
        
        .proficiency-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .prof-badge {{
            background: #8b0000;
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .money-display {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }}
        
        .coin {{
            background: linear-gradient(135deg, #ffd700, #ffed4e);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #b8860b;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .coin-amount {{
            font-size: 20px;
            font-weight: 700;
            color: #2c1810;
        }}
        
        .coin-type {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        
        .spell-list {{
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .spell-item {{
            padding: 8px;
            margin: 5px 0;
            background: linear-gradient(to right, #f0e6ff, #fff);
            border-left: 3px solid #4b0082;
            border-radius: 3px;
            font-size: 14px;
        }}
        
        .bottom-section {{
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .character-sheet {{
                box-shadow: none;
                border: 2px solid black;
            }}
        }}
    </style>
</head>
<body>
    <div class="character-sheet">
        <div class="header">
            <div class="character-name">{name}</div>
            <div class="character-title">{race} {char_class} - Nivel {level}</div>
        </div>
        
        <div class="info-bar">
            <div class="info-item">
                <div class="info-label">Puntos de Golpe</div>
                <div class="info-value">{hp_current} / {hp_max}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Clase de Armadura</div>
                <div class="info-value">{ac}</div>
            </div>
            <div class="info-item">
                <div class="info-label">THAC0</div>
                <div class="info-value">{thac0}</div>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Columna Izquierda: Atributos -->
            <div class="section">
                <div class="section-title">Atributos</div>
                <div class="attribute">
                    <span class="attr-name">FUE</span>
                    <span class="attr-value">{attrs.get('FUE', 10)}</span>
                    <span class="attr-modifier">({get_modifier(attrs.get('FUE', 10)):+d})</span>
                </div>
                <div class="attribute">
                    <span class="attr-name">DES</span>
                    <span class="attr-value">{attrs.get('DES', 10)}</span>
                    <span class="attr-modifier">({get_modifier(attrs.get('DES', 10)):+d})</span>
                </div>
                <div class="attribute">
                    <span class="attr-name">CON</span>
                    <span class="attr-value">{attrs.get('CON', 10)}</span>
                    <span class="attr-modifier">({get_modifier(attrs.get('CON', 10)):+d})</span>
                </div>
                <div class="attribute">
                    <span class="attr-name">INT</span>
                    <span class="attr-value">{attrs.get('INT', 10)}</span>
                    <span class="attr-modifier">({get_modifier(attrs.get('INT', 10)):+d})</span>
                </div>
                <div class="attribute">
                    <span class="attr-name">SAB</span>
                    <span class="attr-value">{attrs.get('SAB', 10)}</span>
                    <span class="attr-modifier">({get_modifier(attrs.get('SAB', 10)):+d})</span>
                </div>
                <div class="attribute">
                    <span class="attr-name">CAR</span>
                    <span class="attr-value">{attrs.get('CAR', 10)}</span>
                    <span class="attr-modifier">({get_modifier(attrs.get('CAR', 10)):+d})</span>
                </div>
            </div>
            
            <!-- Columna Central: Combate y Armas -->
            <div>
                <div class="section">
                    <div class="section-title">Tiradas de Salvación</div>
                    <div class="saves-grid">
                        <div class="save-item">
                            <span class="save-name">Parálisis</span>
                            <span class="save-value">{saves.get('paralisis', 14)}</span>
                        </div>
                        <div class="save-item">
                            <span class="save-name">Varitas</span>
                            <span class="save-value">{saves.get('varitas', 16)}</span>
                        </div>
                        <div class="save-item">
                            <span class="save-name">Petrificación</span>
                            <span class="save-value">{saves.get('petrificacion', 15)}</span>
                        </div>
                        <div class="save-item">
                            <span class="save-name">Aliento</span>
                            <span class="save-value">{saves.get('aliento', 17)}</span>
                        </div>
                        <div class="save-item">
                            <span class="save-name">Conjuros</span>
                            <span class="save-value">{saves.get('conjuros', 17)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="section" style="margin-top: 20px;">
                    <div class="section-title">Armas Equipadas</div>
                    {f'''<div class="weapon-item">
                        <div class="weapon-name">⚔️ {equipped['arma_principal']['nombre']}</div>
                        <div class="weapon-stats">
                            <span class="weapon-stat">Ataque: {equipped['arma_principal']['ataque']:+d}</span>
                            <span class="weapon-stat">Daño: {equipped['arma_principal']['daño']}</span>
                        </div>
                    </div>''' if equipped.get('arma_principal') else '<p style="color: #999; font-style: italic;">Sin arma equipada</p>'}
                    
                    {f'''<div class="weapon-item">
                        <div class="weapon-name">🗡️ {equipped['arma_secundaria']['nombre']}</div>
                        <div class="weapon-stats">
                            <span class="weapon-stat">Ataque: {equipped['arma_secundaria']['ataque']:+d}</span>
                            <span class="weapon-stat">Daño: {equipped['arma_secundaria']['daño']}</span>
                        </div>
                    </div>''' if equipped.get('arma_secundaria') else ''}
                    
                    {f'''<div style="margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                        <strong>🛡️ Armadura:</strong> {equipped['armadura']['nombre']} (CA {equipped['armadura']['ca']})
                    </div>''' if equipped.get('armadura') else ''}
                    
                    {f'''<div style="margin-top: 5px; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                        <strong>🛡️ Escudo:</strong> {equipped['escudo']['nombre']} ({equipped['escudo']['ca_bonus']:+d} CA)
                    </div>''' if equipped.get('escudo') else ''}
                </div>
            </div>
            
            <!-- Columna Derecha: Dinero -->
            <div class="section">
                <div class="section-title">Dinero</div>
                <div class="money-display">
                    <div class="coin">
                        <div class="coin-amount">{money.get('po', 0)}</div>
                        <div class="coin-type">Oro</div>
                    </div>
                    <div class="coin" style="background: linear-gradient(135deg, #c0c0c0, #e8e8e8);">
                        <div class="coin-amount">{money.get('pp', 0)}</div>
                        <div class="coin-type">Plata</div>
                    </div>
                    <div class="coin" style="background: linear-gradient(135deg, #cd7f32, #e8a87c);">
                        <div class="coin-amount">{money.get('pe', 0)}</div>
                        <div class="coin-type">Electrum</div>
                    </div>
                    <div class="coin" style="background: linear-gradient(135deg, #b87333, #d4a373);">
                        <div class="coin-amount">{money.get('pc', 0)}</div>
                        <div class="coin-type">Cobre</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="bottom-section">
            <div class="section">
                <div class="section-title">Pericias</div>
                <div style="margin-bottom: 15px;">
                    <strong style="color: #8b0000;">Armas:</strong>
                    <div class="proficiency-list" style="margin-top: 8px;">
                        {' '.join([f'<span class="prof-badge">{prof}</span>' for prof in profs.get('armas', [])]) or '<p style="color: #999; font-style: italic;">Ninguna</p>'}
                    </div>
                </div>
                <div>
                    <strong style="color: #8b0000;">No-Armas:</strong>
                    <div class="proficiency-list" style="margin-top: 8px;">
                        {' '.join([f'<span class="prof-badge" style="background: #4b0082;">{prof}</span>' for prof in profs.get('no_armas', [])]) or '<p style="color: #999; font-style: italic;">Ninguna</p>'}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Equipo ({len(equipment)} objetos)</div>
                <ul class="equipment-list">
                    {' '.join([f'<li class="equipment-item">• {item}</li>' for item in equipment[:15]]) or '<p style="color: #999; font-style: italic;">Sin equipo</p>'}
                    {f'<li style="color: #999; font-style: italic; padding: 8px;">... y {len(equipment) - 15} objetos más</li>' if len(equipment) > 15 else ''}
                </ul>
            </div>
        </div>
        
        {f'''<div class="section" style="margin-top: 20px;">
            <div class="section-title">Hechizos Conocidos ({len(spells)})</div>
            <div class="spell-list">
                {' '.join([f'<div class="spell-item">✨ {spell}</div>' for spell in spells])}
            </div>
        </div>''' if spells else ''}
        
        <div style="text-align: center; margin-top: 30px; padding: 15px; background: rgba(139, 0, 0, 0.1); border-radius: 5px;">
            <p style="color: #8b0000; font-style: italic;">Advanced Dungeons & Dragons 2nd Edition</p>
        </div>
    </div>
</body>
</html>"""
    
    # Guardar el archivo HTML
    output_path = Path(output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Ficha HTML generada: {output_path}")
    print(f"  Abre el archivo en tu navegador para verla")
    return output_path


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python generar_html_ficha.py <archivo_personaje.json>")
        return
    
    input_file = sys.argv[1]
    
    # Cargar datos del personaje
    if input_file.endswith('.json'):
        with open(input_file, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
    else:
        print("❌ Solo se soportan archivos .json")
        return
    
    # Generar HTML
    output_name = f"{character_data.get('name', 'personaje')}_ficha.html"
    generate_html_sheet(character_data, output_name)


if __name__ == "__main__":
    main()
