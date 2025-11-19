# Gestor de personajes de AD&D 2e
# Convierte PDFs en dataset y gestiona creación de personajes según reglas oficiales

import fitz  # PyMuPDF
import re
import pandas as pd
import os
import json
from collections import defaultdict
import logging
import pickle
from pathlib import Path
import random

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar base de datos de hechizos
try:
    from spells_database import WIZARD_SPELLS, CLERIC_SPELLS, TOTAL_WIZARD, TOTAL_CLERIC
    SPELLS_DB_AVAILABLE = True
except ImportError:
    SPELLS_DB_AVAILABLE = False
    logger.warning("⚠️ No se pudo cargar spells_database.py")

# ============================================================================
# SISTEMA DE EXTRACCIÓN Y CARGA DE DATOS DE PDFs
# ============================================================================

class ADnDDataLoader:
    """Extrae y carga datos de los PDFs de AD&D 2e"""
    
    def __init__(self, pdf_dir=".", cache_file="adnd_data_cache.pkl"):
        self.pdf_dir = Path(pdf_dir)
        self.cache_file = Path(cache_file)
        self.rules = {}
        self.classes = {}
        self.races = {}
        self.spells = {}
        self.equipment = {}
        self.kits = {}  # Kits de personaje por clase
        
    def load_or_extract_data(self):
        """Carga datos del cache o extrae de PDFs si no existe"""
        if self.cache_file.exists():
            logger.info(f"📂 Cargando datos desde cache: {self.cache_file}")
            with open(self.cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self.rules = cached_data.get('rules', {})
                self.classes = cached_data.get('classes', {})
                self.races = cached_data.get('races', {})
                self.spells = cached_data.get('spells', {})
                self.equipment = cached_data.get('equipment', {})
            logger.info("✅ Datos cargados correctamente del cache")
        else:
            logger.info("🔍 Cache no encontrado. Extrayendo datos de PDFs...")
            self.extract_all_pdfs()
            self.save_cache()
    
    def extract_all_pdfs(self):
        """Extrae información de todos los PDFs disponibles"""
        pdf_files = {
            'Manual_jugador.pdf': self.extract_player_manual,
            'Manual_DM.pdf': self.extract_dm_manual,
            'Manual_monstruos.pdf': self.extract_monster_manual,
            'Completo_Enano.pdf': self.extract_race_manual,
            'AD&D - Combate.pdf': self.extract_combat_manual,
            'AD&D 2E - The Complete Advanced Dungeons & Dragons 2nd Edition Archive.pdf': self.extract_complete_archive
        }
        
        for pdf_name, extract_func in pdf_files.items():
            pdf_path = self.pdf_dir / pdf_name
            if pdf_path.exists():
                logger.info(f"📖 Procesando: {pdf_name}")
                try:
                    extract_func(pdf_path)
                except Exception as e:
                    logger.error(f"❌ Error procesando {pdf_name}: {e}")
            else:
                logger.warning(f"⚠️  PDF no encontrado: {pdf_name}")
    
    def extract_player_manual(self, pdf_path):
        """Extrae datos del Manual del Jugador"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text()
            
            # Extraer clases
            self._extract_classes(full_text)
            # Extraer razas
            self._extract_races(full_text)
            # Extraer hechizos
            self._extract_spells(full_text)
            # Extraer reglas de atributos
            self._extract_attribute_rules(full_text)
            
            doc.close()
            logger.info(f"✅ Manual del Jugador procesado: {len(self.classes)} clases, {len(self.spells)} hechizos")
            
        except Exception as e:
            logger.error(f"Error extrayendo Manual del Jugador: {e}")
    
    def extract_dm_manual(self, pdf_path):
        """Extrae datos del Manual del DM"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text()
            
            # Extraer reglas de combate
            self._extract_combat_rules(full_text)
            # Extraer tablas de experiencia
            self._extract_experience_tables(full_text)
            
            doc.close()
            logger.info("✅ Manual del DM procesado")
            
        except Exception as e:
            logger.error(f"Error extrayendo Manual del DM: {e}")
    
    def extract_monster_manual(self, pdf_path):
        """Extrae datos del Manual de Monstruos"""
        try:
            doc = fitz.open(pdf_path)
            logger.info("✅ Manual de Monstruos cargado (datos básicos)")
            doc.close()
        except Exception as e:
            logger.error(f"Error extrayendo Manual de Monstruos: {e}")
    
    def extract_race_manual(self, pdf_path):
        """Extrae datos del manual de razas específico (Completo Enano)"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text()
            
            # Extraer información específica de enanos
            self._extract_dwarf_details(full_text)
            
            doc.close()
            logger.info("✅ Manual de razas (Enano) procesado")
        except Exception as e:
            logger.error(f"Error extrayendo manual de razas: {e}")
    
    def extract_combat_manual(self, pdf_path):
        """Extrae reglas expandidas de combate"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text()
            
            # Extraer reglas de combate expandidas
            self._extract_advanced_combat_rules(full_text)
            # Extraer maniobras especiales
            self._extract_combat_maneuvers(full_text)
            # Extraer reglas de iniciativa
            self._extract_initiative_rules(full_text)
            
            doc.close()
            logger.info("✅ Manual de Combate procesado")
        except Exception as e:
            logger.error(f"Error extrayendo manual de combate: {e}")
    
    def extract_complete_archive(self, pdf_path):
        """Extrae datos del archivo completo de AD&D 2E"""
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            logger.info(f"📚 Procesando archivo completo: {total_pages} páginas")
            
            full_text = ""
            # Procesar en lotes para evitar sobrecarga de memoria
            batch_size = 50
            
            for i in range(0, total_pages, batch_size):
                end_page = min(i + batch_size, total_pages)
                logger.info(f"  Procesando páginas {i+1}-{end_page}/{total_pages}")
                
                batch_text = ""
                for page_num in range(i, end_page):
                    batch_text += doc[page_num].get_text()
                
                full_text += batch_text
            
            # Extraer todo tipo de información
            self._extract_classes(full_text)
            self._extract_races(full_text)
            self._extract_spells(full_text)
            self._extract_equipment(full_text)
            self._extract_proficiencies(full_text)
            self._extract_kits(full_text)
            
            doc.close()
            logger.info("✅ Archivo completo procesado")
        except Exception as e:
            logger.error(f"Error extrayendo archivo completo: {e}")
    
    def _extract_classes(self, text):
        """Extrae información de clases del texto"""
        # Clases básicas completas de AD&D 2e
        base_classes = {
            'Guerrero': {
                'requisitos': {'FUE': 9},
                'requisitos_primarios': ['FUE'],
                'dado_golpe': 10,
                'thac0_inicial': 20,
                'progresion_thac0': 1,
                'ts_base': {'paralisis': 14, 'varitas': 16, 'petrificacion': 15, 'aliento': 17, 'conjuros': 17},
                'armas_permitidas': 'todas',
                'armaduras_permitidas': 'todas',
                'especialidades': ['Paladin', 'Ranger'],
                'habilidades': ['Ataques múltiples', 'Especialización en arma'],
                'descripcion': 'Maestro del combate y las armas'
            },
            'Paladín': {
                'requisitos': {'FUE': 12, 'CON': 9, 'SAB': 13, 'CAR': 17},
                'requisitos_primarios': ['FUE', 'CAR'],
                'dado_golpe': 10,
                'thac0_inicial': 20,
                'progresion_thac0': 1,
                'ts_base': {'paralisis': 14, 'varitas': 16, 'petrificacion': 15, 'aliento': 17, 'conjuros': 17},
                'armas_permitidas': 'todas',
                'armaduras_permitidas': 'todas',
                'hechizos': True,
                'tipo_hechizos': 'Clérigo',
                'nivel_hechizos_inicial': 9,
                'habilidades': ['Detectar mal', 'Protección +2', 'Imposición de manos', 'Curar enfermedades', 'Inmune a enfermedades'],
                'codigo': 'Debe ser Legal Bueno',
                'descripcion': 'Guerrero sagrado con poderes divinos'
            },
            'Ranger': {
                'requisitos': {'FUE': 13, 'DES': 13, 'CON': 14, 'SAB': 14},
                'requisitos_primarios': ['FUE', 'DES', 'SAB'],
                'dado_golpe': 10,
                'thac0_inicial': 20,
                'progresion_thac0': 1,
                'ts_base': {'paralisis': 14, 'varitas': 16, 'petrificacion': 15, 'aliento': 17, 'conjuros': 17},
                'armas_permitidas': 'todas',
                'armaduras_permitidas': 'todas',
                'hechizos': True,
                'tipo_hechizos': 'Druida',
                'nivel_hechizos_inicial': 8,
                'habilidades': ['Rastrear', 'Dos estilos de combate', 'Enemigo racial'],
                'descripcion': 'Guerrero explorador de la naturaleza'
            },
            'Mago': {
                'requisitos': {'INT': 9},
                'requisitos_primarios': ['INT'],
                'dado_golpe': 4,
                'thac0_inicial': 20,
                'progresion_thac0': 3,
                'ts_base': {'paralisis': 14, 'varitas': 11, 'petrificacion': 13, 'aliento': 15, 'conjuros': 12},
                'armas_permitidas': ['daga', 'baston', 'dardo', 'honda', 'cuchillo', 'ballesta'],
                'armaduras_permitidas': 'ninguna',
                'hechizos': True,
                'especialidades': ['Abjurador', 'Conjurador', 'Adivinador', 'Encantador', 'Ilusionista', 'Invocador', 'Nigromante', 'Transmutador'],
                'habilidades': ['Familar', 'Investigación mágica', 'Crear objetos mágicos'],
                'descripcion': 'Maestro de la magia arcana'
            },
            'Especialista': {
                'base': 'Mago',
                'requisitos': {'INT': 9},
                'escuelas': {
                    'Abjurador': {'opuesta': 'Alteración', 'prohibidas': ['Alteración', 'Ilusión']},
                    'Conjurador': {'opuesta': 'Invocación', 'prohibidas': ['Adivinación (mayor)', 'Invocación']},
                    'Adivinador': {'opuesta': 'Conjuración', 'prohibidas': []},
                    'Encantador': {'opuesta': 'Invocación', 'prohibidas': ['Invocación', 'Necromancia']},
                    'Ilusionista': {'opuesta': 'Necromancia', 'prohibidas': ['Necromancia', 'Invocación', 'Abjuración']},
                    'Invocador': {'opuesta': 'Encantamiento', 'prohibidas': ['Encantamiento', 'Conjuración']},
                    'Nigromante': {'opuesta': 'Ilusión', 'prohibidas': ['Ilusión', 'Encantamiento']},
                    'Transmutador': {'opuesta': 'Abjuración', 'prohibidas': ['Abjuración', 'Necromancia', 'Encantamiento']}
                },
                'beneficios': '+1 hechizo por nivel de la escuela',
                'descripcion': 'Mago especializado en una escuela de magia'
            },
            'Clérigo': {
                'requisitos': {'SAB': 9},
                'requisitos_primarios': ['SAB'],
                'dado_golpe': 8,
                'thac0_inicial': 20,
                'progresion_thac0': 2,
                'ts_base': {'paralisis': 10, 'varitas': 14, 'petrificacion': 13, 'aliento': 16, 'conjuros': 15},
                'armas_permitidas': ['todas las romas'],
                'armaduras_permitidas': 'todas',
                'hechizos': True,
                'habilidades': ['Expulsar muertos vivientes', 'Bonificador TS vs hechizos +2'],
                'descripcion': 'Campeón de la fe con poder divino'
            },
            'Druida': {
                'base': 'Clérigo',
                'requisitos': {'SAB': 12, 'CAR': 15},
                'requisitos_primarios': ['SAB', 'CAR'],
                'dado_golpe': 8,
                'thac0_inicial': 20,
                'progresion_thac0': 2,
                'ts_base': {'paralisis': 10, 'varitas': 14, 'petrificacion': 13, 'aliento': 16, 'conjuros': 15},
                'armas_permitidas': ['daga', 'hoz', 'dardo', 'lanza', 'honda', 'baston', 'cimitarra'],
                'armaduras_permitidas': ['cuero', 'cuero tachonado', 'escudo de madera'],
                'alineamiento': 'Debe ser Neutral',
                'hechizos': True,
                'esferas': ['Animal', 'Elemental', 'Curación', 'Vegetal', 'Clima'],
                'habilidades': ['Lenguaje druídico secreto', 'Identificar plantas/animales', 'Pasar sin rastro', 'Forma animal', 'Inmune a encantamiento/hechizo de criaturas del bosque'],
                'descripcion': 'Guardián de la naturaleza y el equilibrio'
            },
            'Ladrón': {
                'requisitos': {'DES': 9},
                'requisitos_primarios': ['DES'],
                'dado_golpe': 6,
                'thac0_inicial': 20,
                'progresion_thac0': 2,
                'ts_base': {'paralisis': 13, 'varitas': 14, 'petrificacion': 12, 'aliento': 16, 'conjuros': 15},
                'armas_permitidas': ['armas cortas y de proyectil'],
                'armaduras_permitidas': 'cuero',
                'habilidades_ladron': {
                    'Abrir Cerraduras': 'base + DES',
                    'Detectar Ruidos': 'base + SAB',
                    'Escalar Muros': 'base + DES',
                    'Esconderse en las Sombras': 'base + DES',
                    'Moverse Sigilosamente': 'base + DES',
                    'Detectar/Desarmar Trampas': 'base + DES',
                    'Robar': 'base + DES',
                    'Leer Lenguajes': 'nivel 4+',
                    'Ataque por la Espalda': 'x2 daño (x3 a nivel 5, x4 a nivel 9, x5 a nivel 13)'
                },
                'descripcion': 'Maestro del sigilo y las habilidades furtivas'
            },
            'Bardo': {
                'requisitos': {'DES': 12, 'INT': 13, 'CAR': 15},
                'requisitos_primarios': ['DES', 'CAR'],
                'dado_golpe': 6,
                'thac0_inicial': 20,
                'progresion_thac0': 2,
                'ts_base': {'paralisis': 13, 'varitas': 14, 'petrificacion': 12, 'aliento': 16, 'conjuros': 15},
                'armas_permitidas': 'todas',
                'armaduras_permitidas': ['cuero', 'cota de mallas', 'escudo'],
                'hechizos': True,
                'tipo_hechizos': 'Mago',
                'nivel_hechizos_inicial': 2,
                'habilidades_ladron': {
                    'Escalar Muros': 50,
                    'Detectar Ruidos': 20,
                    'Robar': 10,
                    'Leer Lenguajes': 5
                },
                'habilidades': ['Influenciar reacciones', 'Conocimiento legendario', 'Usar objetos mágicos'],
                'descripcion': 'Trovador mágico con habilidades variadas'
            },
            'Monje': {
                'requisitos': {'FUE': 15, 'DES': 15, 'SAB': 15},
                'requisitos_primarios': ['FUE', 'DES', 'SAB'],
                'dado_golpe': 4,
                'thac0_inicial': 20,
                'progresion_thac0': 2,
                'ts_base': {'paralisis': 13, 'varitas': 14, 'petrificacion': 12, 'aliento': 16, 'conjuros': 15},
                'armas_permitidas': ['armas de monje'],
                'armaduras_permitidas': 'ninguna',
                'alineamiento': 'Debe ser Legal',
                'habilidades': {
                    'CA base': '10 - nivel',
                    'Ataques desarmados': '1d4 + bonif nivel',
                    'Esquivar proyectiles': 'Nivel 2+',
                    'Caída lenta': 'Nivel 4+',
                    'Ataque aturdidor': 'Nivel 1+',
                    'Inmune a enfermedades': 'Nivel 3+',
                    'Curación': '1 PG por día',
                    'Hablar con animales': 'Nivel 4+'
                },
                'descripcion': 'Maestro marcial asceta'
            }
        }
        
        # Intentar extraer más clases del texto si existen
        self._parse_class_data_from_text(text, base_classes)
        self.classes.update(base_classes)
        logger.info(f"✅ Clases cargadas: {len(base_classes)} clases")
    
    def _extract_races(self, text):
        """Extrae información de razas del texto"""
        base_races = {
            'Humano': {
                'ajustes_atributos': {},
                'clases_permitidas': ['Todas'],
                'multiclase': False,
                'habilidades_especiales': ['Sin restricción de nivel', 'Puede ser de cualquier clase'],
                'limite_nivel': 'Ilimitado',
                'descripcion': 'Raza versátil sin limitaciones'
            },
            # ELFOS
            'Elfo Alto': {
                'ajustes_atributos': {'DES': 1, 'CON': -1},
                'clases_permitidas': ['Guerrero', 'Mago', 'Ladrón', 'Clérigo', 'Ranger'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Mago', 'Guerrero/Ladrón', 'Mago/Ladrón', 'Guerrero/Mago/Ladrón'],
                'habilidades_especiales': [
                    'Resistencia 90% a Sueño y Encantamiento',
                    'Infravisión 60 pies',
                    'Detectar puertas secretas (1 en 6 pasando cerca, 2 en 6 buscando)',
                    'Sorpresa +1 (solo en cuero o menos)',
                    '+1 ataque con arco, espada corta y larga'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 11, 'Mago': 15, 'Ladrón': 12},
                'idiomas': ['Común', 'Élfico', 'Gnomo', 'Mediano', 'Goblin', 'Hobgoblin', 'Orco', 'Gnoll'],
                'descripcion': 'Elfos nobles y eruditos'
            },
            'Elfo Gris': {
                'ajustes_atributos': {'DES': 1, 'CON': -1},
                'clases_permitidas': ['Guerrero', 'Mago', 'Ladrón', 'Clérigo', 'Ranger'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Mago', 'Guerrero/Ladrón', 'Mago/Ladrón'],
                'habilidades_especiales': [
                    'Resistencia 90% a Sueño y Encantamiento',
                    'Infravisión 60 pies',
                    'Detectar puertas secretas',
                    '+1 a Inteligencia y Sabiduría'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 9, 'Mago': 20, 'Ladrón': 11},
                'descripcion': 'Elfos sabios y contemplativos'
            },
            'Elfo Silvano': {
                'ajustes_atributos': {'DES': 1, 'CON': -1},
                'clases_permitidas': ['Guerrero', 'Mago', 'Ladrón', 'Clérigo', 'Ranger', 'Druida'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Mago', 'Guerrero/Ladrón', 'Mago/Ladrón', 'Guerrero/Druida'],
                'habilidades_especiales': [
                    'Resistencia 90% a Sueño y Encantamiento',
                    'Infravisión 60 pies',
                    'Esconderse en bosque (4 en 6)',
                    'Detectar puertas secretas',
                    'Sigilo mejorado en naturaleza'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 10, 'Mago': 12, 'Ladrón': 13, 'Ranger': 12},
                'descripcion': 'Elfos del bosque, ágiles y furtivos'
            },
            'Drow (Elfo Oscuro)': {
                'ajustes_atributos': {'DES': 2, 'CON': -2, 'INT': 1, 'CAR': 1},
                'clases_permitidas': ['Guerrero', 'Mago', 'Ladrón', 'Clérigo'],
                'multiclase': True,
                'habilidades_especiales': [
                    'Resistencia 90% a Sueño y Encantamiento',
                    'Infravisión 120 pies',
                    'Habilidades mágicas innatas (Oscuridad, Luz Feérica, Detectar Magia)',
                    '+2 TS vs Magia',
                    'Sensible a la luz del sol (-2 ataque en luz brillante)'
                ],
                'infravisión': 120,
                'limite_nivel': {'Guerrero': 12, 'Mago': 16, 'Ladrón': 15, 'Clérigo': 12},
                'descripcion': 'Elfos oscuros de la Infraoscuridad (NPC usualmente)'
            },
            # ENANOS
            'Enano de las Montañas': {
                'ajustes_atributos': {'CON': 1, 'CAR': -1},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Ladrón', 'Guerrero/Clérigo'],
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    'Infravisión 60 pies',
                    'Detectar pendiente (1-5 en d6)',
                    'Detectar nuevas construcciones (1-5 en d6)',
                    'Detectar muros móviles (1-4 en d6)',
                    'Detectar trampas de piedra (1-3 en d6)',
                    '+1 ataque contra orcos, goblins, hobgoblins',
                    'Los gigantes sufren -4 ataque contra enanos'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 15, 'Ladrón': 12, 'Clérigo': 10},
                'idiomas': ['Común', 'Enano', 'Gnomo', 'Goblin', 'Kobold', 'Orco'],
                'descripcion': 'Enanos robustos de las montañas'
            },
            'Enano de las Colinas': {
                'ajustes_atributos': {'CON': 1, 'CAR': -1},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Ladrón', 'Guerrero/Clérigo'],
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    'Infravisión 60 pies',
                    'Detectar profundidad (1-3 en d6)',
                    'Detectar trampas de piedra (1-2 en d6)',
                    '+1 ataque contra orcos y goblins'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 13, 'Ladrón': 10, 'Clérigo': 8},
                'descripcion': 'Enanos artesanos de las colinas'
            },
            'Enano Gris (Duergar)': {
                'ajustes_atributos': {'CON': 1, 'CAR': -2},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo'],
                'multiclase': True,
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    'Infravisión 120 pies',
                    'Habilidades mágicas (Invisibilidad, Agrandar)',
                    'Inmune a parálisis, ilusión y veneno',
                    'Sensible a la luz del sol (-2 ataque)'
                ],
                'infravisión': 120,
                'limite_nivel': {'Guerrero': 10, 'Ladrón': 12, 'Clérigo': 9},
                'descripcion': 'Enanos oscuros de la Infraoscuridad (NPC usualmente)'
            },
            # HALFLINGS (MEDIANOS)
            'Mediano Piesligeros': {
                'ajustes_atributos': {'DES': 1, 'FUE': -1},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Ladrón'],
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    '+1 ataque con honda y proyectiles',
                    'Sigilo mejorado (+2)',
                    'Infravisión 30 pies',
                    'Difícil de golpear para criaturas grandes (+1 CA)'
                ],
                'infravisión': 30,
                'limite_nivel': {'Guerrero': 8, 'Ladrón': 12, 'Clérigo': 8},
                'idiomas': ['Común', 'Mediano', 'Enano', 'Elfo', 'Gnomo', 'Goblin', 'Orco'],
                'descripcion': 'Medianos aventureros y curiosos'
            },
            'Mediano Pelofirme': {
                'ajustes_atributos': {'DES': 1, 'FUE': -1},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo'],
                'multiclase': False,
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    '+1 ataque con honda',
                    'Infravisión 30 pies',
                    'Resistencia superior al veneno'
                ],
                'infravisión': 30,
                'limite_nivel': {'Guerrero': 10, 'Ladrón': 10, 'Clérigo': 7},
                'descripcion': 'Medianos robustos y hogareños'
            },
            'Mediano Fuerte': {
                'ajustes_atributos': {'DES': 1, 'FUE': -1, 'CON': 1},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo'],
                'multiclase': True,
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    '+1 ataque con honda y espada',
                    'Infravisión 60 pies',
                    'Más alto y fuerte que otros medianos'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 9, 'Ladrón': 11, 'Clérigo': 8},
                'descripcion': 'Medianos altos y aventureros'
            },
            # GNOMOS
            'Gnomo de las Rocas': {
                'ajustes_atributos': {'INT': 1, 'SAB': -1},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo', 'Mago', 'Ilusionista'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Ladrón', 'Guerrero/Ilusionista', 'Ladrón/Ilusionista'],
                'habilidades_especiales': [
                    'Resistencia +4 TS vs Veneno y Magia',
                    'Infravisión 60 pies',
                    'Detectar pendiente (1-5 en d6)',
                    'Detectar construcción reciente (1-5 en d6)',
                    '+1 ataque contra kobolds y goblins',
                    'Los gigantes sufren -4 ataque contra gnomos',
                    'Hablar con animales madrigueros'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 11, 'Ladrón': 13, 'Ilusionista': 16},
                'idiomas': ['Común', 'Gnomo', 'Enano', 'Mediano', 'Goblin', 'Kobold'],
                'descripcion': 'Gnomos ingeniosos e ilusionistas'
            },
            'Gnomo de las Profundidades (Svirfneblin)': {
                'ajustes_atributos': {'DES': 1, 'SAB': 1, 'FUE': -1, 'CAR': -2},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Ilusionista', 'Clérigo'],
                'multiclase': True,
                'habilidades_especiales': [
                    'Resistencia superior vs Magia',
                    'Infravisión 120 pies',
                    'Esconderse en piedra (4 en 6)',
                    'Inmune a ilusiones',
                    'Habilidades mágicas (Ceguera, Difuminar, Cambiar Forma)',
                    'Detectar muros móviles, trampas, profundidad'
                ],
                'infravisión': 120,
                'limite_nivel': {'Guerrero': 10, 'Ladrón': 12, 'Ilusionista': 14},
                'descripcion': 'Gnomos de la Infraoscuridad (raro como PC)'
            },
            # MEDIO-RAZAS
            'Semielfo': {
                'ajustes_atributos': {},
                'clases_permitidas': ['Todas excepto Monje'],
                'multiclase': True,
                'multiclase_opciones': ['Cualquier combinación de 2'],
                'habilidades_especiales': [
                    'Resistencia 30% a Sueño y Encantamiento',
                    'Infravisión 60 pies',
                    'Detectar puertas secretas (1 en 6)',
                    'Puede alcanzar niveles ilimitados en una clase'
                ],
                'infravisión': 60,
                'limite_nivel': 'Ilimitado en una clase, limitado en otras',
                'idiomas': ['Común', 'Élfico', 'y otros según INT'],
                'descripcion': 'Híbrido entre humano y elfo'
            },
            'Semiorco': {
                'ajustes_atributos': {'FUE': 1, 'CON': 1, 'CAR': -2},
                'clases_permitidas': ['Guerrero', 'Ladrón', 'Clérigo', 'Asesino'],
                'multiclase': True,
                'multiclase_opciones': ['Guerrero/Ladrón', 'Guerrero/Clérigo', 'Guerrero/Asesino', 'Clérigo/Ladrón', 'Clérigo/Asesino'],
                'habilidades_especiales': [
                    'Infravisión 60 pies',
                    '+1 PG adicional por dado de golpe'
                ],
                'infravisión': 60,
                'limite_nivel': {'Guerrero': 15, 'Ladrón': 12, 'Clérigo': 12, 'Asesino': 15},
                'idiomas': ['Común', 'Orco'],
                'descripcion': 'Híbrido entre humano y orco, fuertes pero rechazados'
            }
        }
        
        # Intentar extraer más razas del texto
        self._parse_race_data_from_text(text, base_races)
        self.races.update(base_races)
        logger.info(f"✅ Razas cargadas: {len(base_races)} razas y subrazas")
    
    def _extract_spells(self, text):
        """Extrae información de hechizos del texto o usa la base de datos"""
        # Usar base de datos de hechizos si está disponible
        if SPELLS_DB_AVAILABLE:
            logger.info("📖 Cargando hechizos desde base de datos...")
            self.spells['Mago'] = WIZARD_SPELLS.copy()
            self.spells['Clérigo'] = CLERIC_SPELLS.copy()
            logger.info(f"✅ Hechizos cargados desde DB: Mago ({TOTAL_WIZARD}), Clérigo ({TOTAL_CLERIC})")
            return
        
        # Fallback: lista reducida si no está disponible la DB
        logger.warning("⚠️ Usando lista reducida de hechizos (base de datos no disponible)")
        
        wizard_spells = {
            'Proyectil Mágico': {'nivel': 1, 'escuela': 'Evocación', 'alcance': '160 yardas', 'descripcion': '1-5 proyectiles, 1d4+1 cada uno'},
            'Escudo': {'nivel': 1, 'escuela': 'Abjuración', 'alcance': '0', 'descripcion': 'Protección invisible'},
            'Armadura': {'nivel': 1, 'escuela': 'Conjuración', 'alcance': 'Toque', 'descripcion': 'Otorga CA 6'},
            'Detectar Magia': {'nivel': 1, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Detecta magia'},
            'Dormir': {'nivel': 1, 'escuela': 'Encantamiento', 'alcance': '30 yardas', 'descripcion': 'Causa sueño (2d4 DG)'},
            'Invisibilidad': {'nivel': 2, 'escuela': 'Ilusión', 'alcance': 'Toque', 'descripcion': 'Invisible hasta atacar'},
            'Bola de Fuego': {'nivel': 3, 'escuela': 'Evocación', 'alcance': '100 yardas', 'descripcion': 'Explosión 1d6/nivel'},
        }
        
        cleric_spells = {
            'Curar Heridas Leves': {'nivel': 1, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura 1d8 PG'},
            'Bendecir': {'nivel': 1, 'esfera': 'Todas', 'alcance': '60 yardas', 'descripcion': '+1 ataque y TS'},
            'Curar Heridas Graves': {'nivel': 3, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura 2d8+nivel PG'},
        }
        
        self.spells['Mago'] = wizard_spells
        self.spells['Clérigo'] = cleric_spells
        logger.info(f"✅ Hechizos básicos cargados: Mago ({len(wizard_spells)}), Clérigo ({len(cleric_spells)})")
    
    def _parse_class_data_from_text(self, text, classes_dict):
        """Intenta extraer clases adicionales del texto PDF"""
        # Esta función puede intentar parsear el texto buscando patrones de clases
        # Por ahora usamos la lista manual completa
        pass
    
    def _parse_race_data_from_text(self, text, races_dict):
        """Intenta extraer razas adicionales del texto PDF"""
        # Esta función puede intentar parsear el texto buscando patrones de razas
        # Por ahora usamos la lista manual completa
        pass
    
    def _extract_attribute_rules(self, text):
        """Extrae reglas de atributos y modificadores"""
        self.rules['attribute_modifiers'] = {
            'FUE': {
                3: {'golpe': -3, 'dano': -1},
                4: {'golpe': -2, 'dano': -1},
                5: {'golpe': -2, 'dano': -1},
                6: {'golpe': -1, 'dano': 0},
                7: {'golpe': -1, 'dano': 0},
                8: {'golpe': 0, 'dano': 0},
                9: {'golpe': 0, 'dano': 0},
                10: {'golpe': 0, 'dano': 0},
                11: {'golpe': 0, 'dano': 0},
                12: {'golpe': 0, 'dano': 0},
                13: {'golpe': 0, 'dano': 0},
                14: {'golpe': 0, 'dano': 0},
                15: {'golpe': 0, 'dano': 0},
                16: {'golpe': 0, 'dano': 1},
                17: {'golpe': 1, 'dano': 1},
                18: {'golpe': 1, 'dano': 2},
            },
            'DES': {
                3: {'reaccion': -3, 'ca': 4, 'proyectil': -3},
                6: {'reaccion': -1, 'ca': 1, 'proyectil': -1},
                9: {'reaccion': 0, 'ca': 0, 'proyectil': 0},
                13: {'reaccion': 0, 'ca': 0, 'proyectil': 0},
                16: {'reaccion': 1, 'ca': -2, 'proyectil': 1},
                17: {'reaccion': 2, 'ca': -3, 'proyectil': 2},
                18: {'reaccion': 2, 'ca': -4, 'proyectil': 2},
            },
            'CON': {
                3: {'pg': -2},
                6: {'pg': -1},
                9: {'pg': 0},
                15: {'pg': 1},
                16: {'pg': 2},
                17: {'pg': 3},
                18: {'pg': 4},
            }
        }
    
    def _extract_combat_rules(self, text):
        """Extrae reglas de combate"""
        self.rules['combat'] = {
            'initiative': 'd10',
            'surprise': 'd10',
            'melee_range': 5,  # pies
            'movement_combat': 'reducido a 1/3'
        }
    
    def _extract_experience_tables(self, text):
        """Extrae tablas de experiencia"""
        self.rules['experience'] = {
            'Guerrero': [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000],
            'Mago': [0, 2500, 5000, 10000, 20000, 40000, 60000, 90000, 135000, 250000],
            'Clérigo': [0, 1500, 3000, 6000, 13000, 27000, 55000, 110000, 225000, 450000],
            'Ladrón': [0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000]
        }
    
    def _extract_dwarf_details(self, text):
        """Extrae detalles específicos de enanos del manual completo"""
        # Mejorar la información de enanos
        if 'Enano' in self.races:
            self.races['Enano']['subrazas'] = {
                'Enano de las Montañas': {
                    'ajustes_adicionales': {'FUE': 1},
                    'habilidades': ['Detectar pendiente', 'Detectar nuevas construcciones']
                },
                'Enano de las Colinas': {
                    'ajustes_adicionales': {},
                    'habilidades': ['Detectar trampas de piedra', 'Detectar profundidad']
                }
            }
            logger.info("✅ Detalles expandidos de Enanos agregados")
    
    def _extract_advanced_combat_rules(self, text):
        """Extrae reglas avanzadas de combate"""
        self.rules['advanced_combat'] = {
            'ataques_multiples': {
                'descripcion': 'Guerreros de alto nivel obtienen ataques adicionales',
                'niveles': {
                    7: '3/2 ataques (3 cada 2 rondas)',
                    13: '2 ataques por ronda'
                }
            },
            'criticos': {
                '20_natural': 'Crítico - Daño máximo o doblar daño (opcional)',
                '1_natural': 'Fallo crítico - Pierde siguiente ataque (opcional)'
            },
            'flanqueo': {
                'bonus': '+2 al ataque',
                'requisitos': 'Atacar por la espalda con aliado en frente'
            },
            'carga': {
                'bonus_ataque': '+2',
                'penalizador_ca': '-1 a CA del cargador',
                'distancia_minima': 10,
                'distancia_maxima': 'Movimiento completo'
            }
        }
        logger.info("✅ Reglas avanzadas de combate cargadas")
    
    def _extract_combat_maneuvers(self, text):
        """Extrae maniobras especiales de combate"""
        self.rules['combat_maneuvers'] = {
            'Desarmar': {
                'descripcion': 'Intento de quitar el arma al oponente',
                'penalizador': '-4 al ataque',
                'ts_oponente': 'Fuerza o Destreza',
                'consecuencia': 'Arma cae al suelo si falla TS'
            },
            'Derribo': {
                'descripcion': 'Derribar al oponente',
                'requisitos': 'Ataque exitoso',
                'ts_oponente': 'Salvación vs Parálisis',
                'consecuencia': 'Oponente cae al suelo (pierde 1 ataque)'
            },
            'Agarre': {
                'descripcion': 'Agarrar e inmovilizar',
                'comparacion': 'FUE vs FUE',
                'consecuencia': 'Oponente inmovilizado'
            },
            'Finta': {
                'descripcion': 'Engañar al oponente',
                'requisitos': 'Usar ranura de ataque',
                'bonus': '+4 al siguiente ataque si tiene éxito'
            }
        }
        logger.info("✅ Maniobras de combate cargadas")
    
    def _extract_initiative_rules(self, text):
        """Extrae reglas de iniciativa"""
        self.rules['initiative'] = {
            'sistema_base': '1d10 por grupo',
            'menor_es_mejor': True,
            'modificadores': {
                'arma_mas_rapida': -2,
                'arma_mas_lenta': +2,
                'carga': -2,
                'conjurar_hechizo': '+tiempo de lanzamiento'
            },
            'velocidad_armas': {
                'Daga': 2,
                'Espada corta': 3,
                'Espada larga': 5,
                'Espada bastarda': 6,
                'Hacha de batalla': 7,
                'Maza': 7,
                'Martillo de guerra': 4,
                'Lanza': 6,
                'Arco corto': 7,
                'Arco largo': 8
            }
        }
        logger.info("✅ Reglas de iniciativa cargadas")
    
    def _extract_equipment(self, text):
        """Extrae información de equipo y armas"""
        self.equipment = {
            'armas': {
                'Espada larga': {
                    'costo': '15 po',
                    'peso': 4,
                    'dano_pq': '1d8',
                    'dano_gr': '1d12',
                    'tipo': 'Cortante',
                    'velocidad': 5
                },
                'Arco largo': {
                    'costo': '75 po',
                    'peso': 3,
                    'dano_pq': '1d6',
                    'dano_gr': '1d6',
                    'tipo': 'Perforante',
                    'alcance': '70/140/210',
                    'velocidad': 8
                },
                'Daga': {
                    'costo': '2 po',
                    'peso': 1,
                    'dano_pq': '1d4',
                    'dano_gr': '1d3',
                    'tipo': 'Perforante',
                    'velocidad': 2
                }
            },
            'armaduras': {
                'Armadura de cuero': {
                    'ca': 8,
                    'costo': '5 po',
                    'peso': 15
                },
                'Cota de mallas': {
                    'ca': 5,
                    'costo': '75 po',
                    'peso': 40
                },
                'Armadura de placas': {
                    'ca': 3,
                    'costo': '400 po',
                    'peso': 50
                }
            }
        }
        logger.info(f"✅ Equipo cargado: {len(self.equipment.get('armas', {}))} armas")
    
    def _extract_proficiencies(self, text):
        """Extrae pericias de arma y no-arma"""
        self.rules['proficiencies'] = {
            'arma': {
                'Guerrero': {
                    'inicial': 4,
                    'por_nivel': 3
                },
                'Mago': {
                    'inicial': 1,
                    'por_nivel': 6
                },
                'Clérigo': {
                    'inicial': 2,
                    'por_nivel': 4
                },
                'Ladrón': {
                    'inicial': 2,
                    'por_nivel': 4
                }
            },
            'no_arma': {
                'inicial': 4,
                'por_nivel': 3,
                'ejemplos': [
                    'Agricultura', 'Herrería', 'Cervecería',
                    'Carpintería', 'Cocina', 'Equitación',
                    'Pesca', 'Herbolaria', 'Caza',
                    'Minería', 'Navegación', 'Nadar'
                ]
            }
        }
        logger.info("✅ Sistema de pericias cargado")
    
    def _extract_kits(self, text):
        """Extrae kits de personaje (arquetipos)"""
        self.kits = {
            'Guerrero': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Amazona': {
                    'requisitos': {'FUE': 13, 'DES': 14, 'CON': 13},
                    'restricciones_sexo': 'Solo mujeres',
                    'habilidades': ['Combate montado', 'Arco largo +1', 'Lanza +1'],
                    'restricciones': 'Debe vivir en comunidad de amazonas',
                    'equipo_inicial': ['Arco largo', 'Lanza', 'Armadura de cuero']
                },
                'Bárbaro': {
                    'requisitos': {'FUE': 15, 'DES': 14, 'CON': 15},
                    'habilidades': ['Rastrear', 'Supervivencia', 'Escalar +10%', 'Saltar +10%'],
                    'restricciones': 'No puede usar armadura de placas, desconfía de magia',
                    'equipo_inicial': ['Hacha de batalla', 'Pieles']
                },
                'Berserker': {
                    'requisitos': {'FUE': 15, 'CON': 15},
                    'habilidades': ['Furia de batalla (+2 ataque, -2 CA)', 'Inmune a miedo'],
                    'restricciones': 'Debe entrar en furia al ver sangre',
                    'equipo_inicial': ['Espada bastarda', 'Hacha']
                },
                'Caballero': {
                    'requisitos': {'FUE': 12, 'CAR': 12},
                    'habilidades': ['Montar a caballo', 'Lanza montado +1', 'Código de honor'],
                    'restricciones': 'Debe seguir código caballeresco, jurar lealtad a señor',
                    'equipo_inicial': ['Espada larga', 'Lanza', 'Armadura de placas', 'Caballo']
                },
                'Gladiador': {
                    'requisitos': {'FUE': 13, 'DES': 13, 'CON': 12},
                    'habilidades': ['Especialización en arma favorita', 'Combate espectacular'],
                    'restricciones': 'Debe pelear en arenas',
                    'equipo_inicial': ['Tridente', 'Red', 'Armadura ligera']
                },
                'Mercenario': {
                    'requisitos': {'FUE': 12},
                    'habilidades': ['Negociación', 'Armas exóticas'],
                    'restricciones': 'Solo lucha por dinero',
                    'equipo_inicial': ['Espada larga', 'Cota de mallas']
                }
            },
            'Ranger': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Guardabosques': {
                    'requisitos': {'SAB': 14},
                    'habilidades': ['Rastrear', 'Empatía animal', 'Supervivencia'],
                    'restricciones': 'Debe proteger la naturaleza',
                    'equipo_inicial': ['Arco largo', 'Espada larga', 'Armadura de cuero']
                },
                'Cazador de Recompensas': {
                    'requisitos': {'SAB': 12},
                    'habilidades': ['Rastrear humanos', 'Interrogar'],
                    'restricciones': 'Solo caza por recompensa',
                    'equipo_inicial': ['Red', 'Lazo', 'Espada corta']
                }
            },
            'Paladín': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Caballero Divino': {
                    'requisitos': {'SAB': 13, 'CAR': 17},
                    'habilidades': ['Detectar mal', 'Curar enfermedades', 'Inmune a miedo'],
                    'restricciones': 'Código de honor estricto, diezmo a la iglesia',
                    'equipo_inicial': ['Espada larga', 'Armadura de placas', 'Símbolo sagrado']
                }
            },
            'Mago': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Especialista en Abjuración': {
                    'requisitos': {'INT': 15, 'SAB': 15},
                    'habilidades': ['+1 hechizo de Abjuración por nivel', 'Bonus salvación vs magia'],
                    'restricciones': 'No puede lanzar hechizos de Alteración',
                    'equipo_inicial': ['Libro de conjuros', 'Componentes', 'Bastón']
                },
                'Especialista en Evocación': {
                    'requisitos': {'INT': 16, 'DES': 16},
                    'habilidades': ['+1 hechizo de Evocación por nivel', '+1 daño hechizos'],
                    'restricciones': 'No puede lanzar hechizos de Conjuración/Convocación',
                    'equipo_inicial': ['Libro de conjuros', 'Varita', 'Componentes']
                },
                'Nigromante': {
                    'requisitos': {'INT': 16, 'SAB': 16},
                    'habilidades': ['+1 hechizo de Nigromancia por nivel', 'Control de no-muertos'],
                    'restricciones': 'No puede lanzar hechizos de Ilusión',
                    'equipo_inicial': ['Libro de conjuros', 'Huesos', 'Velas negras']
                }
            },
            'Clérigo': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Sacerdote de la Guerra': {
                    'requisitos': {'FUE': 12, 'SAB': 12},
                    'habilidades': ['Armas adicionales permitidas', 'Combate +1'],
                    'restricciones': 'Debe promover conflictos justos',
                    'equipo_inicial': ['Martillo de guerra', 'Armadura de placas', 'Símbolo sagrado']
                },
                'Curandero': {
                    'requisitos': {'SAB': 16},
                    'habilidades': ['Curación doble', 'Herbalismo', 'Diagnosticar'],
                    'restricciones': 'Pacifista, no puede usar armas letales',
                    'equipo_inicial': ['Bastón', 'Hierbas medicinales', 'Vendas']
                }
            },
            'Druida': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Guardián del Bosque': {
                    'requisitos': {'SAB': 14, 'CAR': 12},
                    'habilidades': ['Hablar con animales', 'Forma animal adicional'],
                    'restricciones': 'Debe proteger su bosque sagrado',
                    'equipo_inicial': ['Hoz', 'Bastón de madera', 'Muérdago']
                }
            },
            'Ladrón': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Asesino': {
                    'requisitos': {'DES': 12, 'INT': 11},
                    'habilidades': ['Ataque furtivo x3', 'Venenos', 'Disfraz'],
                    'restricciones': 'Debe aceptar contratos de asesinato',
                    'equipo_inicial': ['Daga envenenada', 'Ganzúas', 'Capa']
                },
                'Acróbata': {
                    'requisitos': {'DES': 15, 'FUE': 12},
                    'habilidades': ['Saltar +30%', 'Caer +20%', 'Equilibrio'],
                    'restricciones': 'No puede usar armadura',
                    'equipo_inicial': ['Bastón', 'Cuerda', 'Ropa ligera']
                },
                'Ladrón de Tumbas': {
                    'requisitos': {'DES': 13, 'INT': 12},
                    'habilidades': ['Detectar trampas +15%', 'Conocimiento de ruinas'],
                    'restricciones': 'Obsesionado con tesoros antiguos',
                    'equipo_inicial': ['Ganzúas', 'Pico pequeño', 'Antorchas']
                }
            },
            'Bardo': {
                'Sin Kit': {
                    'requisitos': {},
                    'habilidades': [],
                    'restricciones': 'Ninguna'
                },
                'Juglar': {
                    'requisitos': {'DES': 12, 'CAR': 15},
                    'habilidades': ['Actuación mejorada', 'Influenciar +20%'],
                    'restricciones': 'Debe entretener en tabernas',
                    'equipo_inicial': ['Laúd', 'Daga', 'Ropa colorida']
                },
                'Heraldo': {
                    'requisitos': {'INT': 13, 'CAR': 14},
                    'habilidades': ['Conocimiento de genealogía', 'Etiqueta noble'],
                    'restricciones': 'Debe servir a la nobleza',
                    'equipo_inicial': ['Trompeta', 'Estandarte', 'Ropa noble']
                }
            }
        }
        
        # También guardar en rules para compatibilidad
        self.rules['kits'] = self.kits
        logger.info(f"✅ {sum(len(kits) for kits in self.kits.values())} kits de personaje cargados")
    
    def save_cache(self):
        """Guarda los datos extraídos en cache"""
        cache_data = {
            'rules': self.rules,
            'classes': self.classes,
            'races': self.races,
            'spells': self.spells,
            'equipment': self.equipment
        }
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        logger.info(f"💾 Datos guardados en cache: {self.cache_file}")
    
    def get_spell(self, class_name, spell_name):
        """Obtiene información de un hechizo específico"""
        if class_name in self.spells and spell_name in self.spells[class_name]:
            return self.spells[class_name][spell_name]
        return None
    
    def get_spells_by_level(self, class_name, level):
        """Obtiene todos los hechizos de un nivel específico"""
        if class_name not in self.spells:
            return []
        return {name: data for name, data in self.spells[class_name].items() if data['nivel'] == level}

