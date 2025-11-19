# 🎲 DM Assistant GUI - Interfaz Gráfica Profesional

## Características Principales

### 🖥️ Interfaz Nativa de Escritorio
- **Tkinter**: Interfaz nativa que se integra perfectamente con Windows
- **Rendimiento óptimo**: Sin dependencia de navegador, respuesta instantánea
- **Diseño profesional**: Layout de 3 paneles con pestañas organizadas

## 🎯 Paneles Principales

### 1️⃣ Panel Izquierdo - Gestión de Personajes

#### Lista de Personajes
- ✅ Auto-detección de archivos `*_character.json`
- ✅ Vista previa: Nombre, Raza, Clase, Nivel, HP
- ✅ Doble clic para cargar personaje
- ✅ Botón de recarga para actualizar lista

#### Personaje Activo
- ✅ Ficha completa con todos los stats
- ✅ Formato visual ASCII art elegante
- ✅ HP, AC, THAC0, XP, Atributos
- ✅ Arma y armadura equipadas

#### Acciones Rápidas
- **HP**: Botones -10/-5/-1/+1/+5/+10
- **HP Personalizado**: Campo para establecer valor exacto
- **XP**: Campo para añadir experiencia
- **Descanso Completo**: Recupera todos los HP
- **Guardar**: Auto-guarda todos los cambios

### 2️⃣ Panel Central - Pestañas de Funcionalidad

#### 🎲 Pestaña DADOS
**Dados Rápidos:**
- Botones: d4, d6, d8, d10, d12, d20, d100
- Clic y listo - resultados instantáneos

**Tirada Personalizada:**
- Campo de notación libre (ej: 3d6+2, 2d10-1)
- Enter para tirar
- Soporte completo de modificadores

**Tirada de Ataque:**
- Campo THAC0
- Campo de bonus
- Cálculo automático de AC impactada
- Detección de críticos (20) y pifias (1)

**Panel de Resultados:**
- Historial completo de tiradas
- Colores para críticos/pifias/éxitos
- Scroll automático
- Formato claro y legible

#### ⚔️ Pestaña COMBATE
**Controles de Combate:**
- ⚔️ Iniciar Combate
- 🎲 Tirar Iniciativa
- ➡️ Siguiente Turno
- ❌ Terminar Combate

**Lista de Combatientes:**
- Vista de árbol con iconos (👤 jugadores, 👹 monstruos)
- Columnas: Nombre, HP, AC, THAC0, Iniciativa
- Resaltado del turno actual
- Actualización en tiempo real

**Acciones de Combate:**
- ⚔️ Atacar: Diálogo de selección de objetivo
- 💊 Curar: Diálogo de cantidad
- 🛡️ Salvación: Diálogo de tipo de salvación

**Indicador de Round:**
- Muestra round actual
- Muestra nombre del combatiente activo
- Actualización automática

#### 👹 Pestaña MONSTRUOS
**Búsqueda:**
- Campo de búsqueda por nombre
- Resultados instantáneos
- Enter para buscar

**Filtro por Tipo:**
- ComboBox con todos los tipos
- 100+ monstruos organizados
- Selección rápida

**Lista de Monstruos:**
- Vista completa: Nombre, HD, AC
- Doble clic para ver ficha
- Scroll suave

**Acciones:**
- 📄 Ver Ficha: Popup con stats completos
- ➕ Añadir al Combate: Integración directa

### 3️⃣ Panel Derecho - Registro de Actividad

**Log en Tiempo Real:**
- Todas las acciones registradas
- Timestamp implícito
- Scroll automático
- Fuente monoespaciada para alineación
- Historial completo de sesión

## 🚀 Cómo Usar

### Inicio
```powershell
python dm_assistant_gui.py
```

### Flujo de Trabajo Típico

#### 1. Preparación de Sesión
```
1. Cargar personaje (doble clic en lista)
2. Verificar stats en panel de personaje activo
3. Revisar monstruos disponibles en pestaña Monstruos
```

#### 2. Durante la Partida
```
🎲 DADOS:
- Clic en d20 para tiradas rápidas
- Usar "Tirada de Ataque" para combate
- Notación personalizada para hechizos/habilidades

⚔️ COMBATE:
- Iniciar Combate
- Añadir monstruos desde pestaña Monstruos
- Tirar Iniciativa
- Usar Siguiente Turno para avanzar
- Botón Atacar para combate
- Ver estado en lista de combatientes
```

#### 3. Gestión de Personaje
```
⚡ ACCIONES RÁPIDAS:
- Daño recibido: Clic en botón -5, -10, etc.
- Curación: Clic en botón +5, +10, etc.
- HP exacto: Escribir valor y clic en ✓
- Experiencia: Escribir XP y Añadir
- Descanso: Clic en "Descanso Completo"
- Guardar: Clic en "Guardar Cambios"
```

## ⚙️ Ventajas sobre HTML

### Rendimiento
- ⚡ **10x más rápido**: Sin overhead de navegador
- ⚡ **Respuesta instantánea**: Sin latencia de red
- ⚡ **Memoria eficiente**: ~50MB vs 500MB+ del navegador

### Usabilidad
- ✅ **Ventanas nativas**: Se integra con el SO
- ✅ **Atajos de teclado**: Enter, Tab, etc.
- ✅ **Copy/Paste nativo**: Ctrl+C/V funciona
- ✅ **No requiere servidor**: Ejecutar y listo

