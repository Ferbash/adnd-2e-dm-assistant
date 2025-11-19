# AD&D 2e Dungeon Master Assistant
# Asistente de Dungeon Master para AD&D 2e

Un completo asistente para Dungeon Masters de Advanced Dungeons & Dragons 2nd Edition que permite consultar reglas, crear personajes, hacer tiradas de dados y gestionar recursos.

A complete assistant for Advanced Dungeons & Dragons 2nd Edition Dungeon Masters that allows you to query rules, create characters, make dice rolls, and manage resources.

## Características / Features

### 🎲 Sistema de Tiradas de Dados / Dice Rolling System
- Soporte para todos los tipos de dados estándar (d4, d6, d8, d10, d12, d20, d100)
- Notación de dados estándar (ej: `2d6+3`, `1d20-1`)
- Generación de puntuaciones de habilidad (3d6 o 4d6 descartando el más bajo)
- Support for all standard dice types (d4, d6, d8, d10, d12, d20, d100)
- Standard dice notation (e.g., `2d6+3`, `1d20-1`)
- Ability score generation (3d6 or 4d6 drop lowest)

### 👤 Creación de Personajes / Character Creation
- **5 Razas disponibles / 5 Available Races:**
  - Humano / Human
  - Elfo / Elf
  - Enano / Dwarf
  - Halfling
  - Semielfo / Half-Elf

- **8 Clases de personaje / 8 Character Classes:**
  - Guerrero / Fighter
  - Mago / Wizard
  - Clérigo / Cleric
  - Ladrón / Thief
  - Paladín / Paladin
  - Ranger
  - Druida / Druid
  - Bardo / Bard

- Ajustes raciales automáticos / Automatic racial adjustments
- Generación automática de puntos de golpe / Automatic hit point generation
- Sistema de modificadores de habilidad / Ability modifier system

### 📚 Referencia de Reglas / Rules Reference
- **6 Categorías de reglas / 6 Rule Categories:**
  - Combate / Combat
  - Tiradas de Salvación / Saving Throws
  - Habilidades / Abilities
  - Magia / Magic
  - Experiencia / Experience
  - Movimiento / Movement

- Búsqueda de reglas por palabra clave / Keyword-based rule search
- Contenido bilingüe (Español/Inglés) / Bilingual content (Spanish/English)

### 🎒 Gestión de Recursos / Resource Management
- Seguimiento de puntos de golpe / Hit point tracking
- Gestión de oro / Gold management
- Inventario de objetos / Item inventory
- Gestión de conjuros para clases mágicas / Spell management for magic classes

## Instalación / Installation

No se requieren dependencias externas. Solo necesitas Python 3.6 o superior.

No external dependencies required. You only need Python 3.6 or higher.

```bash
# Clonar el repositorio / Clone the repository
git clone https://github.com/Ferbash/adnd-2e-dm-assistant.git
cd adnd-2e-dm-assistant

# Ejecutar el asistente / Run the assistant
python adnd_assistant.py
```

## Uso / Usage

### Interfaz CLI / CLI Interface

Ejecuta el asistente principal / Run the main assistant:

```bash
python adnd_assistant.py
```

El menú principal ofrece las siguientes opciones:

1. **Consultar Reglas** - Ver reglas por categoría
2. **Crear Personaje** - Crear un nuevo personaje paso a paso
3. **Ver Personajes** - Listar todos los personajes creados
4. **Gestionar Personaje** - Modificar recursos del personaje activo
5. **Hacer Tirada de Dados** - Realizar tiradas usando notación estándar
6. **Búsqueda de Reglas** - Buscar reglas por palabra clave
7. **Ver Todas las Reglas** - Mostrar todas las reglas disponibles

### Ejemplos de Uso / Usage Examples

#### Creación de Personaje / Character Creation