# ============================================================================
# SISTEMA DE GENERACIÓN DE ATRIBUTOS
# ============================================================================

import random

class AttributeGenerator:
    """Genera atributos según las reglas de AD&D 2e"""
    
    @staticmethod
    def roll_3d6():
        """Método estándar: 3d6"""
        return sum(random.randint(1, 6) for _ in range(3))
    
    @staticmethod
    def roll_4d6_drop_lowest():
        """Método heroico: 4d6, descarta el más bajo"""
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort()
        return sum(rolls[1:])
    
    @staticmethod
    def method_1():
        """Método 1: Tirar 3d6 seis veces, asignar en orden"""
        return [AttributeGenerator.roll_3d6() for _ in range(6)]
    
    @staticmethod
    def method_2():
        """Método 2: Tirar 3d6 doce veces, escoger los mejores 6"""
        rolls = [AttributeGenerator.roll_3d6() for _ in range(12)]
        rolls.sort(reverse=True)
        return rolls[:6]
    
    @staticmethod
    def method_3():
        """Método 3: Tirar 3d6 seis veces, asignar donde se desee"""
        return [AttributeGenerator.roll_3d6() for _ in range(6)]
    
    @staticmethod
    def method_4():
        """Método 4 (Heroico): 4d6 descartando el más bajo, seis veces"""
        return [AttributeGenerator.roll_4d6_drop_lowest() for _ in range(6)]