### Funcionalidad
- ✅ **Multi-ventana**: Popups para fichas de monstruos
- ✅ **Diálogos nativos**: Confirmaciones, inputs
- ✅ **Treeview**: Listas jerárquicas profesionales
- ✅ **Scrollbars nativas**: Suaves y eficientes

## 🎨 Características Visuales

### Layout Profesional
- **PanedWindow**: Paneles redimensionables
- **Notebook**: Pestañas organizadas
- **LabelFrame**: Agrupación clara de controles
- **ScrolledText**: Áreas de texto con scroll integrado

### Tipografía
- **Consolas**: Fuente monoespaciada para datos
- **Arial**: Fuente sans-serif para UI
- **Tamaños variables**: 9-12pt según importancia

### Feedback Visual
- **Colores en dados**: Verde (éxito), Rojo (pifia), Dorado (crítico)
- **Resaltado de turno**: Fondo azul claro en combatiente activo
- **Iconos de texto**: 👤 👹 ⚔️ 🎲 para identificación rápida

## 🔧 Requisitos Técnicos

### Software
- Python 3.7+
- Tkinter (incluido con Python en Windows)
- Módulos del proyecto: dados.py, combate.py

### Archivos Necesarios
```
progrmas/
├── dm_assistant_gui.py      # ← Interfaz gráfica
├── dados.py                  # Sistema de dados
├── combate.py                # Sistema de combate
└── *_character.json          # Personajes
```

## 📋 Funcionalidades Implementadas

### ✅ Gestión de Personajes
- [x] Cargar personajes desde JSON
- [x] Vista previa en lista
- [x] Ficha completa
- [x] Modificar HP (relativo y absoluto)
- [x] Añadir XP
- [x] Descanso completo
- [x] Auto-guardado

### ✅ Sistema de Dados
- [x] Dados rápidos (d4-d100)
- [x] Notación personalizada
- [x] Tiradas de ataque con THAC0
- [x] Detección de críticos/pifias
- [x] Historial de resultados
- [x] Colores para feedback

### ✅ Base de Datos de Monstruos
- [x] 100+ monstruos cargados
- [x] Búsqueda por nombre
- [x] Filtro por tipo
- [x] Fichas completas (popup)
- [x] Integración con combate

### ✅ Gestor de Combate
- [x] Iniciar/terminar combate
- [x] Añadir jugadores automático
- [x] Añadir monstruos desde DB
- [x] Tirar iniciativa
- [x] Sistema de turnos
- [x] Atacar con diálogo de objetivo
- [x] Curación
- [x] Tiradas de salvación
- [x] Verificación de fin de combate
- [x] Actualizar HP del personaje al terminar

### ✅ Registro y Log
- [x] Log de todas las acciones
- [x] Scroll automático
- [x] Formato legible
- [x] Persistencia durante sesión

## 🆚 Comparación: GUI vs Web vs Terminal

| Característica | GUI (Tkinter) | Web (Flask) | Terminal |
|---------------|---------------|-------------|----------|
| Velocidad | ⚡⚡⚡ | ⚡ | ⚡⚡ |
| Usabilidad | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| Instalación | ✅ Simple | ⚠️ Requiere Flask | ✅ Simple |
| Memoria | ~50MB | ~500MB+ | ~10MB |
| Multi-ventana | ✅ Sí | ❌ No | ❌ No |
| Gráficos | ✅ Nativos | ⚠️ HTML/CSS | ❌ ASCII |
| Portabilidad | ⚠️ Python req. | ✅ Navegador | ✅ Mejor |
| Aprendizaje | ⭐⭐ | ⭐ | ⭐⭐⭐ |

## 🐛 Solución de Problemas

### La ventana no aparece
```powershell
# Verificar que tkinter está instalado
python -c "import tkinter; print('OK')"
```

### Error al cargar personajes
- Verificar que los archivos JSON tienen formato correcto
- Campo `hp` debe ser: `{"current": X, "max": Y}`
- Usar dm_assistant.py en terminal para verificar formato

### Monstruos no aparecen
- El MonsterDatabase se carga de combate.py
- Verificar que combate.py está en el mismo directorio

## 🎯 Próximas Mejoras

### Planeadas
- [ ] Menú de archivo completo (abrir, guardar, exportar)
- [ ] Temas de color (oscuro/claro)
- [ ] Atajos de teclado personalizables
- [ ] Gráficos de barras para HP
- [ ] Mini-mapa de combate
- [ ] Exportar log a archivo
- [ ] Importar personajes desde PDF

### Considerando
- [ ] Integración con generador de personajes (AD&D.py)
- [ ] Editor de personajes in-app
- [ ] Calculadora de XP por encuentro
- [ ] Generador de tesoro
- [ ] Tablas de referencia rápida

## 📝 Notas de Desarrollo

### Arquitectura
- **Orientado a objetos**: Cada panel es una clase
- **Separación de responsabilidades**: UI / Lógica / Datos
- **Event-driven**: Callbacks para todas las acciones

### Código Limpio
- **Docstrings**: Todas las funciones documentadas
- **Type hints**: Tipos donde es relevante
- **Nombres descriptivos**: Variables y funciones claras

---

**¡Disfruta tu partida con la mejor interfaz para AD&D 2e!** ⚔️🎲
