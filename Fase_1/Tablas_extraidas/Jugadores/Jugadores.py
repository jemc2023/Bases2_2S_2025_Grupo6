from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random
import os

def configurar_driver():
    """Configura el driver de Chrome con opciones para evitar detección"""
    options = Options()
    # Hacer que parezca un navegador normal
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--lang=es')
    options.add_argument('--window-size=1920,1080')
    
    # User agent realista
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    print("🚗 Iniciando Chrome Driver...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    # Script para ocultar que es Selenium
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def obtener_paises_con_selenium(driver):
    """Obtiene todos los links de países desde la página principal USANDO SOLO SELENIUM"""
    url_base = "https://www.losmundialesdefutbol.com/jugadores.php"
    print(f"🌍 Accediendo a: {url_base}")
    
    driver.get(url_base)
    print("  ⏳ Esperando que cargue la página...")
    time.sleep(5)  # Esperar que cargue
    
    paises = []
    
    try:
        # Buscar TODOS los enlaces
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        print(f"  📊 Total de enlaces encontrados: {len(enlaces)}")
        
        for enlace in enlaces:
            try:
                href = enlace.get_attribute("href")
                texto = enlace.text.strip()
                
                # Buscar enlaces a índices de países
                if href and "jugadores_indice/" in href:
                    # Verificar que tiene bandera (imagen)
                    imagenes = enlace.find_elements(By.TAG_NAME, "img")
                    tiene_bandera = False
                    for img in imagenes:
                        alt = img.get_attribute("alt") or ""
                        if "Bandera" in alt:
                            tiene_bandera = True
                            break
                    
                    # Si tiene bandera o el texto es un país conocido
                    if tiene_bandera or (texto and len(texto) > 2):
                        # Evitar duplicados
                        if not any(p['url'] == href for p in paises):
                            paises.append({
                                'nombre': texto if texto else href.split('/')[-1].replace('.php', '').capitalize(),
                                'url': href
                            })
                            print(f"  ✓ País encontrado: {texto}")
            except Exception as e:
                continue
        
        # Si no encontramos con banderas, buscar en la sección "Jugadores por Selección"
        if not paises:
            print("  🔍 Buscando en sección 'Jugadores por Selección'...")
            # Buscar el encabezado
            headers = driver.find_elements(By.TAG_NAME, "strong")
            for header in headers:
                if "Jugadores por Selección" in header.text:
                    # Encontrar el contenedor padre y buscar enlaces
                    contenedor = header.find_element(By.XPATH, "..")
                    enlaces_pais = contenedor.find_elements(By.TAG_NAME, "a")
                    
                    for enlace in enlaces_pais:
                        href = enlace.get_attribute("href")
                        texto = enlace.text.strip()
                        if href and texto and "jugadores_indice/" in href:
                            paises.append({
                                'nombre': texto,
                                'url': href
                            })
                            print(f"  ✓ País encontrado: {texto}")
                    break
    
    except Exception as e:
        print(f"  ⚠️ Error buscando países: {e}")
    
    print(f"📊 Total de países encontrados: {len(paises)}")
    return paises

def obtener_jugadores_desde_pais(driver, url_pais, nombre_pais):
    """Obtiene todos los links de jugadores desde la página de un país"""
    print(f"\n  📂 Accediendo a país: {nombre_pais}")
    print(f"  📡 URL: {url_pais}")
    
    driver.get(url_pais)
    time.sleep(4)  # Esperar que cargue
    
    jugadores = []
    
    try:
        # Buscar todos los enlaces
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        
        for enlace in enlaces:
            try:
                href = enlace.get_attribute("href")
                texto = enlace.text.strip()
                
                # Buscar enlaces a páginas de jugadores individuales
                if href and "/jugadores/" in href and ".php" in href:
                    # Filtrar textos que no son nombres de jugadores
                    if (texto and len(texto) > 1 and 
                        texto not in ['Inicio', 'Estadísticas', 'Mundiales', 'Selecciones', 
                                    'Jugadores', 'por Apellido', 'por Selección', 'Javier Hernandez'] and
                        not any(j['url'] == href for j in jugadores)):
                        
                        # Extraer referencia (nombre del archivo)
                        referencia = href.split('/')[-1]
                        
                        jugadores.append({
                            'nombre_referencia': texto,
                            'url': href,
                            'referencia': referencia,
                            'pais': nombre_pais
                        })
                        print(f"    ✓ Jugador: {texto}")
            except:
                continue
                
    except Exception as e:
        print(f"    ⚠️ Error buscando jugadores: {e}")
    
    print(f"    📊 Total jugadores encontrados en {nombre_pais}: {len(jugadores)}")
    return jugadores

def extraer_datos_jugador(driver, url_jugador, jugador_info):
    """Extrae los datos específicos de la página de un jugador"""
    print(f"      ⏳ Accediendo a jugador: {jugador_info['nombre_referencia']}")
    
    driver.get(url_jugador)
    time.sleep(3)  # Esperar que cargue
    
    datos = {
        'jugador': jugador_info['nombre_referencia'],
        'pais': jugador_info['pais'],
        'referencia': jugador_info['referencia'],
        'nombre_completo': '',
        'birthday': '',
        'height': '',
        'url': url_jugador
    }
    
    try:
        # Buscar la tabla de información personal
        tablas = driver.find_elements(By.TAG_NAME, "table")
        
        for tabla in tablas:
            texto_tabla = tabla.text
            if "Nombre completo" in texto_tabla or "Fecha de Nacimiento" in texto_tabla:
                filas = tabla.find_elements(By.TAG_NAME, "tr")
                
                for fila in filas:
                    try:
                        celdas = fila.find_elements(By.TAG_NAME, "td")
                        if len(celdas) >= 2:
                            etiqueta = celdas[0].text.strip().replace(':', '')
                            valor = celdas[1].text.strip()
                            
                            if "Nombre completo" in etiqueta:
                                datos['nombre_completo'] = valor
                            elif "Fecha de Nacimiento" in etiqueta:
                                datos['birthday'] = valor
                            elif "Altura" in etiqueta:
                                datos['height'] = valor
                    except:
                        continue
                break
        
        # Si no encontramos el nombre completo, buscar en h1
        if not datos['nombre_completo']:
            try:
                h1 = driver.find_element(By.CSS_SELECTOR, "h1.tc-1")
                if h1:
                    texto = h1.text
                    datos['nombre_completo'] = texto.replace('en los Mundiales de Fútbol', '').strip()
            except:
                pass
        
        print(f"      ✓ Datos extraídos: Nombre={datos['nombre_completo'][:30]}..., Birthday={datos['birthday']}, Height={datos['height']}")
        
    except Exception as e:
        print(f"      ⚠️ Error extrayendo datos: {e}")
    
    return datos

def guardar_csv(jugadores, nombre_archivo='jugadores_mundiales.csv'):
    """Guarda los datos en un archivo CSV"""
    if not jugadores:
        print("❌ No hay datos para guardar")
        return
    
    with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['id', 'jugador', 'pais', 'referencia', 'nombre_completo', 'birthday', 'height', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, jugador in enumerate(jugadores, 1):
            jugador['id'] = i
            writer.writerow(jugador)
    
    print(f"\n💾 Guardados {len(jugadores)} jugadores en '{nombre_archivo}'")

def mostrar_resumen(jugadores):
    """Muestra un resumen de los datos recolectados"""
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"Total de jugadores procesados: {len(jugadores)}")
    
    if jugadores:
        # Contar por país
        paises = {}
        for j in jugadores:
            paises[j['pais']] = paises.get(j['pais'], 0) + 1
        
        print("\n📌 Jugadores por país (top 10):")
        for pais, count in sorted(paises.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {pais}: {count} jugadores")
        
        # Mostrar algunos ejemplos
        print("\n📌 Primeros 5 jugadores:")
        for j in jugadores[:5]:
            print(f"  {j['id']}. {j['jugador']} ({j['pais']})")
            if j['nombre_completo']:
                print(f"     Nombre: {j['nombre_completo']}")
            if j['birthday']:
                print(f"     Nacimiento: {j['birthday']}")
            if j['height']:
                print(f"     Altura: {j['height']}")
            print()

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
print("="*60)
print("🚀 WEB SCRAPING DE JUGADORES DE MUNDIALES (SELENIUM PURO)")
print("="*60)

driver = None
try:
    # Configurar driver
    driver = configurar_driver()
    
    # Paso 1: Obtener todos los países
    print("\n📋 PASO 1: OBTENER PAÍSES")
    paises = obtener_paises_con_selenium(driver)
    
    if not paises:
        print("❌ No se pudieron obtener los países")
        
        # Preguntar si quiere introducir URLs manualmente
        print("\n¿Quieres introducir las URLs de países manualmente?")
        respuesta = input("(s/n): ").strip().lower()
        if respuesta == 's':
            paises = []
            while True:
                url = input("URL del país (o 'fin' para terminar): ").strip()
                if url.lower() == 'fin':
                    break
                nombre = input("Nombre del país: ").strip()
                paises.append({'nombre': nombre, 'url': url})
        else:
            exit()
    
    print(f"\n✅ Lista de {len(paises)} países:")
    for i, pais in enumerate(paises, 1):
        print(f"  {i}. {pais['nombre']}")
    
    # Configurar límites
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN")
    print("="*60)
    
    try:
        num_paises = int(input(f"¿Cuántos países procesar? (1-{len(paises)}): ").strip())
        if num_paises < 1 or num_paises > len(paises):
            num_paises = len(paises)
    except:
        num_paises = len(paises)
    
    try:
        num_jugadores = int(input("¿Cuántos jugadores por país? (0 para todos): ").strip())
        if num_jugadores < 0:
            num_jugadores = 0
    except:
        num_jugadores = 0
    
    print(f"\n📊 Procesando {num_paises} países")
    if num_jugadores > 0:
        print(f"📊 {num_jugadores} jugadores por país")
    else:
        print(f"📊 Todos los jugadores por país")
    
    # Procesar
    todos_los_jugadores = []
    
    for i, pais in enumerate(paises[:num_paises], 1):
        print(f"\n📁 [{i}/{num_paises}] PROCESANDO PAÍS: {pais['nombre']}")
        
        jugadores_pais = obtener_jugadores_desde_pais(driver, pais['url'], pais['nombre'])
        
        if not jugadores_pais:
            print(f"  ⚠️ No se encontraron jugadores")
            continue
        
        # Limitar jugadores si es necesario
        if num_jugadores > 0 and num_jugadores < len(jugadores_pais):
            jugadores_procesar = jugadores_pais[:num_jugadores]
            print(f"  📊 Procesando {num_jugadores} de {len(jugadores_pais)} jugadores")
        else:
            jugadores_procesar = jugadores_pais
            print(f"  📊 Procesando todos los {len(jugadores_pais)} jugadores")
        
        # Procesar cada jugador
        for j, jugador_info in enumerate(jugadores_procesar, 1):
            print(f"    [{j}/{len(jugadores_procesar)}] ", end="")
            
            datos = extraer_datos_jugador(driver, jugador_info['url'], jugador_info)
            if datos:
                todos_los_jugadores.append(datos)
            
            # Pausa entre jugadores
            if j < len(jugadores_procesar):
                time.sleep(random.uniform(1, 2))
        
        # Pausa entre países
        if i < num_paises:
            print(f"  ⏳ Pausa de 3 segundos...")
            time.sleep(3)
    
    # Guardar resultados
    guardar_csv(todos_los_jugadores)
    mostrar_resumen(todos_los_jugadores)
    
    print(f"\n✅ PROCESO COMPLETADO!")

except KeyboardInterrupt:
    print("\n\n⚠️ Proceso interrumpido por el usuario")
    if 'todos_los_jugadores' in locals() and todos_los_jugadores:
        guardar_csv(todos_los_jugadores, 'jugadores_mundiales_PARCIAL.csv')
        print(f"💾 Datos parciales guardados")

except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    if 'todos_los_jugadores' in locals() and todos_los_jugadores:
        guardar_csv(todos_los_jugadores, 'jugadores_mundiales_ERROR.csv')

finally:
    if driver:
        print("🔒 Cerrando navegador...")
        driver.quit()