"""
Biblioteca de reglas AD&D 2e - Sistema de consulta inteligente
Incluye reglas, conjuros, clases, habilidades, objetos mágicos, etc.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import re


class RuleBook:
    """Base de datos de reglas de AD&D 2e"""
    
    def __init__(self):
        self.rules = self._load_rules()
        self.spells = self._load_spells()
        self.classes = self._load_classes()
        self.abilities = self._load_abilities()
        self.magic_items = self._load_magic_items()
        self.equipment = self._load_equipment()
        
    def _load_rules(self) -> Dict[str, Any]:
        """Carga reglas del juego"""
        return {
            "Combate": {
                "Iniciativa": {
                    "descripcion": "Cada combatiente tira 1d10. Mayor resultado actúa primero.",
                    "modificadores": "DES modifica iniciativa: 18+ (+2), 16-17 (+1), 6-7 (-1), 5- (-2)",
                    "sorpresa": "Tirar 1d10. 1-3 = sorprendido (pierde primer turno)"
                },
                "Ataque": {
                    "descripcion": "Tirar 1d20, comparar con THAC0",
                    "formula": "THAC0 - Tirada ≥ AC del objetivo = Impacta",
                    "critico": "20 natural = impacto automático + doble daño",
                    "pifia": "1 natural = fallo automático",
                    "modificadores": {
                        "cobertura": "1/4 (+1 AC), 1/2 (+2 AC), 3/4 (+3 AC), Total (+4 AC)",
                        "superioridad_numerica": "2vs1 (+1), 3+vs1 (+2)",
                        "terreno_elevado": "+1 al atacante",
                        "cegado": "-4 al ataque",
                        "invisible": "+4 al ataque del invisible"
                    }
                },
                "Daño": {
                    "descripcion": "Tirar dados de daño del arma + modificadores",
                    "modificador_fuerza": {
                        "3-5": -2,
                        "6-7": -1,
                        "8-15": 0,
                        "16": 1,
                        "17": 2,
                        "18": 2,
                        "18/01-50": 3,
                        "18/51-99": 4,
                        "18/00": 5
                    },
                    "critico": "Doble daño en crítico (20 natural)",
                    "minimo": "Siempre al menos 1 de daño si impacta"
                },
                "AC (Clase de Armadura)": {
                    "descripcion": "Menor es mejor. AC 10 = sin armadura, AC -10 = mejor posible",
                    "armaduras": {
                        "Sin armadura": 10,
                        "Armadura de cuero": 8,
                        "Armadura de cuero tachonado": 7,
                        "Cota de mallas": 5,
                        "Armadura de bandas": 4,
                        "Armadura de placas": 3,
                        "Armadura completa": 1
                    },
                    "escudos": "Escudo -1 AC",
                    "destreza": {
                        "3-5": +4,
                        "6": +3,
                        "7-8": +2,
                        "9-11": +1,
                        "12-14": 0,
                        "15": -1,
                        "16": -2,
                        "17": -3,
                        "18+": -4
                    }
                },
                "THAC0": {
                    "descripcion": "To Hit Armor Class 0 - Número necesario para impactar AC 0",
                    "por_nivel": {
                        "Guerrero 1": 20,
                        "Guerrero 2": 19,
                        "Guerrero 3": 18,
                        "Guerrero 4": 17,
                        "Guerrero 5": 16,
                        "Guerrero 6": 15,
                        "Guerrero 7": 14,
                        "Clérigo/Pícaro 1-3": 20,
                        "Clérigo/Pícaro 4-6": 19,
                        "Clérigo/Pícaro 7-9": 18,
                        "Mago 1-5": 20,
                        "Mago 6-10": 19
                    }
                },
                "Movimiento": {
                    "descripcion": "Metros por round (6 segundos)",
                    "base_humano": 12,
                    "base_enano": 9,
                    "base_elfo": 12,
                    "base_mediano": 9,
                    "carga": "Carga pesada reduce movimiento a la mitad",
                    "carrera": "x3 movimiento, pero no puede atacar ese round"
                }
            },
            
            "Tiradas de Salvación": {
                "descripcion": "Tirar 1d20, igualar o superar el valor de salvación",
                "tipos": [
                    "Paralización, Veneno o Muerte por Magia",
                    "Varita Mágica",
                    "Petrificación o Transformación",
                    "Soplo de Dragón",
                    "Conjuro, Bastón o Vara"
                ],
                "modificadores": {
                    "Sabiduría": "Bonifica salvaciones vs. magia mental",
                    "Destreza": "Bonifica salvaciones vs. área de efecto",
                    "Constitución": "Bonifica salvaciones vs. veneno"
                }
            },
            
            "Chequeos de Atributos": {
                "descripcion": "Tirar 1d20, resultado ≤ atributo = éxito",
                "fuerza": "Abrir puertas, doblar barras, levantar peso",
                "destreza": "Equilibrio, esquivar, coger objetos",
                "constitucion": "Resistir enfermedad, aguantar aliento",
                "inteligencia": "Recordar información, resolver acertijos",
                "sabiduria": "Percepción, intuición, detectar mentiras",
                "carisma": "Persuasión, liderazgo, reacciones NPC"
            },
            
            "Experiencia y Niveles": {
                "descripcion": "XP por monstruos derrotados, objetivos cumplidos, tesoros",
                "xp_monstruos": "Varía según HD del monstruo",
                "xp_tesoro": "1 XP por cada 1 PO de valor",
                "xp_roleplay": "Bonificaciones por buen roleplay",
                "nivel_maximo": "Varía por clase (generalmente 20)"
            },
            
            "Descanso y Curación": {
                "descanso_corto": "1 hora de descanso",
                "descanso_largo": "8 horas de sueño completo",
                "curacion_natural": "1 HP por día de descanso completo",
                "curacion_magica": "Conjuros de curación inmediatos",
                "muerte": "A 0 HP = inconsciente, a -10 HP = muerte"
            },
            
            "Magia": {
                "lanzamiento": {
                    "descripcion": "Requiere memorización previa de conjuros",
                    "tiempo": "Varía por conjuro (1 acción a varios rounds)",
                    "componentes": "Verbal, Somático, Material (según conjuro)",
                    "interrupcion": "Daño durante lanzamiento = conjuro perdido",
                    "concentracion": "Algunos conjuros requieren concentración continua"
                },
                "memorizacion": {
                    "descripcion": "Tras descanso largo, el mago memoriza conjuros",
                    "tiempo": "15 minutos por nivel de conjuro",
                    "limite": "Según nivel del mago y INT",
                    "grimorio": "Debe tener acceso al grimorio"
                },
                "escuelas": [
                    "Abjuración (protección)",
                    "Conjuración (invocar)",
                    "Adivinación (información)",
                    "Encantamiento (controlar mentes)",
                    "Evocación (energía destructiva)",
                    "Ilusión (engaños)",
                    "Nigromancia (muerte/no-muertos)",
                    "Transmutación (transformar)"
                ]
            },
            
            "Movimiento Especial": {
                "escalar": "Chequeo de Fuerza, velocidad = movimiento/4",
                "nadar": "Chequeo de Fuerza, velocidad = movimiento/2",
                "saltar": "Largo: FUE pies. Alto: FUE/4 pies",
                "caida": "1d6 por cada 3m (máximo 20d6)",
                "sigilo": "Chequeo de Destreza opuesto a Percepción"
            },
            
            "Moral (Monstruos)": {
                "descripcion": "Chequeo 2d10 ≤ Moral del monstruo",
                "cuando_chequear": [
                    "Primera baja del grupo",
                    "50% del grupo derrotado",
                    "Líder derrotado",
                    "Circunstancias aterradoras"
                ],
                "fallo": "Monstruo huye o se rinde"
            },
            
            "Iluminación": {
                "antorcha": "9m de luz, 3m adicionales de penumbra, 1 hora",
                "linterna": "15m de luz, 6 horas con aceite",
                "luz_magica": "Según conjuro",
                "vision_oscuridad": {
                    "Enanos": "Infravisión 18m",
                    "Elfos": "Infravisión 18m",
                    "Medianos": "Infravisión 18m"
                }
            },
            
            "Reacciones NPC": {
                "descripcion": "Tirar 2d10 + modificador CAR",
                "tabla": {
                    "2-": "Hostil, ataca",
                    "3-5": "Hostil, puede atacar",
                    "6-8": "Cauteloso, desconfiado",
                    "9-11": "Neutral, indiferente",
                    "12-14": "Amistoso, servicial",
                    "15+": "Entusiasta, muy servicial"
                }
            },
            
            "Sorpresa": {
                "descripcion": "Ambos bandos tiran 1d10 al inicio del encuentro",
                "sorprendido": "1-3 en 1d10 = pierde 1 round",
                "detectar_trampa": "1-2 en 1d6 (pícaros mejoran esto)"
            }
        }
    
    def _load_spells(self) -> Dict[str, Any]:
        """Carga conjuros de mago y clérigo"""
        return {
            # CONJUROS DE MAGO NIVEL 1
            "Armadura Arcana": {
                "nivel": 1,
                "clase": "Mago",
                "escuela": "Conjuración",
                "tiempo": "1 acción",
                "duracion": "1 hora/nivel",
                "alcance": "Personal",
                "componentes": "V, S, M (trozo de cuero)",
                "efecto": "AC 4 + 1 por cada 5 niveles del mago",
                "descripcion": "Crea una armadura mágica invisible que protege al mago."
            },
            "Detectar Magia": {
                "nivel": 1,
                "clase": "Mago",
                "escuela": "Adivinación",
                "tiempo": "1 acción",
                "duracion": "2 rounds/nivel",
                "alcance": "18m",
                "componentes": "V, S",
                "efecto": "Detecta objetos, criaturas o áreas mágicas en un cono de 18m",
                "descripcion": "Revela la presencia de magia. Concentración: identifica escuela."
            },
            "Luz": {
                "nivel": 1,
                "clase": "Mago",
                "escuela": "Evocación",
                "tiempo": "1 acción",
                "duracion": "1 turno/nivel",
                "alcance": "36m",
                "componentes": "V, M (luciérnaga)",
                "efecto": "Ilumina 12m de radio",
                "descripcion": "Crea luz equivalente a una antorcha en un objeto o punto."
            },
            "Misiles Mágicos": {
                "nivel": 1,
                "clase": "Mago",
                "escuela": "Evocación",
                "tiempo": "1 acción",
                "duracion": "Instantáneo",
                "alcance": "45m",
                "componentes": "V, S",
                "efecto": "1d4+1 daño por misil, +1 misil cada 2 niveles (máx 5)",
                "descripcion": "Proyectiles mágicos que impactan automáticamente.",
                "daño": "1d4+1 por misil"
            },
            "Dormir": {
                "nivel": 1,
                "clase": "Mago",
                "escuela": "Encantamiento",
                "tiempo": "1 acción",
                "duracion": "5 rounds/nivel",
                "alcance": "27m",
                "componentes": "V, S, M (arena fina)",
                "efecto": "Duerme criaturas con 4 HD o menos en área de 9m de radio",
                "descripcion": "Afecta a 2d4 HD de criaturas, empezando por las más débiles.",
                "salvacion": "Ninguna"
            },
            "Escudo": {
                "nivel": 1,
                "clase": "Mago",
                "escuela": "Abjuración",
                "tiempo": "1 acción",
                "duracion": "5 rounds/nivel",
                "alcance": "Personal",
                "componentes": "V, S",
                "efecto": "AC 2 contra proyectiles, AC 4 contra otras cosas, inmune a Misiles Mágicos",
                "descripcion": "Crea un escudo invisible que protege al mago."
            },
            
            # CONJUROS DE MAGO NIVEL 2
            "Bola de Fuego Minúscula": {
                "nivel": 2,
                "clase": "Mago",
                "escuela": "Evocación",
                "tiempo": "2 acciones",
                "duracion": "Instantáneo",
                "alcance": "12m",
                "componentes": "V, S, M (bola de guano de murciélago)",
                "efecto": "1d3 por nivel de daño de fuego en 5m de radio",
                "descripcion": "Versión menor de Bola de Fuego.",
                "daño": "1d3/nivel",
                "salvacion": "Mitad de daño"
            },
            "Invisibilidad": {
                "nivel": 2,
                "clase": "Mago",
                "escuela": "Ilusión",
                "tiempo": "2 acciones",
                "duracion": "Hasta atacar o lanzar conjuro",
                "alcance": "Toque",
                "componentes": "V, S, M (pestaña de goma arábiga)",
                "efecto": "Criatura u objeto se vuelve invisible",
                "descripcion": "El objetivo se vuelve invisible. Termina al atacar."
            },
            "Telaraña": {
                "nivel": 2,
                "clase": "Mago",
                "escuela": "Conjuración",
                "tiempo": "2 acciones",
                "duracion": "2 turnos/nivel",
                "alcance": "15m",
                "componentes": "V, S, M (telaraña)",
                "efecto": "Crea telarañas pegajosas en área de 6x6x6m",
                "descripcion": "Las criaturas quedan atrapadas. FUE para liberarse.",
                "salvacion": "Esquiva si tiene espacio"
            },
            
            # CONJUROS DE MAGO NIVEL 3
            "Bola de Fuego": {
                "nivel": 3,
                "clase": "Mago",
                "escuela": "Evocación",
                "tiempo": "3 acciones",
                "duracion": "Instantáneo",
                "alcance": "30m",
                "componentes": "V, S, M (bola de guano de murciélago + azufre)",
                "efecto": "1d6 por nivel de daño de fuego en 6m de radio (máx 10d6)",
                "descripcion": "Explosión de fuego devastadora.",
                "daño": "1d6/nivel (máx 10d6)",
                "salvacion": "Mitad de daño"
            },
            "Rayo": {
                "nivel": 3,
                "clase": "Mago",
                "escuela": "Evocación",
                "tiempo": "3 acciones",
                "duracion": "Instantáneo",
                "alcance": "12m",
                "componentes": "V, S, M (pelo + vara de ámbar)",
                "efecto": "1d6 por nivel de daño eléctrico en línea de 24m (máx 10d6)",
                "descripcion": "Rayo de electricidad que rebota en paredes.",
                "daño": "1d6/nivel (máx 10d6)",
                "salvacion": "Mitad de daño"
            },
            "Volar": {
                "nivel": 3,
                "clase": "Mago",
                "escuela": "Transmutación",
                "tiempo": "1 acción",
                "duracion": "1 turno/nivel",
                "alcance": "Toque",
                "componentes": "V, S, M (pluma de ala)",
                "efecto": "Velocidad de vuelo 18m/round",
                "descripcion": "El objetivo puede volar a voluntad."
            },
            
            # CONJUROS DE CLÉRIGO NIVEL 1
            "Curar Heridas Leves": {
                "nivel": 1,
                "clase": "Clérigo",
                "escuela": "Nigromancia",
                "tiempo": "5 acciones",
                "duracion": "Permanente",
                "alcance": "Toque",
                "componentes": "V, S",
                "efecto": "Cura 1d8 HP",
                "descripcion": "Canaliza energía positiva para curar heridas.",
                "curacion": "1d8"
            },
            "Bendición": {
                "nivel": 1,
                "clase": "Clérigo",
                "escuela": "Conjuración",
                "tiempo": "1 round",
                "duracion": "6 rounds",
                "alcance": "18m",
                "componentes": "V, S, M (agua bendita)",
                "efecto": "+1 ataque y moral para aliados en 15m de radio",
                "descripcion": "Bendice a los aliados, mejorando sus capacidades."
            },
            "Crear Agua": {
                "nivel": 1,
                "clase": "Clérigo",
                "escuela": "Conjuración",
                "tiempo": "1 round",
                "duracion": "Permanente",
                "alcance": "9m",
                "componentes": "V, S",
                "efecto": "Crea 12 litros de agua/nivel",
                "descripcion": "Crea agua potable de la nada."
            },
            "Detectar Mal": {
                "nivel": 1,
                "clase": "Clérigo",
                "escuela": "Adivinación",
                "tiempo": "1 round",
                "duracion": "1 turno + 5 rounds/nivel",
                "alcance": "36m",
                "componentes": "V, S, M (símbolo sagrado)",
                "efecto": "Detecta criaturas o intenciones malvadas",
                "descripcion": "Revela la presencia de mal en un cono de 36m."
            },
            "Protección contra el Mal": {
                "nivel": 1,
                "clase": "Clérigo",
                "escuela": "Abjuración",
                "tiempo": "1 acción",
                "duracion": "3 rounds/nivel",
                "alcance": "Toque",
                "componentes": "V, S, M (círculo de plata)",
                "efecto": "+2 AC y salvaciones contra criaturas malvadas",
                "descripcion": "Crea una barrera contra el mal. Impide posesión."
            },
            
            # CONJUROS DE CLÉRIGO NIVEL 2
            "Aguantar Elementos": {
                "nivel": 2,
                "clase": "Clérigo",
                "escuela": "Abjuración",
                "tiempo": "1 round",
                "duracion": "1 hora/nivel",
                "alcance": "Toque",
                "componentes": "V, S",
                "efecto": "Protección contra calor o frío extremo",
                "descripcion": "El objetivo es inmune a temperaturas extremas."
            },
            "Detener Persona": {
                "nivel": 2,
                "clase": "Clérigo",
                "escuela": "Encantamiento",
                "tiempo": "5 acciones",
                "duracion": "2 rounds/nivel",
                "alcance": "36m",
                "componentes": "V, S, M (hierro)",
                "efecto": "Paraliza 1-4 humanos o humanoides",
                "descripcion": "Inmoviliza completamente al objetivo.",
                "salvacion": "Niega efecto"
            },
            "Silencio 5m Radio": {
                "nivel": 2,
                "clase": "Clérigo",
                "escuela": "Abjuración",
                "tiempo": "5 acciones",
                "duracion": "2 rounds/nivel",
                "alcance": "36m",
                "componentes": "V, S",
                "efecto": "Zona de silencio absoluto de 5m de radio",
                "descripcion": "Impide lanzar conjuros con componente verbal."
            },
            
            # CONJUROS DE CLÉRIGO NIVEL 3
            "Curar Enfermedad": {
                "nivel": 3,
                "clase": "Clérigo",
                "escuela": "Nigromancia",
                "tiempo": "1 round",
                "duracion": "Permanente",
                "alcance": "Toque",
                "componentes": "V, S",
                "efecto": "Cura toda enfermedad",
                "descripcion": "Elimina enfermedades y parásitos del objetivo."
            },
            "Disipar Magia": {
                "nivel": 3,
                "clase": "Clérigo",
                "escuela": "Abjuración",
                "tiempo": "6 acciones",
                "duracion": "Permanente",
                "alcance": "36m",
                "componentes": "V, S",
                "efecto": "Elimina efectos mágicos",
                "descripcion": "Termina conjuros activos. Chequeo de nivel del lanzador."
            },
            "Oración": {
                "nivel": 3,
                "clase": "Clérigo",
                "escuela": "Conjuración",
                "tiempo": "6 acciones",
                "duracion": "1 round/nivel",
                "alcance": "0",
                "componentes": "V, S, M (símbolo sagrado)",
                "efecto": "Aliados +1 todo, enemigos -1 todo",
                "descripcion": "Invoca bendición divina en el campo de batalla."
            }
        }
    
    def _load_classes(self) -> Dict[str, Any]:
        """Carga información de clases"""
        return {
            "Guerrero": {
                "dado_golpe": "d10",
                "requisito_principal": "Fuerza",
                "razas_permitidas": ["Humano", "Enano", "Elfo", "Mediano", "Semielfo", "Semiorco"],
                "armaduras": "Todas",
                "armas": "Todas",
                "habilidades_especiales": [
                    "Bonificación a ataques cada nivel",
                    "Múltiples ataques a niveles altos",
                    "Construcción de fortaleza a nivel 9"
                ],
                "nivel_maximo": 20,
                "xp_nivel_2": 2000,
                "xp_nivel_3": 4000,
                "salvaciones": "Mejores vs. muerte y transformación"
            },
            "Clérigo": {
                "dado_golpe": "d8",
                "requisito_principal": "Sabiduría",
                "razas_permitidas": ["Humano", "Enano", "Mediano", "Semielfo"],
                "armaduras": "Todas (sin filo - no espadas/dagas típicamente)",
                "armas": "Contundentes (maza, martillo, mangual)",
                "conjuros": "Divinos - no requieren grimorio",
                "habilidades_especiales": [
                    "Expulsar no-muertos",
                    "Conjuros divinos desde nivel 1",
                    "Construcción de templo a nivel 8"
                ],
                "nivel_maximo": 20,
                "expulsion": "2d6 vs. HD de no-muerto"
            },
            "Mago": {
                "dado_golpe": "d4",
                "requisito_principal": "Inteligencia",
                "razas_permitidas": ["Humano", "Elfo", "Semielfo"],
                "armaduras": "Ninguna",
                "armas": "Daga, bastón, dardo, cuchillo",
                "conjuros": "Arcanos - requieren grimorio",
                "habilidades_especiales": [
                    "Mayor variedad de conjuros",
                    "Investigación mágica",
                    "Creación de objetos mágicos",
                    "Construcción de torre a nivel 10"
                ],
                "nivel_maximo": 20,
                "especialización": "Puede especializarse en escuela de magia"
            },
            "Pícaro": {
                "dado_golpe": "d6",
                "requisito_principal": "Destreza",
                "razas_permitidas": ["Humano", "Enano", "Elfo", "Mediano", "Semielfo", "Semiorco"],
                "armaduras": "Ligeras (cuero, cuero tachonado)",
                "armas": "Arma de proyectil, espada corta, daga",
                "habilidades_especiales": [
                    "Ataque furtivo (+4 ataque, daño x2 por la espalda)",
                    "Abrir cerraduras",
                    "Detectar/Desarmar trampas",
                    "Moverse en silencio",
                    "Esconderse en las sombras",
                    "Robar",
                    "Escalar muros",
                    "Leer lenguajes (nivel 4+)"
                ],
                "nivel_maximo": 20,
                "ataque_furtivo": "x2 daño niveles 1-4, x3 niveles 5-8, x4 niveles 9-12, x5 niveles 13+"
            },
            "Explorador": {
                "dado_golpe": "d10",
                "requisito_principal": "Fuerza, Destreza, Sabiduría",
                "razas_permitidas": ["Humano", "Elfo", "Semielfo"],
                "armaduras": "Todas",
                "armas": "Todas",
                "conjuros": "Divinos (nivel 8+)",
                "habilidades_especiales": [
                    "Rastrear",
                    "Estilo de combate a dos armas",
                    "Enemigo favorito (+4 daño)",
                    "Conjuros de druida a nivel 8",
                    "Atraer seguidores a nivel 10"
                ],
                "nivel_maximo": 20,
                "rastrear": "+1 por nivel al chequeo"
            },
            "Paladín": {
                "dado_golpe": "d10",
                "requisito_principal": "Fuerza, Carisma",
                "requisitos_minimos": "FUE 12, CON 9, SAB 13, CAR 17",
                "razas_permitidas": ["Humano"],
                "armaduras": "Todas",
                "armas": "Todas",
                "alineamiento": "Solo Legal Bueno",
                "conjuros": "Divinos (nivel 9+)",
                "habilidades_especiales": [
                    "Detectar mal (18m, a voluntad)",
                    "Inmune a enfermedad",
                    "Curar mediante imposición de manos (2 HP/nivel, 1 vez/día)",
                    "Expulsar no-muertos como clérigo 2 niveles menor",
                    "Conjuros de clérigo a nivel 9",
                    "Invocar montura celestial (nivel 4+)"
                ],
                "nivel_maximo": 20,
                "codigo": "Debe seguir código estricto de honor"
            }
        }
    
    def _load_abilities(self) -> Dict[str, Any]:
        """Carga efectos de atributos"""
        return {
            "Fuerza": {
                "combate": {
                    "modificador_ataque": "Suma a tiradas de ataque melé",
                    "modificador_daño": "Suma a daño melé",
                    "tabla": {
                        "3": {"ataque": -3, "daño": -1},
                        "4-5": {"ataque": -2, "daño": -1},
                        "6-7": {"ataque": -1, "daño": 0},
                        "8-15": {"ataque": 0, "daño": 0},
                        "16": {"ataque": 0, "daño": 1},
                        "17": {"ataque": 1, "daño": 1},
                        "18": {"ataque": 1, "daño": 2},
                        "18/01-50": {"ataque": 1, "daño": 3},
                        "18/51-99": {"ataque": 2, "daño": 3},
                        "18/00": {"ataque": 2, "daño": 4},
                        "19": {"ataque": 3, "daño": 7}
                    }
                },
                "carga": "Peso máximo transportable",
                "puertas": "Probabilidad de abrir puerta atascada"
            },
            "Destreza": {
                "combate": {
                    "modificador_ac": "Bonifica/penaliza CA",
                    "modificador_proyectil": "Bonifica ataques a distancia",
                    "tabla": {
                        "3": {"ac": 4, "proyectil": -3},
                        "4": {"ac": 3, "proyectil": -2},
                        "5": {"ac": 2, "proyectil": -1},
                        "6": {"ac": 1, "proyectil": 0},
                        "7-14": {"ac": 0, "proyectil": 0},
                        "15": {"ac": -1, "proyectil": 0},
                        "16": {"ac": -2, "proyectil": 1},
                        "17": {"ac": -3, "proyectil": 2},
                        "18": {"ac": -4, "proyectil": 2},
                        "19": {"ac": -4, "proyectil": 3}
                    }
                },
                "iniciativa": "Modificador a iniciativa",
                "habilidades_picaro": "Bonifica habilidades de pícaro"
            },
            "Constitución": {
                "hp": "HP adicionales por nivel",
                "tabla": {
                    "3": -2,
                    "4-6": -1,
                    "7-14": 0,
                    "15": 1,
                    "16": 2,
                    "17": 2,
                    "18": 2,
                    "19": 2
                },
                "curacion": "Bonifica curación natural",
                "resistencia": "Salvaciones vs. veneno y muerte"
            },
            "Inteligencia": {
                "idiomas": "Número de idiomas que puede aprender",
                "conjuros_mago": "Probabilidad de aprender conjuro, conjuros/nivel",
                "tabla": {
                    "9": {"prob_aprender": 35, "max_nivel": 4, "max_conjuros": 6},
                    "10": {"prob_aprender": 40, "max_nivel": 5, "max_conjuros": 7},
                    "11": {"prob_aprender": 45, "max_nivel": 5, "max_conjuros": 7},
                    "12": {"prob_aprender": 50, "max_nivel": 6, "max_conjuros": 7},
                    "13": {"prob_aprender": 55, "max_nivel": 6, "max_conjuros": 9},
                    "14": {"prob_aprender": 60, "max_nivel": 7, "max_conjuros": 9},
                    "15": {"prob_aprender": 65, "max_nivel": 7, "max_conjuros": 11},
                    "16": {"prob_aprender": 70, "max_nivel": 8, "max_conjuros": 11},
                    "17": {"prob_aprender": 75, "max_nivel": 8, "max_conjuros": 14},
                    "18": {"prob_aprender": 85, "max_nivel": 9, "max_conjuros": 18},
                    "19": {"prob_aprender": 95, "max_nivel": 9, "max_conjuros": "todos"}
                }
            },
            "Sabiduría": {
                "conjuros_clerigo": "Conjuros de bonificación",
                "salvacion_mental": "Bonifica salvaciones vs. magia mental",
                "tabla": {
                    "13": {"bonificacion_1": 1},
                    "14": {"bonificacion_1": 2},
                    "15": {"bonificacion_1": 2, "bonificacion_2": 1},
                    "16": {"bonificacion_1": 2, "bonificacion_2": 2},
                    "17": {"bonificacion_1": 2, "bonificacion_2": 2, "bonificacion_3": 1},
                    "18": {"bonificacion_1": 2, "bonificacion_2": 2, "bonificacion_3": 1, "bonificacion_4": 1}
                }
            },
            "Carisma": {
                "reacciones": "Modificador a reacciones NPC",
                "seguidores": "Número máximo de seguidores leales",
                "tabla": {
                    "3": {"reaccion": -5, "seguidores": 0},
                    "4": {"reaccion": -4, "seguidores": 1},
                    "5": {"reaccion": -3, "seguidores": 2},
                    "6": {"reaccion": -2, "seguidores": 2},
                    "7": {"reaccion": -1, "seguidores": 3},
                    "8-12": {"reaccion": 0, "seguidores": 4},
                    "13": {"reaccion": 1, "seguidores": 5},
                    "14": {"reaccion": 1, "seguidores": 6},
                    "15": {"reaccion": 3, "seguidores": 7},
                    "16": {"reaccion": 4, "seguidores": 8},
                    "17": {"reaccion": 6, "seguidores": 10},
                    "18": {"reaccion": 8, "seguidores": 15}
                }
            }
        }
    
    def _load_magic_items(self) -> Dict[str, Any]:
        """Carga objetos mágicos comunes"""
        return {
            "Espada +1": {
                "tipo": "Arma",
                "bonificacion": "+1 ataque y daño",
                "rareza": "Común"
            },
            "Armadura +1": {
                "tipo": "Armadura",
                "bonificacion": "+1 AC (AC -1 mejor)",
                "rareza": "Común"
            },
            "Poción de Curación": {
                "tipo": "Poción",
                "efecto": "Cura 2d4+2 HP",
                "uso": "Acción para beber"
            },
            "Varita de Misiles Mágicos": {
                "tipo": "Varita",
                "cargas": "50 cargas",
                "efecto": "Lanza Misiles Mágicos (1 carga por misil)",
                "rareza": "Poco común"
            },
            "Anillo de Protección +1": {
                "tipo": "Anillo",
                "bonificacion": "+1 AC y salvaciones",
                "rareza": "Poco común"
            },
            "Capa Élfica": {
                "tipo": "Objeto maravilloso",
                "efecto": "+2 a Esconderse",
                "rareza": "Poco común"
            },
            "Botas de Velocidad": {
                "tipo": "Objeto maravilloso",
                "efecto": "x2 velocidad por 10 rounds/día",
                "rareza": "Raro"
            }
        }
    
    def _load_equipment(self) -> Dict[str, Any]:
        """Carga equipo estándar"""
        return {
            "Armas": {
                "Daga": {"daño": "1d4", "tipo": "Perforante", "peso": 0.5, "precio": 2},
                "Espada corta": {"daño": "1d6", "tipo": "Cortante", "peso": 1.5, "precio": 10},
                "Espada larga": {"daño": "1d8", "tipo": "Cortante", "peso": 2, "precio": 15},
                "Espada bastarda": {"daño": "1d10/2d8", "tipo": "Cortante", "peso": 3, "precio": 25},
                "Espada a dos manos": {"daño": "1d10", "tipo": "Cortante", "peso": 5, "precio": 50},
                "Hacha de mano": {"daño": "1d6", "tipo": "Cortante", "peso": 2, "precio": 1},
                "Hacha de batalla": {"daño": "1d8", "tipo": "Cortante", "peso": 3.5, "precio": 5},
                "Maza": {"daño": "1d6", "tipo": "Contundente", "peso": 3, "precio": 5},
                "Martillo de guerra": {"daño": "1d4+1", "tipo": "Contundente", "peso": 2.5, "precio": 2},
                "Lanza": {"daño": "1d6/1d8", "tipo": "Perforante", "peso": 2.5, "precio": 1},
                "Arco corto": {"daño": "1d6", "tipo": "Perforante", "alcance": "15/30/45m", "peso": 1, "precio": 30},
                "Arco largo": {"daño": "1d8", "tipo": "Perforante", "alcance": "21/42/63m", "peso": 1.5, "precio": 75},
                "Ballesta ligera": {"daño": "1d6", "tipo": "Perforante", "alcance": "18/36/54m", "peso": 2, "precio": 35}
            },
            "Armaduras": {
                "Cuero": {"ac": 8, "peso": 7, "precio": 5},
                "Cuero tachonado": {"ac": 7, "peso": 10, "precio": 20},
                "Cota de anillas": {"ac": 7, "peso": 15, "precio": 100},
                "Cota de escamas": {"ac": 6, "peso": 18, "precio": 120},
                "Cota de mallas": {"ac": 5, "peso": 20, "precio": 75},
                "Armadura de bandas": {"ac": 4, "peso": 17.5, "precio": 200},
                "Armadura de placas": {"ac": 3, "peso": 22.5, "precio": 600},
                "Escudo pequeño": {"ac": -1, "peso": 2, "precio": 3},
                "Escudo mediano": {"ac": -1, "peso": 5, "precio": 7},
                "Escudo de cuerpo": {"ac": -1, "peso": 7.5, "precio": 10}
            },
            "Equipo de aventurero": {
                "Mochila": {"capacidad": "15kg", "precio": 2},
                "Saco": {"capacidad": "15kg", "precio": 1},
                "Cuerda (15m)": {"peso": 3.5, "precio": 1},
                "Antorcha": {"duración": "1 hora", "precio": 0.01},
                "Aceite (frasco)": {"duración": "6 horas", "precio": 0.1},
                "Raciones (1 día)": {"peso": 1, "precio": 0.5},
                "Odre de agua": {"capacidad": "1 litro", "precio": 0.5},
                "Pedernal y yesca": {"precio": 0.5},
                "Pala": {"peso": 3, "precio": 2},
                "Palanca": {"peso": 2.5, "precio": 2},
                "Martillo": {"peso": 1, "precio": 0.5},
                "Estacas (12)": {"peso": 1.5, "precio": 0.3}
            }
        }
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Búsqueda inteligente en toda la biblioteca
        
        Args:
            query: Término de búsqueda
            category: Categoría opcional (rules, spells, classes, abilities, items, equipment)
        """
        query_lower = query.lower()
        results = []
        
        # Determinar categorías a buscar
        categories = {
            'rules': self.rules,
            'spells': self.spells,
            'classes': self.classes,
            'abilities': self.abilities,
            'magic_items': self.magic_items,
            'equipment': self.equipment
        }
        
        if category:
            categories = {category: categories.get(category, {})}
        
        # Buscar en cada categoría
        for cat_name, cat_data in categories.items():
            self._search_recursive(query_lower, cat_data, cat_name, [], results)
        
        return results
    
    def _search_recursive(self, query: str, data: Any, category: str, path: List[str], results: List[Dict]):
        """Búsqueda recursiva en estructura de datos"""
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                new_path = path + [key]
                
                # Coincidencia exacta o parcial en clave
                if query in key_lower:
                    results.append({
                        'category': category,
                        'path': ' → '.join(new_path),
                        'name': key,
                        'content': value,
                        'relevance': self._calculate_relevance(query, key_lower, value)
                    })
                
                # Buscar en valores
                if isinstance(value, (str, int, float)):
                    value_str = str(value).lower()
                    if query in value_str:
                        results.append({
                            'category': category,
                            'path': ' → '.join(new_path),
                            'name': key,
                            'content': value,
                            'relevance': self._calculate_relevance(query, key_lower, value_str)
                        })
                else:
                    self._search_recursive(query, value, category, new_path, results)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._search_recursive(query, item, category, path + [f"[{i}]"], results)
    
    def _calculate_relevance(self, query: str, key: str, value: Any) -> int:
        """Calcula relevancia del resultado (0-100)"""
        relevance = 0
        
        # Coincidencia exacta en clave
        if query == key:
            relevance += 50
        elif query in key:
            relevance += 30
        
        # Coincidencia en valor
        if isinstance(value, str):
            value_lower = value.lower()
            if query == value_lower:
                relevance += 30
            elif query in value_lower:
                relevance += 10
        
        # Palabras completas
        if f" {query} " in f" {key} ":
            relevance += 20
        
        return min(relevance, 100)
    
    def format_result(self, result: Dict) -> str:
        """Formatea un resultado de búsqueda"""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"📚 {result['category'].upper()}: {result['name']}")
        output.append(f"📍 Ruta: {result['path']}")
        output.append(f"{'='*70}")
        
        content = result['content']
        
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, dict):
                    output.append(f"\n{key}:")
                    for sub_key, sub_value in value.items():
                        output.append(f"  • {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    output.append(f"\n{key}:")
                    for item in value:
                        output.append(f"  • {item}")
                else:
                    output.append(f"{key}: {value}")
        else:
            output.append(str(content))
        
        return '\n'.join(output)


def main():
    """Demostración del sistema de consulta"""
    rulebook = RuleBook()
    
    print("📚 BIBLIOTECA DE REGLAS AD&D 2e")
    print("="*70)
    print("\nBúsquedas de ejemplo:")
    
    # Ejemplos de búsqueda
    queries = [
        ("iniciativa", None),
        ("bola de fuego", "spells"),
        ("guerrero", "classes"),
        ("fuerza", "abilities")
    ]
    
    for query, category in queries:
        print(f"\n{'='*70}")
        print(f"Buscando: '{query}'" + (f" en {category}" if category else ""))
        print(f"{'='*70}")
        
        results = rulebook.search(query, category)
        
        if results:
            # Ordenar por relevancia
            results.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Mostrar top 3 resultados
            for i, result in enumerate(results[:3], 1):
                print(rulebook.format_result(result))
                if i < len(results[:3]):
                    print()
        else:
            print("No se encontraron resultados.")


if __name__ == '__main__':
    main()
