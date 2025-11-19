# 📚 Ejemplos de Uso del Sistema de Consulta

## Sesión de ejemplo usando dm_assistant.py con biblio.py

### Escenario: El mago del grupo quiere lanzar Bola de Fuego

**DM:** "Ves un grupo de orcos aproximándose. ¿Qué haces?"

**Jugador:** "Quiero lanzar Bola de Fuego, pero no recuerdo el alcance ni el daño exacto"

```bash
🎲 DM> /spell bola de fuego
```

**Resultado:**
```
======================================================================
📚 SPELLS: Bola de Fuego
📍 Ruta: Bola de Fuego
======================================================================
nivel: 3
clase: Mago
escuela: Evocación
tiempo: 3 acciones
duracion: Instantáneo
alcance: 30m
componentes: V, S, M (bola de guano de murciélago + azufre)
efecto: 1d6 por nivel de daño de fuego en 6m de radio (máx 10d6)
descripcion: Explosión de fuego devastadora.
daño: 1d6/nivel (máx 10d6)
salvacion: Mitad de daño
```

**DM:** "Perfecto, el mago es nivel 5, así que hace 5d6 de daño. Los orcos pueden hacer tirada de salvación para mitad de daño."

---

### Escenario: Duda sobre el sistema de iniciativa

**Jugador:** "¿Cómo funciona la iniciativa otra vez?"

```bash
🎲 DM> /rules iniciativa
```

**Resultado:**
```
======================================================================
📚 RULES: Iniciativa
📍 Ruta: Combate → Iniciativa
======================================================================
descripcion: Cada combatiente tira 1d10. Mayor resultado actúa primero.
modificadores: DES modifica iniciativa: 18+ (+2), 16-17 (+1), 6-7 (-1), 5- (-2)
sorpresa: Tirar 1d10. 1-3 = sorprendido (pierde primer turno)
```

**DM:** "Ahora recuerdo, cada uno tira 1d10 y suma su modificador de DES"

---

### Escenario: Nuevo jugador quiere saber sobre la clase Pícaro

**Jugador:** "¿Qué habilidades tiene un pícaro?"

```bash
🎲 DM> /class pícaro
```

**Resultado:**
```
======================================================================
📚 CLASSES: Pícaro
📍 Ruta: Pícaro
======================================================================
dado_golpe: d6
requisito_principal: Destreza
razas_permitidas:
  • Humano
  • Enano
  • Elfo
  • Mediano
  • Semielfo
  • Semiorco
armaduras: Ligeras (cuero, cuero tachonado)
armas: Arma de proyectil, espada corta, daga
habilidades_especiales:
  • Ataque furtivo (+4 ataque, daño x2 por la espalda)
  • Abrir cerraduras
  • Detectar/Desarmar trampas
  • Moverse en silencio
  • Esconderse en las sombras
  • Robar
  • Escalar muros
  • Leer lenguajes (nivel 4+)
nivel_maximo: 20
ataque_furtivo: x2 daño niveles 1-4, x3 niveles 5-8, x4 niveles 9-12, x5 niveles 13+
```

---

### Escenario: Consultar modificadores de Fuerza durante combate

**Jugador:** "Mi guerrero tiene FUE 18/75, ¿cuánto de bonus de daño es?"

```bash
🎲 DM> /ability fuerza
```

**Resultado:**
```
======================================================================
📚 ABILITIES: Fuerza
📍 Ruta: Fuerza
======================================================================
combate:
  • modificador_ataque: Suma a tiradas de ataque melé
  • modificador_daño: Suma a daño melé
  • tabla: 
    '18/51-99': {'ataque': 2, 'daño': 3}
    ...
```

**DM:** "Con 18/75, tienes +2 al ataque y +3 al daño"

---

### Escenario: Buscar info de arma

**Jugador:** "¿Cuánto daño hace un arco largo?"

```bash
🎲 DM> /item arco largo
```

**Resultado:**
```
======================================================================
📚 EQUIPMENT: Arco largo
📍 Ruta: Equipo → Armas → Arco largo
======================================================================
daño: 1d8
tipo: Perforante
alcance: 21/42/63m
peso: 1.5
precio: 75
```

---

### Escenario: Regla de THAC0 durante combate

**Jugador:** "¿Qué THAC0 tiene un guerrero nivel 5?"

```bash
🎲 DM> /rules THAC0
```