# ============================================================================
# CLASE PERSONAJE ACTUALIZADA
# ============================================================================

class Character:
    """Personaje de AD&D 2e con reglas completas"""
    
    def __init__(self, name, data_loader):
        self.name = name
        self.data_loader = data_loader
        self.race = None
        self.character_class = None
        self.level = 1
        self.experience = 0
        
        # Atributos básicos
        self.attributes = {
            'FUE': 10,
            'DES': 10,
            'CON': 10,
            'INT': 10,
            'SAB': 10,
            'CAR': 10
        }
        
        # Combate
        self.hit_points_max = 0
        self.hit_points_current = 0
        self.armor_class = 10
        self.thac0 = 20
        
        # Salvaciones
        self.saving_throws = {
            'paralisis': 14,
            'varitas': 16,
            'petrificacion': 15,
            'aliento': 17,
            'conjuros': 17
        }
        
        # Habilidades, equipo, hechizos
        self.skills = {}
        self.proficiencies = {
            'armas': [],
            'no_armas': []
        }
        self.kit = None
        self.equipment = []
        self.equipped = {
            'arma_principal': None,  # {'nombre': str, 'ataque': int, 'daño': str}
            'arma_secundaria': None,
            'armadura': None,  # {'nombre': str, 'ca': int}
            'escudo': None  # {'nombre': str, 'ca_bonus': int}
        }
        self.money = {'po': 0, 'pp': 0, 'pe': 0, 'pc': 0}  # oro, plata, electrum, cobre
        self.spells = []
        self.known_spells = []  # Hechizos que conoce (magos)
        self.prepared_spells = []  # Hechizos preparados
        
    def generate_attributes(self, method=4):
        """Genera atributos usando el método especificado"""
        methods = {
            1: AttributeGenerator.method_1,
            2: AttributeGenerator.method_2,
            3: AttributeGenerator.method_3,
            4: AttributeGenerator.method_4
        }
        
        if method not in methods:
            logger.warning(f"Método {method} no reconocido. Usando método 4 (heroico).")
            method = 4
        
        values = methods[method]()
        attr_names = ['FUE', 'DES', 'CON', 'INT', 'SAB', 'CAR']
        
        logger.info(f"🎲 Generando atributos con Método {method}")
        logger.info(f"   Valores: {values}")
        
        # Si es método 3 o 4, permitir asignación libre
        if method in [3, 4]:
            for i, attr in enumerate(attr_names):
                self.attributes[attr] = values[i]
        else:
            for i, attr in enumerate(attr_names):
                self.attributes[attr] = values[i]
        
        return values
    
    def set_race(self, race_name):
        """Establece la raza y aplica modificadores"""
        if race_name not in self.data_loader.races:
            logger.error(f"❌ Raza '{race_name}' no encontrada")
            return False
        
        self.race = race_name
        race_data = self.data_loader.races[race_name]
        
        # Aplicar ajustes raciales
        for attr, modifier in race_data['ajustes_atributos'].items():
            self.attributes[attr] += modifier
            logger.info(f"   {attr}: {self.attributes[attr]-modifier} → {self.attributes[attr]} (modificador racial: {modifier:+d})")
        
        logger.info(f"✅ Raza establecida: {race_name}")
        return True
    
    def set_class(self, class_name):
        """Establece la clase y verifica requisitos"""
        if class_name not in self.data_loader.classes:
            logger.error(f"❌ Clase '{class_name}' no encontrada")
            return False
        
        class_data = self.data_loader.classes[class_name]
        
        # Verificar requisitos (si existen)
        requisitos = class_data.get('requisitos', {})
        for attr, min_val in requisitos.items():
            if self.attributes.get(attr, 0) < min_val:
                logger.error(f"❌ No cumple requisito: {attr} {self.attributes.get(attr, 0)} < {min_val}")
                return False
        
        # Verificar si la raza permite esta clase
        if self.race:
            race_data = self.data_loader.races.get(self.race, {})
            clases_permitidas = race_data.get('clases_permitidas', [])
            
            # Si la raza permite "Todas", aceptar cualquier clase
            if 'Todas' not in clases_permitidas and class_name not in clases_permitidas:
                logger.error(f"❌ La raza {self.race} no puede ser {class_name}")
                return False
        
        self.character_class = class_name
        self.thac0 = class_data.get('thac0_inicial', 20)
        self.saving_throws = class_data.get('ts_base', {}).copy()
        
        # Calcular PG iniciales
        self._calculate_hit_points()
        
        dado_golpe = class_data.get('dado_golpe', '?')
        logger.info(f"✅ Clase establecida: {class_name}")
        logger.info(f"   Dado de Golpe: d{dado_golpe}")
        logger.info(f"   THAC0: {self.thac0}")
        logger.info(f"   PG Máximos: {self.hit_points_max}")
        
        return True
    
    def _calculate_hit_points(self):
        """Calcula los puntos de golpe según clase y CON"""
        if not self.character_class:
            return
        
        class_data = self.data_loader.classes.get(self.character_class, {})
        hit_die = class_data.get('dado_golpe', 4)
        
        # Tirar dado de golpe (nivel 1 = máximo)
        base_hp = hit_die  # En nivel 1, generalmente se toma el máximo
        
        # Aplicar modificador de CON
        con_mod = self._get_constitution_modifier()
        self.hit_points_max = max(1, base_hp + con_mod)
        self.hit_points_current = self.hit_points_max
    
    def _get_constitution_modifier(self):
        """Obtiene el modificador de Constitución para PG"""
        con = self.attributes['CON']
        if con <= 3:
            return -2
        elif con <= 6:
            return -1
        elif con <= 14:
            return 0
        elif con == 15:
            return 1
        elif con == 16:
            return 2
        elif con == 17:
            return 3
        else:
            return 4
    
    def learn_spell(self, spell_name, spell_class=None):
        """Aprende un hechizo nuevo"""
        if not spell_class:
            spell_class = self.character_class
        
        spell_data = self.data_loader.get_spell(spell_class, spell_name)
        if not spell_data:
            logger.error(f"❌ Hechizo '{spell_name}' no encontrado para {spell_class}")
            return False
        
        if spell_name not in self.known_spells:
            self.known_spells.append(spell_name)
            logger.info(f"📖 Hechizo aprendido: {spell_name}")
            return True
        else:
            logger.warning(f"⚠️  Ya conoces el hechizo: {spell_name}")
            return False
    
    def prepare_spell(self, spell_name):
        """Prepara un hechizo conocido"""
        if spell_name not in self.known_spells:
            logger.error(f"❌ No conoces el hechizo: {spell_name}")
            return False
        
        if spell_name not in self.prepared_spells:
            self.prepared_spells.append(spell_name)
            logger.info(f"✨ Hechizo preparado: {spell_name}")
            return True
        else:
            logger.warning(f"⚠️  El hechizo ya está preparado: {spell_name}")
            return False
    
    def show_spell_details(self, spell_name):
        """Muestra los detalles de un hechizo"""
        spell_data = self.data_loader.get_spell(self.character_class, spell_name)
        if not spell_data:
            logger.error(f"❌ Hechizo no encontrado: {spell_name}")
            return
        
        print(f"\n{'='*60}")
        print(f"📜 HECHIZO: {spell_name}")
        print(f"{'='*60}")
        print(f"Nivel: {spell_data['nivel']}")
        print(f"Escuela: {spell_data.get('escuela', spell_data.get('esfera', 'N/A'))}")
        print(f"Componentes: {spell_data['componentes']}")
        print(f"Tiempo de Lanzamiento: {spell_data['tiempo_lanzamiento']}")
        print(f"Alcance: {spell_data['alcance']}")
        print(f"Duración: {spell_data['duracion']}")
        print(f"Área de Efecto: {spell_data['area_efecto']}")
        print(f"TS: {spell_data['ts']}")
        print(f"\nDescripción:")
        print(f"{spell_data['descripcion']}")
        print(f"{'='*60}\n")
    
    def assign_proficiencies(self):
        """Asigna pericias de armas y no-armas según la clase"""
        if not self.character_class:
            return
        
        class_data = self.data_loader.classes.get(self.character_class, {})
        
        # Pericias de armas según clase
        weapon_slots = {
            'Guerrero': 4, 'Paladín': 3, 'Ranger': 3,
            'Mago': 1, 'Especialista': 1,
            'Clérigo': 2, 'Druida': 2,
            'Ladrón': 2, 'Bardo': 2, 'Monje': 1
        }.get(self.character_class, 2)
        
        # Pericias de no-armas
        non_weapon_slots = {
            'Guerrero': 3, 'Paladín': 3, 'Ranger': 3,
            'Mago': 4, 'Especialista': 4,
            'Clérigo': 3, 'Druida': 3,
            'Ladrón': 3, 'Bardo': 4, 'Monje': 3
        }.get(self.character_class, 3)
        
        # Bonus de INT para pericias no-armas
        int_val = self.attributes.get('INT', 10)
        if int_val >= 16:
            non_weapon_slots += 2
        elif int_val >= 13:
            non_weapon_slots += 1
        
        logger.info(f"📋 Espacios de pericias:")
        logger.info(f"   Armas: {weapon_slots}")
        logger.info(f"   No-Armas: {non_weapon_slots}")
        
        return weapon_slots, non_weapon_slots
    
    def assign_starting_equipment(self):
        """Asigna equipo inicial según la clase"""
        if not self.character_class:
            return
        
        # Dinero inicial (tirada de dados según clase)
        money_dice = {
            'Guerrero': (5, 4, 10),  # 5d4 x10
            'Paladín': (5, 4, 10),
            'Ranger': (5, 4, 10),
            'Mago': (1, 4, 10),  # 1d4 x10
            'Especialista': (1, 4, 10),
            'Clérigo': (3, 6, 10),  # 3d6 x10
            'Druida': (3, 6, 10),
            'Ladrón': (2, 6, 10),  # 2d6 x10
            'Bardo': (2, 6, 10),
            'Monje': (5, 4, 1)  # 5d4 (sin multiplicador)
        }.get(self.character_class, (3, 6, 10))
        
        import random
        num_dice, die_size, multiplier = money_dice
        gold = sum(random.randint(1, die_size) for _ in range(num_dice)) * multiplier
        self.money['po'] = gold
        
        # Equipo básico según clase
        basic_equipment = {
            'Guerrero': ['Espada larga', 'Escudo', 'Armadura de cota de mallas', 'Mochila', 'Odre', 'Raciones (1 semana)'],
            'Paladín': ['Espada larga', 'Escudo', 'Armadura de cota de mallas', 'Símbolo sagrado', 'Mochila', 'Raciones (1 semana)'],
            'Ranger': ['Espada larga', 'Arco largo', '20 flechas', 'Armadura de cuero', 'Mochila', 'Cuerda (50 pies)', 'Raciones (1 semana)'],
            'Mago': ['Daga', 'Libro de hechizos', 'Componentes de hechizos', 'Mochila', 'Tinta y pluma', 'Raciones (1 semana)'],
            'Especialista': ['Daga', 'Libro de hechizos', 'Componentes de hechizos', 'Mochila', 'Tinta y pluma', 'Raciones (1 semana)'],
            'Clérigo': ['Maza', 'Escudo', 'Armadura de cota de mallas', 'Símbolo sagrado', 'Agua bendita', 'Mochila', 'Raciones (1 semana)'],
            'Druida': ['Hoz', 'Dardo (6)', 'Armadura de cuero', 'Muérdago sagrado', 'Mochila', 'Raciones (1 semana)'],
            'Ladrón': ['Espada corta', 'Daga', 'Armadura de cuero', 'Ganzúas', 'Cuerda (50 pies)', 'Mochila', 'Raciones (1 semana)'],
            'Bardo': ['Espada larga', 'Daga', 'Armadura de cuero', 'Instrumento musical', 'Mochila', 'Raciones (1 semana)'],
            'Monje': ['Bastón', 'Túnica', 'Cuerda (50 pies)', 'Mochila', 'Raciones (1 semana)']
        }.get(self.character_class, ['Daga', 'Mochila', 'Raciones (1 semana)'])
        
        self.equipment = basic_equipment.copy()
        
        logger.info(f"💰 Dinero inicial: {gold} po")
        logger.info(f"🎒 Equipo básico ({len(self.equipment)} objetos)")
        
        return gold, basic_equipment
    
    def assign_kit(self, kit_name=None):
        """Asigna un kit de personaje (opcional)"""
        available_kits = self.data_loader.kits.get(self.character_class, {})
        
        if not available_kits:
            logger.info("No hay kits disponibles para esta clase")
            return None
        
        if kit_name and kit_name in available_kits:
            self.kit = kit_name
            kit_data = available_kits[kit_name]
            logger.info(f"🎭 Kit asignado: {kit_name}")
            
            # Aplicar bonificaciones del kit
            if 'habilidades' in kit_data:
                for habilidad, bonus in kit_data['habilidades'].items():
                    self.skills[habilidad] = self.skills.get(habilidad, 0) + bonus
            
            return kit_data
        
        return None
    
    def to_dict(self):
        """Convierte el personaje a diccionario para guardar"""
        return {
            'name': self.name,
            'race': self.race,
            'class': self.character_class,
            'level': self.level,
            'experience': self.experience,
            'attributes': self.attributes,
            'hit_points_max': self.hit_points_max,
            'hit_points_current': self.hit_points_current,
            'armor_class': self.armor_class,
            'thac0': self.thac0,
            'saving_throws': self.saving_throws,
            'skills': self.skills,
            'proficiencies': self.proficiencies,
            'kit': self.kit,
            'equipment': self.equipment,
            'equipped': self.equipped,
            'money': self.money,
            'known_spells': self.known_spells,
            'prepared_spells': self.prepared_spells
        }
    
    def edit_attributes(self):
        """Permite editar atributos del personaje"""
        print("\n--- EDITAR ATRIBUTOS ---")
        for attr in ['FUE', 'DES', 'CON', 'INT', 'SAB', 'CAR']:
            current = self.attributes[attr]
            try:
                new_val = input(f"{attr} (actual: {current}, Enter para mantener): ").strip()
                if new_val:
                    self.attributes[attr] = int(new_val)
                    print(f"✓ {attr} cambiado a {self.attributes[attr]}")
            except ValueError:
                print("❌ Valor inválido, manteniendo actual")
        
        # Recalcular dependencias
        if self.character_class:
            self._calculate_hit_points()
            self._recalculate_ac()
    
    def edit_hp(self):
        """Editar puntos de golpe"""
        print(f"\nPG actuales: {self.hit_points_current}/{self.hit_points_max}")
        try:
            new_current = input(f"Nuevos PG actuales (Enter={self.hit_points_current}): ").strip()
            if new_current:
                self.hit_points_current = max(0, int(new_current))
            
            new_max = input(f"Nuevos PG máximos (Enter={self.hit_points_max}): ").strip()
            if new_max:
                self.hit_points_max = max(1, int(new_max))
            
            print(f"✓ PG actualizados: {self.hit_points_current}/{self.hit_points_max}")
        except ValueError:
            print("❌ Valor inválido")
    
    def show_character_sheet(self):
        """Muestra la ficha del personaje"""
        print(f"\n{'='*60}")
        print(f"🎭 FICHA DE PERSONAJE: {self.name}")
        print(f"{'='*60}")
        print(f"Raza: {self.race or 'No establecida'}")
        print(f"Clase: {self.character_class or 'No establecida'}")
        if self.kit:
            print(f"Kit: {self.kit}")
        print(f"Nivel: {self.level} (XP: {self.experience})")
        print(f"Experiencia: {self.experience}")
        
        print(f"\n--- ATRIBUTOS ---")
        for attr, value in self.attributes.items():
            print(f"{attr}: {value}")
        
        print(f"\n--- COMBATE ---")
        print(f"PG: {self.hit_points_current}/{self.hit_points_max}")
        print(f"CA: {self.armor_class}")
        print(f"THAC0: {self.thac0}")
        
        print(f"\n--- TIRADAS DE SALVACIÓN ---")
        for ts, value in self.saving_throws.items():
            print(f"{ts.capitalize()}: {value}")
        
        # Pericias
        if self.proficiencies['armas'] or self.proficiencies['no_armas']:
            print(f"\n--- PERICIAS ---")
            if self.proficiencies['armas']:
                print(f"Armas: {', '.join(self.proficiencies['armas'])}")
            if self.proficiencies['no_armas']:
                print(f"No-Armas: {', '.join(self.proficiencies['no_armas'])}")
        
        # Equipo
        if self.equipment:
            print(f"\n--- EQUIPO ({len(self.equipment)} objetos) ---")
            for item in self.equipment:
                print(f"  • {item}")
        
        # Dinero
        if any(self.money.values()):
            print(f"\n--- DINERO ---")
            coins = []
            if self.money.get('po', 0) > 0:
                coins.append(f"{self.money['po']} po")
            if self.money.get('pp', 0) > 0:
                coins.append(f"{self.money['pp']} pp")
            if self.money.get('pe', 0) > 0:
                coins.append(f"{self.money['pe']} pe")
            if self.money.get('pc', 0) > 0:
                coins.append(f"{self.money['pc']} pc")
            if coins:
                print(", ".join(coins))
        
        # Hechizos
        if self.known_spells:
            print(f"\n--- HECHIZOS CONOCIDOS ({len(self.known_spells)}) ---")
            for spell in self.known_spells:
                print(f"  • {spell}")
        
        if self.prepared_spells:
            print(f"\n--- HECHIZOS PREPARADOS ({len(self.prepared_spells)}) ---")
            for spell in self.prepared_spells:
                print(f"  • {spell}")
        
        # Equipamiento
        if any(self.equipped.values()):
            print(f"\n--- EQUIPADO ---")
            if self.equipped['arma_principal']:
                wp = self.equipped['arma_principal']
                print(f"Arma Principal: {wp['nombre']} (Ataque: {wp['ataque']:+d}, Daño: {wp['daño']})")
            if self.equipped['arma_secundaria']:
                ws = self.equipped['arma_secundaria']
                print(f"Arma Secundaria: {ws['nombre']} (Ataque: {ws['ataque']:+d}, Daño: {ws['daño']})")
            if self.equipped['armadura']:
                arm = self.equipped['armadura']
                print(f"Armadura: {arm['nombre']} (CA: {arm['ca']})")
            if self.equipped['escudo']:
                esc = self.equipped['escudo']
                print(f"Escudo: {esc['nombre']} (Bonus CA: {esc['ca_bonus']:+d})")
        
        print(f"{'='*60}\n")
    
    def equip_weapon(self, weapon_name, slot='principal'):
        """Equipa un arma y calcula bonificaciones de ataque/daño"""
        if weapon_name not in self.equipment:
            logger.warning(f"'{weapon_name}' no está en el inventario")
            return False
        
        # Bonificador de FUE para ataque y daño
        str_bonus = self._get_strength_bonus()
        
        # Base de datos de armas (daño típico)
        weapon_data = {
            'Daga': {'daño': '1d4', 'ataque_base': 0},
            'Espada corta': {'daño': '1d6', 'ataque_base': 0},
            'Espada larga': {'daño': '1d8', 'ataque_base': 0},
            'Espada bastarda': {'daño': '2d4', 'ataque_base': 0},
            'Espada de dos manos': {'daño': '1d10', 'ataque_base': 0},
            'Hacha de batalla': {'daño': '1d8', 'ataque_base': 0},
            'Hacha de dos manos': {'daño': '1d10', 'ataque_base': 0},
            'Maza': {'daño': '1d6+1', 'ataque_base': 0},
            'Martillo de guerra': {'daño': '1d4+1', 'ataque_base': 0},
            'Mangual': {'daño': '1d6+1', 'ataque_base': 0},
            'Lanza': {'daño': '1d6', 'ataque_base': 0},
            'Alabarda': {'daño': '1d10', 'ataque_base': 0},
            'Arco corto': {'daño': '1d6', 'ataque_base': 0},
            'Arco largo': {'daño': '1d6', 'ataque_base': 0},
            'Ballesta': {'daño': '1d4', 'ataque_base': 0},
            'Bastón': {'daño': '1d6', 'ataque_base': 0},
            'Hoz': {'daño': '1d4+1', 'ataque_base': 0},
            'Dardo': {'daño': '1d3', 'ataque_base': 0},
        }
        
        # Buscar arma por nombre parcial
        weapon_info = None
        for key in weapon_data:
            if key.lower() in weapon_name.lower():
                weapon_info = weapon_data[key]
                break
        
        if not weapon_info:
            # Arma desconocida, valores por defecto
            weapon_info = {'daño': '1d6', 'ataque_base': 0}
        
        # Bonus de pericia (+1 si tiene pericia en el arma)
        proficiency_bonus = 0
        for prof in self.proficiencies['armas']:
            if prof.lower() in weapon_name.lower() or weapon_name.lower() in prof.lower():
                proficiency_bonus = 1
                break
        
        weapon_slot = 'arma_principal' if slot == 'principal' else 'arma_secundaria'
        self.equipped[weapon_slot] = {
            'nombre': weapon_name,
            'ataque': weapon_info['ataque_base'] + str_bonus + proficiency_bonus,
            'daño': weapon_info['daño'] + (f"{str_bonus:+d}" if str_bonus != 0 else '')
        }
        
        logger.info(f"✓ {weapon_name} equipado en {slot}")
        return True
    
    def equip_armor(self, armor_name):
        """Equipa armadura y calcula CA"""
        if armor_name not in self.equipment:
            logger.warning(f"'{armor_name}' no está en el inventario")
            return False
        
        # Base de datos de armaduras
        armor_data = {
            'Sin armadura': {'ca': 10},
            'Cuero': {'ca': 8},
            'Cuero tachonado': {'ca': 7},
            'Armadura de cuero': {'ca': 8},
            'Cota de mallas': {'ca': 5},
            'Cota de anillas': {'ca': 7},
            'Cota de escamas': {'ca': 6},
            'Brigantina': {'ca': 6},
            'Armadura de bandas': {'ca': 4},
            'Armadura de placas': {'ca': 3},
            'Armadura completa': {'ca': 1},
        }
        
        # Buscar armadura por nombre parcial
        armor_info = None
        for key in armor_data:
            if key.lower() in armor_name.lower():
                armor_info = armor_data[key]
                break
        
        if not armor_info:
            armor_info = {'ca': 7}  # CA por defecto
        
        self.equipped['armadura'] = {
            'nombre': armor_name,
            'ca': armor_info['ca']
        }
        
        self._recalculate_ac()
        logger.info(f"✓ {armor_name} equipado")
        return True
    
    def equip_shield(self, shield_name):
        """Equipa escudo y mejora CA"""
        if shield_name not in self.equipment:
            logger.warning(f"'{shield_name}' no está en el inventario")
            return False
        
        self.equipped['escudo'] = {
            'nombre': shield_name,
            'ca_bonus': -1  # Los escudos mejoran CA en -1
        }
        
        self._recalculate_ac()
        logger.info(f"✓ {shield_name} equipado")
        return True
    
    def _recalculate_ac(self):
        """Recalcula CA basado en armadura, escudo y DES"""
        base_ac = 10
        
        # CA de armadura
        if self.equipped['armadura']:
            base_ac = self.equipped['armadura']['ca']
        
        # Bonus de escudo
        if self.equipped['escudo']:
            base_ac += self.equipped['escudo']['ca_bonus']
        
        # Bonus de DES (solo si no lleva armadura pesada)
        dex_bonus = (self.attributes['DES'] - 10) // 2
        if self.equipped['armadura']:
            # Armaduras pesadas limitan bonus de DES
            if self.equipped['armadura']['ca'] <= 4:
                dex_bonus = min(dex_bonus, 0)  # Sin bonus en armadura pesada
        
        base_ac -= dex_bonus  # En AD&D, CA menor es mejor
        self.armor_class = max(base_ac, -10)  # Mínimo CA -10
    
    def _get_strength_bonus(self):
        """Obtiene bonus de FUE para ataque y daño"""
        fue = self.attributes['FUE']
        if fue >= 18:
            return 3
        elif fue >= 16:
            return 2
        elif fue >= 14:
            return 1
        elif fue <= 5:
            return -2
        elif fue <= 7:
            return -1
        return 0
    
    def level_up(self):
        """Sube de nivel al personaje"""
        if not self.character_class:
            logger.error("❌ No se puede subir de nivel sin clase")
            return False
        
        self.level += 1
        class_data = self.data_loader.classes.get(self.character_class, {})
        
        # Calcular nuevos HP
        hit_die = class_data.get('dado_golpe', 4)
        import random
        hp_roll = random.randint(1, hit_die)
        con_mod = self._get_constitution_modifier()
        hp_gain = max(1, hp_roll + con_mod)
        
        self.hit_points_max += hp_gain
        self.hit_points_current += hp_gain
        
        # Mejorar THAC0 (baja 1 cada ciertos niveles según clase)
        thac0_progression = {
            'Guerrero': 1,  # Mejora cada nivel
            'Paladín': 1,
            'Ranger': 1,
            'Clérigo': 2,  # Mejora cada 2 niveles
            'Druida': 2,
            'Ladrón': 2,
            'Bardo': 2,
            'Mago': 3,  # Mejora cada 3 niveles
            'Especialista': 3
        }
        
        progression_rate = thac0_progression.get(self.character_class, 2)
        if self.level % progression_rate == 0:
            self.thac0 -= 1
        
        # Mejorar tiradas de salvación (cada 3-4 niveles)
        if self.level % 4 == 0:
            for save in self.saving_throws:
                self.saving_throws[save] = max(1, self.saving_throws[save] - 1)
        
        logger.info(f"✨ ¡Nivel {self.level} alcanzado!")
        logger.info(f"   +{hp_gain} PG (Total: {self.hit_points_max})")
        logger.info(f"   THAC0: {self.thac0}")
        
        return True
    
    def add_experience(self, xp):
        """Añade puntos de experiencia"""
        self.experience += xp
        logger.info(f"💎 +{xp} XP (Total: {self.experience})")
        
        # Tabla de experiencia simplificada (varía por clase)
        xp_table = {
            1: 0,
            2: 2000,
            3: 4000,
            4: 8000,
            5: 16000,
            6: 32000,
            7: 64000,
            8: 125000,
            9: 250000,
            10: 500000
        }
        
        # Verificar si sube de nivel
        next_level = self.level + 1
        if next_level in xp_table and self.experience >= xp_table[next_level]:
            print(f"\n🎉 ¡Has alcanzado suficiente experiencia para nivel {next_level}!")
            return True
        return False

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_character_interactive(data_loader):
    """Crea un personaje de forma interactiva"""
    print("\n" + "="*60)
    print("🎲 CREADOR DE PERSONAJES AD&D 2e")
    print("="*60)
    
    # Nombre
    name = input("\nNombre del personaje: ").strip()
    character = Character(name, data_loader)
    
    # Generar atributos
    print("\n--- GENERACIÓN DE ATRIBUTOS ---")
    print("Métodos disponibles:")
    print("  [1] Método 1: 3d6 en orden (clásico)")
    print("  [2] Método 2: 3d6 doce veces, elegir mejores 6")
    print("  [3] Método 3: 3d6 seis veces, asignar libremente")
    print("  [4] Método 4: 4d6 descartando menor (heroico) - RECOMENDADO")
    
    while True:
        try:
            method = int(input("\nElige método (1-4): ").strip())
            if 1 <= method <= 4:
                break
        except ValueError:
            pass
        print("❌ Opción inválida. Elige 1, 2, 3 o 4.")
    
    # Bucle para repetir tiradas hasta que el jugador esté conforme
    satisfied = False
    while not satisfied:
        values = character.generate_attributes(method)
        print("\n📊 Atributos generados:")
        for attr, val in character.attributes.items():
            print(f"   {attr}: {val}")
        
        total = sum(character.attributes.values())
        print(f"\nTotal: {total}")
        
        try:
            confirm = input("\n¿Estás conforme con estas tiradas? (s/n, Enter=sí): ").strip().lower()
            if confirm in ['s', 'si', 'sí', '']:
                satisfied = True
            else:
                print("\n🎲 Tirando de nuevo...")
        except (KeyboardInterrupt, EOFError):
            print("\n⚠ Usando estas tiradas")
            satisfied = True
    
    # Elegir raza
    print("\n--- SELECCIÓN DE RAZA ---")
    races = list(data_loader.races.keys())
    for i, race in enumerate(races, 1):
        print(f"  [{i}] {race}")
    
    while True:
        try:
            race_choice = int(input("\nElige raza (número): ").strip())
            if 1 <= race_choice <= len(races):
                race_name = races[race_choice - 1]
                if character.set_race(race_name):
                    break
        except ValueError:
            pass
        print("❌ Opción inválida.")
    
    # Elegir clase
    print("\n--- SELECCIÓN DE CLASE ---")
    race_data = data_loader.races[character.race]
    available_classes = race_data['clases_permitidas']
    
    # Si la raza permite "Todas" las clases, usar la lista completa
    if 'Todas' in available_classes:
        available_classes = list(data_loader.classes.keys())
    
    print("Clases disponibles para tu raza:")
    for i, cls in enumerate(available_classes, 1):
        class_data = data_loader.classes.get(cls, {})
        requisitos = class_data.get('requisitos', {})
        if requisitos:
            req_text = ", ".join([f"{attr} {val}+" for attr, val in requisitos.items()])
            print(f"  [{i}] {cls} (Req: {req_text})")
        else:
            print(f"  [{i}] {cls}")
    
    while True:
        try:
            class_choice = int(input("\nElige clase (número): ").strip())
            if 1 <= class_choice <= len(available_classes):
                class_name = available_classes[class_choice - 1]
                if character.set_class(class_name):
                    break
        except ValueError:
            pass
        print("❌ Opción inválida o no cumples los requisitos.")
    
    # Seleccionar Kit
    print("\n--- SELECCIÓN DE KIT ---")
    available_kits = data_loader.kits.get(character.character_class, {})
    
    if available_kits:
        print(f"Kits disponibles para {character.character_class}:")
        kit_list = list(available_kits.keys())
        
        for i, kit_name in enumerate(kit_list, 1):
            kit_data = available_kits[kit_name]
            req = kit_data.get('requisitos', {})
            
            # Verificar si cumple requisitos
            cumple = all(character.attributes.get(attr, 0) >= val for attr, val in req.items())
            marca = "✓" if cumple else "✗"
            
            req_text = ", ".join([f"{attr} {val}+" for attr, val in req.items()]) if req else "Ninguno"
            
            print(f"  [{i}] {marca} {kit_name}")
            if req:
                print(f"      Req: {req_text}")
            if kit_data.get('habilidades'):
                print(f"      Habilidades: {', '.join(kit_data['habilidades'][:2])}")
        
        while True:
            try:
                kit_choice = input("\nElige kit (número, 0 para ninguno): ").strip()
                if kit_choice == '0':
                    print("Sin kit seleccionado")
                    break
                
                idx = int(kit_choice) - 1
                if 0 <= idx < len(kit_list):
                    selected_kit = kit_list[idx]
                    kit_data = available_kits[selected_kit]
                    
                    # Verificar requisitos
                    requisitos = kit_data.get('requisitos', {})
                    cumple_requisitos = all(
                        character.attributes.get(attr, 0) >= val 
                        for attr, val in requisitos.items()
                    )
                    
                    if not cumple_requisitos:
                        print("❌ No cumples los requisitos para este kit")
                        continue
                    
                    # Verificar restricción de sexo si existe
                    if kit_data.get('restricciones_sexo'):
                        print(f"\n⚠️  {kit_data['restricciones_sexo']}")
                        confirm = input("¿Confirmas la selección? (s/n): ").strip().lower()
                        if confirm not in ['s', 'si', 'sí']:
                            continue
                    
                    # Asignar kit
                    character.assign_kit(selected_kit)
                    
                    # Mostrar información del kit
                    print(f"\n✓ Kit '{selected_kit}' seleccionado")
                    if kit_data.get('habilidades'):
                        print(f"  Habilidades: {', '.join(kit_data['habilidades'])}")
                    if kit_data.get('restricciones'):
                        print(f"  Restricciones: {kit_data['restricciones']}")
                    
                    # Agregar equipo inicial del kit si existe
                    if kit_data.get('equipo_inicial'):
                        print(f"  Equipo adicional del kit:")
                        for item in kit_data['equipo_inicial']:
                            if item not in character.equipment:
                                character.equipment.append(item)
                                print(f"    + {item}")
                    
                    break
            except (ValueError, IndexError):
                print("❌ Opción inválida")
    else:
        print("No hay kits disponibles para esta clase")
    
    # Hechizos iniciales para lanzadores
    if character.character_class in ['Mago', 'Clérigo']:
        print(f"\n--- HECHIZOS INICIALES DE {character.character_class.upper()} ---")
        available_spells = data_loader.get_spells_by_level(character.character_class, 1)
        
        if available_spells:
            print("Hechizos de nivel 1 disponibles:")
            spell_list = list(available_spells.keys())
            for i, spell in enumerate(spell_list, 1):
                print(f"  [{i}] {spell}")
            
            # Magos pueden aprender varios, clérigos los preparan todos
            if character.character_class == 'Mago':
                num_spells = min(2, len(spell_list))  # 2 hechizos iniciales
                print(f"\nPuedes aprender {num_spells} hechizos iniciales.")
                for _ in range(num_spells):
                    while True:
                        try:
                            choice = int(input(f"Elige hechizo #{_+1} (número): ").strip())
                            if 1 <= choice <= len(spell_list):
                                spell_name = spell_list[choice - 1]
                                character.learn_spell(spell_name)
                                break
                        except ValueError:
                            pass
                        print("❌ Opción inválida.")
            else:
                # Clérigos conocen todos sus hechizos de nivel
                for spell_name in spell_list:
                    character.learn_spell(spell_name)
    
    # Asignar pericias
    print("\n--- PERICIAS ---")
    proficiency_result = character.assign_proficiencies()
    if proficiency_result:
        weapon_slots, non_weapon_slots = proficiency_result
        print(f"Tienes {weapon_slots} espacios de pericias de armas")
        print(f"Tienes {non_weapon_slots} espacios de pericias de no-armas")
        
        # Pericias de armas sugeridas según clase
        weapon_suggestions = {
            'Guerrero': ['Espada larga', 'Arco largo', 'Lanza', 'Hacha de batalla'],
            'Paladín': ['Espada larga', 'Lanza', 'Arco largo'],
            'Ranger': ['Espada larga', 'Arco largo', 'Lanza'],
            'Mago': ['Daga', 'Bastón'],
            'Especialista': ['Daga', 'Bastón'],
            'Clérigo': ['Maza', 'Martillo de guerra', 'Mangual'],
            'Druida': ['Hoz', 'Dardo', 'Bastón'],
            'Ladrón': ['Espada corta', 'Daga', 'Ballesta'],
            'Bardo': ['Espada larga', 'Daga', 'Arco corto'],
            'Monje': ['Bastón', 'Combate sin armas']
        }.get(character.character_class, ['Daga', 'Espada corta'])
        
        print(f"\nPericias de armas sugeridas: {', '.join(weapon_suggestions[:weapon_slots])}")
        try:
            auto_weapons = input("¿Asignar automáticamente? (s/n/m para manual, Enter=sí): ").strip().lower()
            if auto_weapons in ['s', 'si', 'sí', '']:
                character.proficiencies['armas'] = weapon_suggestions[:weapon_slots]
                print(f"✓ Asignadas: {', '.join(character.proficiencies['armas'])}")
            elif auto_weapons == 'm':
                print("\nEscribe las pericias de armas (separadas por coma):")
                manual_weapons = input(f"Ingresa {weapon_slots} pericias: ").strip()
                character.proficiencies['armas'] = [w.strip() for w in manual_weapons.split(',')][:weapon_slots]
                print(f"✓ Asignadas: {', '.join(character.proficiencies['armas'])}")
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operación cancelada")
            return None
        
        # Pericias de no-armas sugeridas
        non_weapon_suggestions = {
            'Guerrero': ['Equitación', 'Armas', 'Supervivencia'],
            'Paladín': ['Equitación', 'Religión', 'Curación'],
            'Ranger': ['Rastrear', 'Supervivencia', 'Conocimiento animal'],
            'Mago': ['Lectura/Escritura', 'Conocimiento arcano', 'Idiomas antiguos'],
            'Especialista': ['Lectura/Escritura', 'Conocimiento arcano', 'Alquimia'],
            'Clérigo': ['Religión', 'Curación', 'Lectura/Escritura'],
            'Druida': ['Herbalismo', 'Conocimiento animal', 'Supervivencia'],
            'Ladrón': ['Escalar', 'Esconderse', 'Moverse sigilosamente'],
            'Bardo': ['Música', 'Idiomas modernos', 'Historia local'],
            'Monje': ['Acrobacias', 'Saltar', 'Concentración']
        }.get(character.character_class, ['Etiqueta', 'Idiomas modernos'])
        
        print(f"\nPericias de no-armas sugeridas: {', '.join(non_weapon_suggestions[:non_weapon_slots])}")
        try:
            auto_non_weapons = input("¿Asignar automáticamente? (s/n/m para manual, Enter=sí): ").strip().lower()
            if auto_non_weapons in ['s', 'si', 'sí', '']:
                character.proficiencies['no_armas'] = non_weapon_suggestions[:non_weapon_slots]
                print(f"✓ Asignadas: {', '.join(character.proficiencies['no_armas'])}")
            elif auto_non_weapons == 'm':
                print("\nEscribe las pericias de no-armas (separadas por coma):")
                manual_non_weapons = input(f"Ingresa {non_weapon_slots} pericias: ").strip()
                character.proficiencies['no_armas'] = [w.strip() for w in manual_non_weapons.split(',')][:non_weapon_slots]
                print(f"✓ Asignadas: {', '.join(character.proficiencies['no_armas'])}")
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operación cancelada")
            return None
    
    # Asignar equipo inicial
    print("\n--- EQUIPO INICIAL ---")
    try:
        gold, equipment = character.assign_starting_equipment()
        print(f"Recibes {gold} piezas de oro")
        print(f"Equipo básico: {', '.join(equipment)}")
        
        # Opción para modificar equipo
        modify = input("\n¿Deseas modificar el equipo? (s/n, Enter=no): ").strip().lower()
        if modify in ['s', 'si', 'sí']:
            print("\nEquipo actual:")
            for i, item in enumerate(character.equipment, 1):
                print(f"  [{i}] {item}")
            print("\nOpciones:")
            print("  [a] Agregar objeto")
            print("  [e] Eliminar objeto")
            print("  [Enter] Terminar")
            
            while True:
                action = input("\n¿Qué deseas hacer? (a/e/Enter): ").strip().lower()
                if action == 'a':
                    new_item = input("Nombre del objeto a agregar: ").strip()
                    if new_item:
                        character.equipment.append(new_item)
                        print(f"✓ '{new_item}' agregado")
                elif action == 'e':
                    print("\nEquipo actual:")
                    for i, item in enumerate(character.equipment, 1):
                        print(f"  [{i}] {item}")
                    try:
                        idx = int(input("Número del objeto a eliminar: ").strip()) - 1
                        if 0 <= idx < len(character.equipment):
                            removed = character.equipment.pop(idx)
                            print(f"✓ '{removed}' eliminado")
                    except (ValueError, IndexError):
                        print("❌ Número inválido")
                else:
                    break
    except Exception as e:
        logger.error(f"Error asignando equipo: {e}")
        print("❌ Error asignando equipo inicial")
    
    # Equipar objetos
    if character.equipment:
        print("\n--- EQUIPAR OBJETOS ---")
        equip = input("¿Deseas equipar armas y armadura ahora? (s/n, Enter=sí): ").strip().lower()
        if equip in ['s', 'si', 'sí', '']:
            # Equipar armadura
            armors = [item for item in character.equipment if any(word in item.lower() 
                     for word in ['armadura', 'cuero', 'cota', 'placas', 'mallas', 'anillas'])]
            if armors:
                print("\nArmaduras disponibles:")
                for i, armor in enumerate(armors, 1):
                    print(f"  [{i}] {armor}")
                try:
                    choice = input("Elige armadura (número, Enter=ninguna): ").strip()
                    if choice:
                        idx = int(choice) - 1
                        if 0 <= idx < len(armors):
                            character.equip_armor(armors[idx])
                            print(f"✓ {armors[idx]} equipado. CA: {character.armor_class}")
                except (ValueError, IndexError):
                    pass
            
            # Equipar escudo
            shields = [item for item in character.equipment if 'escudo' in item.lower()]
            if shields:
                print("\nEscudos disponibles:")
                for i, shield in enumerate(shields, 1):
                    print(f"  [{i}] {shield}")
                try:
                    choice = input("Elige escudo (número, Enter=ninguno): ").strip()
                    if choice:
                        idx = int(choice) - 1
                        if 0 <= idx < len(shields):
                            character.equip_shield(shields[idx])
                            print(f"✓ {shields[idx]} equipado. CA: {character.armor_class}")
                except (ValueError, IndexError):
                    pass
            
            # Equipar arma principal
            weapons = [item for item in character.equipment if any(word in item.lower() 
                      for word in ['espada', 'hacha', 'maza', 'martillo', 'lanza', 'daga', 
                                   'arco', 'ballesta', 'bastón', 'mangual', 'hoz', 'alabarda'])]
            if weapons:
                print("\nArmas disponibles:")
                for i, weapon in enumerate(weapons, 1):
                    print(f"  [{i}] {weapon}")
                try:
                    choice = input("Elige arma principal (número, Enter=ninguna): ").strip()
                    if choice:
                        idx = int(choice) - 1
                        if 0 <= idx < len(weapons):
                            character.equip_weapon(weapons[idx], 'principal')
                            wp = character.equipped['arma_principal']
                            print(f"✓ {wp['nombre']} equipado. Ataque: {wp['ataque']:+d}, Daño: {wp['daño']}")
                except (ValueError, IndexError):
                    pass
                
                # Arma secundaria (opcional)
                if len(weapons) > 1:
                    try:
                        choice = input("Elige arma secundaria (número, Enter=ninguna): ").strip()
                        if choice:
                            idx = int(choice) - 1
                            if 0 <= idx < len(weapons):
                                character.equip_weapon(weapons[idx], 'secundaria')
                                ws = character.equipped['arma_secundaria']
                                print(f"✓ {ws['nombre']} equipado. Ataque: {ws['ataque']:+d}, Daño: {ws['daño']}")
                    except (ValueError, IndexError):
                        pass
    
    print("\n✅ ¡Personaje creado exitosamente!")
    character.show_character_sheet()
    
    return character

