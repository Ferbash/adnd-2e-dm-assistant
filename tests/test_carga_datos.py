# Script de prueba para verificar la carga de datos desde los PDFs
import sys
import os
import io

# Configurar codificación UTF-8 para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Importar la clase principal
sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

# Cargar el módulo AD&D
adnd = import_module('AD&D')

print("="*70)
print("TEST DE CARGA DE DATOS DE AD&D 2E")
print("="*70)

# Crear instancia del cargador de datos
loader = adnd.ADnDDataLoader()

print("\n📚 Cargando datos de los PDFs...")
loader.load_or_extract_data()

print("\n" + "="*70)
print("📊 RESUMEN DE DATOS CARGADOS")
print("="*70)

# Mostrar clases
print(f"\n🗡️  CLASES DISPONIBLES ({len(loader.classes)}):")
for class_name, class_data in loader.classes.items():
    print(f"  • {class_name}")
    dado_golpe = class_data.get('dado_golpe', class_data.get('hit_die', '?'))
    thac0 = class_data.get('thac0_inicial', class_data.get('base_thac0', '?'))
    print(f"    - Dado de golpe: d{dado_golpe}")
    print(f"    - THAC0 inicial: {thac0}")
    if class_data.get('hechizos') or class_data.get('puede_lanzar_hechizos'):
        print(f"    - Puede lanzar hechizos: Sí")

# Mostrar razas
print(f"\n🧝 RAZAS DISPONIBLES ({len(loader.races)}):")
for race_name, race_data in loader.races.items():
    print(f"  • {race_name}")
    ajustes = race_data.get('ajustes_atributos', {})
    if ajustes:
        ajustes_str = ", ".join([f"{k}: {v:+d}" for k, v in ajustes.items()])
        print(f"    - Ajustes: {ajustes_str}")
    habilidades = race_data.get('habilidades_especiales', [])
    if habilidades:
        print(f"    - Habilidades: {', '.join(habilidades)}")

# Mostrar hechizos
print(f"\n✨ HECHIZOS DISPONIBLES:")
for class_name, spells in loader.spells.items():
    print(f"  • {class_name}: {len(spells)} hechizos")
    # Contar por nivel
    by_level = {}
    for spell_name, spell_data in spells.items():
        nivel = spell_data['nivel']
        by_level[nivel] = by_level.get(nivel, 0) + 1
    
    for nivel in sorted(by_level.keys()):
        print(f"    - Nivel {nivel}: {by_level[nivel]} hechizos")

# Mostrar reglas cargadas
print(f"\n📜 REGLAS Y SISTEMAS CARGADOS:")
for rule_category in loader.rules.keys():
    print(f"  • {rule_category}")

# Mostrar equipo
if loader.equipment:
    print(f"\n⚔️  EQUIPO DISPONIBLE:")
    if 'armas' in loader.equipment:
        print(f"  • Armas: {len(loader.equipment['armas'])}")
    if 'armaduras' in loader.equipment:
        print(f"  • Armaduras: {len(loader.equipment['armaduras'])}")

print("\n" + "="*70)
print("✅ PRUEBA DE CREACIÓN DE PERSONAJE")
print("="*70)

# Crear un personaje de prueba
char = adnd.Character("Elminster el Sabio", loader)
print(f"\n🎲 Generando atributos (Método 4 - Heroico)...")
attrs = char.generate_attributes(method=4)
print(f"   Valores generados: {attrs}")

print(f"\n🧝 Estableciendo raza: Elfo")
char.set_race('Elfo')

print(f"\n🧙 Estableciendo clase: Mago")
char.set_class('Mago')

print(f"\n📋 FICHA DEL PERSONAJE:")
print(f"   Nombre: {char.name}")
print(f"   Raza: {char.race}")
print(f"   Clase: {char.character_class}")
print(f"   Nivel: {char.level}")
print(f"\n   Atributos:")
for attr, value in char.attributes.items():
    print(f"     {attr}: {value}")

# Mostrar algunos hechizos disponibles
print(f"\n✨ HECHIZOS DISPONIBLES PARA MAGOS NIVEL 1:")
mago_spells_1 = loader.get_spells_by_level('Mago', 1)
for spell_name, spell_data in list(mago_spells_1.items())[:5]:
    print(f"  • {spell_name}")
    print(f"    {spell_data['descripcion']}")

print("\n" + "="*70)
print("✅ ¡PRUEBA COMPLETADA EXITOSAMENTE!")
print("="*70)