**Resultado:**
```
======================================================================
📚 RULES: THAC0
📍 Ruta: Combate → THAC0
======================================================================
descripcion: To Hit Armor Class 0 - Número necesario para impactar AC 0
por_nivel:
  • Guerrero 1: 20
  • Guerrero 2: 19
  • Guerrero 3: 18
  • Guerrero 4: 17
  • Guerrero 5: 16
  • Guerrero 6: 15
  ...
```

**DM:** "Un guerrero nivel 5 tiene THAC0 16"

---

### Escenario: Consultar objeto mágico encontrado

**DM:** "Encuentran una Poción de Curación en el cofre"

**Jugador:** "¿Cuánto cura?"

```bash
🎲 DM> /item poción de curación
```

**Resultado:**
```
======================================================================
📚 MAGIC_ITEMS: Poción de Curación
📍 Ruta: Poción de Curación
======================================================================
tipo: Poción
efecto: Cura 2d4+2 HP
uso: Acción para beber
```

---

## Flujo de Combate Completo con Consultas

```bash
# Cargar personaje
🎲 DM> /character Flurim_hijo_de_Drebem_character.json
✅ Personaje Flurim hijo de Drebem cargado

# Iniciar combate
⚔️ Flurim [Enano Guerrero Nv.1] HP:14/14
🎲 DM> /combat start
⚔️ Combate iniciado

# Agregar enemigos
⚔️ Flurim [Enano Guerrero Nv.1] HP:14/14
🎲 DM> /combat add o
  1. Ogro
  2. Orco
  3. Oso búho

# Seleccionar orco
⚔️ Flurim [Enano Guerrero Nv.1] HP:14/14
🎲 DM> 2

# Consultar stats del orco
⚔️ Flurim [Enano Guerrero Nv.1] HP:14/14
🎲 DM> /monster orco
🐉 ORCO - HD: 1
HP: 7 | AC: 6 | THAC0: 19
Daño: 1d8 (espada)

# Iniciar combate
⚔️ Flurim [Enano Guerrero Nv.1] HP:14/14
🎲 DM> /combat init
🎯 Iniciativa calculada
📏 Distancia inicial: 10m (cerca)

# Consultar regla de distancia
⚔️ COMBATE Round 1 | Dist: 10m | PJs: 1 | Enemigos: 1
🎯 Turno: Flurim (HP: 14/14)
🎲 DM> /rules movimiento
📚 Movimiento: 12m/round base para humanos/enanos

# Acercarse
⚔️ COMBATE Round 1 | Dist: 10m | PJs: 1 | Enemigos: 1
🎯 Turno: Flurim (HP: 14/14)
🎲 DM> /combat move approach
📏 Distancia cambiada: 10m → MELÉ

# Atacar
⚔️ COMBATE Round 1 | Dist: MELÉ | PJs: 1 | Enemigos: 1
🎯 Turno: Flurim (HP: 14/14)
🎲 DM> /combat attack 1
🎲 Tirada: 15 + modificadores
🎯 ¡IMPACTO! Daño: 6
💀 Orco derrotado
```

---

## Búsquedas Rápidas Comunes

### Durante Preparación de Conjuros
```bash
/spell detectar magia
/spell luz
/spell dormir
/spell curar heridas
```

### Durante Creación de Personaje
```bash
/class guerrero
/class clérigo
/ability fuerza
/ability destreza
/item armadura de placas
/item espada larga
```

### Durante Exploración
```bash
/rules escalar
/rules nadar
/rules caída
/rules iluminación
/rules sorpresa
```

### Durante Combate
```bash
/rules iniciativa
/rules ataque
/rules daño
/rules AC
/rules THAC0
/rules salvación
```

### Durante Roleplay
```bash
/rules reacciones NPC
/rules chequeos de atributos
/ability carisma
```

---

## Tips de Uso

1. **Búsqueda parcial funciona:** `/spell bola` encuentra "Bola de Fuego"
2. **No distingue mayúsculas:** `/spell DORMIR` = `/spell dormir`
3. **Muestra múltiples resultados:** Si hay varias coincidencias, muestra las mejores
4. **Categorías opcionales:** `/rules` busca solo en reglas, más rápido
5. **Sin categoría busca todo:** Omite categoría para buscar en toda la biblioteca

---

🎲 **¡Consulta rápida sin interrumpir la inmersión!** 🎲
