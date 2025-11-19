"""
Sistema de Combate AD&D 2e
Gestiona encuentros de combate con personajes y criaturas del manual de monstruos
Integra el sistema de dados y aplica todas las reglas de combate
"""

import json
import random
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .dados import DiceRoller


class Monster:
    """Representa una criatura del manual de monstruos"""
    def __init__(self, name: str, data: dict):
        self.name = name
        self.original_data = data
        
        # Estadísticas básicas
        self.ac = data.get('ac', 10)
        self.hd = data.get('hd', '1d8')  # Hit Dice
        self.hp = data.get('hp', 0)
        self.max_hp = self.hp
        self.thac0 = data.get('thac0', 20)
        
        # Ataques y daño
        self.attacks = data.get('attacks', ['1d4'])  # Lista de dados de daño por ataque
        self.num_attacks = len(self.attacks)
        
        # Movimiento y características
        self.movement = data.get('movement', 12)
        self.morale = data.get('morale', 10)
        
        # Salvaciones (si no están, usar valores por defecto según HD)
        self.saves = data.get('saves', self._default_saves())
        
        # Habilidades especiales
        self.special_abilities = data.get('special', [])
        self.resistances = data.get('resistances', [])
        self.immunities = data.get('immunities', [])
        
        # Estado de combate
        self.initiative = 0
        self.is_surprised = False
        self.conditions = []  # paralizado, envenenado, etc.
        self.is_alive = True
        
    def _default_saves(self) -> dict:
        """Genera salvaciones por defecto basadas en HD"""
        # Simplificado - usar HD para determinar nivel de salvación
        hd_num = int(self.hd.split('d')[0]) if 'd' in self.hd else 1
        base = max(20 - hd_num, 10)
        return {
            'Paralización, Veneno o Muerte por Magia': base,
            'Varita Mágica': base + 1,
            'Petrificación o Transformación': base + 2,
            'Soplo de Dragón': base - 1,
            'Conjuro, Bastón o Vara': base + 1
        }
    
    def take_damage(self, damage: int) -> str:
        """Aplica daño al monstruo"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            return f"💀 {self.name} ha muerto!"
        percentage = (self.hp / self.max_hp) * 100
        if percentage < 25:
            return f"⚠️ {self.name} está gravemente herido ({self.hp}/{self.max_hp} HP)"
        elif percentage < 50:
            return f"🩸 {self.name} está seriamente herido ({self.hp}/{self.max_hp} HP)"
        else:
            return f"✅ {self.name} recibe {damage} de daño ({self.hp}/{self.max_hp} HP)"
    
    def heal(self, amount: int) -> str:
        """Cura al monstruo"""
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        healed = self.hp - old_hp
        return f"💚 {self.name} se cura {healed} HP ({self.hp}/{self.max_hp})"
    
    def get_attack_bonus(self) -> int:
        """Calcula bonus de ataque basado en HD"""
        # Monstruos más poderosos tienen mejor THAC0
        return 0  # Bonus se aplica por situación específica
    
    def __str__(self):
        status = "💀" if not self.is_alive else ("⚠️" if self.hp < self.max_hp / 2 else "💚")
        return f"{status} {self.name} - HP: {self.hp}/{self.max_hp}, AC: {self.ac}, THAC0: {self.thac0}"


class MonsterDatabase:
    """Base de datos de monstruos del manual"""
    def __init__(self):
        self.monsters = self._load_monsters()
        self._build_indices()
    
    def _build_indices(self):
        """Construye índices para búsqueda rápida"""
        self.by_hd = {}  # Por rango de HD
        self.by_type = {}  # Por tipo de criatura
        self.by_environment = {}  # Por ambiente
        self.by_challenge = {}  # Por nivel de desafío (HD simplificado)
        
        for name, data in self.monsters.items():
            # Índice por HD
            hd_str = data.get('hd', '1d8')
            hd_num = int(hd_str.split('d')[0]) if 'd' in hd_str else 1
            
            if hd_num <= 1:
                challenge = "Muy Fácil"
            elif hd_num <= 3:
                challenge = "Fácil"
            elif hd_num <= 6:
                challenge = "Medio"
            elif hd_num <= 10:
                challenge = "Difícil"
            else:
                challenge = "Muy Difícil"
            
            if challenge not in self.by_challenge:
                self.by_challenge[challenge] = []
            self.by_challenge[challenge].append(name)
            
            # Índice por tipo
            creature_type = data.get('type', 'Otro')
            if creature_type not in self.by_type:
                self.by_type[creature_type] = []
            self.by_type[creature_type].append(name)
            
            # Índice por ambiente
            environment = data.get('environment', 'Variado')
            if environment not in self.by_environment:
                self.by_environment[environment] = []
            self.by_environment[environment].append(name)
    
    def _load_monsters(self) -> dict:
        """Carga monstruos desde JSON o genera biblioteca básica"""
        monsters_file = Path(__file__).parent / "monstruos.json"
        
        if monsters_file.exists():
            with open(monsters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Biblioteca completa de monstruos de AD&D 2e
            return {
                # === HUMANOIDES MENORES (HD 1-2) ===
                "Goblin": {
                    "type": "Humanoide", "environment": "Subterráneo/Colinas",
                    "ac": 6, "hd": "1d8", "hp": 4, "thac0": 20,
                    "attacks": ["1d6"], "movement": 6, "morale": 8,
                    "special": ["Infravisión 60'", "-1 ataque luz solar"],
                    "xp": 15
                },
                "Kobold": {
                    "type": "Humanoide", "environment": "Subterráneo/Bosque",
                    "ac": 7, "hd": "1d4", "hp": 2, "thac0": 20,
                    "attacks": ["1d4"], "movement": 6, "morale": 6,
                    "special": ["Infravisión 60'", "-1 ataque luz solar", "Trampas astutas"],
                    "xp": 7
                },
                "Orco": {
                    "type": "Humanoide", "environment": "Subterráneo/Montañas",
                    "ac": 6, "hd": "1d8", "hp": 5, "thac0": 19,
                    "attacks": ["1d8"], "movement": 12, "morale": 11,
                    "special": ["Infravisión 60'", "-1 ataque luz solar"],
                    "xp": 15
                },
                "Hobgoblin": {
                    "type": "Humanoide", "environment": "Subterráneo/Colinas",
                    "ac": 5, "hd": "1d8+1", "hp": 6, "thac0": 19,
                    "attacks": ["1d8"], "movement": 9, "morale": 11,
                    "special": ["Infravisión 60'", "Disciplinados +1 moral"],
                    "xp": 35
                },
                "Gnoll": {
                    "type": "Humanoide", "environment": "Desierto/Sabana",
                    "ac": 5, "hd": "2d8", "hp": 9, "thac0": 19,
                    "attacks": ["2d4"], "movement": 9, "morale": 11,
                    "special": ["Infravisión 60'", "Hiena-humanoide"],
                    "xp": 35
                },
                
                # === NO-MUERTOS (HD 1-4) ===
                "Esqueleto": {
                    "type": "No-muerto", "environment": "Variado",
                    "ac": 7, "hd": "1d8", "hp": 5, "thac0": 19,
                    "attacks": ["1d6"], "movement": 12, "morale": 12,
                    "special": ["Inmune: frío, encantamiento, sueño", "Armas cortantes 1/2 daño"],
                    "immunities": ["frío", "encantamiento", "sueño"],
                    "xp": 65
                },
                "Zombi": {
                    "type": "No-muerto", "environment": "Variado",
                    "ac": 8, "hd": "2d8", "hp": 9, "thac0": 19,
                    "attacks": ["1d8"], "movement": 6, "morale": 12,
                    "special": ["Inmune: frío, encantamiento, sueño", "Siempre actúa último"],
                    "immunities": ["frío", "encantamiento", "sueño"],
                    "xp": 65
                },
                "Sombra": {
                    "type": "No-muerto", "environment": "Subterráneo/Ruinas",
                    "ac": 7, "hd": "3d8+3", "hp": 16, "thac0": 17,
                    "attacks": ["1d4+1"], "movement": 12, "morale": 12,
                    "special": ["Drenar 1 FUE por impacto", "Inmune: frío, encantamiento", "+1 o mejor para impactar"],
                    "immunities": ["frío", "encantamiento"],
                    "xp": 175
                },
                "Aparición": {
                    "type": "No-muerto", "environment": "Ruinas/Tumbas",
                    "ac": 4, "hd": "4d8", "hp": 18, "thac0": 17,
                    "attacks": ["1d6"], "movement": 15, "morale": 12,
                    "special": ["Drenar 1 nivel por impacto", "Solo armas mágicas", "Inmune: frío, parálisis"],
                    "immunities": ["frío", "parálisis", "veneno"],
                    "xp": 975
                },
                
                # === ANIMALES (HD 1-5) ===
                "Rata Gigante": {
                    "type": "Animal", "environment": "Subterráneo/Ciudad",
                    "ac": 7, "hd": "1d4", "hp": 2, "thac0": 20,
                    "attacks": ["1d3"], "movement": 12, "morale": 5,
                    "special": ["5% enfermedad por mordida"],
                    "xp": 7
                },
                "Lobo": {
                    "type": "Animal", "environment": "Bosque/Montañas",
                    "ac": 7, "hd": "2d8+2", "hp": 11, "thac0": 19,
                    "attacks": ["1d4+1"], "movement": 18, "morale": 11,
                    "special": ["Olfato agudo", "Caza en manada"],
                    "xp": 35
                },
                "Oso Negro": {
                    "type": "Animal", "environment": "Bosque/Montañas",
                    "ac": 7, "hd": "3d8+3", "hp": 17, "thac0": 17,
                    "attacks": ["1d3", "1d3", "1d6"], "movement": 12, "morale": 10,
                    "special": ["Abrazo 2d4 si ambas garras impactan"],
                    "xp": 120
                },
                "Oso Pardo": {
                    "type": "Animal", "environment": "Bosque/Montañas",
                    "ac": 6, "hd": "5d8+5", "hp": 27, "thac0": 15,
                    "attacks": ["1d6", "1d6", "1d8"], "movement": 12, "morale": 11,
                    "special": ["Abrazo 2d6 si ambas garras impactan"],
                    "xp": 270
                },
                "Jabalí": {
                    "type": "Animal", "environment": "Bosque",
                    "ac": 7, "hd": "3d8+3", "hp": 17, "thac0": 17,
                    "attacks": ["3d4"], "movement": 15, "morale": 10,
                    "special": ["Carga: daño doble si corre 20'+"],
                    "xp": 120
                },
                
                # === GIGANTES Y GRANDES HUMANOIDES (HD 4-15) ===
                "Ogro": {
                    "type": "Gigante", "environment": "Montañas/Colinas",
                    "ac": 5, "hd": "4d8+1", "hp": 19, "thac0": 17,
                    "attacks": ["1d10"], "movement": 9, "morale": 11,
                    "special": ["Gran tamaño", "Come humanos"],
                    "xp": 175
                },
                "Troll": {
                    "type": "Gigante", "environment": "Pantanos/Montañas",
                    "ac": 4, "hd": "6d8+6", "hp": 33, "thac0": 15,
                    "attacks": ["1d4+4", "1d4+4", "1d8+4"], "movement": 12, "morale": 14,
                    "special": ["Regeneración 3 HP/round", "Fuego/ácido previenen regeneración"],
                    "xp": 650
                },
                "Gigante de Colina": {
                    "type": "Gigante", "environment": "Colinas/Montañas",
                    "ac": 4, "hd": "12d8+1", "hp": 55, "thac0": 9,
                    "attacks": ["2d8"], "movement": 12, "morale": 13,
                    "special": ["Arrojar rocas 2d8 (alcance 200')"],
                    "xp": 2000
                },
                "Gigante de Piedra": {
                    "type": "Gigante", "environment": "Montañas/Cuevas",
                    "ac": 0, "hd": "14d8+1", "hp": 64, "thac0": 7,
                    "attacks": ["2d10"], "movement": 12, "morale": 14,
                    "special": ["Arrojar rocas 3d10", "Camuflaje en piedra"],
                    "xp": 4000
                },
                
                # === DRAGONES (HD 6-11) ===
                "Dragón Blanco Juvenil": {
                    "type": "Dragón", "environment": "Ártico/Montañas Frías",
                    "ac": 3, "hd": "6d8+6", "hp": 33, "thac0": 15,
                    "attacks": ["1d6", "1d6", "2d8"], "movement": 12,
                    "morale": 15,
                    "special": ["Soplo: cono 70' frío 3d8+3", "Inmune: frío", "Vuela 24"],
                    "immunities": ["frío"],
                    "xp": 975
                },
                "Dragón Verde Joven": {
                    "type": "Dragón", "environment": "Bosque/Selva",
                    "ac": 2, "hd": "8d8+8", "hp": 44, "thac0": 13,
                    "attacks": ["1d8", "1d8", "2d10"], "movement": 9,
                    "morale": 16,
                    "special": ["Soplo: nube 50' gas cloro 4d8+4", "Inmune: gas", "Vuela 24"],
                    "immunities": ["gas", "veneno"],
                    "xp": 1400
                },
                "Dragón Rojo Adulto": {
                    "type": "Dragón", "environment": "Montañas/Volcanes",
                    "ac": -1, "hd": "11d8+11", "hp": 60, "thac0": 10,
                    "attacks": ["1d10", "1d10", "3d8"], "movement": 9,
                    "morale": 17,
                    "special": ["Soplo: cono 90' fuego 6d10+11", "Inmune: fuego", "Vuela 24", "Magia nivel 5"],
                    "immunities": ["fuego"],
                    "xp": 8000
                },
                
                # === CRIATURAS MÁGICAS (HD 3-9) ===
                "Doppelganger": {
                    "type": "Cambiaformas", "environment": "Subterráneo/Ciudad",
                    "ac": 5, "hd": "4d8", "hp": 18, "thac0": 17,
                    "attacks": ["1d12"], "movement": 9, "morale": 10,
                    "special": ["Cambiar forma (humanoide)", "ESP continuo", "Inmune: sueño, encantamiento"],
                    "immunities": ["sueño", "encantamiento"],
                    "xp": 420
                },
                "Medusa": {
                    "type": "Monstruoso", "environment": "Subterráneo/Ruinas",
                    "ac": 5, "hd": "6d8", "hp": 27, "thac0": 15,
                    "attacks": ["1d4"], "movement": 9, "morale": 12,
                    "special": ["Mirada petrifica", "Cabello de serpientes (veneno)"],
                    "xp": 1400
                },
                "Basilisco": {
                    "type": "Monstruoso", "environment": "Subterráneo",
                    "ac": 4, "hd": "6d8+3", "hp": 30, "thac0": 15,
                    "attacks": ["1d10"], "movement": 6, "morale": 12,
                    "special": ["Mirada petrifica", "Toque petrifica"],
                    "xp": 975
                },
                "Manticora": {
                    "type": "Monstruoso", "environment": "Montañas/Desierto",
                    "ac": 4, "hd": "6d8+3", "hp": 30, "thac0": 15,
                    "attacks": ["1d4", "1d4", "1d8"], "movement": 12,
                    "morale": 13,
                    "special": ["24 espinas cola 1d6 (alcance 180')", "Vuela 18"],
                    "xp": 975
                },
                "Quimera": {
                    "type": "Monstruoso", "environment": "Montañas/Colinas",
                    "ac": 6, "hd": "9d8", "hp": 40, "thac0": 12,
                    "attacks": ["1d3", "1d3", "2d4", "3d4", "1d10"], "movement": 9,
                    "morale": 14,
                    "special": ["Soplo fuego 3d8 (cabeza dragón)", "Vuela 18"],
                    "xp": 2000
                },
                
                # === DEMONIOS Y DIABLOS (HD 7-13) ===
                "Demonio Menor (Manes)": {
                    "type": "Demonio", "environment": "Planos Inferiores",
                    "ac": 7, "hd": "1d8", "hp": 4, "thac0": 19,
                    "attacks": ["1d4", "1d4"], "movement": 3, "morale": 12,
                    "special": ["+1 o mejor para impactar", "Inmune: fuego, gas"],
                    "immunities": ["fuego", "gas"],
                    "xp": 65
                },
                "Demonio Tipo I (Vrock)": {
                    "type": "Demonio", "environment": "Planos Inferiores",
                    "ac": 0, "hd": "8d8", "hp": 36, "thac0": 13,
                    "attacks": ["1d4", "1d4", "1d8", "1d8"], "movement": 12,
                    "morale": 16,
                    "special": ["Teleportar", "Magia", "+2 o mejor para impactar", "Vuela 18"],
                    "immunities": ["fuego", "gas", "electricidad"],
                    "xp": 3000
                },
                "Diablo Barbado": {
                    "type": "Diablo", "environment": "Planos Inferiores",
                    "ac": -1, "hd": "6d8+6", "hp": 33, "thac0": 15,
                    "attacks": ["2d4", "2d4", "1d3"], "movement": 9,
                    "morale": 15,
                    "special": ["Barba causa enfermedad", "+1 o mejor para impactar", "Magia"],
                    "immunities": ["fuego", "veneno"],
                    "xp": 1400
                },
                
                # === CRIATURAS VOLADORAS (HD 2-7) ===
                "Grifo": {
                    "type": "Monstruoso", "environment": "Montañas",
                    "ac": 3, "hd": "7d8+3", "hp": 34, "thac0": 13,
                    "attacks": ["1d4", "1d4", "2d8"], "movement": 12,
                    "morale": 14,
                    "special": ["Vuela 30", "Montable"],
                    "xp": 650
                },
                "Hipogrifo": {
                    "type": "Monstruoso", "environment": "Montañas/Colinas",
                    "ac": 5, "hd": "3d8+1", "hp": 15, "thac0": 17,
                    "attacks": ["1d6", "1d6", "1d10"], "movement": 18,
                    "morale": 11,
                    "special": ["Vuela 36", "Montable"],
                    "xp": 175
                },
                "Wyvern": {
                    "type": "Dragón", "environment": "Montañas/Acantilados",
                    "ac": 3, "hd": "7d8+7", "hp": 38, "thac0": 13,
                    "attacks": ["2d8", "1d6"], "movement": 6,
                    "morale": 13,
                    "special": ["Veneno aguijón (salvación o muerte)", "Vuela 24"],
                    "xp": 975
                },
                "Pegaso": {
                    "type": "Monstruoso", "environment": "Montañas/Planicies",
                    "ac": 6, "hd": "4d8+4", "hp": 22, "thac0": 17,
                    "attacks": ["1d6", "1d6"], "movement": 24,
                    "morale": 14,
                    "special": ["Vuela 48", "Montable (buenos)", "Teleportación 1/día"],
                    "xp": 270
                },
                
                # === LIMOS Y CUBOS (HD 2-10) ===
                "Limo Verde": {
                    "type": "Limo", "environment": "Subterráneo",
                    "ac": 9, "hd": "2d8", "hp": 9, "thac0": 19,
                    "attacks": ["Especial"], "movement": 0, "morale": 12,
                    "special": ["Disuelve todo excepto piedra/vidrio", "Caída de techo"],
                    "immunities": ["frío", "fuego (parcial)"],
                    "xp": 65
                },
                "Cubo Gelatinoso": {
                    "type": "Limo", "environment": "Subterráneo",
                    "ac": 8, "hd": "4d8", "hp": 18, "thac0": 17,
                    "attacks": ["2d4"], "movement": 6, "morale": 12,
                    "special": ["Parálisis al tocar", "Transparente (sorpresa)", "Inmune: frío, rayo"],
                    "immunities": ["frío", "electricidad"],
                    "xp": 270
                },
                "Pudín Negro": {
                    "type": "Limo", "environment": "Subterráneo",
                    "ac": 6, "hd": "10d8", "hp": 45, "thac0": 11,
                    "attacks": ["3d8"], "movement": 6, "morale": 12,
                    "special": ["Divide con armas/rayo", "Disuelve metal/madera", "Inmune: frío"],
                    "immunities": ["frío", "veneno"],
                    "xp": 3000
                },
                
                # === INSECTOS GIGANTES (HD 1-4) ===
                "Araña Gigante": {
                    "type": "Vermin", "environment": "Bosque/Subterráneo",
                    "ac": 6, "hd": "2d8+2", "hp": 11, "thac0": 19,
                    "attacks": ["1d6"], "movement": 12, "morale": 9,
                    "special": ["Veneno (salvación o muerte)", "Telaraña"],
                    "xp": 175
                },
                "Escarabajo de Fuego Gigante": {
                    "type": "Vermin", "environment": "Subterráneo/Bosque",
                    "ac": 4, "hd": "1d8+3", "hp": 7, "thac0": 19,
                    "attacks": ["2d4"], "movement": 12, "morale": 10,
                    "special": ["Glándulas luz (10' radio)", "Resiste fuego"],
                    "xp": 65
                },
                "Hormiga Gigante": {
                    "type": "Vermin", "environment": "Bosque/Pradera",
                    "ac": 3, "hd": "4d8", "hp": 18, "thac0": 17,
                    "attacks": ["2d6"], "movement": 18, "morale": 12,
                    "special": ["Veneno (salvación o 2d6 daño)", "Colonia organizada"],
                    "xp": 270
                },
                
                # === PLANAR Y ELEMENTALES (HD 8-16) ===
                "Elemental de Fuego (8 HD)": {
                    "type": "Elemental", "environment": "Plano del Fuego",
                    "ac": 2, "hd": "8d8", "hp": 36, "thac0": 13,
                    "attacks": ["2d6"], "movement": 12, "morale": 15,
                    "special": ["Inmune: fuego", "Daño doble a criaturas frías", "+2 o mejor para impactar"],
                    "immunities": ["fuego", "veneno"],
                    "xp": 2000
                },
                "Elemental de Agua (12 HD)": {
                    "type": "Elemental", "environment": "Plano del Agua",
                    "ac": 2, "hd": "12d8", "hp": 54, "thac0": 9,
                    "attacks": ["3d8"], "movement": 6, "morale": 15,
                    "special": ["Control agua", "Ahogar", "+2 o mejor para impactar"],
                    "immunities": ["veneno"],
                    "xp": 5000
                },
                "Djinni": {
                    "type": "Genio", "environment": "Plano del Aire",
                    "ac": 4, "hd": "7d8+3", "hp": 34, "thac0": 13,
                    "attacks": ["2d8"], "movement": 9, "morale": 14,
                    "special": ["Magia (conjuro 3/día)", "Torbellino", "Vuela 24", "Crear comida/agua"],
                    "xp": 2000
                },
                "Efreeti": {
                    "type": "Genio", "environment": "Plano del Fuego",
                    "ac": 2, "hd": "10d8", "hp": 45, "thac0": 11,
                    "attacks": ["3d8"], "movement": 9, "morale": 15,
                    "special": ["Magia (conjuro 3/día)", "Muro de fuego", "Inmune: fuego", "Vuela 24"],
                    "immunities": ["fuego"],
                    "xp": 4000
                },
                
                # === LICÁNTROPOS (HD 3-7) ===
                "Hombre Lobo": {
                    "type": "Licántropo", "environment": "Bosque/Civilización",
                    "ac": 5, "hd": "4d8+3", "hp": 21, "thac0": 17,
                    "attacks": ["2d4"], "movement": 15, "morale": 11,
                    "special": ["Solo plata/mágico", "Contagio licantropía", "Puede controlar lobos"],
                    "immunities": ["armas normales"],
                    "xp": 420
                },
                "Hombre Oso": {
                    "type": "Licántropo", "environment": "Bosque/Montañas",
                    "ac": 2, "hd": "7d8+3", "hp": 34, "thac0": 13,
                    "attacks": ["2d4", "2d4", "2d8"], "movement": 9, "morale": 12,
                    "special": ["Solo plata/mágico", "Contagio licantropía", "Abrazo si 2 garras"],
                    "immunities": ["armas normales"],
                    "xp": 975
                },
                "Hombre Tigre": {
                    "type": "Licántropo", "environment": "Selva/Sabana",
                    "ac": 3, "hd": "6d8+2", "hp": 29, "thac0": 15,
                    "attacks": ["1d6", "1d6", "2d6"], "movement": 15, "morale": 12,
                    "special": ["Solo plata/mágico", "Contagio licantropía", "Sorpresa mejorada"],
                    "immunities": ["armas normales"],
                    "xp": 650
                },
                "Hombre Rata": {
                    "type": "Licántropo", "environment": "Ciudad/Alcantarillas",
                    "ac": 6, "hd": "3d8+1", "hp": 15, "thac0": 17,
                    "attacks": ["1d8"], "movement": 12, "morale": 9,
                    "special": ["Solo plata/mágico", "Contagio licantropía", "Control ratas"],
                    "immunities": ["armas normales"],
                    "xp": 270
                },
                "Hombre Jabalí": {
                    "type": "Licántropo", "environment": "Bosque",
                    "ac": 4, "hd": "5d8+2", "hp": 24, "thac0": 15,
                    "attacks": ["3d6"], "movement": 15, "morale": 12,
                    "special": ["Solo plata/mágico", "Contagio licantropía", "Carga feroz"],
                    "immunities": ["armas normales"],
                    "xp": 420
                },
                
                # === MÁS NO-MUERTOS (HD 3-9) ===
                "Ghoul": {
                    "type": "No-muerto", "environment": "Tumbas/Subterráneo",
                    "ac": 6, "hd": "2d8", "hp": 9, "thac0": 19,
                    "attacks": ["1d3", "1d3", "1d6"], "movement": 9, "morale": 12,
                    "special": ["Parálisis al tocar (salvación)", "Inmune: sueño, encantamiento"],
                    "immunities": ["sueño", "encantamiento"],
                    "xp": 175
                },
                "Wight": {
                    "type": "No-muerto", "environment": "Tumbas/Ruinas",
                    "ac": 5, "hd": "4d8+3", "hp": 21, "thac0": 17,
                    "attacks": ["1d4"], "movement": 12, "morale": 12,
                    "special": ["Drenar 1 nivel energía", "Solo plata/mágico", "Infravisión"],
                    "immunities": ["armas normales", "sueño", "encantamiento"],
                    "xp": 975
                },
                "Wraith": {
                    "type": "No-muerto", "environment": "Ruinas/Cementerios",
                    "ac": 3, "hd": "5d8+3", "hp": 26, "thac0": 15,
                    "attacks": ["1d6"], "movement": 12, "morale": 13,
                    "special": ["Drenar 1 nivel energía", "Solo plata/mágico", "Vuela 24"],
                    "immunities": ["armas normales", "sueño", "encantamiento"],
                    "xp": 1400
                },
                "Momia": {
                    "type": "No-muerto", "environment": "Tumbas/Desierto",
                    "ac": 3, "hd": "6d8+3", "hp": 30, "thac0": 15,
                    "attacks": ["1d12"], "movement": 6, "morale": 15,
                    "special": ["Miedo (salvación)", "Putrefacción momia", "+1 o mejor para impactar"],
                    "immunities": ["armas normales débiles", "veneno", "parálisis"],
                    "xp": 2000
                },
                "Espectro": {
                    "type": "No-muerto", "environment": "Ruinas Antiguas",
                    "ac": 2, "hd": "7d8+3", "hp": 34, "thac0": 13,
                    "attacks": ["1d8"], "movement": 15, "morale": 14,
                    "special": ["Drenar 2 niveles energía", "+1 o mejor para impactar", "Incorpóreo"],
                    "immunities": ["armas normales", "veneno", "parálisis"],
                    "xp": 3000
                },
                "Vampiro": {
                    "type": "No-muerto", "environment": "Castillos/Criptas",
                    "ac": 1, "hd": "8d8+3", "hp": 39, "thac0": 13,
                    "attacks": ["1d6+4"], "movement": 12, "morale": 16,
                    "special": ["Drenar 2 niveles", "Regenera 3 HP/round", "Forma gaseosa", "Encanto", "Convoca criaturas"],
                    "immunities": ["armas normales", "ajo", "agua corriente", "luz solar"],
                    "xp": 8000
                },
                "Lich": {
                    "type": "No-muerto", "environment": "Fortaleza Oculta",
                    "ac": 0, "hd": "12d8", "hp": 54, "thac0": 9,
                    "attacks": ["1d10"], "movement": 6, "morale": 18,
                    "special": ["Toque paralizante", "Miedo aura 60'", "Magia nivel 18+", "+1 o mejor"],
                    "immunities": ["armas normales", "frío", "electricidad", "veneno"],
                    "xp": 15000
                },
                
                # === MÁS DRAGONES ===
                "Dragón Negro Joven": {
                    "type": "Dragón", "environment": "Pantanos",
                    "ac": 2, "hd": "7d8+7", "hp": 38, "thac0": 13,
                    "attacks": ["1d6", "1d6", "3d6"], "movement": 12, "morale": 15,
                    "special": ["Soplo: línea 60' ácido 4d8+4", "Inmune: ácido", "Vuela 24", "Nada 24"],
                    "immunities": ["ácido"],
                    "xp": 1400
                },
                "Dragón Azul Joven": {
                    "type": "Dragón", "environment": "Desierto",
                    "ac": 1, "hd": "9d8+9", "hp": 49, "thac0": 12,
                    "attacks": ["1d8", "1d8", "3d8"], "movement": 9, "morale": 16,
                    "special": ["Soplo: línea 100' rayo 5d8+5", "Inmune: electricidad", "Vuela 24", "Cava 6"],
                    "immunities": ["electricidad"],
                    "xp": 3000
                },
                "Dragón Bronce Adulto": {
                    "type": "Dragón", "environment": "Costas",
                    "ac": -1, "hd": "12d8+12", "hp": 66, "thac0": 9,
                    "attacks": ["1d8", "1d8", "4d6"], "movement": 9, "morale": 17,
                    "special": ["Soplo: línea 90' rayo O nube gas", "Inmune: electricidad", "Vuela 24", "Nada 24", "Magia"],
                    "immunities": ["electricidad"],
                    "xp": 8000
                },
                "Dragón Plateado Viejo": {
                    "type": "Dragón", "environment": "Montañas Altas",
                    "ac": -3, "hd": "15d8+15", "hp": 82, "thac0": 6,
                    "attacks": ["1d10", "1d10", "5d6"], "movement": 9, "morale": 18,
                    "special": ["Soplo: cono 90' frío O nube gas", "Inmune: frío, gas", "Vuela 24", "Magia nivel 7", "Forma humana"],
                    "immunities": ["frío", "gas"],
                    "xp": 15000
                },
                "Dragón Dorado Anciano": {
                    "type": "Dragón", "environment": "Islas Lejanas",
                    "ac": -5, "hd": "18d8+18", "hp": 99, "thac0": 3,
                    "attacks": ["2d4", "2d4", "6d6"], "movement": 12, "morale": 19,
                    "special": ["Soplo: cono 90' fuego O nube gas", "Inmune: fuego, gas", "Vuela 24", "Magia nivel 11", "Forma animal"],
                    "immunities": ["fuego", "gas"],
                    "xp": 20000
                },
                
                # === GIGANTES ADICIONALES ===
                "Gigante de Fuego": {
                    "type": "Gigante", "environment": "Volcanes/Montañas",
                    "ac": 3, "hd": "15d8+5", "hp": 72, "thac0": 6,
                    "attacks": ["2d10"], "movement": 12, "morale": 15,
                    "special": ["Arrojar rocas 2d10", "Inmune: fuego", "Forja legendaria"],
                    "immunities": ["fuego"],
                    "xp": 5000
                },
                "Gigante de Hielo": {
                    "type": "Gigante", "environment": "Tundra/Glaciares",
                    "ac": 4, "hd": "14d8+7", "hp": 70, "thac0": 7,
                    "attacks": ["2d10"], "movement": 12, "morale": 14,
                    "special": ["Arrojar rocas/hielo 2d10", "Inmune: frío"],
                    "immunities": ["frío"],
                    "xp": 4000
                },
                "Gigante de las Nubes": {
                    "type": "Gigante", "environment": "Montañas Altas/Nubes",
                    "ac": 2, "hd": "16d8+2", "hp": 74, "thac0": 5,
                    "attacks": ["3d10"], "movement": 15, "morale": 16,
                    "special": ["Arrojar rocas 3d10", "Olfato excelente", "Castillo en nubes"],
                    "xp": 6000
                },
                "Gigante de las Tormentas": {
                    "type": "Gigante", "environment": "Océanos/Islas",
                    "ac": 1, "hd": "19d8+5", "hp": 90, "thac0": 2,
                    "attacks": ["3d10"], "movement": 15, "morale": 17,
                    "special": ["Arrojar rayos 8d6", "Control clima", "Inmune: electricidad", "Nada 30"],
                    "immunities": ["electricidad"],
                    "xp": 10000
                },
                "Ettín": {
                    "type": "Gigante", "environment": "Colinas/Cuevas",
                    "ac": 3, "hd": "10d8", "hp": 45, "thac0": 11,
                    "attacks": ["2d8", "3d6"], "movement": 12, "morale": 13,
                    "special": ["Dos cabezas (sorpresa difícil)", "2 ataques/round"],
                    "xp": 3000
                },
                
                # === HUMANOIDES ACUÁTICOS ===
                "Sahuagin": {
                    "type": "Humanoide", "environment": "Océano",
                    "ac": 5, "hd": "2d8+2", "hp": 11, "thac0": 19,
                    "attacks": ["1d4", "1d4", "2d4"], "movement": 12, "morale": 12,
                    "special": ["Nada 24", "Frenesí sangre +1 ataque", "Controla tiburones"],
                    "xp": 120
                },
                "Locathah": {
                    "type": "Humanoide", "environment": "Agua Dulce",
                    "ac": 6, "hd": "2d8", "hp": 9, "thac0": 19,
                    "attacks": ["1d6"], "movement": 12, "morale": 10,
                    "special": ["Nada 18", "Lanceros expertos"],
                    "xp": 35
                },
                "Triton": {
                    "type": "Humanoide", "environment": "Océano Profundo",
                    "ac": 5, "hd": "3d8+3", "hp": 16, "thac0": 17,
                    "attacks": ["2d4"], "movement": 15, "morale": 13,
                    "special": ["Nada 24", "Magia limitada", "Convoca criaturas marinas"],
                    "xp": 175
                },
                "Merrow": {
                    "type": "Humanoide", "environment": "Océano/Ríos",
                    "ac": 6, "hd": "4d8+4", "hp": 22, "thac0": 17,
                    "attacks": ["2d6", "2d6", "1d4"], "movement": 12, "morale": 12,
                    "special": ["Nada 18", "Ogro acuático", "Anfibio"],
                    "xp": 270
                },
                
                # === ABERRACIONES ===
                "Beholder": {
                    "type": "Aberración", "environment": "Subterráneo Profundo",
                    "ac": 0, "hd": "12d8", "hp": 54, "thac0": 9,
                    "attacks": ["2d4"], "movement": 3, "morale": 16,
                    "special": ["10 rayos oculares variados", "Ojo central anti-magia", "Vuela 3", "Mordida"],
                    "xp": 10000
                },
                "Mind Flayer": {
                    "type": "Aberración", "environment": "Subterráneo Profundo",
                    "ac": 5, "hd": "8d8+4", "hp": 40, "thac0": 13,
                    "attacks": ["4x1d4"], "movement": 12, "morale": 14,
                    "special": ["Ataque psiónico", "Extracción cerebro", "Inmune: ilusión", "Magia psiónica"],
                    "immunities": ["ilusión"],
                    "xp": 4000
                },
                "Aboleth": {
                    "type": "Aberración", "environment": "Lagos Subterráneos",
                    "ac": 4, "hd": "8d8", "hp": 36, "thac0": 13,
                    "attacks": ["4x1d6"], "movement": 3, "morale": 15,
                    "special": ["Esclavizar (salvación)", "Mucus transformador", "Nada 18", "Magia psiónica"],
                    "xp": 3000
                },
                "Umber Hulk": {
                    "type": "Aberración", "environment": "Subterráneo",
                    "ac": 2, "hd": "8d8+8", "hp": 44, "thac0": 13,
                    "attacks": ["3d4", "3d4", "2d10"], "movement": 6, "morale": 13,
                    "special": ["Mirada confusión", "Cava 6", "Mandíbulas poderosas"],
                    "xp": 2000
                },
                "Rust Monster": {
                    "type": "Aberración", "environment": "Subterráneo",
                    "ac": 2, "hd": "5d8", "hp": 22, "thac0": 15,
                    "attacks": ["Especial"], "movement": 18, "morale": 7,
                    "special": ["Toque oxida metal instantáneamente", "Antenas detectan metal"],
                    "xp": 650
                },
                
                # === CONSTRUCTOS ===
                "Gólem de Carne": {
                    "type": "Constructo", "environment": "Laboratorio",
                    "ac": 9, "hd": "9d8", "hp": 40, "thac0": 12,
                    "attacks": ["2d8", "2d8"], "movement": 8, "morale": 20,
                    "special": ["+1 o mejor", "Inmune: magia excepto fuego/frío", "Miedo aura", "Berserk"],
                    "immunities": ["magia (parcial)", "veneno", "parálisis"],
                    "xp": 3000
                },
                "Gólem de Hierro": {
                    "type": "Constructo", "environment": "Templo/Fortaleza",
                    "ac": 3, "hd": "18d8", "hp": 81, "thac0": 3,
                    "attacks": ["4d10"], "movement": 6, "morale": 20,
                    "special": ["+3 o mejor", "Soplo gas veneno", "Inmune: magia", "Absorbe rayo"],
                    "immunities": ["magia", "veneno", "parálisis", "armas débiles"],
                    "xp": 15000
                },
                "Gólem de Piedra": {
                    "type": "Constructo", "environment": "Templo",
                    "ac": 5, "hd": "14d8", "hp": 63, "thac0": 7,
                    "attacks": ["3d8"], "movement": 6, "morale": 20,
                    "special": ["+2 o mejor", "Slow emite 1/turno", "Inmune: magia excepto algunos conjuros"],
                    "immunities": ["magia (parcial)", "veneno", "parálisis"],
                    "xp": 8000
                },
                "Homúnculo": {
                    "type": "Constructo", "environment": "Laboratorio Mago",
                    "ac": 6, "hd": "2d8", "hp": 9, "thac0": 19,
                    "attacks": ["1d3"], "movement": 6, "morale": 12,
                    "special": ["Mordida causa sueño", "Vuela 18", "Enlace telepático con creador"],
                    "xp": 175
                },
                
                # === PLANTAS MONSTRUOSAS ===
                "Treant": {
                    "type": "Planta", "environment": "Bosque Antiguo",
                    "ac": 0, "hd": "12d8", "hp": 54, "thac0": 9,
                    "attacks": ["5d6", "5d6"], "movement": 12, "morale": 15,
                    "special": ["Animar árboles", "Vulnerable: fuego", "Guardián bosque"],
                    "xp": 4000
                },
                "Shambling Mound": {
                    "type": "Planta", "environment": "Pantano",
                    "ac": 0, "hd": "9d8", "hp": 40, "thac0": 12,
                    "attacks": ["2d8", "2d8"], "movement": 6, "morale": 14,
                    "special": ["Absorbe electricidad", "Envolver", "Inmune: fuego"],
                    "immunities": ["electricidad", "fuego"],
                    "xp": 3000
                },
                "Yellow Musk Creeper": {
                    "type": "Planta", "environment": "Ruinas Selváticas",
                    "ac": 9, "hd": "3d8", "hp": 13, "thac0": 17,
                    "attacks": ["Especial"], "movement": 0, "morale": 12,
                    "special": ["Polen control mental", "Crea zombis vegetales"],
                    "xp": 270
                },
                
                # === CRIATURAS DE FUEGO/HIELO ===
                "Salamandra": {
                    "type": "Elemental", "environment": "Plano del Fuego",
                    "ac": 5, "hd": "7d8+3", "hp": 34, "thac0": 13,
                    "attacks": ["1d6", "2d6"], "movement": 9, "morale": 14,
                    "special": ["Calor abrasador 1d6", "Inmune: fuego", "Constriñe"],
                    "immunities": ["fuego"],
                    "xp": 975
                },
                "Remorhaz": {
                    "type": "Animal", "environment": "Tundra",
                    "ac": 0, "hd": "11d8+11", "hp": 60, "thac0": 10,
                    "attacks": ["6d6"], "movement": 12, "morale": 13,
                    "special": ["Calor corporal 10d4", "Traga entero", "Inmune: frío"],
                    "immunities": ["frío"],
                    "xp": 5000
                },
                "Yeti": {
                    "type": "Animal", "environment": "Montañas Heladas",
                    "ac": 6, "hd": "4d8+4", "hp": 22, "thac0": 17,
                    "attacks": ["1d6", "1d6"], "movement": 15, "morale": 12,
                    "special": ["Abrazo 2d8", "Inmune: frío", "Mirada paraliza"],
                    "immunities": ["frío"],
                    "xp": 420
                },
                
                # === CRIATURAS SUBTERRÁNEAS ===
                "Bulette": {
                    "type": "Monstruoso", "environment": "Subterráneo/Planicies",
                    "ac": -2, "hd": "9d8+9", "hp": 49, "thac0": 12,
                    "attacks": ["4d12"], "movement": 15, "morale": 13,
                    "special": ["Salto 6'", "Cava 9", "Detección vibración", "Armadura placas"],
                    "xp": 4000
                },
                "Hook Horror": {
                    "type": "Monstruoso", "environment": "Subterráneo",
                    "ac": 3, "hd": "5d8", "hp": 22, "thac0": 15,
                    "attacks": ["1d8", "1d8"], "movement": 9, "morale": 11,
                    "special": ["Ecolocación", "Inmune: sonido"],
                    "immunities": ["sonido"],
                    "xp": 420
                },
                "Carrion Crawler": {
                    "type": "Vermin", "environment": "Subterráneo",
                    "ac": 3, "hd": "3d8+1", "hp": 15, "thac0": 17,
                    "attacks": ["8x parálisis"], "movement": 12, "morale": 10,
                    "special": ["Tentáculos paralizantes (salvación)", "Trepar paredes"],
                    "xp": 270
                },
                
                # === BESTIAS MÍTICAS ===
                "Unicornio": {
                    "type": "Monstruoso", "environment": "Bosque Virgen",
                    "ac": 2, "hd": "4d8+4", "hp": 22, "thac0": 17,
                    "attacks": ["1d8", "1d8", "1d12"], "movement": 24, "morale": 14,
                    "special": ["Cuerno mágico", "Teleport 360'/día", "Detectar bien/mal", "Curar enfermedad"],
                    "xp": 975
                },
                "Nightmare": {
                    "type": "Planar", "environment": "Planos Inferiores",
                    "ac": -4, "hd": "6d8+6", "hp": 33, "thac0": 15,
                    "attacks": ["2d4", "2d4"], "movement": 15, "morale": 14,
                    "special": ["Llamas 1d8", "Vuela 36", "Plano Astral", "Montable (malvados)"],
                    "immunities": ["fuego"],
                    "xp": 1400
                },
                "Couatl": {
                    "type": "Planar", "environment": "Selva/Templos",
                    "ac": 5, "hd": "9d8", "hp": 40, "thac0": 12,
                    "attacks": ["1d3", "2d4"], "movement": 6, "morale": 16,
                    "special": ["Mordida veneno (salvación)", "Magia nivel 5", "Vuela 18", "Forma etérea"],
                    "xp": 3000
                },
                "Lammasu": {
                    "type": "Planar", "environment": "Desierto/Templos",
                    "type": "Monstruoso", "environment": "Desierto/Ruinas",
                    "ac": 6, "hd": "7d8+3", "hp": 34, "thac0": 13,
                    "attacks": ["1d6", "1d6"], "movement": 12, "morale": 15,
                    "special": ["Magia nivel 6", "Vuela 24", "Dimensión Door 1/día"],
                    "xp": 2000
                },
                
                # === CRIATURAS FUERTES (HD 10+) ===
                "Tarrasque": {
                    "type": "Monstruoso", "environment": "Profundidades",
                    "ac": -3, "hd": "30d8+30", "hp": 165, "thac0": -5,
                    "attacks": ["1d12", "1d12", "2d8", "2d8", "2d10", "4d6"], "movement": 9, "morale": 20,
                    "special": ["Regenera 1 HP/round", "Reflejar rayos", "Traga entero", "Inmune: fuego, veneno"],
                    "immunities": ["fuego", "veneno", "armas +3 o menos"],
                    "xp": 50000
                },
                "Balor": {
                    "type": "Demonio", "environment": "Abismo",
                    "ac": -2, "hd": "13d8+13", "hp": 71, "thac0": 8,
                    "attacks": ["1d12+1", "3d6"], "movement": 15, "morale": 18,
                    "special": ["Espada +1", "Látigo decapita", "Llamas aura 2d6", "Magia", "Vuela 15"],
                    "immunities": ["fuego", "gas", "electricidad", "veneno"],
                    "xp": 20000
                },
                "Pit Fiend": {
                    "type": "Diablo", "environment": "Nueve Infiernos",
                    "ac": -3, "hd": "13d8+13", "hp": 71, "thac0": 8,
                    "attacks": ["2d4", "2d4"], "movement": 15, "morale": 18,
                    "special": ["Regenera 2 HP/round", "Aura miedo", "Magia", "+2 o mejor", "Vuela 15"],
                    "immunities": ["fuego", "veneno"],
                    "xp": 20000
                }
            }
    
    def get_monster(self, name: str) -> Optional[Monster]:
        """Obtiene un monstruo por nombre"""
        if name in self.monsters:
            return Monster(name, self.monsters[name].copy())
        return None
    
    def list_monsters(self, sort_by: str = "name") -> List[str]:
        """Lista todos los monstruos disponibles
        
        Args:
            sort_by: 'name', 'hd', 'xp', 'ac'
        """
        if sort_by == "name":
            return sorted(self.monsters.keys())
        elif sort_by == "hd":
            return sorted(self.monsters.keys(), 
                         key=lambda x: int(self.monsters[x].get('hd', '1d8').split('d')[0]))
        elif sort_by == "xp":
            return sorted(self.monsters.keys(), 
                         key=lambda x: self.monsters[x].get('xp', 0), reverse=True)
        elif sort_by == "ac":
            return sorted(self.monsters.keys(), 
                         key=lambda x: self.monsters[x].get('ac', 10))
        return sorted(self.monsters.keys())
    
    def search_monsters(self, query: str) -> Dict[str, dict]:
        """Busca monstruos por nombre (búsqueda parcial)
        Retorna diccionario {nombre: datos}
        """
        query = query.lower()
        results = {}
        for name, data in self.monsters.items():
            if query in name.lower():
                results[name] = data
        return results
    
    def filter_by_challenge(self, level: str) -> List[str]:
        """Filtra por nivel de desafío
        
        Args:
            level: 'Muy Fácil', 'Fácil', 'Medio', 'Difícil', 'Muy Difícil'
        """
        return sorted(self.by_challenge.get(level, []))
    
    def filter_by_type(self, creature_type: str) -> List[str]:
        """Filtra por tipo de criatura"""
        return sorted(self.by_type.get(creature_type, []))
    
    def filter_by_environment(self, environment: str) -> List[str]:
        """Filtra por ambiente"""
        return sorted(self.by_environment.get(environment, []))
    
    def filter_by_hd_range(self, min_hd: int, max_hd: int) -> List[str]:
        """Filtra por rango de HD"""
        results = []
        for name, data in self.monsters.items():
            hd_str = data.get('hd', '1d8')
            hd_num = int(hd_str.split('d')[0]) if 'd' in hd_str else 1
            if min_hd <= hd_num <= max_hd:
                results.append(name)
        return sorted(results)
    
    def get_types(self) -> List[str]:
        """Obtiene lista de todos los tipos de criaturas"""
        return sorted(self.by_type.keys())
    
    def get_environments(self) -> List[str]:
        """Obtiene lista de todos los ambientes"""
        return sorted(self.by_environment.keys())
    
    def get_challenges(self) -> List[str]:
        """Obtiene lista de niveles de desafío"""
        return ["Muy Fácil", "Fácil", "Medio", "Difícil", "Muy Difícil"]
    
    def get_monster_details(self, name: str) -> Optional[dict]:
        """Obtiene detalles completos de un monstruo"""
        return self.monsters.get(name)
    
    def print_monster_card(self, name: str):
        """Imprime ficha detallada de monstruo"""
        monster = self.monsters.get(name)
        if not monster:
            print(f"❌ Monstruo '{name}' no encontrado")
            return
        
        print(f"\n{'='*60}")
        print(f"🐉 {name.upper()}")
        print(f"{'='*60}")
        print(f"Tipo: {monster.get('type', 'Desconocido')}")
        print(f"Ambiente: {monster.get('environment', 'Variado')}")
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  Clase de Armadura: {monster.get('ac', 10)}")
        print(f"  Dados de Golpe: {monster.get('hd', '1d8')}")
        print(f"  Puntos de Golpe: {monster.get('hp', 0)} (promedio)")
        print(f"  THAC0: {monster.get('thac0', 20)}")
        print(f"  Movimiento: {monster.get('movement', 12)}")
        print(f"  Moral: {monster.get('morale', 10)}")
        print(f"\n⚔️ ATAQUES:")
        attacks = monster.get('attacks', [])
        for i, atk in enumerate(attacks, 1):
            print(f"  Ataque {i}: {atk} de daño")
        print(f"\n✨ HABILIDADES ESPECIALES:")
        for special in monster.get('special', []):
            print(f"  • {special}")
        if monster.get('immunities'):
            print(f"\n🛡️ INMUNIDADES:")
            for imm in monster['immunities']:
                print(f"  • {imm.capitalize()}")
        print(f"\n💰 Valor en XP: {monster.get('xp', 0)}")
        print(f"{'='*60}\n")
    
    def random_encounter(self, challenge: str = None, environment: str = None) -> Optional[str]:
        """Genera un encuentro aleatorio
        
        Args:
            challenge: Nivel de desafío opcional
            environment: Ambiente opcional
        """
        candidates = list(self.monsters.keys())
        
        if challenge:
            candidates = [m for m in candidates if m in self.by_challenge.get(challenge, [])]
        
        if environment:
            candidates = [m for m in candidates if m in self.by_environment.get(environment, [])]
        
        if not candidates:
            return None
        
        return random.choice(candidates)
    
    def save_custom_monster(self, name: str, data: dict):
        """Guarda un monstruo personalizado"""
        self.monsters[name] = data
        self._build_indices()  # Reconstruir índices
        self._save_to_file()
    
    def _save_to_file(self):
        """Guarda la base de datos a archivo"""
        monsters_file = Path(__file__).parent / "monstruos.json"
        with open(monsters_file, 'w', encoding='utf-8') as f:
            json.dump(self.monsters, f, indent=2, ensure_ascii=False)


class Combatant:
    """Wrapper para participantes de combate (personajes o monstruos)"""
    def __init__(self, entity, is_player: bool = True):
        self.entity = entity
        self.is_player = is_player
        self.initiative = 0
        self.actions_this_round = 0
        self.max_actions = 1
        
        # Estado temporal de combate
        self.temp_ac_bonus = 0
        self.temp_attack_bonus = 0
        self.temp_damage_bonus = 0
        
        # Distancia de combate (en metros)
        self.distance_to_enemies = 1  # 1 = melé, >1 = distancia
        
    @property
    def name(self) -> str:
        if self.is_player:
            return self.entity.get('name', 'Personaje')
        return self.entity.name
    
    @property
    def hp(self) -> int:
        if self.is_player:
            return self.entity.get('hp', {}).get('current', 0)
        return self.entity.hp
    
    @property
    def max_hp(self) -> int:
        if self.is_player:
            return self.entity.get('hp', {}).get('max', 0)
        return self.entity.max_hp
    
    @property
    def ac(self) -> int:
        base_ac = self.entity.get('ac', 10) if self.is_player else self.entity.ac
        return base_ac + self.temp_ac_bonus
    
    @property
    def thac0(self) -> int:
        return self.entity.get('thac0', 20) if self.is_player else self.entity.thac0
    
    @property
    def is_alive(self) -> bool:
        if self.is_player:
            return self.entity.get('hp', {}).get('current', 0) > 0
        return self.entity.is_alive
    
    def take_damage(self, damage: int) -> str:
        if self.is_player:
            current = self.entity['hp']['current']
            current -= damage
            self.entity['hp']['current'] = max(0, current)
            if current <= 0:
                return f"💀 {self.name} ha caído inconsciente!"
            elif current < self.max_hp * 0.25:
                return f"⚠️ {self.name} está gravemente herido ({current}/{self.max_hp} HP)"
            else:
                return f"🩸 {self.name} recibe {damage} de daño ({current}/{self.max_hp} HP)"
        else:
            return self.entity.take_damage(damage)
    
    def heal(self, amount: int) -> str:
        if self.is_player:
            current = self.entity['hp']['current']
            old_hp = current
            current = min(current + amount, self.max_hp)
            self.entity['hp']['current'] = current
            healed = current - old_hp
            return f"💚 {self.name} se cura {healed} HP ({current}/{self.max_hp})"
        else:
            return self.entity.heal(amount)
    
    def __str__(self):
        status = "💀" if not self.is_alive else ("⚠️" if self.hp < self.max_hp / 2 else "💚")
        return f"{status} {self.name} - HP: {self.hp}/{self.max_hp}, AC: {self.ac}, THAC0: {self.thac0}"


class CombatManager:
    """Gestiona un encuentro de combate completo"""
    def __init__(self):
        self.combatants: List[Combatant] = []
        self.round_number = 0
        self.initiative_order: List[Combatant] = []
        self.current_turn_index = 0
        self.dice_roller = DiceRoller()
        self.monster_db = MonsterDatabase()
        self.combat_log: List[str] = []
        self.combat_distance = 1  # Distancia global entre grupos (1=melé, 10=cerca, 30=lejos)
        
    def add_player(self, character_file: str) -> bool:
        """Carga y agrega un personaje al combate"""
        try:
            with open(character_file, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            combatant = Combatant(char_data, is_player=True)
            self.combatants.append(combatant)
            self.log(f"✅ {combatant.name} se une al combate")
            return True
        except Exception as e:
            print(f"❌ Error cargando personaje: {e}")
            return False
    
    def add_monster(self, monster_name: str, custom_name: str = None) -> bool:
        """Agrega un monstruo al combate"""
        monster = self.monster_db.get_monster(monster_name)
        if monster:
            if custom_name:
                monster.name = custom_name
            
            # Tirar HP si es necesario
            if monster.hp == 0:
                hd_roll = self.dice_roller.roll(monster.hd, 0, f"HP de {monster.name}")
                monster.hp = hd_roll['total']
                monster.max_hp = monster.hp
            
            combatant = Combatant(monster, is_player=False)
            self.combatants.append(combatant)
            self.log(f"🐉 {monster.name} entra en combate - HP: {monster.hp}, AC: {monster.ac}")
            return True
        else:
            print(f"❌ Monstruo '{monster_name}' no encontrado")
            return False
    
    def roll_initiative(self):
        """Tira iniciativa para todos los combatientes"""
        self.log("\n" + "="*60)
        self.log("🎲 TIRANDO INICIATIVA")
        self.log("="*60)
        
        for combatant in self.combatants:
            if combatant.is_alive:
                # Tirar 1d10 para iniciativa
                roll = self.dice_roller.roll("1d10", 0, f"Iniciativa de {combatant.name}")
                
                # Bonus por DES para jugadores
                if combatant.is_player:
                    abilities = combatant.entity.get('abilities', combatant.entity.get('attributes', {}))
                    dex = abilities.get('dexterity', abilities.get('DES', 10))
                    dex_bonus = self._get_dex_initiative_bonus(dex)
                    combatant.initiative = roll['total'] + dex_bonus
                    self.log(f"  {combatant.name}: {roll['total']} + {dex_bonus} (DES) = {combatant.initiative}")
                else:
                    combatant.initiative = roll['total']
                    self.log(f"  {combatant.name}: {roll['total']}")
        
        # Ordenar por iniciativa (mayor primero)
        self.initiative_order = sorted(
            [c for c in self.combatants if c.is_alive],
            key=lambda x: x.initiative,
            reverse=True
        )
        
        self.log("\n📋 Orden de iniciativa:")
        for i, combatant in enumerate(self.initiative_order, 1):
            self.log(f"  {i}. {combatant.name} ({combatant.initiative})")
        
        self.current_turn_index = 0
    
    def _get_dex_initiative_bonus(self, dex: int) -> int:
        """Bonus de iniciativa por DES según AD&D 2e"""
        if dex >= 18: return 2
        elif dex >= 16: return 1
        elif dex <= 5: return -2
        elif dex <= 7: return -1
        return 0
    
    def start_combat(self):
        """Inicia el combate"""
        self.roll_initiative()
        self.roll_starting_distance()
        self.round_number = 1
        self.log("\n⚔️ ¡EL COMBATE COMIENZA! ⚔️")
        self.log(f"\n{'='*60}")
        self.log(f"⚔️ ROUND {self.round_number} ⚔️")
        self.log(f"{'='*60}\n")
    
    def roll_starting_distance(self):
        """Determina distancia inicial del combate"""
        self.log("\n📏 DETERMINANDO DISTANCIA INICIAL")
        self.log("="*60)
        
        # Tirar 1d10 para distancia inicial (en metros)
        # 1-3: Melé (1m), 4-7: Cerca (10m), 8-10: Lejos (30m)
        distance_roll = self.dice_roller.roll("1d10", 0, "Distancia inicial")
        roll_value = distance_roll['total']
        
        if roll_value <= 3:
            self.combat_distance = 1
            distance_desc = "MELÉ"
        elif roll_value <= 7:
            self.combat_distance = 10
            distance_desc = "CERCA (10m)"
        else:
            self.combat_distance = 30
            distance_desc = "LEJOS (30m)"
        
        self.log(f"  Tirada: {roll_value} → {distance_desc}")
        self.log(f"  Los combatientes comienzan a {distance_desc}")
    
    def move_combatant(self, combatant: Combatant, action: str) -> str:
        """Mueve un combatante (acercarse/alejarse)
        La distancia es global entre los dos grupos
        
        Args:
            action: 'approach' (acercarse) o 'retreat' (retroceder)
        """
        if action == 'approach':
            if self.combat_distance <= 1:
                return f"⚠️ Los combatientes ya están en melé"
            
            # Acercarse: reducir distancia global
            old_distance = self.combat_distance
            if self.combat_distance >= 30:
                self.combat_distance = 10
            elif self.combat_distance >= 10:
                self.combat_distance = 1
            else:
                self.combat_distance = 1
            
            new_distance = self.combat_distance
            return f"🏃 {combatant.name} se acerca → Distancia de combate: {old_distance}m → {new_distance}m"
        
        elif action == 'retreat':
            # Retroceder: aumentar distancia global
            old_distance = self.combat_distance
            if self.combat_distance <= 1:
                self.combat_distance = 10
            elif self.combat_distance <= 10:
                self.combat_distance = 30
            else:
                return f"⚠️ Los combatientes ya están lo más lejos posible (30m)"
            
            new_distance = self.combat_distance
            return f"🏃 {combatant.name} retrocede → Distancia de combate: {old_distance}m → {new_distance}m"
        
        return f"❌ Acción de movimiento inválida"
    
    def next_round(self):
        """Avanza al siguiente round"""
        self.round_number += 1
        self.current_turn_index = 0
        
        # Regeneración y efectos de inicio de round
        for combatant in self.combatants:
            if not combatant.is_player and combatant.is_alive:
                if hasattr(combatant.entity, 'special_abilities'):
                    for ability in combatant.entity.special_abilities:
                        if 'Regeneración' in ability:
                            # Extraer cantidad de regeneración
                            import re
                            match = re.search(r'(\d+)\s*HP', ability)
                            if match:
                                regen = int(match.group(1))
                                msg = combatant.heal(regen)
                                self.log(f"  🔄 {msg}")
        
        self.log(f"\n{'='*60}")
        self.log(f"⚔️ ROUND {self.round_number} ⚔️")
        self.log(f"{'='*60}\n")
        
        # Re-tirar iniciativa cada round (regla opcional, puede cambiarse)
        # self.roll_initiative()
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Obtiene el combatiente actual"""
        if self.current_turn_index < len(self.initiative_order):
            return self.initiative_order[self.current_turn_index]
        return None
    
    def next_turn(self):
        """Avanza al siguiente turno"""
        self.current_turn_index += 1
        if self.current_turn_index >= len(self.initiative_order):
            self.next_round()
    
    def make_attack(self, attacker: Combatant, defender: Combatant, weapon_index: int = 0) -> dict:
        """Realiza un ataque"""
        result = {
            'hit': False,
            'damage': 0,
            'critical': False,
            'fumble': False,
            'message': '',
            'cannot_attack': False
        }
        
        # Verificar distancia y arma
        if attacker.is_player:
            equipped = attacker.entity.get('equipped', {})
            weapon_name = equipped.get('arma_principal', None)
            
            if weapon_name:
                equipment = attacker.entity.get('equipment', {})
                weapon = equipment.get(weapon_name, {})
                weapon_type = weapon.get('type', 'weapon')
                
                # Verificar si el arma es de melé o distancia
                is_ranged = weapon_type in ['bow', 'crossbow', 'ranged'] or 'arco' in weapon_name.lower()
                
                if self.combat_distance > 1 and not is_ranged:
                    result['cannot_attack'] = True
                    result['message'] = f"❌ {attacker.name} no puede atacar en melé a {self.combat_distance}m de distancia"
                    result['message'] += f"\n   💡 Usa /combat move approach para acercarte"
                    return result
                elif self.combat_distance <= 1 and is_ranged:
                    result['message'] = f"⚠️ {attacker.name} usa arma a distancia en melé (penalización -4)"
            else:
                # Sin arma equipada
                if self.combat_distance > 1:
                    result['cannot_attack'] = True
                    result['message'] = f"❌ {attacker.name} no puede atacar desarmado a {self.combat_distance}m"
                    result['message'] += f"\n   💡 Usa /combat move approach para acercarte"
                    return result
        else:
            # Monstruos - la mayoría son melé
            # TODO: Agregar soporte para monstruos con ataques a distancia
            if self.combat_distance > 1:
                result['cannot_attack'] = True
                result['message'] = f"❌ {attacker.name} no puede atacar a {self.combat_distance}m (ataque melé)"
                result['message'] += f"\n   💡 El monstruo debe acercarse"
                return result
        
        # Tirada de ataque (1d20)
        attack_roll = self.dice_roller.roll("1d20", 0, f"Ataque de {attacker.name}")
        d20_roll = attack_roll['rolls'][0]
        
        # Crítico automático (20 natural)
        if d20_roll == 20:
            result['critical'] = True
            result['hit'] = True
            result['message'] += f"\n🎯 ¡CRÍTICO! {attacker.name} acierta automáticamente" if result['message'] else f"🎯 ¡CRÍTICO! {attacker.name} acierta automáticamente"
        # Pifia automática (1 natural)
        elif d20_roll == 1:
            result['fumble'] = True
            result['message'] = f"💥 ¡PIFIA! {attacker.name} falla completamente"
            return result
        else:
            # Calcular si impacta: THAC0 - tirada >= AC objetivo
            needed_roll = attacker.thac0 - defender.ac
            result['hit'] = d20_roll >= needed_roll
            
            if result['hit']:
                result['message'] = f"✅ {attacker.name} impacta a {defender.name} (tiró {d20_roll}, necesitaba {needed_roll})"
            else:
                result['message'] = f"❌ {attacker.name} falla el ataque a {defender.name} (tiró {d20_roll}, necesitaba {needed_roll})"
                return result
        
        # Si impactó, tirar daño
        if result['hit']:
            if attacker.is_player:
                # Buscar arma equipada
                equipped = attacker.entity.get('equipped', {})
                weapon_name = equipped.get('arma_principal', None)
                
                if weapon_name:
                    equipment = attacker.entity.get('equipment', {})
                    weapon = equipment.get(weapon_name, {})
                    damage_dice = weapon.get('damage', '1d4')
                else:
                    damage_dice = '1d2'  # Ataque desarmado
                
                # Bonus de FUE (abilities o attributes)
                abilities = attacker.entity.get('abilities', attacker.entity.get('attributes', {}))
                str_val = abilities.get('strength', abilities.get('FUE', 10))
                str_bonus = self._get_str_damage_bonus(str_val)
                
                damage_roll = self.dice_roller.roll(damage_dice, str_bonus, f"Daño de {attacker.name}")
                result['damage'] = max(1, damage_roll['total'])  # Mínimo 1 de daño
                
                result['message'] += f"\n  💥 Causa {result['damage']} de daño"
            else:
                # Monstruo
                if weapon_index < len(attacker.entity.attacks):
                    damage_dice = attacker.entity.attacks[weapon_index]
                    damage_roll = self.dice_roller.roll(damage_dice, 0, f"Daño de {attacker.name}")
                    result['damage'] = damage_roll['total']
                    result['message'] += f"\n  💥 Causa {result['damage']} de daño"
            
            # Doble daño en crítico
            if result['critical']:
                result['damage'] *= 2
                result['message'] += f" (x2 por crítico = {result['damage']})"
            
            # Aplicar daño
            damage_msg = defender.take_damage(result['damage'])
            result['message'] += f"\n  {damage_msg}"
        
        return result
    
    def _get_str_damage_bonus(self, strength: int) -> int:
        """Bonus de daño por FUE según AD&D 2e"""
        if strength >= 18: return 2
        elif strength >= 16: return 1
        elif strength <= 5: return -2
        elif strength <= 7: return -1
        return 0
    
    def make_saving_throw(self, combatant: Combatant, save_type: str) -> dict:
        """Realiza una tirada de salvación"""
        result = {
            'success': False,
            'roll': 0,
            'needed': 20,
            'message': ''
        }
        
        # Obtener valor de salvación
        if combatant.is_player:
            saves = combatant.entity.get('saving_throws', {})
            needed = saves.get(save_type, 20)
        else:
            saves = combatant.entity.saves
            needed = saves.get(save_type, 20)
        
        # Tirar 1d20
        roll = self.dice_roller.roll("1d20", 0, f"Salvación de {combatant.name}")
        d20_roll = roll['total']
        
        result['roll'] = d20_roll
        result['needed'] = needed
        result['success'] = d20_roll >= needed
        
        if result['success']:
            result['message'] = f"✅ {combatant.name} supera la salvación (tiró {d20_roll}, necesitaba {needed})"
        else:
            result['message'] = f"❌ {combatant.name} falla la salvación (tiró {d20_roll}, necesitaba {needed})"
        
        return result
    
    def check_combat_end(self) -> Optional[str]:
        """Verifica si el combate ha terminado"""
        players_alive = any(c.is_alive for c in self.combatants if c.is_player)
        monsters_alive = any(c.is_alive for c in self.combatants if not c.is_player)
        
        if not players_alive:
            return "💀 Todos los personajes han caído. DERROTA"
        elif not monsters_alive:
            return "🎉 Todos los enemigos han sido derrotados. ¡VICTORIA!"
        
        return None
    
    def show_combat_status(self):
        """Muestra el estado actual del combate"""
        print(f"\n{'='*60}")
        print(f"⚔️ ESTADO DEL COMBATE - Round {self.round_number} ⚔️")
        print(f"{'='*60}")
        
        # Mostrar distancia global
        distance_str = "MELÉ" if self.combat_distance <= 1 else f"{self.combat_distance}m"
        print(f"\n📏 Distancia de combate: {distance_str}\n")
        
        print("👥 PERSONAJES:")
        for c in self.combatants:
            if c.is_player:
                print(f"  {c}")
        
        print("\n🐉 ENEMIGOS:")
        for c in self.combatants:
            if not c.is_player:
                print(f"  {c}")
        
        print(f"\n{'='*60}\n")
    
    def log(self, message: str):
        """Agrega mensaje al log de combate"""
        self.combat_log.append(message)
        print(message)
    
    def save_combat_log(self, filename: str = "combat_log.txt"):
        """Guarda el log de combate a archivo"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.combat_log))
        print(f"📝 Log guardado en {filename}")


def main():
    """Menú principal del sistema de combate"""
    combat = CombatManager()
    
    while True:
        print("\n" + "="*60)
        print("⚔️  SISTEMA DE COMBATE AD&D 2e  ⚔️")
        print("="*60)
        print("\n📋 CONFIGURACIÓN DEL ENCUENTRO:")
        print("  [1] Cargar personaje")
        print("  [2] Agregar monstruo (búsqueda manual)")
        print("  [3] Buscar monstruo (nombre, tipo, ambiente, HD)")
        print("  [4] Ver detalles de monstruo")
        print("  [5] Encuentro aleatorio")
        print("  [6] Listar combatientes actuales")
        print("\n⚔️ COMBATE:")
        print("  [7] Iniciar combate")
        print("  [8] Turno automático (IA controla monstruos)")
        print("  [9] Turno manual (controlar cada acción)")
        print("  [10] Ver estado del combate")
        print("\n📊 UTILIDADES:")
        print("  [11] Guardar log de combate")
        print("  [12] Reiniciar combate")
        print("  [0] Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == '0':
            print("¡Hasta luego!")
            break
        
        elif choice == '1':
            # Cargar personaje
            char_file = input("Nombre del archivo de personaje (ej: personaje.json): ").strip()
            if not char_file.endswith('.json'):
                char_file += '.json'
            combat.add_player(char_file)
        
        elif choice == '2':
            # Agregar monstruo manualmente
            monster_name = input("Nombre del monstruo: ").strip()
            custom_name = input("Nombre personalizado (Enter para usar el original): ").strip()
            combat.add_monster(monster_name, custom_name if custom_name else None)
        
        elif choice == '3':
            # Búsqueda avanzada de monstruos
            print("\n🔍 BÚSQUEDA DE MONSTRUOS:")
            print("  [1] Por nombre")
            print("  [2] Por tipo de criatura")
            print("  [3] Por ambiente")
            print("  [4] Por nivel de desafío")
            print("  [5] Por rango de HD")
            print("  [6] Listar todos")
            
            search_choice = input("Tipo de búsqueda: ").strip()
            
            if search_choice == '1':
                query = input("Buscar por nombre: ").strip()
                results = combat.monster_db.search_monsters(query)
                if results:
                    print(f"\n📋 Encontrados {len(results)} monstruos:")
                    for i, name in enumerate(results, 1):
                        data = combat.monster_db.monsters[name]
                        print(f"  {i}. {name} - HD: {data['hd']}, AC: {data['ac']}, XP: {data['xp']}")
                else:
                    print("❌ No se encontraron monstruos")
            
            elif search_choice == '2':
                types = combat.monster_db.get_types()
                print("\n📋 Tipos disponibles:")
                for i, t in enumerate(types, 1):
                    print(f"  {i}. {t}")
                try:
                    type_idx = int(input("Selecciona tipo (número): ").strip()) - 1
                    if 0 <= type_idx < len(types):
                        results = combat.monster_db.filter_by_type(types[type_idx])
                        print(f"\n🐉 Monstruos tipo '{types[type_idx]}':")
                        for i, name in enumerate(results, 1):
                            data = combat.monster_db.monsters[name]
                            print(f"  {i}. {name} - HD: {data['hd']}, AC: {data['ac']}")
                except ValueError:
                    print("❌ Entrada inválida")
            
            elif search_choice == '3':
                environments = combat.monster_db.get_environments()
                print("\n📋 Ambientes disponibles:")
                for i, env in enumerate(environments, 1):
                    print(f"  {i}. {env}")
                try:
                    env_idx = int(input("Selecciona ambiente (número): ").strip()) - 1
                    if 0 <= env_idx < len(environments):
                        results = combat.monster_db.filter_by_environment(environments[env_idx])
                        print(f"\n🌍 Monstruos de '{environments[env_idx]}':")
                        for i, name in enumerate(results, 1):
                            data = combat.monster_db.monsters[name]
                            print(f"  {i}. {name} - HD: {data['hd']}, AC: {data['ac']}")
                except ValueError:
                    print("❌ Entrada inválida")
            
            elif search_choice == '4':
                challenges = combat.monster_db.get_challenges()
                print("\n📋 Niveles de desafío:")
                for i, ch in enumerate(challenges, 1):
                    print(f"  {i}. {ch}")
                try:
                    ch_idx = int(input("Selecciona nivel (número): ").strip()) - 1
                    if 0 <= ch_idx < len(challenges):
                        results = combat.monster_db.filter_by_challenge(challenges[ch_idx])
                        print(f"\n⚔️ Monstruos de dificultad '{challenges[ch_idx]}':")
                        for i, name in enumerate(results, 1):
                            data = combat.monster_db.monsters[name]
                            print(f"  {i}. {name} - HD: {data['hd']}, AC: {data['ac']}, XP: {data['xp']}")
                except ValueError:
                    print("❌ Entrada inválida")
            
            elif search_choice == '5':
                try:
                    min_hd = int(input("HD mínimo: ").strip())
                    max_hd = int(input("HD máximo: ").strip())
                    results = combat.monster_db.filter_by_hd_range(min_hd, max_hd)
                    print(f"\n📊 Monstruos con {min_hd}-{max_hd} HD:")
                    for i, name in enumerate(results, 1):
                        data = combat.monster_db.monsters[name]
                        print(f"  {i}. {name} - HD: {data['hd']}, AC: {data['ac']}, XP: {data['xp']}")
                except ValueError:
                    print("❌ Entrada inválida")
            
            elif search_choice == '6':
                print("\n📋 TODOS LOS MONSTRUOS:")
                for i, name in enumerate(combat.monster_db.list_monsters(), 1):
                    data = combat.monster_db.monsters[name]
                    print(f"  {i}. {name} - HD: {data['hd']}, AC: {data['ac']}, Tipo: {data.get('type', 'N/A')}")
        
        elif choice == '4':
            # Ver detalles de monstruo
            monster_name = input("Nombre del monstruo: ").strip()
            combat.monster_db.print_monster_card(monster_name)
        
        elif choice == '5':
            # Encuentro aleatorio
            print("\n🎲 ENCUENTRO ALEATORIO:")
            print("  [1] Totalmente aleatorio")
            print("  [2] Por nivel de desafío")
            print("  [3] Por ambiente")
            
            rand_choice = input("Tipo: ").strip()
            
            monster_name = None
            if rand_choice == '1':
                monster_name = combat.monster_db.random_encounter()
            elif rand_choice == '2':
                challenges = combat.monster_db.get_challenges()
                print("\nNiveles:")
                for i, ch in enumerate(challenges, 1):
                    print(f"  {i}. {ch}")
                try:
                    ch_idx = int(input("Nivel: ").strip()) - 1
                    if 0 <= ch_idx < len(challenges):
                        monster_name = combat.monster_db.random_encounter(challenge=challenges[ch_idx])
                except ValueError:
                    pass
            elif rand_choice == '3':
                environments = combat.monster_db.get_environments()
                print("\nAmbientes:")
                for i, env in enumerate(environments, 1):
                    print(f"  {i}. {env}")
                try:
                    env_idx = int(input("Ambiente: ").strip()) - 1
                    if 0 <= env_idx < len(environments):
                        monster_name = combat.monster_db.random_encounter(environment=environments[env_idx])
                except ValueError:
                    pass
            
            if monster_name:
                print(f"\n🎲 ¡Encuentro con {monster_name}!")
                combat.monster_db.print_monster_card(monster_name)
                add = input("¿Agregar al combate? (s/n): ").strip().lower()
                if add == 's':
                    custom_name = input("Nombre personalizado (Enter para original): ").strip()
                    combat.add_monster(monster_name, custom_name if custom_name else None)
        
        elif choice == '6':
            # Listar combatientes
            if not combat.combatants:
                print("\n⚠️ No hay combatientes en el encuentro")
            else:
                print("\n👥 COMBATIENTES:")
                for i, c in enumerate(combat.combatants, 1):
                    team = "JUGADOR" if c.is_player else "ENEMIGO"
                    print(f"  {i}. [{team}] {c}")
        
        elif choice == '7':
            # Iniciar combate
            if len(combat.combatants) < 2:
                print("\n⚠️ Se necesitan al menos 2 combatientes")
            else:
                combat.start_combat()
        
        elif choice == '8':
            # Turno automático
            if combat.round_number == 0:
                print("\n⚠️ Primero debes iniciar el combate (opción 7)")
                continue
            
            # Verificar si el combate terminó
            end_msg = combat.check_combat_end()
            if end_msg:
                combat.log(f"\n{end_msg}")
                continue
            
            current = combat.get_current_combatant()
            if not current:
                combat.next_round()
                current = combat.get_current_combatant()
            
            if current:
                combat.log(f"\n🎯 Turno de {current.name}")
                
                if current.is_player:
                    # Jugador - mostrar opciones
                    print("\nAcciones disponibles:")
                    print("  [1] Atacar")
                    print("  [2] Lanzar conjuro")
                    print("  [3] Usar objeto")
                    print("  [4] Defender")
                    print("  [5] Huir")
                    
                    action = input("Acción: ").strip()
                    
                    if action == '1':
                        # Atacar
                        enemies = [c for c in combat.combatants if not c.is_player and c.is_alive]
                        if not enemies:
                            print("No hay enemigos vivos")
                        else:
                            print("\nObjetivos:")
                            for i, e in enumerate(enemies, 1):
                                print(f"  {i}. {e}")
                            
                            target_idx = int(input("Atacar a (número): ").strip()) - 1
                            if 0 <= target_idx < len(enemies):
                                result = combat.make_attack(current, enemies[target_idx])
                                combat.log(result['message'])
                else:
                    # Monstruo - IA simple
                    players = [c for c in combat.combatants if c.is_player and c.is_alive]
                    if players:
                        # Atacar al jugador con menos HP
                        target = min(players, key=lambda x: x.hp)
                        
                        # Si tiene múltiples ataques
                        num_attacks = len(current.entity.attacks) if hasattr(current.entity, 'attacks') else 1
                        for i in range(num_attacks):
                            if target.is_alive:
                                result = combat.make_attack(current, target, i)
                                combat.log(result['message'])
                
                combat.next_turn()
        
        elif choice == '9':
            # Turno manual completo
            if combat.round_number == 0:
                print("\n⚠️ Primero debes iniciar el combate (opción 7)")
                continue
            
            end_msg = combat.check_combat_end()
            if end_msg:
                combat.log(f"\n{end_msg}")
                continue
            
            current = combat.get_current_combatant()
            if not current:
                combat.next_round()
                current = combat.get_current_combatant()
            
            if current:
                combat.log(f"\n🎯 Turno de {current.name}")
                combat.show_combat_status()
                
                print("\nAcciones:")
                print("  [1] Atacar")
                print("  [2] Tirada de salvación")
                print("  [3] Curar")
                print("  [4] Pasar turno")
                
                action = input("Acción: ").strip()
                
                if action == '1':
                    # Seleccionar objetivo
                    valid_targets = [c for c in combat.combatants if c != current and c.is_alive]
                    print("\nObjetivos:")
                    for i, t in enumerate(valid_targets, 1):
                        print(f"  {i}. {t}")
                    
                    try:
                        target_idx = int(input("Atacar a (número): ").strip()) - 1
                        if 0 <= target_idx < len(valid_targets):
                            result = combat.make_attack(current, valid_targets[target_idx])
                            combat.log(result['message'])
                    except ValueError:
                        print("❌ Entrada inválida")
                
                elif action == '2':
                    save_types = [
                        "Paralización, Veneno o Muerte por Magia",
                        "Varita Mágica",
                        "Petrificación o Transformación",
                        "Soplo de Dragón",
                        "Conjuro, Bastón o Vara"
                    ]
                    print("\nTipos de salvación:")
                    for i, st in enumerate(save_types, 1):
                        print(f"  {i}. {st}")
                    
                    try:
                        save_idx = int(input("Tipo (número): ").strip()) - 1
                        if 0 <= save_idx < len(save_types):
                            result = combat.make_saving_throw(current, save_types[save_idx])
                            combat.log(result['message'])
                    except ValueError:
                        print("❌ Entrada inválida")
                
                elif action == '3':
                    try:
                        amount = int(input("Cantidad de curación: ").strip())
                        msg = current.heal(amount)
                        combat.log(msg)
                    except ValueError:
                        print("❌ Cantidad inválida")
                
                combat.next_turn()
        
        elif choice == '10':
            # Ver estado
            combat.show_combat_status()
        
        elif choice == '11':
            # Guardar log
            filename = input("Nombre del archivo (Enter para 'combat_log.txt'): ").strip()
            if not filename:
                filename = "combat_log.txt"
            combat.save_combat_log(filename)
        
        elif choice == '12':
            # Reiniciar
            confirm = input("¿Reiniciar combate? (s/n): ").strip().lower()
            if confirm == 's':
                combat = CombatManager()
                print("✅ Combate reiniciado")


if __name__ == "__main__":
    main()
