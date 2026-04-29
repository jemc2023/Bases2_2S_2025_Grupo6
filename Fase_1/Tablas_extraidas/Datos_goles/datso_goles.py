from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import random
import re
import os
import subprocess
import psutil
import socket

# ============================================
# SCRAPER DE GOLES Y PENALES - VERSIÓN QUE GUARDA TODOS LOS PENALES
# ============================================

class ScraperGolesPenales:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        self.contador_goles = 1
        self.contador_penales = 1
        # Archivos de salida
        self.archivo_goles = 'goles.csv'
        self.archivo_penales = 'penales.csv'
        self.archivo_errores = 'errores.csv'
        print("🚀 Inicializando scraper de goles y penales...")
        
    def encontrar_tor_browser(self):
        rutas_posibles = [
            r"C:\programas mios\Tor Browser\Browser\firefox.exe",
            r"C:\Users\Angel\Desktop\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files\Tor Browser\Browser\firefox.exe",
        ]
        
        for ruta in rutas_posibles:
            if os.path.exists(ruta):
                print(f"  ✅ Tor Browser encontrado en: {ruta}")
                return ruta
        
        print("  ❌ No se encontró Tor Browser")
        return None
    
    def encontrar_geckodriver(self):
        ruta_local = os.path.join(os.path.dirname(__file__), "geckodriver.exe")
        if os.path.exists(ruta_local):
            print(f"  ✅ GeckoDriver encontrado en: {ruta_local}")
            return ruta_local
        
        if os.path.exists("geckodriver.exe"):
            print(f"  ✅ GeckoDriver encontrado en el directorio actual")
            return "geckodriver.exe"
        
        print("  ❌ No se encontró geckodriver.exe")
        return None
    
    def esperar_puerto(self, puerto, timeout=60):
        print(f"  ⏳ Esperando puerto {puerto}...")
        inicio = time.time()
        while time.time() - inicio < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', puerto))
                sock.close()
                if result == 0:
                    print(f"  ✅ Puerto {puerto} disponible")
                    return True
            except:
                pass
            time.sleep(2)
        return False
    
    def iniciar_tor_browser(self):
        if not self.ruta_tor:
            return False
        
        try:
            print("  🔥 Iniciando Tor Browser...")
            tor_dir = os.path.dirname(self.ruta_tor)
            
            self.tor_process = subprocess.Popen(
                [self.ruta_tor, "--marionette"],
                cwd=tor_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print("  ⏳ Esperando 60 segundos para que Tor se conecte...")
            time.sleep(60)
            
            self.esperar_puerto(self.puerto_proxy, 30)
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def cerrar_tor_browser(self):
        if self.tor_process:
            try:
                parent = psutil.Process(self.tor_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                print("  🔒 Tor Browser cerrado")
            except:
                pass
    
    def aceptar_consentimiento(self, driver):
        try:
            print("    🔍 Buscando botón de consentimiento...")
            
            selectores = [
                "//button[@aria-label='Consent']",
                "//button[contains(text(), 'Consent')]",
                "//button[contains(text(), 'Aceptar')]",
                "//button[contains(text(), 'Accept')]",
                ".fc-button.fc-cta-consent",
            ]
            
            for selector in selectores:
                try:
                    if selector.startswith("//"):
                        boton = driver.find_element(By.XPATH, selector)
                    else:
                        boton = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if boton and boton.is_displayed():
                        print(f"    ✅ Botón encontrado")
                        boton.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            print("    ⏭️ No se encontró botón de consentimiento")
            return False
            
        except Exception as e:
            return False
    
    def configurar_driver_con_tor(self):
        if not self.ruta_tor or not self.ruta_geckodriver:
            return None
        
        options = Options()
        
        tor_profile = os.path.join(os.path.dirname(self.ruta_tor), "TorBrowser", "Data", "Browser", "profile.default")
        if os.path.exists(tor_profile):
            options.profile = tor_profile
        
        options.binary_location = self.ruta_tor
        
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", self.puerto_proxy)
        options.set_preference("network.proxy.socks_version", 5)
        options.set_preference("network.proxy.socks_remote_dns", True)
        
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0")
        
        try:
            service = Service(executable_path=self.ruta_geckodriver)
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(180)
            return driver
        except Exception as e:
            print(f"  ❌ Error configurando driver: {e}")
            return None
    
    def obtener_con_tor(self, url, descripcion, reintentos=5):
        for intento in range(reintentos):
            driver = self.configurar_driver_con_tor()
            if not driver:
                time.sleep(5)
                continue
            
            try:
                print(f"    🌍 Intento {intento + 1}/{reintentos} - {descripcion}")
                
                driver.set_page_load_timeout(120)
                driver.get(url)
                time.sleep(random.uniform(5, 8))
                
                self.aceptar_consentimiento(driver)
                
                title = driver.title.lower()
                page_source = driver.page_source.lower()
                
                if "403" in title or "forbidden" in page_source:
                    print(f"    ⚠️ Página bloqueada (403)")
                    driver.quit()
                    time.sleep(60)
                    continue
                
                print(f"    ✅ Página cargada")
                return driver
                
            except TimeoutException:
                print(f"    ⚠️ Timeout")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(30)
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:100]}")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(30)
        
        return None
    
    def extraer_info_basica(self, driver, fila):
        return {
            'mundial': fila['mundial'],
            'pais1': fila['pais1'],
            'pais2': fila['pais2'],
            'tipo_ronda': fila['tipo_ronda'],
            'grupo': fila['grupo']
        }
    
    def extraer_goles_y_penales_de_goles(self, driver, info):
        """Extrae goles y también guarda los penales que aparecen en la sección de goles"""
        goles = []
        penales_de_goles = []
        # Usar un set para evitar duplicados de penales
        penales_vistos = set()
        
        try:
            goles_divs = driver.find_elements(By.CSS_SELECTOR, "div.a-left.clearfix.clear.overflow-x-auto div[style*='min-height']")
            print(f"        🔍 Encontrados {len(goles_divs)} posibles goles")
            
            for gol_div in goles_divs:
                try:
                    texto = gol_div.text
                    if not texto or "Goles:" in texto:
                        continue
                    
                    # Extraer minuto
                    match_min = re.search(r'(\d+)\'?', texto)
                    if not match_min:
                        continue
                    minuto = int(match_min.group(1))
                    
                    # Determinar si fue en tiempo extra
                    fue_tiempo_extra = (minuto > 90) or 'ET' in texto or 'et' in texto.lower()
                    
                    # Extraer jugador
                    try:
                        enlace = gol_div.find_element(By.TAG_NAME, "a")
                        jugador = enlace.text.strip()
                        referencia = enlace.get_attribute("href").split('/')[-1]
                    except:
                        lineas = texto.split('\n')
                        jugador = lineas[1].strip() if len(lineas) >= 2 else texto
                        referencia = ""
                    
                    jugador_limpio = re.sub(r'\s*\([^)]*\)', '', jugador).strip()
                    
                    estilo = gol_div.get_attribute("style") or ""
                    if "padding-right" in estilo or "right" in estilo:
                        equipo = info['pais1']
                    else:
                        equipo = info['pais2']
                    
                    es_penal = '(pen)' in texto.lower() or 'de penal' in texto.lower()
                    
                    # Crear una clave única para evitar duplicados
                    clave_penal = f"{jugador_limpio}_{minuto}_{equipo}"
                    
                    if es_penal and clave_penal not in penales_vistos:
                        print(f"        ⚠️ Es penal, guardando en penales: {jugador_limpio}")
                        penal = {
                            'id': self.contador_penales,
                            'mundial': info['mundial'],
                            'pais1': info['pais1'],
                            'pais2': info['pais2'],
                            'tipo_ronda': info['tipo_ronda'],
                            'grupo': info['grupo'],
                            'turno': 0,
                            'jugador': jugador_limpio,
                            'referencia': referencia,
                            'equipo': equipo,
                            'anotado': True,
                            'detalle': 'gol_normal'
                        }
                        penales_de_goles.append(penal)
                        penales_vistos.add(clave_penal)
                        self.contador_penales += 1
                    elif not es_penal:
                        goles.append({
                            'id': self.contador_goles,
                            'mundial': info['mundial'],
                            'pais1': info['pais1'],
                            'pais2': info['pais2'],
                            'tipo_ronda': info['tipo_ronda'],
                            'grupo': info['grupo'],
                            'minuto': minuto,
                            'jugador': jugador_limpio,
                            'referencia': referencia,
                            'equipo': equipo,
                            'fue_tiempo_extra': fue_tiempo_extra
                        })
                        self.contador_goles += 1
                        print(f"        ⚽ Gol: {minuto}' {jugador_limpio} ({equipo}){' (TE)' if fue_tiempo_extra else ''}")
                        
                except Exception as e:
                    print(f"        ⚠️ Error en gol: {e}")
                    continue
                    
        except Exception as e:
            print(f"        ⚠️ Error general en goles: {e}")
        
        return goles, penales_de_goles
    
    def extraer_penales_de_tanda(self, driver, info):
        """Extrae los penales de la tanda (con colores) - VERSIÓN CORREGIDA"""
        penales = []
        try:
            # Buscar la sección de penales
            try:
                encabezado = driver.find_element(By.XPATH, "//*[contains(text(), 'Definición por Penales')]")
                print(f"        🎯 ENCONTRADA SECCIÓN DE PENALES")
            except NoSuchElementException:
                return []
            
            # Buscar el contenedor que sigue
            contenedor = encabezado.find_element(By.XPATH, "./following::div[contains(@class, 'left')]")
            
            # Ver quién patea primero
            try:
                primero_elem = driver.find_element(By.XPATH, "//div[contains(text(), 'patea primero')]")
                texto_primero = primero_elem.text
                patea_primero = texto_primero.replace('patea primero', '').strip()
                print(f"        🎯 Patea primero: {patea_primero}")
            except:
                patea_primero = ""
                print(f"        🎯 No se especifica quién patea primero")
            
            # Encontrar todos los penales - ¡CORREGIDO!
            # La columna izquierda = equipo que patea primero
            # La columna derecha = equipo que patea segundo
            penales_primero = contenedor.find_elements(By.CSS_SELECTOR, "div.left.a-right.w-50")
            penales_segundo = contenedor.find_elements(By.CSS_SELECTOR, "div.left.w-50:not(.a-right)")
            
            print(f"        🎯 Penales de {patea_primero}: {len(penales_primero)}")
            print(f"        🎯 Penales del otro equipo: {len(penales_segundo)}")
            
            # Determinar qué equipo es cada uno
            if patea_primero == info['pais1']:
                equipo_primero = info['pais1']
                equipo_segundo = info['pais2']
            else:
                equipo_primero = info['pais2']
                equipo_segundo = info['pais1']
            
            print(f"        🎯 {equipo_primero} patea primero, {equipo_segundo} patea segundo")
            
            # Procesar penales por turno - AHORA CORRECTO
            # El número de turnos es el máximo entre los dos arrays
            max_penales = max(len(penales_primero), len(penales_segundo))
            
            for i in range(max_penales):
                turno = i + 1
                print(f"        🎯 Turno {turno}:")
                
                # Penal del equipo que patea PRIMERO (columna izquierda)
                if i < len(penales_primero):
                    penal_data = self._procesar_penal_div(penales_primero[i])
                    if penal_data:
                        penal = {
                            'id': self.contador_penales,
                            'mundial': info['mundial'],
                            'pais1': info['pais1'],
                            'pais2': info['pais2'],
                            'tipo_ronda': info['tipo_ronda'],
                            'grupo': info['grupo'],
                            'turno': turno,
                            'jugador': penal_data['jugador'],
                            'referencia': penal_data['referencia'],
                            'equipo': equipo_primero,
                            'anotado': penal_data['anotado'],
                            'detalle': penal_data['detalle']
                        }
                        penales.append(penal)
                        self.contador_penales += 1
                        
                        estado = "✅ GOL" if penal_data['anotado'] else f"❌ {penal_data['detalle'].upper()}"
                        print(f"          {estado} - {penal_data['jugador']} ({equipo_primero})")
                
                # Penal del equipo que patea SEGUNDO (columna derecha)
                if i < len(penales_segundo):
                    penal_data = self._procesar_penal_div(penales_segundo[i])
                    if penal_data:
                        penal = {
                            'id': self.contador_penales,
                            'mundial': info['mundial'],
                            'pais1': info['pais1'],
                            'pais2': info['pais2'],
                            'tipo_ronda': info['tipo_ronda'],
                            'grupo': info['grupo'],
                            'turno': turno,
                            'jugador': penal_data['jugador'],
                            'referencia': penal_data['referencia'],
                            'equipo': equipo_segundo,
                            'anotado': penal_data['anotado'],
                            'detalle': penal_data['detalle']
                        }
                        penales.append(penal)
                        self.contador_penales += 1
                        
                        estado = "✅ GOL" if penal_data['anotado'] else f"❌ {penal_data['detalle'].upper()}"
                        print(f"          {estado} - {penal_data['jugador']} ({equipo_segundo})")
                
        except Exception as e:
            print(f"      ⚠️ Error en penales: {e}")
        
        return penales
    
    def _procesar_penal_div(self, div):
        """Procesa un div individual de penal"""
        try:
            # Obtener el HTML para analizar colores
            html = div.get_attribute("innerHTML")
            
            # Determinar si fue gol (verde) o fallado (rojo #C33)
            if 'background-color: green' in html or '#339966' in html:
                anotado = True
                detalle = ""
                print(f"            Color: VERDE → Gol")
            else:
                anotado = False
                if '(atajado)' in html:
                    detalle = "atajado"
                elif '(palo)' in html:
                    detalle = "palo"
                elif '(desviado)' in html:
                    detalle = "desviado"
                else:
                    detalle = "fallado"
                print(f"            Color: ROJO → {detalle.upper()}")
            
            # Extraer jugador
            try:
                enlace = div.find_element(By.TAG_NAME, "a")
                jugador = enlace.text.strip()
                referencia = enlace.get_attribute("href").split('/')[-1]
                print(f"            Jugador: {jugador} (con enlace)")
            except:
                texto = div.text.strip()
                # Eliminar cualquier texto entre paréntesis
                jugador = re.sub(r'\s*\([^)]*\)', '', texto).strip()
                referencia = ""
                print(f"            Jugador: {jugador} (sin enlace)")
            
            return {
                'jugador': jugador,
                'referencia': referencia,
                'anotado': anotado,
                'detalle': detalle
            }
        except Exception as e:
            print(f"            ❌ Error procesando penal: {e}")
            return None
    
    def guardar_goles(self, goles):
        if not goles:
            return
        
        modo = 'a' if os.path.exists(self.archivo_goles) else 'w'
        with open(self.archivo_goles, modo, newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 
                     'minuto', 'jugador', 'referencia', 'equipo', 'fue_tiempo_extra']
            writer = csv.DictWriter(f, fieldnames=campos)
            if modo == 'w':
                writer.writeheader()
            for gol in goles:
                writer.writerow(gol)
        
        print(f"      💾 Guardados {len(goles)} goles en {self.archivo_goles}")
    
    def guardar_penales(self, penales):
        if not penales:
            return
        
        modo = 'a' if os.path.exists(self.archivo_penales) else 'w'
        with open(self.archivo_penales, modo, newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 
                     'turno', 'jugador', 'referencia', 'equipo', 'anotado', 'detalle']
            writer = csv.DictWriter(f, fieldnames=campos)
            if modo == 'w':
                writer.writeheader()
            for penal in penales:
                writer.writerow(penal)
        
        print(f"      💾 Guardados {len(penales)} penales en {self.archivo_penales}")
    
    def guardar_error(self, fila, error):
        modo = 'a' if os.path.exists(self.archivo_errores) else 'w'
        with open(self.archivo_errores, modo, newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if modo == 'w':
                writer.writerow(['mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'url', 'error'])
            writer.writerow([
                fila.get('mundial', ''),
                fila.get('pais1', ''),
                fila.get('pais2', ''),
                fila.get('tipo_ronda', ''),
                fila.get('grupo', ''),
                fila.get('url', ''),
                str(error)
            ])
    
    def procesar_partido(self, fila):
        url = fila['url']
        print(f"\n    📄 {fila['pais1']} vs {fila['pais2']} - {fila['tipo_ronda']} {fila['mundial']}")
        
        driver = self.obtener_con_tor(url, "partido")
        if not driver:
            self.guardar_error(fila, "No se pudo cargar la página")
            return False
        
        try:
            info = self.extraer_info_basica(driver, fila)
            
            # Extraer goles y penales de la sección de goles
            goles, penales_de_goles = self.extraer_goles_y_penales_de_goles(driver, info)
            if goles:
                self.guardar_goles(goles)
            
            # Guardar penales de la sección de goles
            if penales_de_goles:
                self.guardar_penales(penales_de_goles)
            
            # Extraer penales de la tanda
            penales_tanda = self.extraer_penales_de_tanda(driver, info)
            if penales_tanda:
                self.guardar_penales(penales_tanda)
            
            return True
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            self.guardar_error(fila, str(e))
            return False
        finally:
            try:
                driver.quit()
            except:
                pass
    
    def ejecutar(self, archivo_csv, max_partidos=None):
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return
        
        try:
            # Leer CSV de entrada
            with open(archivo_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                partidos = list(reader)
            
            print(f"\n📊 Partidos a procesar: {len(partidos)}")
            
            if max_partidos and max_partidos < len(partidos):
                partidos = partidos[:max_partidos]
                print(f"📊 Limitando a {max_partidos} partidos")
            
            # Cargar últimos IDs
            if os.path.exists(self.archivo_goles):
                with open(self.archivo_goles, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'id' in row and row['id'].isdigit():
                            self.contador_goles = max(self.contador_goles, int(row['id']) + 1)
                print(f"📊 Último ID goles: {self.contador_goles - 1}")
            
            if os.path.exists(self.archivo_penales):
                with open(self.archivo_penales, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'id' in row and row['id'].isdigit():
                            self.contador_penales = max(self.contador_penales, int(row['id']) + 1)
                print(f"📊 Último ID penales: {self.contador_penales - 1}")
            
            exitosos = 0
            fallidos = 0
            
            for i, fila in enumerate(partidos, 1):
                print(f"\n📁 [{i}/{len(partidos)}]", end="")
                
                if self.procesar_partido(fila):
                    exitosos += 1
                else:
                    fallidos += 1
                
                if i < len(partidos):
                    pausa = random.uniform(3, 6)
                    print(f"    ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            print("\n" + "="*60)
            print("✅ PROCESO COMPLETADO!")
            print("="*60)
            print(f"📊 Partidos exitosos: {exitosos}")
            print(f"📊 Partidos fallidos: {fallidos}")
            print(f"📁 Archivos generados:")
            
            for archivo in [self.archivo_goles, self.archivo_penales, self.archivo_errores]:
                if os.path.exists(archivo):
                    size = os.path.getsize(archivo)
                    with open(archivo, 'r', encoding='utf-8-sig') as f:
                        lineas = len(f.readlines())
                    print(f"   • {archivo} - {lineas-1} registros ({size} bytes)")
                else:
                    print(f"   • {archivo} - NO EXISTE")
            
        finally:
            self.cerrar_tor_browser()

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("⚽ SCRAPER DE GOLES Y PENALES - VERSIÓN FINAL")
    print("="*60)
    print("\n📌 Este script:")
    print("   1. Lee un CSV con la lista de partidos")
    print("   2. Para cada partido, extrae GOLES y PENALES (de ambas secciones)")
    print("   3. Genera 2 archivos CSV: goles.csv y penales.csv")
    
    archivo_entrada = input("\n📂 Nombre del CSV de entrada (ej: 'todos_los_partidos.csv'): ").strip()
    if not archivo_entrada:
        archivo_entrada = "todos_los_partidos.csv"
    
    if not os.path.exists(archivo_entrada):
        print(f"❌ No se encontró el archivo {archivo_entrada}")
        exit()
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperGolesPenales()
    
    if not scraper.ruta_tor:
        print("\n❌ No se encontró Tor Browser")
        exit()
    
    if not scraper.ruta_geckodriver:
        print("\n❌ No se encontró geckodriver.exe")
        print("💡 Debe estar en la misma carpeta que este script")
        exit()
    
    try:
        max_partidos = input("\n¿Máximo de partidos a procesar? (Enter para todos): ").strip()
        max_partidos = int(max_partidos) if max_partidos else None
        
        print("\n" + "="*60)
        print("🚀 INICIANDO PROCESO...")
        print("⏱️  Esto puede tomar varias horas")
        print("="*60)
        
        scraper.ejecutar(archivo_entrada, max_partidos)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido")
        scraper.cerrar_tor_browser()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        scraper.cerrar_tor_browser()