```python
from character import create_character_interactive

# Crear personaje interactivamente
character = create_character_interactive()

# O crear manualmente
from character import Character

abilities = {
    "Fuerza": 16,
    "Destreza": 14,
    "Constitución": 15,
    "Inteligencia": 10,
    "Sabiduría": 12,
    "Carisma": 8
}

char = Character("Thorin", "Enano", "Guerrero", ability_scores=abilities)
print(char)
```

#### Tiradas de Dados / Dice Rolling

```python
from dice_roller import DiceRoller

# Tirada básica / Basic roll
total, rolls = DiceRoller.roll(2, 6)  # 2d6
print(f"Total: {total}, Tiradas: {rolls}")

# Usar notación / Use notation
total, rolls = DiceRoller.roll_from_notation("2d6+3")
print(f"2d6+3 = {total}")

# Generar puntuaciones de habilidad / Generate ability scores
scores = DiceRoller.roll_ability_scores_4d6_drop_lowest()
print(f"Puntuaciones: {scores}")
```

#### Consulta de Reglas / Rules Query

```python
from rules import RulesReference

# Buscar reglas / Search rules
results = RulesReference.search_rules("combate")
for result in results:
    print(f"{result['titulo']}: {result['descripcion']}")

# Ver una categoría / View a category
RulesReference.display_category("combate")
```

#### Gestión de Recursos / Resource Management

```python
from character import Character

char = Character("Gandalf", "Humano", "Mago")

# Modificar HP
char.modify_resource("HP", -5)  # Recibir daño / Take damage
char.modify_resource("HP", 3)   # Curar / Heal

# Gestionar oro / Manage gold
char.modify_resource("Oro", 100)  # Ganar oro / Gain gold
char.modify_resource("Oro", -30)  # Gastar oro / Spend gold

# Gestionar items / Manage items
char.add_item("Espada larga +1")
char.add_item("Poción de curación")
char.remove_item("Poción de curación")

print(char)
```

## Testing / Pruebas

El proyecto incluye tests comprehensivos para todas las funcionalidades principales.

The project includes comprehensive tests for all core functionality.

```bash
# Ejecutar todos los tests / Run all tests
python -m unittest discover -s . -p "test_*.py" -v

# Ejecutar tests específicos / Run specific tests
python -m unittest test_dice_roller.py -v
python -m unittest test_character.py -v
python -m unittest test_rules.py -v
```

**57 tests en total / 57 total tests:**
- 18 tests para tiradas de dados / dice rolling tests
- 19 tests para creación de personajes / character creation tests
- 20 tests para referencia de reglas / rules reference tests

## Estructura del Proyecto / Project Structure

```
adnd-2e-dm-assistant/
├── adnd_assistant.py      # Aplicación CLI principal / Main CLI application
├── dice_roller.py         # Sistema de tiradas / Dice rolling system
├── character.py           # Creación de personajes / Character creation
├── rules.py              # Referencia de reglas / Rules reference
├── test_dice_roller.py   # Tests de dados / Dice tests
├── test_character.py     # Tests de personajes / Character tests
├── test_rules.py         # Tests de reglas / Rules tests
├── requirements.txt      # Dependencias / Dependencies
├── .gitignore           # Archivos ignorados / Ignored files
└── README.md            # Este archivo / This file
```

## Características Técnicas / Technical Features

- ✅ Sin dependencias externas / No external dependencies
- ✅ Python 3.6+ compatible
- ✅ Código documentado bilingüe / Bilingual documented code
- ✅ 57 tests unitarios / 57 unit tests
- ✅ Interfaz CLI interactiva / Interactive CLI interface
- ✅ Validación de datos robusta / Robust data validation

## Contribuir / Contributing

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Licencia / License

Este proyecto está disponible para uso personal y educativo.

This project is available for personal and educational use.

## Autor / Author

Ferbash

## Agradecimientos / Acknowledgments

- Basado en las reglas de Advanced Dungeons & Dragons 2nd Edition
- Based on Advanced Dungeons & Dragons 2nd Edition rules
