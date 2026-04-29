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
# SCRAPER PARA MUNDIALES 1938 Y 1934
# ============================================

class ScraperJugadoresAntiguos:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        self.start_id = 10918  # 🔥 Continuamos desde 10918 (último ID + 1)
        self.jugadores_procesados = set()
        self.archivo_checkpoint = "jugadores_1938_1934_checkpoint.csv"
        print("🚀 Inicializando scraper para mundiales 1938 y 1934...")
        
    def encontrar_tor_browser(self):
        """Encuentra la ruta de Tor Browser"""
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
        """Encuentra geckodriver.exe en el directorio actual"""
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
        """Espera a que un puerto esté disponible"""
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
        """Inicia Tor Browser"""
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
        """Cierra Tor Browser"""
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
        """Acepta el consentimiento de cookies si aparece"""
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
        """Configura Firefox con proxy de Tor"""
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
        
        try:
            service = Service(executable_path=self.ruta_geckodriver)
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(180)
            return driver
        except Exception as e:
            print(f"  ❌ Error configurando driver: {e}")
            return None
    
    def obtener_con_tor(self, url, descripcion, reintentos=5):
        """Obtiene una página con reintentos usando Tor"""
        
        for intento in range(reintentos):
            driver = self.configurar_driver_con_tor()
            if not driver:
                time.sleep(5)
                continue
            
            try:
                print(f"    🌍 Intento {intento + 1}/{reintentos} - {descripcion}")
                
                driver.get(url)
                time.sleep(5)
                
                self.aceptar_consentimiento(driver)
                
                page_source = driver.page_source.lower()
                title = driver.title.lower()
                
                if "403" in title or "forbidden" in page_source:
                    print(f"    ⚠️ Página bloqueada (403), esperando 30 segundos...")
                    driver.quit()
                    time.sleep(30)
                    continue
                
                print(f"    ✅ Página cargada")
                return driver
                
            except TimeoutException:
                print(f"    ⚠️ Timeout, reintentando...")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(15)
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:100]}")
                try:
                    driver.quit()
                except:
                    pass
                
                if intento < reintentos - 1:
                    espera = 15 * (intento + 1)
                    print(f"    ⏳ Reintentando en {espera} segundos...")
                    time.sleep(espera)
        
        return None
    
    def cargar_checkpoint(self):
        """Carga jugadores ya procesados desde checkpoint"""
        if os.path.exists(self.archivo_checkpoint):
            print(f"📂 Cargando checkpoint desde: {self.archivo_checkpoint}")
            try:
                with open(self.archivo_checkpoint, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'referencia' in row and row['referencia']:
                            self.jugadores_procesados.add(row['referencia'])
                    
                    # Actualizar start_id basado en el último ID
                    max_id = 0
                    with open(self.archivo_checkpoint, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if 'id' in row and row['id'].isdigit():
                                max_id = max(max_id, int(row['id']))
                    
                    if max_id >= self.start_id:
                        self.start_id = max_id + 1
                    
                    print(f"  ✅ Cargados {len(self.jugadores_procesados)} jugadores ya procesados")
                    print(f"  ✅ Continuando desde ID: {self.start_id}")
                    return True
            except Exception as e:
                print(f"  ⚠️ Error cargando checkpoint: {e}")
        
        print("  📝 No se encontró checkpoint, comenzando desde cero")
        return False
    
    def guardar_checkpoint(self, jugadores, es_parcial=False):
        """Guarda checkpoint con los jugadores procesados hasta ahora"""
        if not jugadores:
            return
        
        nombre_archivo = self.archivo_checkpoint if not es_parcial else "jugadores_1938_1934_PARCIAL.csv"
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'pais', 'grupo', 'jugador', 'referencia', 'camiseta', 'posicion']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for j in jugadores:
                writer.writerow({
                    'id': j.get('id', ''),
                    'mundial': j.get('mundial', ''),
                    'pais': j.get('pais', '').strip(),
                    'grupo': j.get('grupo', '').strip(),
                    'jugador': j.get('jugador', '').strip(),
                    'referencia': j.get('referencia', '').strip(),
                    'camiseta': j.get('camiseta', '').strip(),
                    'posicion': j.get('posicion', '').strip()
                })
        
        print(f"💾 Checkpoint guardado: {len(jugadores)} jugadores en '{nombre_archivo}'")
    
    def obtener_jugadores_de_plantel(self, url, año, pais, grupo=""):
        """Extrae jugadores de un plantel específico (para 1938 y 1934)"""
        
        for intento in range(self.reintentos_globales):
            print(f"\n    📄 Procesando {pais} ({año}) - Intento {intento + 1}/{self.reintentos_globales}")
            
            driver = self.obtener_con_tor(url, f"plantel {pais}")
            
            if not driver:
                if intento < self.reintentos_globales - 1:
                    print(f"      ⏳ Reintentando en 15 segundos...")
                    time.sleep(15)
                continue
            
            jugadores = []
            
            try:
                # Verificar bloqueo
                page_source = driver.page_source.lower()
                title = driver.title.lower()
                
                if "403" in title or "forbidden" in page_source:
                    print(f"      ⚠️ Página bloqueada")
                    driver.quit()
                    if intento < self.reintentos_globales - 1:
                        print(f"      ⏳ Esperando 25 segundos...")
                        time.sleep(25)
                    continue
                
                # Buscar tablas de jugadores
                tablas = driver.find_elements(By.CSS_SELECTOR, "table.pad-y5")
                
                if not tablas:
                    print(f"      ⚠️ No se encontraron tablas de jugadores")
                
                for tabla in tablas:
                    try:
                        # Determinar posición por el encabezado
                        try:
                            encabezado = tabla.find_element(By.CSS_SELECTOR, "tr.t-enc-2")
                            texto_encabezado = encabezado.text.strip()
                            
                            posicion = "Desconocida"
                            if "Arquero" in texto_encabezado or "Portero" in texto_encabezado:
                                posicion = "Arquero"
                            elif "Defensor" in texto_encabezado:
                                posicion = "Defensor"
                            elif "Mediocampista" in texto_encabezado:
                                posicion = "Mediocampista"
                            elif "Delantero" in texto_encabezado:
                                posicion = "Delantero"
                            else:
                                continue
                        except:
                            continue
                        
                        # Filas de jugadores
                        filas = tabla.find_elements(By.CSS_SELECTOR, "tr.a-top.bb-2")
                        
                        for fila in filas:
                            try:
                                celdas = fila.find_elements(By.TAG_NAME, "td")
                                if len(celdas) >= 2:
                                    # Número de camiseta (puede estar vacío)
                                    try:
                                        camiseta_texto = celdas[0].text.strip()
                                        if not camiseta_texto or camiseta_texto == "":
                                            camiseta = ""
                                        else:
                                            camiseta = camiseta_texto
                                    except:
                                        camiseta = ""
                                    
                                    # Jugador
                                    try:
                                        enlace = celdas[1].find_element(By.TAG_NAME, "a")
                                        jugador = enlace.text.strip()
                                        href = enlace.get_attribute("href")
                                        referencia = href.split('/')[-1] if href else ""
                                    except:
                                        jugador = celdas[1].text.strip()
                                        referencia = ""
                                    
                                    # Verificar si ya fue procesado
                                    if referencia and referencia in self.jugadores_procesados:
                                        print(f"        ⏭️ {jugador} ya procesado")
                                        continue
                                    
                                    if jugador:
                                        jugadores.append({
                                            'mundial': año,
                                            'pais': pais,
                                            'grupo': grupo,
                                            'jugador': jugador,
                                            'referencia': referencia,
                                            'camiseta': camiseta,
                                            'posicion': posicion
                                        })
                                        self.jugadores_procesados.add(referencia)
                                        print(f"        ✓ {jugador} - #{camiseta or '?'} ({posicion})")
                            except:
                                continue
                    except:
                        continue
                
                print(f"    ✅ Total jugadores para {pais}: {len(jugadores)}")
                return jugadores
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                if intento < self.reintentos_globales - 1:
                    print(f"      ⏳ Reintentando en 15 segundos...")
                    time.sleep(15)
            finally:
                try:
                    driver.quit()
                except:
                    pass
        
        print(f"    ❌ No se pudo procesar {pais}")
        return []
    
    def ejecutar(self):
        """Ejecuta el scraping para 1938 y 1934"""
        
        # Cargar checkpoint
        self.cargar_checkpoint()
        
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return []
        
        try:
            todos_jugadores = []
            
            # ============================================
            # MUNDIAL 1938 - FRANCIA
            # ============================================
            print("\n" + "="*60)
            print("🏆 MUNDIAL 1938 - FRANCIA")
            print("="*60)
            
            paises_1938 = [
                ("Alemania", "https://www.losmundialesdefutbol.com/planteles/1938_alemania_jugadores.php"),
                ("Austria", "https://www.losmundialesdefutbol.com/planteles/1938_austria_jugadores.php"),
                ("Bélgica", "https://www.losmundialesdefutbol.com/planteles/1938_belgica_jugadores.php"),
                ("Brasil", "https://www.losmundialesdefutbol.com/planteles/1938_brasil_jugadores.php"),
                ("Checoslovaquia", "https://www.losmundialesdefutbol.com/planteles/1938_checoslovaquia_jugadores.php"),
                ("Cuba", "https://www.losmundialesdefutbol.com/planteles/1938_cuba_jugadores.php"),
                ("Francia", "https://www.losmundialesdefutbol.com/planteles/1938_francia_jugadores.php"),
                ("Hungría", "https://www.losmundialesdefutbol.com/planteles/1938_hungria_jugadores.php"),
                ("Indias Orientales", "https://www.losmundialesdefutbol.com/planteles/1938_indias_orientales_jugadores.php"),
                ("Italia", "https://www.losmundialesdefutbol.com/planteles/1938_italia_jugadores.php"),
                ("Noruega", "https://www.losmundialesdefutbol.com/planteles/1938_noruega_jugadores.php"),
                ("Países Bajos", "https://www.losmundialesdefutbol.com/planteles/1938_holanda_jugadores.php"),
                ("Polonia", "https://www.losmundialesdefutbol.com/planteles/1938_polonia_jugadores.php"),
                ("Rumania", "https://www.losmundialesdefutbol.com/planteles/1938_rumania_jugadores.php"),
                ("Suecia", "https://www.losmundialesdefutbol.com/planteles/1938_suecia_jugadores.php"),
                ("Suiza", "https://www.losmundialesdefutbol.com/planteles/1938_suiza_jugadores.php"),
            ]
            
            for i, (pais, url) in enumerate(paises_1938, 1):
                print(f"\n📁 [{i}/{len(paises_1938)}] {pais}")
                jugadores = self.obtener_jugadores_de_plantel(url, "1938", pais, "")
                todos_jugadores.extend(jugadores)
                
                # Guardar checkpoint después de cada país
                if jugadores:
                    self.guardar_checkpoint(todos_jugadores, es_parcial=True)
                
                if i < len(paises_1938):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            # ============================================
            # MUNDIAL 1934 - ITALIA
            # ============================================
            print("\n" + "="*60)
            print("🏆 MUNDIAL 1934 - ITALIA")
            print("="*60)
            
            paises_1934 = [
                ("Suiza", "https://www.losmundialesdefutbol.com/planteles/1934_suiza_jugadores.php"),
                ("Suecia", "https://www.losmundialesdefutbol.com/planteles/1934_suecia_jugadores.php"),
                ("Rumania", "https://www.losmundialesdefutbol.com/planteles/1934_rumania_jugadores.php"),
                ("Países Bajos", "https://www.losmundialesdefutbol.com/planteles/1934_holanda_jugadores.php"),
                ("Italia", "https://www.losmundialesdefutbol.com/planteles/1934_italia_jugadores.php"),
                ("Hungría", "https://www.losmundialesdefutbol.com/planteles/1934_hungria_jugadores.php"),
                ("Francia", "https://www.losmundialesdefutbol.com/planteles/1934_francia_jugadores.php"),
                ("Estados Unidos", "https://www.losmundialesdefutbol.com/planteles/1934_estados_unidos_jugadores.php"),
                ("España", "https://www.losmundialesdefutbol.com/planteles/1934_espana_jugadores.php"),
                ("Egipto", "https://www.losmundialesdefutbol.com/planteles/1934_egipto_jugadores.php"),
                ("Checoslovaquia", "https://www.losmundialesdefutbol.com/planteles/1934_checoslovaquia_jugadores.php"),
                ("Brasil", "https://www.losmundialesdefutbol.com/planteles/1934_brasil_jugadores.php"),
                ("Bélgica", "https://www.losmundialesdefutbol.com/planteles/1934_belgica_jugadores.php"),
                ("Austria", "https://www.losmundialesdefutbol.com/planteles/1934_austria_jugadores.php"),
                ("Argentina", "https://www.losmundialesdefutbol.com/planteles/1934_argentina_jugadores.php"),
                ("Alemania", "https://www.losmundialesdefutbol.com/planteles/1934_alemania_jugadores.php"),
            ]
            
            for i, (pais, url) in enumerate(paises_1934, 1):
                print(f"\n📁 [{i}/{len(paises_1934)}] {pais}")
                jugadores = self.obtener_jugadores_de_plantel(url, "1934", pais, "")
                todos_jugadores.extend(jugadores)
                
                # Guardar checkpoint después de cada país
                if jugadores:
                    self.guardar_checkpoint(todos_jugadores, es_parcial=True)
                
                if i < len(paises_1934):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            return todos_jugadores
            
        finally:
            self.cerrar_tor_browser()
    
    def guardar_csv(self, jugadores, nombre='jugadores_1938_1934.csv'):
        """Guarda los datos en CSV con IDs comenzando desde 10918"""
        if not jugadores:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'pais', 'grupo', 'jugador', 'referencia', 'camiseta', 'posicion']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for i, j in enumerate(jugadores, self.start_id):
                writer.writerow({
                    'id': i,
                    'mundial': j.get('mundial', ''),
                    'pais': j.get('pais', '').strip(),
                    'grupo': j.get('grupo', '').strip(),
                    'jugador': j.get('jugador', '').strip(),
                    'referencia': j.get('referencia', '').strip(),
                    'camiseta': j.get('camiseta', '').strip(),
                    'posicion': j.get('posicion', '').strip()
                })
        
        print(f"\n💾 Guardados {len(jugadores)} jugadores en '{nombre}'")
        print(f"📊 IDs desde {self.start_id} hasta {self.start_id + len(jugadores) - 1}")

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("⚽ SCRAPER PARA MUNDIALES 1938 Y 1934")
    print("="*60)
    print("\n📌 Características:")
    print("   • Mundial 1938: 16 países")
    print("   • Mundial 1934: 16 países")
    print("   • Total: 32 países")
    print(f"   • ID inicial: {10918}")
    print("\n📊 Datos a extraer:")
    print("   • Año del mundial")
    print("   • País")
    print("   • Grupo (vacío para estos mundiales)")
    print("   • Jugador")
    print("   • Referencia (archivo PHP)")
    print("   • Camiseta (puede estar vacía)")
    print("   • Posición")
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperJugadoresAntiguos()
    
    if not scraper.ruta_tor:
        print("\n❌ No se encontró Tor Browser")
        exit()
    
    if not scraper.ruta_geckodriver:
        print("\n❌ No se encontró geckodriver.exe")
        print("💡 Debe estar en la misma carpeta que este script")
        exit()
    
    try:
        nombre = input("\nNombre CSV (Enter para 'jugadores_1938_1934.csv'): ").strip()
        nombre = nombre or 'jugadores_1938_1934.csv'
        
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING...")
        print("⏱️  Procesando 32 países...")
        print("="*60)
        
        jugadores = scraper.ejecutar()
        
        if jugadores:
            scraper.guardar_csv(jugadores, nombre)
            print(f"\n✅ COMPLETADO!")
            print(f"📁 Archivo: {nombre}")
            print(f"📊 Total jugadores: {len(jugadores)}")
        else:
            print("\n❌ No hay datos")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido")
        scraper.cerrar_tor_browser()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        scraper.cerrar_tor_browser()