def save_character(character, filename=None):
    """Guarda el personaje en un archivo JSON"""
    if not filename:
        filename = f"{character.name.replace(' ', '_')}_character.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(character.to_dict(), f, indent=4, ensure_ascii=False)
    
    logger.info(f"💾 Personaje guardado en: {filename}")
    return filename

def load_character(filename, data_loader):
    """Carga un personaje desde un archivo JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        character = Character(data['name'], data_loader)
        character.race = data.get('race')
        character.character_class = data.get('class')
        character.level = data.get('level', 1)
        character.experience = data.get('experience', 0)
        character.attributes = data.get('attributes', {})
        character.hit_points_max = data.get('hit_points_max', 0)
        character.hit_points_current = data.get('hit_points_current', 0)
        character.armor_class = data.get('armor_class', 10)
        character.thac0 = data.get('thac0', 20)
        character.saving_throws = data.get('saving_throws', {})
        character.skills = data.get('skills', {})
        character.proficiencies = data.get('proficiencies', {'armas': [], 'no_armas': []})
        character.kit = data.get('kit')
        character.equipment = data.get('equipment', [])
        character.equipped = data.get('equipped', {
            'arma_principal': None,
            'arma_secundaria': None,
            'armadura': None,
            'escudo': None
        })
        character.money = data.get('money', {'po': 0, 'pp': 0, 'pe': 0, 'pc': 0})
        character.known_spells = data.get('known_spells', [])
        character.prepared_spells = data.get('prepared_spells', [])
        
        logger.info(f"📂 Personaje cargado: {character.name}")
        return character
        
    except Exception as e:
        logger.error(f"❌ Error cargando personaje: {e}")
        return None
        character.known_spells = data.get('known_spells', [])
        character.prepared_spells = data.get('prepared_spells', [])
        
        logger.info(f"📂 Personaje cargado: {character.name}")
        return character
        
    except Exception as e:
        logger.error(f"❌ Error cargando personaje: {e}")
        return None

# ============================================================================
# PROGRAMA PRINCIPAL
# ============================================================================

def main():
    """Función principal del programa"""
    print("\n" + "="*60)
    print("⚔️  GESTOR DE PERSONAJES AD&D 2e ⚔️")
    print("="*60)
    
    # Inicializar cargador de datos
    logger.info("🔧 Inicializando sistema...")
    data_loader = ADnDDataLoader()
    data_loader.load_or_extract_data()
    
    if not data_loader.classes:
        logger.error("❌ No se pudieron cargar los datos. Verifica los PDFs.")
        return
    
    logger.info(f"✅ Sistema listo:")
    logger.info(f"   - {len(data_loader.classes)} clases cargadas")
    logger.info(f"   - {len(data_loader.races)} razas cargadas")
    logger.info(f"   - {sum(len(spells) for spells in data_loader.spells.values())} hechizos cargados")
    
    while True:
        print("\n" + "-"*60)
        print("MENÚ PRINCIPAL")
        print("-"*60)
        print("  [1] Crear nuevo personaje")
        print("  [2] Cargar personaje existente")
        print("  [3] Generar ficha HTML de personaje")
        print("  [4] Ver lista de hechizos")
        print("  [5] Ver clases disponibles")
        print("  [6] Ver razas disponibles")
        print("  [7] Regenerar cache de datos")
        print("  [0] Salir")
        
        choice = input("\nElige una opción: ").strip()
        
        if choice == '1':
            character = create_character_interactive(data_loader)
            save_choice = input("\n¿Guardar personaje? (s/n): ").strip().lower()
            if save_choice == 's':
                filename = save_character(character)
                
                # Ofrecer generar ficha oficial
                pdf_choice = input("\n¿Generar ficha de personaje HTML? (s/n): ").strip().lower()
                if pdf_choice == 's':
                    try:
                        import subprocess
                        json_file = filename
                        subprocess.run(['python', 'generar_html_ficha.py', json_file], check=True)
                    except Exception as e:
                        logger.error(f"Error generando ficha HTML: {e}")
                        print("❌ No se pudo generar la ficha HTML")
        
        elif choice == '2':
            filename = input("Nombre del archivo (ej: personaje.json): ").strip()
            character = load_character(filename, data_loader)
            if character:
                character.show_character_sheet()
                
                # Menú de personaje expandido
                while True:
                    print("\n" + "-"*60)
                    print("MENÚ DE PERSONAJE")
                    print("-"*60)
                    print("  [1] Ver hechizo")
                    print("  [2] Preparar hechizo")
                    print("  [3] Subir de nivel")
                    print("  [4] Añadir experiencia")
                    print("  [5] Editar atributos")
                    print("  [6] Editar HP")
                    print("  [7] Gestionar equipo")
                    print("  [8] Gestionar dinero")
                    print("  [9] Ver ficha completa")
                    print("  [10] Guardar cambios")
                    print("  [0] Volver al menú principal")
                    
                    sub_choice = input("\nOpción: ").strip()
                    
                    if sub_choice == '1' and character.known_spells:
                        for i, spell in enumerate(character.known_spells, 1):
                            print(f"  [{i}] {spell}")
                        try:
                            idx = int(input("Número de hechizo: ").strip()) - 1
                            if 0 <= idx < len(character.known_spells):
                                character.show_spell_details(character.known_spells[idx])
                        except ValueError:
                            pass
                    
                    elif sub_choice == '2' and character.known_spells:
                        for i, spell in enumerate(character.known_spells, 1):
                            marker = "✓" if spell in character.prepared_spells else " "
                            print(f"  [{marker}] [{i}] {spell}")
                        try:
                            idx = int(input("Número de hechizo a preparar: ").strip()) - 1
                            if 0 <= idx < len(character.known_spells):
                                character.prepare_spell(character.known_spells[idx])
                        except ValueError:
                            pass
                    
                    elif sub_choice == '3':
                        confirm = input(f"¿Subir de nivel {character.level} → {character.level + 1}? (s/n): ").strip().lower()
                        if confirm == 's':
                            character.level_up()
                            character.show_character_sheet()
                    
                    elif sub_choice == '4':
                        try:
                            xp = int(input("Cantidad de XP a añadir: ").strip())
                            if character.add_experience(xp):
                                level_up = input("¿Deseas subir de nivel ahora? (s/n): ").strip().lower()
                                if level_up == 's':
                                    character.level_up()
                        except ValueError:
                            print("❌ Valor inválido")
                    
                    elif sub_choice == '5':
                        character.edit_attributes()
                        character.show_character_sheet()
                    
                    elif sub_choice == '6':
                        character.edit_hp()
                    
                    elif sub_choice == '7':
                        # Gestionar equipo
                        while True:
                            print("\n--- EQUIPO ACTUAL ---")
                            for i, item in enumerate(character.equipment, 1):
                                print(f"  [{i}] {item}")
                            print("\n[a] Agregar  [e] Eliminar  [Enter] Volver")
                            action = input("Acción: ").strip().lower()
                            
                            if action == 'a':
                                # Mostrar equipo disponible
                                print("\n--- EQUIPO DISPONIBLE ---")
                                
                                # Armas
                                if data_loader.equipment.get('armas'):
                                    print("\n🗡️ ARMAS:")
                                    armas = list(data_loader.equipment['armas'].keys())
                                    for i, arma in enumerate(armas, 1):
                                        info = data_loader.equipment['armas'][arma]
                                        print(f"  [{i}] {arma} - {info.get('costo', '?')} (Daño: {info.get('dano_pq', '?')})")
                                
                                # Armaduras
                                if data_loader.equipment.get('armaduras'):
                                    print("\n🛡️ ARMADURAS:")
                                    armaduras = list(data_loader.equipment['armaduras'].keys())
                                    base_idx = len(data_loader.equipment.get('armas', {}))
                                    for i, armor in enumerate(armaduras, base_idx + 1):
                                        info = data_loader.equipment['armaduras'][armor]
                                        print(f"  [{i}] {armor} - {info.get('costo', '?')} (CA: {info.get('ca', '?')})")
                                
                                # Objetos comunes
                                print("\n📦 OBJETOS COMUNES:")
                                common_items = [
                                    "Mochila", "Cuerda (15m)", "Antorcha", "Pedernal y yesca",
                                    "Raciones (1 día)", "Odre", "Saco", "Tienda pequeña",
                                    "Manta", "Ganzúas", "Espejo de acero", "Símbolo sagrado",
                                    "Libro de conjuros", "Componentes de hechizos", "Poción de curación"
                                ]
                                start_idx = len(data_loader.equipment.get('armas', {})) + len(data_loader.equipment.get('armaduras', {}))
                                for i, item in enumerate(common_items, start_idx + 1):
                                    print(f"  [{i}] {item}")
                                
                                print("\nEscribe el número del objeto o su nombre:")
                                new_item = input("Objeto: ").strip()
                                
                                # Verificar si es un número
                                try:
                                    idx = int(new_item) - 1
                                    all_items = (
                                        list(data_loader.equipment.get('armas', {}).keys()) +
                                        list(data_loader.equipment.get('armaduras', {}).keys()) +
                                        common_items
                                    )
                                    if 0 <= idx < len(all_items):
                                        new_item = all_items[idx]
                                except ValueError:
                                    pass
                                
                                if new_item:
                                    character.equipment.append(new_item)
                                    print(f"✓ '{new_item}' agregado")
                            
                            elif action == 'e':
                                try:
                                    idx = int(input("Número del objeto a eliminar: ").strip()) - 1
                                    if 0 <= idx < len(character.equipment):
                                        removed = character.equipment.pop(idx)
                                        print(f"✓ '{removed}' eliminado")
                                except (ValueError, IndexError):
                                    print("❌ Número inválido")
                            else:
                                break
                    
                    elif sub_choice == '8':
                        # Gestionar dinero
                        print("\n--- DINERO ACTUAL ---")
                        for coin, amount in character.money.items():
                            print(f"{coin.upper()}: {amount}")
                        
                        for coin in ['po', 'pp', 'pe', 'pc']:
                            try:
                                new_val = input(f"{coin.upper()} (Enter para mantener): ").strip()
                                if new_val:
                                    character.money[coin] = max(0, int(new_val))
                            except ValueError:
                                pass
                        print("✓ Dinero actualizado")
                    
                    elif sub_choice == '9':
                        character.show_character_sheet()
                    
                    elif sub_choice == '10':
                        save_character(character, filename)
                    
                    elif sub_choice == '0':
                        save_prompt = input("¿Guardar cambios antes de salir? (s/n): ").strip().lower()
                        if save_prompt == 's':
                            save_character(character, filename)
                        break
        
        elif choice == '3':
            # Generar ficha HTML
            from pathlib import Path
            json_files = list(Path('.').glob('*_character.json'))
            
            if not json_files:
                print("\n❌ No hay personajes guardados en formato JSON")
            else:
                print("\n--- PERSONAJES DISPONIBLES ---")
                for i, f in enumerate(json_files, 1):
                    print(f"  [{i}] {f.stem.replace('_character', '')}")
                
                print("  [0] Generar ficha HTML para todos")
                
                try:
                    html_choice = input("\nElige personaje (número): ").strip()
                    
                    if html_choice == '0':
                        # Generar ficha HTML para todos
                        try:
                            import subprocess
                            for json_file in json_files:
                                subprocess.run(['python', 'generar_html_ficha.py', str(json_file)], check=True)
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            print("❌ Error generando fichas HTML")
                    else:
                        idx = int(html_choice) - 1
                        if 0 <= idx < len(json_files):
                            try:
                                import subprocess
                                subprocess.run(['python', 'generar_html_ficha.py', str(json_files[idx])], check=True)
                            except Exception as e:
                                logger.error(f"Error: {e}")
                                print("❌ Error generando ficha HTML")
                except ValueError:
                    print("❌ Opción inválida")
        
        elif choice == '4':
            print("\n--- HECHIZOS DISPONIBLES ---")
            for class_name, spells in data_loader.spells.items():
                print(f"\n{class_name}:")
                for spell_name, spell_data in spells.items():
                    print(f"  • {spell_name} (Nivel {spell_data['nivel']})")
        
        elif choice == '5':
            print("\n--- CLASES DISPONIBLES ---")
            for class_name, class_data in data_loader.classes.items():
                requisitos = class_data.get('requisitos', {})
                if requisitos:
                    req_text = ", ".join([f"{attr} {val}+" for attr, val in requisitos.items()])
                else:
                    req_text = "Ninguno"
                print(f"\n{class_name}:")
                print(f"  Requisitos: {req_text}")
                print(f"  Dado de Golpe: d{class_data.get('dado_golpe', '?')}")
                print(f"  THAC0 inicial: {class_data.get('thac0_inicial', 20)}")
        
        elif choice == '6':
            print("\n--- RAZAS DISPONIBLES ---")
            for race_name, race_data in data_loader.races.items():
                print(f"\n{race_name}:")
                if race_data['ajustes_atributos']:
                    mods = ", ".join([f"{attr} {mod:+d}" for attr, mod in race_data['ajustes_atributos'].items()])
                    print(f"  Modificadores: {mods}")
                
                # Mostrar clases de forma más clara
                clases = race_data['clases_permitidas']
                if 'Todas' in clases:
                    print(f"  Clases: Todas ({len(data_loader.classes)} disponibles)")
                else:
                    print(f"  Clases: {', '.join(clases)}")
                
                if race_data['habilidades_especiales']:
                    print(f"  Habilidades: {', '.join(race_data['habilidades_especiales'][:3])}...")  # Limitar a 3
        
        elif choice == '7':
            logger.info("🔄 Regenerando cache de datos...")
            if data_loader.cache_file.exists():
                data_loader.cache_file.unlink()
            data_loader.extract_all_pdfs()
            data_loader.save_cache()
            logger.info("✅ Cache regenerado")
        
        elif choice == '0':
            print("\n👋 ¡Hasta pronto, aventurero!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()
        
