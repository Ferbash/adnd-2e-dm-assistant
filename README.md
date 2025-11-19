# 🎲 AD&D 2e - Sistema Completo de Gestión de Partidas

Sistema integral para Advanced Dungeons & Dragons 2nd Edition que incluye creación de personajes, gestión de combate, consulta de reglas y herramientas de DM.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Módulos](#módulos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación](#documentación)
- [Requisitos](#requisitos)

## ✨ Características

### 🎭 Creación de Personajes
- Generación completa según reglas AD&D 2e
- 6 razas: Humano, Enano, Elfo, Mediano, Semielfo, Gnomo
- 6 clases: Guerrero, Clérigo, Mago, Pícaro, Explorador, Paladín
- Sistema de atributos (3d6 o punto buy)
- Selección de habilidades, equipo y conjuros
- Exportación a JSON

### ⚔️ Sistema de Combate
- 94 monstruos con estadísticas completas
- Iniciativa con modificadores de DES
- Sistema THAC0 oficial
- Críticos (20) y pifias (1)
- Sistema de distancias (melé/10m/30m)
- Combate automático con threshold de HP
- Gestión de múltiples combatientes

### 📚 Consulta de Reglas
- Base de datos completa de reglas AD&D 2e
- 25+ conjuros (niveles 1-3) con stats completas
- Información de clases y atributos
- Objetos mágicos y equipo estándar
- Búsqueda inteligente con ranking de relevancia
- Acceso instantáneo durante partidas

### 🎮 Interfaces Múltiples
- **Consola:** Terminal interactivo con comandos
- **GUI:** Interfaz gráfica Tkinter profesional
- **Party Manager:** Gestión de hasta 5 personajes
- **Creador visual:** Wizard paso a paso

### 🎲 Sistema de Dados
- Motor de dados completo (XdY+Z)
- Tiradas de ataque con THAC0
- Tiradas de daño con modificadores
- Salvaciones y chequeos de atributos
- Historial de tiradas

## 🚀 Instalación

### Requisitos
- Python 3.7 o superior
- Windows, Linux o MacOS
- Librerías estándar de Python (incluidas)

### Instalación

```bash
# Clonar o descargar el repositorio
cd "AD&D/progrmas"

# (Opcional) Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# No requiere instalación de dependencias adicionales
```

## 🎯 Uso Rápido

### Asistente de DM (Consola)
```bash
python dm_assistant.py
```

Comandos principales:
```
/character <archivo.json>  # Cargar personaje
/combat start             # Iniciar combate
/combat add <monstruo>    # Agregar enemigo
/combat init              # Comenzar combate
/combat attack 1          # Atacar enemigo 1
/spell bola de fuego      # Consultar conjuro
/rules iniciativa         # Consultar regla
/help                     # Ver todos los comandos
```

### Asistente de DM (GUI)
```bash
python dm_assistant_gui.py
```

Interfaz gráfica con 3 paneles:
- Panel izquierdo: Información del personaje
- Panel central: Consola de comandos
- Panel derecho: Estado de combate

### Creador de Personajes
```bash
python character_creator.py
```

Wizard interactivo paso a paso:
1. Nombre y concepto
2. Raza y clase
3. Atributos (tirada o punto buy)
4. Habilidades y proficiencias
5. Equipo inicial
6. Conjuros (si aplica)
7. Guardar personaje

### Gestor de Grupo
```bash
python party_manager.py
```

Gestión de hasta 5 personajes:
- Cargar/guardar grupo completo
- Modificar HP y XP
- Ver estadísticas
- Exportar/importar

## 📦 Módulos

### Core (Sistema Principal)
- **dados.py** - Motor de dados y tiradas
- **combate.py** - Sistema de combate + 94 monstruos
- **biblio.py** - Base de datos de reglas y conjuros
- **spells_database.py** - Conjuros para creación de personajes
- **character_creator.py** - Creador de personajes

### Interfaces
- **dm_assistant.py** - Asistente de consola
- **dm_assistant_gui.py** - Asistente gráfico
- **party_manager_console.py** - Gestor de grupo (consola)
- **party_manager.py** - Gestor de grupo (GUI)

### Utils
- **generar_pdf_ficha.py** - Exportar ficha a PDF
- **generar_html_ficha.py** - Exportar ficha a HTML
- **pdf_py.py** - Utilidades de PDF

## 📁 Estructura del Proyecto

```
AD&D/progrmas/
├── core/                      # Módulos principales
│   ├── __init__.py
│   ├── dados.py              # Sistema de dados
│   ├── combate.py            # Combate + monstruos
│   ├── biblio.py             # Base de datos de reglas
│   ├── spells_database.py    # Conjuros
│   └── character_creator.py  # Creador de personajes
│
├── interfaces/               # Interfaces de usuario
│   ├── __init__.py
│   ├── dm_assistant.py       # Asistente (consola)
│   ├── dm_assistant_gui.py   # Asistente (GUI)
│   ├── party_manager_console.py
│   └── party_manager.py
│
├── utils/                    # Herramientas auxiliares
│   ├── __init__.py
│   ├── generar_pdf_ficha.py
│   ├── generar_html_ficha.py
│   └── pdf_py.py
│
├── data/                     # Datos de personajes
│   ├── *.json               # Personajes guardados
│   └── party_*.json         # Grupos guardados
│
├── docs/                     # Documentación
│   ├── README_BIBLIO.md
│   ├── EJEMPLOS_BIBLIO.md
│   ├── DOCUMENTACION_TECNICA_BIBLIO.md
│   └── README_GUI.md
│
├── tests/                    # Tests y demos
│   ├── test_biblio.py
│   ├── test_carga_datos.py
│   └── demo_biblio.py
│
├── resources/                # Recursos y PDFs
│   ├── *.pdf                # Manuales
│   ├── *.html               # Fichas generadas
│   └── *.pkl                # Caché
│
├── dm_assistant.py           # Launcher consola
├── dm_assistant_gui.py       # Launcher GUI
├── character_creator.py      # Launcher creador
├── party_manager.py          # Launcher party manager
└── README.md                 # Este archivo
```

## 📖 Documentación

### Documentación Completa
- **[README_BIBLIO.md](docs/README_BIBLIO.md)** - Sistema de consulta de reglas
- **[EJEMPLOS_BIBLIO.md](docs/EJEMPLOS_BIBLIO.md)** - Casos de uso del sistema de consulta
- **[DOCUMENTACION_TECNICA_BIBLIO.md](docs/DOCUMENTACION_TECNICA_BIBLIO.md)** - Arquitectura técnica
- **[README_GUI.md](docs/README_GUI.md)** - Guía de interfaz gráfica

### Ejemplos de Comandos

#### Gestión de Personajes
```bash
/character Flurim_hijo_de_Drebem_character.json  # Cargar
/sheet                                            # Ver ficha
/hp +5                                            # Curar 5 HP
/hp -10                                           # Recibir 10 daño
/xp 100                                           # Agregar XP
/rest                                             # Descanso completo
/save                                             # Guardar cambios
```

#### Sistema de Dados
```bash
/dice 2d6+3          # Tirar dados
/d20 +5              # d20 con modificador
/attack              # Ataque del personaje
/damage              # Daño del personaje
/save veneno         # Salvación vs veneno
/check fuerza        # Chequeo de FUE
```

#### Combate
```bash
/combat start                # Iniciar combate
/combat add orco            # Agregar orco
/combat add o               # Buscar 'o' (lista numerada)
/combat init                # Tirar iniciativa
/combat status              # Ver estado
/combat attack 1            # Atacar enemigo 1
/combat move approach       # Acercarse
/combat auto 3              # Auto-combate (parar si HP≤3)
/combat next                # Siguiente turno
/combat end                 # Terminar combate
```

#### Consulta de Reglas
```bash
/rules iniciativa           # Reglas de iniciativa
/rules THAC0                # Sistema THAC0
/spell bola de fuego        # Info de conjuro
/spell curar heridas        # Conjuro de curación
/class guerrero             # Info de clase
/ability fuerza             # Info de atributo
/item espada larga          # Info de arma
/item poción de curación    # Objeto mágico
```

#### Monstruos
```bash
/monster orco               # Ver stats de orco
/monster dragón rojo        # Ver dragón
/monsters list              # Listar todos (94)
/monsters search gob        # Buscar 'gob'
/monsters type no-muerto    # Filtrar no-muertos
/monsters random            # Encuentro aleatorio
```

## 🔧 Requisitos del Sistema

### Software
- **Python:** 3.7 o superior
- **Sistema Operativo:** Windows, Linux, MacOS
- **RAM:** 256 MB mínimo
- **Espacio:** 50 MB

### Dependencias
Todas las dependencias son de la biblioteca estándar de Python:
- `tkinter` - Interfaz gráfica (incluido en Python)
- `json` - Manejo de datos
- `pathlib` - Rutas de archivos
- `pickle` - Serialización
- `subprocess` - Ejecución de procesos

No requiere instalación de paquetes adicionales.

## 🎮 Casos de Uso

### Sesión de Juego Completa

1. **Preparación**
```bash
python dm_assistant.py
/character Flurim_hijo_de_Drebem_character.json
```

2. **Exploración y encuentro**
```bash
/monsters random
# Resultado: Orcos!
```

3. **Inicio de combate**
```bash
/combat start
/combat add orco
/combat add orco
/combat init
```

4. **Durante el combate**
```bash
# Consultar regla
/rules iniciativa

# Turno del jugador
/combat attack 1
# Tirada: 15 + mods = Impacto! Daño: 8

# Siguiente turno
/combat next
```

5. **Fin del combate**
```bash
/combat status
# Todos los enemigos derrotados
/combat end
```

6. **Curación y descanso**
```bash
/hp -12              # Personaje herido
/spell curar heridas # Consultar conjuro
/hp +8               # Aplicar curación
/save                # Guardar progreso
```

### Crear Nuevo Personaje

```bash
python character_creator.py

# Seguir wizard:
# 1. Nombre: "Thorin Escudo de Hierro"
# 2. Raza: Enano (2)
# 3. Clase: Guerrero (1)
# 4. Atributos: Tirar dados (1)
# 5. Seleccionar equipo inicial
# 6. Guardar: "Thorin_character.json"
```

### Gestionar Grupo de 5 Personajes

```bash
python party_manager.py

# Menú:
# 1. Cargar personajes
# 2. Modificar HP después de combate
# 3. Asignar XP
# 4. Guardar grupo completo
# 5. Ver resumen de todo el grupo
```

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'core'"
```bash
# Asegúrate de ejecutar desde el directorio raíz
cd "AD&D/progrmas"
python dm_assistant.py
```

### Error al cargar personaje
```bash
# Verifica que el archivo JSON esté en data/
# Usa ruta relativa:
/character data/personaje.json
```

### Combate no inicia
```bash
# Secuencia correcta:
/combat start        # 1. Iniciar
/combat add monstruo # 2. Agregar enemigos
/combat init         # 3. Tirar iniciativa
```

## 🤝 Contribuciones

Este es un proyecto personal de Fernando Bassini para partidas de AD&D 2e.

## 📜 Licencia

Este software es para uso personal en partidas de AD&D 2e.
Las reglas de AD&D 2e son propiedad de TSR/Wizards of the Coast.
Este trabajo es gratuito para dudas Bassinita@gmail.com

## 👥 Créditos

- **Sistema:** AD&D 2nd Edition (TSR/Wizards of the Coast)
- **Desarrollo:** Sistema creado para facilitar partidas de AD&D 2e por Fernando Bassini
- **Manuales:** Player's Handbook, DMG, Monstrous Manual

## 📞 Soporte

Para problemas o preguntas, consulta la documentación en `docs/`.

Escribeme bassini@gmail.com 
---

## 🎲 Inicio Rápido - Cheatsheet

```bash
# Asistente de DM (recomendado para nuevos usuarios)
python dm_assistant.py

# Comandos esenciales:
/help                    # Ver todos los comandos
/character <archivo>     # Cargar personaje
/combat start            # Iniciar combate
/spell <nombre>          # Consultar conjuro
/rules <búsqueda>        # Consultar regla

# Crear personaje nuevo
python character_creator.py

# Interfaz gráfica
python dm_assistant_gui.py

# Gestor de grupo
python party_manager.py
```

---

**Versión:** 1.0
**Última actualización:** Noviembre 2025
**Python:** 3.7+

🎲 **¡Que tengas grandes aventuras!** 🎲
