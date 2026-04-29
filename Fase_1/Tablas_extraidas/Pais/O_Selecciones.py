from bs4 import BeautifulSoup
import csv
import os

def extraer_selecciones_desde_archivo(archivo_html):
    """
    Extrae solo número y nombre de las selecciones del archivo HTML
    """
    # Leer el archivo HTML
    with open(archivo_html, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Buscar la tabla que contiene las selecciones
    tabla = soup.find('table', class_='panel')
    
    if not tabla:
        print("❌ No se encontró la tabla de selecciones")
        return []
    
    # Encontrar todas las filas de la tabla (cada selección es una fila)
    filas = tabla.find_all('tr')
    
    selecciones = []
    
    print(f"📊 Procesando {len(filas)} filas...")
    
    for fila in filas:
        try:
            # Buscar el número (está en un div con width:30px)
            div_numero = fila.find('div', style=lambda x: x and 'width: 30px' in x)
            if not div_numero:
                continue
                
            numero = div_numero.get_text(strip=True).replace('.', '')
            
            # Buscar el nombre (está después de la imagen)
            img = fila.find('img')
            if not img:
                continue
                
            # El nombre es el texto que sigue a la imagen
            nombre_tag = img.find_next_sibling(text=True)
            if nombre_tag:
                nombre = nombre_tag.strip()
            else:
                # Si no hay texto directo, buscar en el contenedor
                contenedor = img.parent
                texto_completo = contenedor.get_text(strip=True)
                # Eliminar el número y la parte de la imagen
                nombre = texto_completo.replace(numero, '').strip()
            
            if nombre and numero:
                selecciones.append({
                    'numero': numero,
                    'nombre': nombre
                })
                print(f"  ✓ {numero}. {nombre}")
                
        except Exception as e:
            print(f"  ⚠️ Error procesando fila: {e}")
            continue
    
    return selecciones

def guardar_csv(selecciones, nombre_archivo='selecciones.csv'):
    """
    Guarda número y nombre en un CSV
    """
    if not selecciones:
        print("❌ No hay datos para guardar")
        return
    
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['numero', 'nombre'])  # Encabezados
        for s in selecciones:
            writer.writerow([s['numero'], s['nombre']])
    
    print(f"\n💾 Guardadas {len(selecciones)} selecciones en '{nombre_archivo}'")

def mostrar_resumen(selecciones):
    """
    Muestra un resumen simple
    """
    print("\n" + "="*60)
    print(f"📋 TOTAL: {len(selecciones)} SELECCIONES")
    print("="*60)
    
    # Mostrar primeras 10
    print("\n📌 Primeras 10 selecciones:")
    for s in selecciones[:10]:
        print(f"  {s['numero']}. {s['nombre']}")
    
    # Mostrar últimas 5
    print("\n📌 Últimas 5 selecciones:")
    for s in selecciones[-5:]:
        print(f"  {s['numero']}. {s['nombre']}")

# ============================================
# EJECUTAR
# ============================================
print("="*60)
print("🚀 EXTRACTOR DE SELECCIONES (SOLO NÚMERO Y NOMBRE)")
print("="*60)

archivo_html = "Selecciones.html"

# Verificar que el archivo existe
if not os.path.exists(archivo_html):
    print(f"❌ ERROR: No se encuentra el archivo '{archivo_html}'")
    print("\n📁 Archivos disponibles:")
    for f in os.listdir('.'):
        if f.endswith('.html'):
            print(f"   • {f}")
    exit()

print(f"📂 Procesando: {archivo_html}")
print(f"📏 Tamaño: {os.path.getsize(archivo_html):,} bytes\n")

selecciones = extraer_selecciones_desde_archivo(archivo_html)

if selecciones:
    guardar_csv(selecciones)
    mostrar_resumen(selecciones)
    
    print(f"\n✅ Listo! Revisa 'selecciones.csv'")
else:
    print("\n❌ No se encontraron selecciones")