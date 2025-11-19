# Base de datos completa de hechizos de AD&D 2E
# Este archivo contiene todos los hechizos de Mago y Clérigo niveles 1-9

WIZARD_SPELLS = {
    # NIVEL 1
    'Afectar Fuegos Normales': {'nivel': 1, 'escuela': 'Alteración', 'alcance': '5 yardas/nivel', 'descripcion': 'Controla fuegos no-mágicos'},
    'Alarma': {'nivel': 1, 'escuela': 'Abjuración/Evocación', 'alcance': '10 yardas', 'descripcion': 'Alarma mental contra intrusos'},
    'Armadura': {'nivel': 1, 'escuela': 'Conjuración', 'alcance': 'Toque', 'descripcion': 'Otorga CA 6'},
    'Caída de Pluma': {'nivel': 1, 'escuela': 'Alteración', 'alcance': '10 yardas/nivel', 'descripcion': 'Los objetos caen lentamente'},
    'Comprensión de Lenguajes': {'nivel': 1, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Comprende lenguajes escritos y hablados'},
    'Detectar Magia': {'nivel': 1, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Detecta objetos y auras mágicas'},
    'Detectar No-muertos': {'nivel': 1, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Detecta muertos vivientes cercanos'},
    'Disco Flotante de Tenser': {'nivel': 1, 'escuela': 'Evocación', 'alcance': '20 yardas', 'descripcion': 'Disco que transporta 100 lb/nivel'},
    'Dormir': {'nivel': 1, 'escuela': 'Encantamiento', 'alcance': '30 yardas', 'descripcion': 'Causa sueño mágico (2d4 DG)'},
    'Encantar Persona': {'nivel': 1, 'escuela': 'Encantamiento', 'alcance': '120 yardas', 'descripcion': 'Encanta a una persona'},
    'Escudo': {'nivel': 1, 'escuela': 'Evocación', 'alcance': '0', 'descripcion': 'Protección invisible, bloquea proyectiles mágicos'},
    'Identificar': {'nivel': 1, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Identifica propiedades mágicas'},
    'Lectura de Magia': {'nivel': 1, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Lee escrituras mágicas'},
    'Luz': {'nivel': 1, 'escuela': 'Alteración', 'alcance': '60 yardas', 'descripcion': 'Crea iluminación'},
    'Manos Ardientes': {'nivel': 1, 'escuela': 'Evocación', 'alcance': '0', 'descripcion': 'Abanico de fuego (1d3+2/nivel)'},
    'Mensajero Animal': {'nivel': 1, 'escuela': 'Encantamiento', 'alcance': '10 yardas', 'descripcion': 'Envía un animal con mensaje'},
    'Protección contra el Mal': {'nivel': 1, 'escuela': 'Abjuración', 'alcance': 'Toque', 'descripcion': 'Barrera contra criaturas malignas'},
    'Proyectil Mágico': {'nivel': 1, 'escuela': 'Evocación', 'alcance': '160 yardas', 'descripcion': '1 a 5 proyectiles, 1d4+1 cada uno'},
    'Rociado de Color': {'nivel': 1, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Ciega/aturde criaturas en cono'},
    'Salto': {'nivel': 1, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Salta 30 pies verticalmente'},
    
    # NIVEL 2
    'Abrir/Cerrar': {'nivel': 2, 'escuela': 'Alteración', 'alcance': '60 yardas', 'descripcion': 'Abre o cierra puertas'},
    'Ceguera': {'nivel': 2, 'escuela': 'Ilusión', 'alcance': '30 yardas + 10/nivel', 'descripcion': 'Ciega a una criatura'},
    'Continuo de Nystul': {'nivel': 2, 'escuela': 'Ilusión', 'alcance': '60 yardas', 'descripcion': 'Ilusión de sonido continuo'},
    'Dardo Ácido de Melf': {'nivel': 2, 'escuela': 'Conjuración', 'alcance': '180 yardas', 'descripcion': 'Crea dardos de ácido'},
    'Detectar Bien/Mal': {'nivel': 2, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Detecta alineamiento'},
    'Detectar Invisibilidad': {'nivel': 2, 'escuela': 'Adivinación', 'alcance': '10 yardas/nivel', 'descripcion': 'Ve criaturas invisibles'},
    'Esfera Flamígera': {'nivel': 2, 'escuela': 'Evocación', 'alcance': '10 yardas/nivel', 'descripcion': 'Esfera de fuego (2d6)'},
    'ESP': {'nivel': 2, 'escuela': 'Adivinación', 'alcance': '90 yardas', 'descripcion': 'Detecta pensamientos'},
    'Flecha Ácida': {'nivel': 2, 'escuela': 'Conjuración', 'alcance': '180 yardas', 'descripcion': '2d4 ácido + 2d4 siguiente ronda'},
    'Fuerza': {'nivel': 2, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Aumenta FUE temporalmente'},
    'Invisibilidad': {'nivel': 2, 'escuela': 'Ilusión', 'alcance': 'Toque', 'descripcion': 'Criatura invisible hasta atacar'},
    'Levitar': {'nivel': 2, 'escuela': 'Alteración', 'alcance': '20 yardas/nivel', 'descripcion': 'Levita verticalmente'},
    'Localizar Objeto': {'nivel': 2, 'escuela': 'Adivinación', 'alcance': '60 yardas + 10/nivel', 'descripcion': 'Localiza objeto conocido'},
    'Nube Hedionda': {'nivel': 2, 'escuela': 'Evocación', 'alcance': '30 yardas', 'descripcion': 'Nube venenosa nauseabunda'},
    'Oscuridad Radio 15 pies': {'nivel': 2, 'escuela': 'Alteración', 'alcance': '10 yardas/nivel', 'descripcion': 'Crea oscuridad total'},
    'Pirotecnia': {'nivel': 2, 'escuela': 'Alteración', 'alcance': '120 yardas', 'descripcion': 'Fuegos artificiales desde fuego'},
    'Rayo Abrasador': {'nivel': 2, 'escuela': 'Evocación', 'alcance': '10 yardas + 5/nivel', 'descripcion': 'Rayo de fuego 1d8+1/nivel'},
    'Soga Encantada': {'nivel': 2, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Soga trepa y abre dimensión de bolsillo'},
    'Telaraña': {'nivel': 2, 'escuela': 'Evocación', 'alcance': '5 yardas/nivel', 'descripcion': 'Telarañas pegajosas'},
    'Toque del Espectro': {'nivel': 2, 'escuela': 'Nigromancia', 'alcance': '0', 'descripcion': 'Toque drena 1d6 FUE'},
    
    # NIVEL 3
    'Bola de Fuego': {'nivel': 3, 'escuela': 'Evocación', 'alcance': '100 yardas + 10/nivel', 'descripcion': 'Explosión 1d6/nivel'},
    'Clarividencia': {'nivel': 3, 'escuela': 'Adivinación', 'alcance': 'Ilimitado', 'descripcion': 'Ve a distancia'},
    'Clariaudiencia': {'nivel': 3, 'escuela': 'Adivinación', 'alcance': 'Ilimitado', 'descripcion': 'Oye a distancia'},
    'Disipar Magia': {'nivel': 3, 'escuela': 'Abjuración', 'alcance': '120 yardas', 'descripcion': 'Cancela efectos mágicos'},
    'Forma Gaseosa': {'nivel': 3, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Cuerpo se vuelve vapor'},
    'Fuerza Fantasmal': {'nivel': 3, 'escuela': 'Ilusión', 'alcance': '60 yardas + 10/nivel', 'descripcion': 'Ilusión visual compleja'},
    'Hedor': {'nivel': 3, 'escuela': 'Evocación', 'alcance': '30 yardas', 'descripcion': 'Nube apesta, causa náusea'},
    'Infravisión': {'nivel': 3, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Otorga infravisión 60 pies'},
    'Invisibilidad Radio 10 pies': {'nivel': 3, 'escuela': 'Ilusión', 'alcance': 'Toque', 'descripcion': 'Grupo invisible'},
    'Lentitud': {'nivel': 3, 'escuela': 'Alteración', 'alcance': '90 yardas + 10/nivel', 'descripcion': 'Ralentiza 1 criatura/nivel'},
    'Parpadeo': {'nivel': 3, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Parpadea entre planos'},
    'Protección contra Proyectiles Normales': {'nivel': 3, 'escuela': 'Abjuración', 'alcance': 'Toque', 'descripcion': 'Inmune a proyectiles no-mágicos'},
    'Relámpago': {'nivel': 3, 'escuela': 'Evocación', 'alcance': '40 yardas + 10/nivel', 'descripcion': 'Rayo 1d6/nivel'},
    'Respirar Bajo el Agua': {'nivel': 3, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Respira agua'},
    'Sugestión': {'nivel': 3, 'escuela': 'Encantamiento', 'alcance': '30 yardas', 'descripcion': 'Implanta sugestión'},
    'Toque Vampírico': {'nivel': 3, 'escuela': 'Necromancia', 'alcance': '0', 'descripcion': 'Drena 1d6 PG/2 niveles, cura'},
    'Volar': {'nivel': 3, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Vuela a velocidad 18'},
    
    # NIVEL 4
    'Alcanzar las Sombras': {'nivel': 4, 'escuela': 'Ilusión', 'alcance': '10 yardas', 'descripcion': 'Crea ilusión del Plano de las Sombras'},
    'Cambiar Forma': {'nivel': 4, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Cambia a criatura de similar tamaño'},
    'Confusión': {'nivel': 4, 'escuela': 'Encantamiento', 'alcance': '120 yardas', 'descripcion': 'Confunde 2d4 + 1/nivel criaturas'},
    'Crecimiento Vegetal': {'nivel': 4, 'escuela': 'Alteración', 'alcance': '160 yardas', 'descripcion': 'Plantas crecen y enmarañan'},
    'Dimensión de Bolsillo': {'nivel': 4, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Bolsillo extradimensional'},
    'Emociones': {'nivel': 4, 'escuela': 'Encantamiento', 'alcance': '10 yardas/nivel', 'descripcion': 'Causa emoción específica'},
    'Encantamiento Masivo': {'nivel': 4, 'escuela': 'Encantamiento', 'alcance': '10 yardas/nivel', 'descripcion': 'Encanta 2d4 criaturas'},
    'Escudo de Fuego': {'nivel': 4, 'escuela': 'Evocación/Alteración', 'alcance': '0', 'descripcion': 'Envuelto en llamas'},
    'Muro de Fuego': {'nivel': 4, 'escuela': 'Evocación', 'alcance': '60 yardas', 'descripcion': 'Muro de fuego 2d4 + 1/nivel'},
    'Muro de Hielo': {'nivel': 4, 'escuela': 'Evocación', 'alcance': '10 yardas/nivel', 'descripcion': 'Muro de hielo grueso'},
    'Ojo del Mago': {'nivel': 4, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Ojo invisible móvil'},
    'Piel de Piedra': {'nivel': 4, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Inmune a ataques físicos (1d4+1/nivel)'},
    'Polimorfar Otros': {'nivel': 4, 'escuela': 'Alteración', 'alcance': '5 yardas/nivel', 'descripcion': 'Cambia forma de criatura'},
    'Puerta Dimensional': {'nivel': 4, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Teletransporte corto'},
    'Remoción de Maldición': {'nivel': 4, 'escuela': 'Abjuración', 'alcance': 'Toque', 'descripcion': 'Remueve maldición'},
    
    # NIVEL 5
    'Animar Muertos': {'nivel': 5, 'escuela': 'Necromancia', 'alcance': '10 yardas', 'descripcion': 'Crea zombis o esqueletos'},
    'Conjurar Elemental': {'nivel': 5, 'escuela': 'Conjuración', 'alcance': '60 yardas', 'descripcion': 'Conjura elemental de 8 DG'},
    'Cono de Frío': {'nivel': 5, 'escuela': 'Evocación', 'alcance': '0', 'descripcion': 'Cono de frío 1d4+1/nivel'},
    'Contactar Otro Plano': {'nivel': 5, 'escuela': 'Adivinación', 'alcance': '0', 'descripcion': 'Pregunta a entidad planar'},
    'Débil Mental': {'nivel': 5, 'escuela': 'Encantamiento', 'alcance': '10 yardas/nivel', 'descripcion': 'Reduce INT a 2'},
    'Dominar Persona': {'nivel': 5, 'escuela': 'Encantamiento', 'alcance': '10 yardas/nivel', 'descripcion': 'Control telepático total'},
    'Muerte Imaginaria': {'nivel': 5, 'escuela': 'Necromancia', 'alcance': 'Toque', 'descripcion': 'Parece muerto'},
    'Muro de Fuerza': {'nivel': 5, 'escuela': 'Evocación', 'alcance': '30 yardas', 'descripcion': 'Barrera invisible invulnerable'},
    'Muro de Piedra': {'nivel': 5, 'escuela': 'Evocación', 'alcance': '5 yardas/nivel', 'descripcion': 'Muro de piedra 2"'},
    'Pasapared': {'nivel': 5, 'escuela': 'Alteración', 'alcance': '30 yardas', 'descripcion': 'Pasaje a través de muros'},
    'Telequinesis': {'nivel': 5, 'escuela': 'Alteración', 'alcance': '10 yardas/nivel', 'descripcion': 'Mueve objetos mentalmente (25 lb/nivel)'},
    'Teletransportación': {'nivel': 5, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Viaje instantáneo'},
    
    # NIVEL 6
    'Anti-Magia': {'nivel': 6, 'escuela': 'Abjuración', 'alcance': '0', 'descripcion': 'Esfera de 10 pies de radio donde no funciona la magia'},
    'Contingencia': {'nivel': 6, 'escuela': 'Evocación', 'alcance': '0', 'descripcion': 'Hechizo preparado se activa con condición'},
    'Desintegración': {'nivel': 6, 'escuela': 'Alteración', 'alcance': '5 yardas/nivel', 'descripcion': 'Desintegra materia'},
    'Globo de Invulnerabilidad': {'nivel': 6, 'escuela': 'Abjuración', 'alcance': '0', 'descripcion': 'Inmune a hechizos nivel 4 o menos'},
    'Muro de Hierro': {'nivel': 6, 'escuela': 'Evocación', 'alcance': '5 yardas/nivel', 'descripcion': 'Muro de hierro'},
    'Transformación': {'nivel': 6, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Mago se vuelve guerrero'},
    
    # NIVEL 7
    'Dedo de la Muerte': {'nivel': 7, 'escuela': 'Necromancia', 'alcance': '60 yardas', 'descripcion': 'Mata a objetivo (TS o muerte)'},
    'Espada de Mordenkainen': {'nivel': 7, 'escuela': 'Evocación', 'alcance': '30 yardas', 'descripcion': 'Espada mágica flotante ataca'},
    'Palabra de Poder Aturdir': {'nivel': 7, 'escuela': 'Conjuración', 'alcance': '5 yardas/nivel', 'descripcion': 'Aturde por PG'},
    'Viaje por el Plano': {'nivel': 7, 'escuela': 'Alteración', 'alcance': 'Toque', 'descripcion': 'Viaja a otros planos'},
    
    # NIVEL 8
    'Laberinto': {'nivel': 8, 'escuela': 'Conjuración', 'alcance': '5 yardas/nivel', 'descripcion': 'Atrapa en laberinto extradimensional'},
    'Palabra de Poder Cegar': {'nivel': 8, 'escuela': 'Conjuración', 'alcance': '5 yardas/nivel', 'descripcion': 'Ciega por PG'},
    'Símbolo': {'nivel': 8, 'escuela': 'Conjuración', 'alcance': 'Toque', 'descripcion': 'Glifo de poder con efecto variado'},
    
    # NIVEL 9
    'Deseo': {'nivel': 9, 'escuela': 'Conjuración', 'alcance': 'Ilimitado', 'descripcion': 'Altera realidad'},
    'Meteor Enjambre': {'nivel': 9, 'escuela': 'Evocación', 'alcance': '40 yardas + 10/nivel', 'descripcion': '4 meteoros causan 10d4 cada uno'},
    'Palabra de Poder Matar': {'nivel': 9, 'escuela': 'Conjuración', 'alcance': '10 yardas/nivel', 'descripcion': 'Mata por PG'},
    'Parada Temporal': {'nivel': 9, 'escuela': 'Alteración', 'alcance': '0', 'descripcion': 'Detiene el tiempo 1d3 rondas'},
}

CLERIC_SPELLS = {
    # NIVEL 1
    'Bendecir': {'nivel': 1, 'esfera': 'Todas', 'alcance': '60 yardas', 'descripcion': '+1 ataque y TS vs miedo'},
    'Comando': {'nivel': 1, 'esfera': 'Encantamiento', 'alcance': '30 yardas', 'descripcion': 'Orden de una palabra'},
    'Crear Agua': {'nivel': 1, 'esfera': 'Elemental', 'alcance': '30 yardas', 'descripcion': '4 galones/nivel'},
    'Curar Heridas Leves': {'nivel': 1, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura 1d8 PG'},
    'Detectar Bien/Mal': {'nivel': 1, 'esfera': 'Todas', 'alcance': '0', 'descripcion': 'Detecta alineamiento'},
    'Detectar Magia': {'nivel': 1, 'esfera': 'Adivinación', 'alcance': '0', 'descripcion': 'Detecta magia'},
    'Luz': {'nivel': 1, 'esfera': 'Solar', 'alcance': '120 yardas', 'descripcion': 'Crea luz'},
    'Protección contra el Mal': {'nivel': 1, 'esfera': 'Protección', 'alcance': 'Toque', 'descripcion': 'Barrera vs mal'},
    'Purificar Alimentos y Bebidas': {'nivel': 1, 'esfera': 'Todas', 'alcance': '30 yardas', 'descripcion': 'Purifica 1 pie cúbico/nivel'},
    'Resistir Frío': {'nivel': 1, 'esfera': 'Protección', 'alcance': 'Toque', 'descripcion': 'Protege del frío'},
    'Santuario': {'nivel': 1, 'esfera': 'Protección', 'alcance': 'Toque', 'descripcion': 'Oponentes evitan atacar'},
    
    # NIVEL 2
    'Ayuda': {'nivel': 2, 'esfera': 'Encantamiento', 'alcance': 'Toque', 'descripcion': '+1 ataque, +1d8 PG temporales'},
    'Aumentar/Reducir': {'nivel': 2, 'esfera': 'Alteración', 'alcance': '10 yardas', 'descripcion': 'Cambia tamaño'},
    'Encontrar Trampas': {'nivel': 2, 'esfera': 'Adivinación', 'alcance': '0', 'descripcion': 'Localiza trampas'},
    'Hablar con Animales': {'nivel': 2, 'esfera': 'Animal', 'alcance': '0', 'descripcion': 'Conversa con animales'},
    'Retener Persona': {'nivel': 2, 'esfera': 'Encantamiento', 'alcance': '120 yardas', 'descripcion': 'Paraliza humanoide'},
    'Silencio 15 pies': {'nivel': 2, 'esfera': 'Protección', 'alcance': '120 yardas', 'descripcion': 'Crea silencio total'},
    'Saber Alineamiento': {'nivel': 2, 'esfera': 'Adivinación', 'alcance': '10 yardas', 'descripcion': 'Revela alineamiento'},
    
    # NIVEL 3
    'Animar Muertos': {'nivel': 3, 'esfera': 'Necromancia', 'alcance': '10 yardas', 'descripcion': 'Crea zombis'},
    'Crear Alimentos y Agua': {'nivel': 3, 'esfera': 'Todas', 'alcance': '10 yardas', 'descripcion': 'Comida para 3 personas/nivel'},
    'Curar Ceguera o Sordera': {'nivel': 3, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura ceguera/sordera'},
    'Curar Enfermedades': {'nivel': 3, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura enfermedad'},
    'Curar Heridas Graves': {'nivel': 3, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura 2d8+1/nivel (max +10)'},
    'Disipar Magia': {'nivel': 3, 'esfera': 'Protección', 'alcance': '60 yardas', 'descripcion': 'Cancela magia'},
    'Luz Continua': {'nivel': 3, 'esfera': 'Solar', 'alcance': '120 yardas', 'descripcion': 'Luz permanente'},
    'Protección contra el Fuego': {'nivel': 3, 'esfera': 'Protección', 'alcance': 'Toque', 'descripcion': 'Inmune a fuego normal'},
    'Respirar Bajo el Agua': {'nivel': 3, 'esfera': 'Elemental/Alteración', 'alcance': 'Toque', 'descripcion': 'Respira agua'},
    
    # NIVEL 4
    'Caminar Sobre el Agua': {'nivel': 4, 'esfera': 'Elemental', 'alcance': 'Toque', 'descripcion': 'Camina sobre agua'},
    'Crear Agua': {'nivel': 4, 'esfera': 'Elemental', 'alcance': '10 yardas', 'descripcion': '8 galones/nivel'},
    'Curar Heridas Críticas': {'nivel': 4, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura 3d8+3'},
    'Detección de Mentiras': {'nivel': 4, 'esfera': 'Adivinación', 'alcance': '30 yardas', 'descripcion': 'Detecta mentiras'},
    'Lenguas': {'nivel': 4, 'esfera': 'Adivinación', 'alcance': 'Toque', 'descripcion': 'Habla cualquier idioma'},
    'Neutralizar Veneno': {'nivel': 4, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Neutraliza veneno'},
    'Protección contra el Mal Radio 10 pies': {'nivel': 4, 'esfera': 'Protección', 'alcance': 'Toque', 'descripcion': 'Barrera vs mal para grupo'},
    
    # NIVEL 5
    'Columna de Fuego': {'nivel': 5, 'esfera': 'Elemental', 'alcance': '60 yardas', 'descripcion': '8d8 de fuego'},
    'Comunión': {'nivel': 5, 'esfera': 'Adivinación', 'alcance': '0', 'descripcion': 'Pregunta a deidad'},
    'Curar Heridas Críticas en Masa': {'nivel': 5, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura 1d8+1/nivel (max +25)'},
    'Dispersar el Mal': {'nivel': 5, 'esfera': 'Protección', 'alcance': 'Toque', 'descripcion': 'Despacha criaturas malignas extraplanares'},
    'Plaga de Insectos': {'nivel': 5, 'esfera': 'Combat', 'alcance': '360 yardas', 'descripcion': 'Enjambre de insectos'},
    'Resucitar': {'nivel': 5, 'esfera': 'Necromancia', 'alcance': 'Toque', 'descripcion': 'Devuelve la vida'},
    'Visión Verdadera': {'nivel': 5, 'esfera': 'Adivinación', 'alcance': 'Toque', 'descripcion': 'Ve todas las cosas como son'},
    
    # NIVEL 6
    'Animar Objetos': {'nivel': 6, 'esfera': 'Combate', 'alcance': '30 yardas', 'descripcion': 'Objetos cobran vida'},
    'Cuchilla de Barrera': {'nivel': 6, 'esfera': 'Creación', 'alcance': '30 yardas', 'descripcion': 'Muro giratorio de cuchillas'},
    'Curar': {'nivel': 6, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Cura todo excepto muerte'},
    'Encontrar el Camino': {'nivel': 6, 'esfera': 'Adivinación', 'alcance': 'Toque', 'descripcion': 'Muestra camino directo'},
    'Palabra de Recuerdo': {'nivel': 6, 'esfera': 'Alteración', 'alcance': '0', 'descripcion': 'Teletransporte a santuario'},
    
    # NIVEL 7
    'Conjurar Elemental de Fuego': {'nivel': 7, 'esfera': 'Elemental/Conjuración', 'alcance': '80 yardas', 'descripcion': 'Conjura elemental 16 DG'},
    'Puerta': {'nivel': 7, 'esfera': 'Alteración', 'alcance': '30 yardas', 'descripcion': 'Portal a otro lugar'},
    'Regeneración': {'nivel': 7, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Regenera extremidades'},
    'Resurrección': {'nivel': 7, 'esfera': 'Necromancia', 'alcance': 'Toque', 'descripcion': 'Revive sin pérdida de CON'},
    'Restauración': {'nivel': 7, 'esfera': 'Curación', 'alcance': 'Toque', 'descripcion': 'Restaura niveles drenados'},
    'Símbolo': {'nivel': 7, 'esfera': 'Conjuración', 'alcance': 'Toque', 'descripcion': 'Glifo mágico'},
}

# Total de hechizos
TOTAL_WIZARD = len(WIZARD_SPELLS)
TOTAL_CLERIC = len(CLERIC_SPELLS)
