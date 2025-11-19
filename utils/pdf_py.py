import PyPDF2
import os

def extraer_paginas_pdf(pdf_entrada, pdf_salida, paginas_a_extraer, max_paginas_permitidas=500):
    """
    Extrae páginas específicas de un PDF y las guarda en un nuevo archivo.

    :param pdf_entrada: La ruta del archivo PDF de entrada.
    :param pdf_salida: La ruta del nuevo archivo PDF de salida.
    :param paginas_a_extraer: Una lista de números de página (empezando en 1) a extraer.
    :param max_paginas_permitidas: Límite máximo de páginas a extraer para evitar problemas de memoria.
    """
    try:
        # Asegúrate de que el archivo de entrada existe
        if not os.path.exists(pdf_entrada):
            print(f"❌ Error: El archivo de entrada '{pdf_entrada}' no fue encontrado.")
            return False

        # Verificar límite de páginas a extraer
        if len(paginas_a_extraer) > max_paginas_permitidas:
            print(f"⚠️ Advertencia: Intentas extraer {len(paginas_a_extraer)} páginas.")
            print(f"   El límite recomendado es {max_paginas_permitidas} páginas para evitar problemas de memoria.")
            respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
            if respuesta != 's':
                print("❌ Operación cancelada.")
                return False

        print(f"🔄 Procesando PDF: {os.path.basename(pdf_entrada)}")
        print(f"📄 Extrayendo {len(paginas_a_extraer)} páginas...")

        # Abre el PDF de entrada
        with open(pdf_entrada, 'rb') as archivo_pdf_entrada:
            lector = PyPDF2.PdfReader(archivo_pdf_entrada)
            
            # Verificar si el PDF está cifrado
            if lector.is_encrypted:
                print("🔒 El PDF está protegido con contraseña.")
                password = input("Ingresa la contraseña (o Enter si no tiene): ").strip()
                if password:
                    if not lector.decrypt(password):
                        print("❌ Contraseña incorrecta.")
                        return False
                else:
                    try:
                        lector.decrypt("")
                    except:
                        print("❌ No se puede acceder al PDF protegido.")
                        return False
            
            escritor = PyPDF2.PdfWriter()
            paginas_procesadas = 0
            total_paginas_pdf = len(lector.pages)

            # Itera sobre los números de página solicitados
            for i, num_pagina in enumerate(paginas_a_extraer, 1):
                try:
                    # Mostrar progreso cada 10 páginas
                    if i % 10 == 0 or i == len(paginas_a_extraer):
                        print(f"⏳ Progreso: {i}/{len(paginas_a_extraer)} páginas procesadas...")

                    # PyPDF2 usa un índice base 0, por lo que restamos 1 al número de página
                    indice_pagina = num_pagina - 1

                    # Verifica si el número de página está dentro del rango válido
                    if 0 <= indice_pagina < total_paginas_pdf:
                        pagina = lector.pages[indice_pagina]
                        escritor.add_page(pagina)
                        paginas_procesadas += 1
                    else:
                        print(f"⚠️ Advertencia: La página {num_pagina} está fuera del rango del documento (total: {total_paginas_pdf} páginas).")
                        
                except Exception as e:
                    print(f"⚠️ Error al procesar la página {num_pagina}: {e}")
                    continue

            if paginas_procesadas == 0:
                print("❌ No se procesaron páginas válidas.")
                return False

            # Escribe las páginas extraídas en un nuevo archivo PDF
            print(f"💾 Guardando archivo: {pdf_salida}")
            with open(pdf_salida, 'wb') as archivo_pdf_salida:
                escritor.write(archivo_pdf_salida)

            print(f"\n✅ ¡Éxito! Se extrajeron {paginas_procesadas} páginas.")
            print(f"✨ Archivo de salida creado en: {pdf_salida}")
            
            # Mostrar información del archivo creado
            tamano_archivo = os.path.getsize(pdf_salida) / (1024 * 1024)  # MB
            print(f"📊 Tamaño del archivo: {tamano_archivo:.2f} MB")
            return True

    except MemoryError:
        print(f"\n❌ Error de memoria: El PDF es demasiado grande.")
        print("💡 Sugerencia: Intenta extraer menos páginas a la vez.")
        return False
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")
        return False

def seleccionar_archivo_pdf():
    """
    Permite al usuario seleccionar un archivo PDF desde la entrada del teclado.
    """
    while True:
        ruta_pdf = input("📁 Ingresa la ruta completa del archivo PDF (o 'salir' para cancelar): ").strip()
        
        if ruta_pdf.lower() == 'salir':
            print("❌ Operación cancelada por el usuario.")
            return None
            
        # Remover comillas si las hay
        ruta_pdf = ruta_pdf.strip('"').strip("'")
        
        if os.path.exists(ruta_pdf) and ruta_pdf.lower().endswith('.pdf'):
            return ruta_pdf
        elif not os.path.exists(ruta_pdf):
            print(f"❌ Error: El archivo '{ruta_pdf}' no existe.")
        elif not ruta_pdf.lower().endswith('.pdf'):
            print(f"❌ Error: El archivo '{ruta_pdf}' no es un PDF válido.")
        else:
            print("❌ Error: Archivo no válido.")
            
