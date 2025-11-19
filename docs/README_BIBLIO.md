# 📚 Sistema de Consulta de Reglas AD&D 2e (biblio.py)

## Descripción
Sistema inteligente de consulta de reglas, conjuros, clases, habilidades y objetos para AD&D 2e.
Integrado con el DM Assistant de consola para acceso rápido durante las partidas.

## Comandos Disponibles

### `/rules <búsqueda>`
Busca cualquier regla del juego.

**Ejemplos:**
```
/rules iniciativa
/rules THAC0
/rules salvación
/rules combate
/rules movimiento
/rules caída
```

**Contenido incluido:**
- Sistema de combate (iniciativa, ataque, daño, AC, THAC0)
- Tiradas de salvación
- Chequeos de atributos
- Experiencia y niveles
- Descanso y curación
- Sistema de magia
- Movimiento especial (escalar, nadar, saltar)
- Moral de monstruos
- Iluminación y visión
- Reacciones NPC
- Sorpresa y trampas

### `/spell <nombre>`
Busca información detallada de un conjuro.

**Ejemplos:**
```
/spell bola de fuego
/spell misiles mágicos
/spell curar heridas leves
/spell invisibilidad
/spell dormir
```

**Información mostrada:**
- Nivel del conjuro
- Clase (Mago/Clérigo)
- Escuela de magia
- Tiempo de lanzamiento
- Duración
- Alcance
- Componentes (V, S, M)
- Efecto completo
- Daño/Curación (si aplica)
- Tirada de salvación

**Conjuros incluidos:**
- **Nivel 1 Mago:** Armadura Arcana, Detectar Magia, Luz, Misiles Mágicos, Dormir, Escudo
- **Nivel 2 Mago:** Bola de Fuego Minúscula, Invisibilidad, Telaraña
- **Nivel 3 Mago:** Bola de Fuego, Rayo, Volar
- **Nivel 1 Clérigo:** Curar Heridas Leves, Bendición, Crear Agua, Detectar Mal, Protección contra el Mal
- **Nivel 2 Clérigo:** Aguantar Elementos, Detener Persona, Silencio 5m Radio
- **Nivel 3 Clérigo:** Curar Enfermedad, Disipar Magia, Oración

### `/class <nombre>`
Muestra información completa de una clase.

**Ejemplos:**
```
/class guerrero
/class mago
/class clérigo
/class pícaro
/class explorador
/class paladín
```

**Información mostrada:**
- Dado de golpe
- Requisitos principales
- Razas permitidas
- Armaduras permitidas
- Armas permitidas
- Habilidades especiales
- Nivel máximo
- XP requerido
- Información de conjuros (si aplica)

### `/ability <atributo>`
Consulta los efectos de un atributo.

**Ejemplos:**
```
/ability fuerza
/ability destreza
/ability constitución
/ability inteligencia
/ability sabiduría
/ability carisma
```

**Información mostrada:**
- Modificadores de combate
- Tablas de bonificadores por puntuación
- Efectos especiales
- Conjuros de bonificación (INT/SAB)
- Idiomas (INT)
- Seguidores (CAR)

### `/item <nombre>`
Busca objetos mágicos o equipo estándar.

**Ejemplos:**
```
/item espada +1
/item poción de curación
/item varita
/item armadura de placas
/item arco largo
```

**Categorías incluidas:**
- **Objetos Mágicos:** Espadas +1, Armaduras +1, Pociones, Varitas, Anillos, Objetos maravillosos
- **Armas:** Todas las armas estándar con daño, tipo, peso, precio
- **Armaduras:** Todas las armaduras con AC, peso, precio
- **Equipo:** Mochila, cuerdas, antorchas, raciones, herramientas

## Base de Datos Incluida

### 📖 Reglas (10+ categorías)
- Combate completo
- Tiradas de salvación
- Chequeos de atributos
- Sistema de magia
- Movimiento y exploración
- Interacción social

### 🔮 Conjuros (25+ conjuros)
- Mago niveles 1-3
- Clérigo niveles 1-3
- Información completa de lanzamiento

### ⚔️ Clases (6 clases)
- Guerrero
- Clérigo
- Mago
- Pícaro
- Explorador
- Paladín

### 💪 Atributos (6 completos)
- Fuerza (combate, carga)
- Destreza (AC, iniciativa, habilidades)
- Constitución (HP, curación)
- Inteligencia (conjuros, idiomas)
- Sabiduría (conjuros, percepción)
- Carisma (reacciones, seguidores)

### 🎁 Objetos Mágicos (7+)
- Armas mágicas
- Armaduras mágicas
- Pociones
- Varitas
- Anillos
- Objetos maravillosos

### 🛡️ Equipo (30+ items)
- Armas (13 tipos)
- Armaduras (9 tipos)
- Equipo de aventurero (15+ items)

## Uso en el DM Assistant

El sistema está completamente integrado en `dm_assistant.py`:

```bash
python dm_assistant.py
```

Durante la partida, usa los comandos directamente:

```
🎲 DM> /rules THAC0
🎲 DM> /spell bola de fuego
🎲 DM> /class mago
🎲 DM> /ability fuerza
🎲 DM> /item espada larga
```

## Búsqueda Inteligente

El sistema incluye búsqueda inteligente con:
- **Coincidencia parcial:** Encuentra "bola" en "Bola de Fuego"
- **Búsqueda en valores:** Busca en descripciones y efectos
- **Ranking por relevancia:** Muestra primero los resultados más relevantes
- **Búsqueda multi-categoría:** Si no especificas categoría, busca en todas

## Ejemplos de Uso en Partida

### Consultar regla durante combate
```
🎲 DM> /rules iniciativa
📚 RULES: Iniciativa
Cada combatiente tira 1d10. Mayor resultado actúa primero.
```

### Verificar efecto de conjuro
```
🎲 DM> /spell misiles mágicos
📚 SPELLS: Misiles Mágicos
Nivel: 1 | Clase: Mago
Daño: 1d4+1 por misil, +1 misil cada 2 niveles (máx 5)
```

### Consultar bonus de atributo
```
🎲 DM> /ability fuerza
📚 ABILITIES: Fuerza
FUE 18: +1 ataque, +2 daño
```

### Buscar información de clase para NPC
```
🎲 DM> /class clérigo
📚 CLASSES: Clérigo
Dado de golpe: d8
Habilidades: Expulsar no-muertos, Conjuros divinos
```

## Características Técnicas

- **Python 3.13+ compatible**
- **Sin dependencias externas**
- **Búsqueda O(n) con ranking de relevancia**
- **Estructura de datos anidada para categorización**
- **Formateo elegante con Unicode**
- **Integración completa con dm_assistant.py**

## Expandir la Base de Datos

Para agregar más contenido, edita `biblio.py`:

```python
def _load_spells(self):
    return {
        "Nuevo Conjuro": {
            "nivel": 1,
            "clase": "Mago",
            # ... más datos
        }
    }
```

Las categorías disponibles son:
- `rules` - Reglas del juego
- `spells` - Conjuros
- `classes` - Clases de personaje
- `abilities` - Atributos
- `magic_items` - Objetos mágicos
- `equipment` - Equipo estándar

## Autor
Sistema creado para facilitar partidas de AD&D 2e con consulta rápida de reglas sin interrumpir el flujo del juego.

---

🎲 **¡Buenas aventuras!** 🎲
