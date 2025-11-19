# -*- coding: utf-8 -*-
"""
Generador de PDF para fichas de personajes AD&D 2E
Lee archivos JSON de personajes y genera PDFs con formato profesional
"""

import json
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class CharacterSheetPDF:
    """Generador de fichas de personaje en PDF"""
    
    def __init__(self, json_file):
        """Inicializa el generador con un archivo JSON"""
        self.json_file = Path(json_file)
        self.character_data = self._load_character()
        
    def _load_character(self):
        """Carga los datos del personaje desde JSON"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error cargando {self.json_file}: {e}")
            sys.exit(1)
    
    def generate_pdf(self, output_file=None):
        """Genera el PDF de la ficha de personaje"""
        if not output_file:
            output_file = self.json_file.stem + "_ficha.pdf"
        
        # Crear el documento PDF
        pdf = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Contenedor para elementos del PDF
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8B0000'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#8B0000'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Título con nombre del personaje
        title = Paragraph(f"<b>{self.character_data['name'].upper()}</b>", title_style)
        elements.append(title)
        
        subtitle = Paragraph(
            f"<b>{self.character_data.get('race', 'N/A')} {self.character_data.get('class', 'N/A')} - Nivel {self.character_data.get('level', 1)}</b>",
            ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#696969'))
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.2*inch))
        
        # Información básica
        basic_info = [
            ['Nivel:', str(self.character_data.get('level', 1)), 'Experiencia:', str(self.character_data.get('experience', 0))],
            ['Raza:', self.character_data.get('race', 'N/A'), 'Clase:', self.character_data.get('class', 'N/A')]
        ]
        
        basic_table = Table(basic_info, colWidths=[1*inch, 2*inch, 1*inch, 2*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D3D3D3')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#D3D3D3')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(basic_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Atributos
        elements.append(Paragraph("<b>ATRIBUTOS</b>", heading_style))
        
        attrs = self.character_data.get('attributes', {})
        attr_data = [
            ['FUE', 'DES', 'CON', 'INT', 'SAB', 'CAR'],
            [str(attrs.get('FUE', 10)), str(attrs.get('DES', 10)), str(attrs.get('CON', 10)),
             str(attrs.get('INT', 10)), str(attrs.get('SAB', 10)), str(attrs.get('CAR', 10))]
        ]
        
        attr_table = Table(attr_data, colWidths=[1*inch]*6)
        attr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(attr_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Combate
        elements.append(Paragraph("<b>COMBATE</b>", heading_style))
        
        combat_data = [
            ['Puntos de Golpe', 'Clase de Armadura', 'THAC0'],
            [f"{self.character_data.get('hit_points_current', 0)}/{self.character_data.get('hit_points_max', 0)}",
             str(self.character_data.get('armor_class', 10)),
             str(self.character_data.get('thac0', 20))]
        ]
        
        combat_table = Table(combat_data, colWidths=[2*inch, 2*inch, 2*inch])
        combat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 13),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(combat_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Tiradas de Salvación
        elements.append(Paragraph("<b>TIRADAS DE SALVACIÓN</b>", heading_style))
        
        saves = self.character_data.get('saving_throws', {})
        save_data = [
            ['Parálisis', 'Varitas', 'Petrificación', 'Aliento', 'Conjuros'],
            [str(saves.get('paralisis', 14)), str(saves.get('varitas', 16)), 
             str(saves.get('petrificacion', 15)), str(saves.get('aliento', 17)), 
             str(saves.get('conjuros', 17))]
        ]
        
        save_table = Table(save_data, colWidths=[1.2*inch]*5)
        save_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#696969')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(save_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Pericias
        proficiencies = self.character_data.get('proficiencies', {})
        if proficiencies.get('armas') or proficiencies.get('no_armas'):
            elements.append(Paragraph("<b>PERICIAS</b>", heading_style))
            
            prof_data = []
            if proficiencies.get('armas'):
                prof_data.append(['Armas:', ', '.join(proficiencies['armas'])])
            if proficiencies.get('no_armas'):
                prof_data.append(['No-Armas:', ', '.join(proficiencies['no_armas'])])
            
            if prof_data:
                prof_table = Table(prof_data, colWidths=[1.5*inch, 4.5*inch])
                prof_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D3D3D3')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(prof_table)
                elements.append(Spacer(1, 0.2*inch))
        
        # Kit
        kit = self.character_data.get('kit')
        if kit:
            elements.append(Paragraph(f"<b>Kit:</b> {kit}", styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Equipo
        equipment = self.character_data.get('equipment', [])
        if equipment:
            elements.append(Paragraph("<b>EQUIPO</b>", heading_style))
            equip_text = "<br/>".join([f"• {item}" for item in equipment])
            elements.append(Paragraph(equip_text, styles['BodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Dinero
        money = self.character_data.get('money', {})
        if any(money.values()):
            coins = []
            if money.get('po', 0) > 0:
                coins.append(f"{money['po']} po")
            if money.get('pp', 0) > 0:
                coins.append(f"{money['pp']} pp")
            if money.get('pe', 0) > 0:
                coins.append(f"{money['pe']} pe")
            if money.get('pc', 0) > 0:
                coins.append(f"{money['pc']} pc")
            if coins:
                elements.append(Paragraph(f"<b>Dinero:</b> {', '.join(coins)}", styles['BodyText']))
                elements.append(Spacer(1, 0.2*inch))
        
        # Hechizos conocidos
        known_spells = self.character_data.get('known_spells', [])
        if known_spells:
            elements.append(Paragraph("<b>HECHIZOS CONOCIDOS</b>", heading_style))
            spell_text = ", ".join(known_spells)
            elements.append(Paragraph(spell_text, styles['BodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Hechizos preparados
        prepared_spells = self.character_data.get('prepared_spells', [])
        if prepared_spells:
            elements.append(Paragraph("<b>HECHIZOS PREPARADOS</b>", heading_style))
            prep_text = ", ".join(prepared_spells)
            elements.append(Paragraph(prep_text, styles['BodyText']))
        
        # Construir PDF
        pdf.build(elements)
        print(f"✅ PDF generado: {output_file}")
        return output_file


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("GENERADOR DE FICHAS PDF - AD&D 2E")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUso: python generar_pdf.py <archivo.json> [salida.pdf]")
        print("     python generar_pdf.py --all  (procesa todos los JSON)")
        print("\nEjemplos:")
        print("  python generar_pdf.py ilron_character.json")
        print("  python generar_pdf.py ilron_character.json mi_ficha.pdf")
        print("  python generar_pdf.py --all")
        
        # Buscar archivos JSON en el directorio actual
        json_files = list(Path('.').glob('*_character.json'))
        if json_files:
            print(f"\nArchivos JSON encontrados ({len(json_files)}):")
            for i, f in enumerate(json_files, 1):
                print(f"  [{i}] {f.name}")
            
            try:
                choice = input("\n¿Generar PDF? (número, 'all' para todos, Enter para salir): ").strip()
                
                if choice.lower() == 'all':
                    print("\nGenerando PDFs para todos los personajes...")
                    for json_file in json_files:
                        try:
                            generator = CharacterSheetPDF(json_file)
                            generator.generate_pdf()
                        except Exception as e:
                            print(f"❌ Error con {json_file.name}: {e}")
                    print(f"\n✅ {len(json_files)} fichas generadas")
                    
                elif choice:
                    idx = int(choice) - 1
                    if 0 <= idx < len(json_files):
                        json_file = json_files[idx]
                        generator = CharacterSheetPDF(json_file)
                        generator.generate_pdf()
                        print(f"\n✅ Proceso completado")
            except (ValueError, IndexError):
                print("Opción inválida")
        else:
            print("\nNo se encontraron archivos JSON de personajes.")
        
        sys.exit(0)
    
    # Procesar argumento --all
    if sys.argv[1] == '--all':
        json_files = list(Path('.').glob('*_character.json'))
        if not json_files:
            print("\n❌ No se encontraron archivos JSON")
            sys.exit(1)
        
        print(f"\nGenerando PDFs para {len(json_files)} personajes...")
        for json_file in json_files:
            try:
                generator = CharacterSheetPDF(json_file)
                generator.generate_pdf()
            except Exception as e:
                print(f"❌ Error con {json_file.name}: {e}")
        
        print(f"\n✅ Proceso completado - {len(json_files)} fichas generadas")
        print("="*70)
        sys.exit(0)
    
    # Procesar argumentos individuales
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Generar PDF
    generator = CharacterSheetPDF(json_file)
    generator.generate_pdf(output_file)
    
    print("\n✅ Proceso completado")
    print("="*70)


if __name__ == "__main__":
    main()