def main():
    """
    Función principal que maneja la interacción con el usuario.
    """
    print("🔧 Extractor de Páginas de PDF")
    print("=" * 40)
    
    # Seleccionar archivo PDF de entrada
    archivo_entrada = seleccionar_archivo_pdf()
    if archivo_entrada is None:
        return
    
    # Mostrar información del PDF
    try:
        # Información del archivo
        tamano_mb = os.path.getsize(archivo_entrada) / (1024 * 1024)
        print(f"\n📄 PDF cargado: {os.path.basename(archivo_entrada)}")
        print(f"💾 Tamaño del archivo: {tamano_mb:.2f} MB")
        
        # Advertencia para archivos muy grandes
        if tamano_mb > 50:
            print("⚠️  ADVERTENCIA: Archivo muy grande (>50 MB)")
            print("   Se recomienda extraer pocas páginas a la vez.")
        
        with open(archivo_entrada, 'rb') as archivo_pdf:
            lector = PyPDF2.PdfReader(archivo_pdf)
            
            # Verificar si está cifrado
            if lector.is_encrypted:
                print("🔒 El PDF está protegido con contraseña.")
            
            total_paginas = len(lector.pages)
            print(f"� Total de páginas: {total_paginas}")
            
            # Advertencia para PDFs con muchas páginas
            if total_paginas > 1000:
                print("⚠️  ADVERTENCIA: PDF con muchas páginas (>1000)")
                print("   Se recomienda extraer en lotes pequeños.")
                
    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")
        return
    
    # Solicitar páginas a extraer
    while True:
        try:
            entrada_paginas = input(f"\n📝 Ingresa las páginas a extraer (1-{total_paginas})\n"
                                  "   Ejemplos: '1,3,5' o '1-5' o '1-3,7,10-12': ").strip()
            
            if entrada_paginas.lower() == 'salir':
                print("❌ Operación cancelada.")
                return
                
            paginas_seleccionadas = parsear_rangos_paginas(entrada_paginas, total_paginas)
            if paginas_seleccionadas:
                break
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada.")
            return
    
    # Solicitar nombre del archivo de salida
    archivo_salida = input("\n💾 Nombre del archivo de salida (ej: 'paginas_extraidas.pdf'): ").strip()
    if not archivo_salida:
        archivo_salida = 'paginas_extraidas.pdf'
    if not archivo_salida.lower().endswith('.pdf'):
        archivo_salida += '.pdf'
    
    # Extraer las páginas
    extraer_paginas_pdf(archivo_entrada, archivo_salida, paginas_seleccionadas)

def parsear_rangos_paginas(entrada, max_paginas):
    """
    Parsea una entrada de rangos de páginas como '1,3,5-7,10'.
    
    :param entrada: String con los rangos de páginas
    :param max_paginas: Número máximo de páginas disponibles
    :return: Lista de números de página
    """
    paginas = []
    try:
        # Dividir por comas
        partes = entrada.split(',')
        for parte in partes:
            parte = parte.strip()
            if '-' in parte:
                # Es un rango
                rango_partes = parte.split('-')
                if len(rango_partes) != 2:
                    print(f"❌ Formato de rango inválido: {parte}")
                    return None
                    
                inicio, fin = int(rango_partes[0].strip()), int(rango_partes[1].strip())
                if inicio < 1 or fin > max_paginas or inicio > fin:
                    print(f"❌ Rango inválido: {inicio}-{fin}")
                    return None
                    
                # Verificar que el rango no sea excesivamente grande
                if fin - inicio > 200:
                    print(f"⚠️ Rango muy grande: {inicio}-{fin} ({fin-inicio+1} páginas)")
                    respuesta = input("¿Continuar? (s/n): ").strip().lower()
                    if respuesta != 's':
                        return None
                        
                paginas.extend(range(inicio, fin + 1))
            else:
                # Es un número individual
                num = int(parte.strip())
                if num < 1 or num > max_paginas:
                    print(f"❌ Página fuera de rango: {num}")
                    return None
                paginas.append(num)
        
        # Remover duplicados y ordenar
        paginas = sorted(list(set(paginas)))
        
        # Verificar límite total de páginas a extraer
        if len(paginas) > 100:
            print(f"⚠️ Vas a extraer {len(paginas)} páginas.")
            print("   Para PDFs grandes, esto podría causar problemas de memoria.")
            respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
            if respuesta != 's':
                return None
        
        print(f"✅ Páginas seleccionadas: {len(paginas)} páginas")
        if len(paginas) <= 20:
            print(f"   Páginas: {paginas}")
        else:
            print(f"   Páginas: {paginas[:10]}...{paginas[-5:]}")
        return paginas
        
    except ValueError:
        print("❌ Formato inválido. Usa: '1,3,5-7,10'")
        return None

# --- Ejecutar el Programa ---
if __name__ == "__main__":
    main()