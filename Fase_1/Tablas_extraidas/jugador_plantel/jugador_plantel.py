from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import random
import re
import os
import subprocess
import psutil
import socket

# ============================================
# SCRAPER DEFINITIVO - CON GECKODRIVER LOCAL
# ============================================

class ScraperJugadoresTor:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        print("🚀 Inicializando scraper con Tor Browser...")
        
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
        # Buscar en el mismo directorio del script
        ruta_local = os.path.join(os.path.dirname(__file__), "geckodriver.exe")
        if os.path.exists(ruta_local):
            print(f"  ✅ GeckoDriver encontrado en: {ruta_local}")
            return ruta_local
        
        # Buscar en el directorio actual
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
        """Configura Firefox con proxy de Tor usando geckodriver local"""
        if not self.ruta_tor or not self.ruta_geckodriver:
            return None
        
        options = Options()
        
        # Usar el perfil de Tor
        tor_profile = os.path.join(os.path.dirname(self.ruta_tor), "TorBrowser", "Data", "Browser", "profile.default")
        if os.path.exists(tor_profile):
            options.profile = tor_profile
        
        options.binary_location = self.ruta_tor
        
        # Configurar proxy SOCKS5 de Tor
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", self.puerto_proxy)
        options.set_preference("network.proxy.socks_version", 5)
        options.set_preference("network.proxy.socks_remote_dns", True)
        
        # Anti-detección
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0")
        
        try:
            # Usar geckodriver local
            service = Service(executable_path=self.ruta_geckodriver)
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(120)
            return driver
        except Exception as e:
            print(f"  ❌ Error configurando driver: {e}")
            return None
    
    def obtener_con_tor(self, url, descripcion, reintentos=2):
        """Obtiene una página con reintentos"""
        
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
                
                # Verificar errores
                page_source = driver.page_source.lower()
                title = driver.title.lower()
                
                if "tor exited" in page_source:
                    print(f"    ⚠️ Error de Tor, reintentando...")
                    driver.quit()
                    time.sleep(10)
                    continue
                
                if "403" in title or "forbidden" in page_source:
                    print(f"    ⚠️ Página bloqueada (403)")
                    driver.quit()
                    time.sleep(15)
                    continue
                
                print(f"    ✅ Página cargada")
                return driver
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:100]}")
                try:
                    driver.quit()
                except:
                    pass
                
                if intento < reintentos - 1:
                    print(f"    ⏳ Reintentando en 10 segundos...")
                    time.sleep(10)
        
        return None
    
    def obtener_lista_mundiales(self):
        """Obtiene todos los mundiales"""
        print("\n🌍 Obteniendo lista de mundiales...")
        
        driver = self.obtener_con_tor(
            "https://www.losmundialesdefutbol.com/mundiales.php", 
            "página principal"
        )
        
        if not driver:
            print("❌ No se pudo acceder")
            return []
        
        mundiales = []
        
        try:
            tablas = driver.find_elements(By.CSS_SELECTOR, "table.c0s5")
            
            if tablas:
                enlaces = tablas[0].find_elements(By.CSS_SELECTOR, "a[href*='mundial']")
                
                for enlace in enlaces:
                    try:
                        href = enlace.get_attribute("href")
                        texto = enlace.text.strip()
                        
                        if href and texto and "Mundial" in texto:
                            match = re.search(r'\b(19|20)\d{2}\b', texto)
                            if match:
                                año = match.group()
                                
                                if año == '2026':
                                    print(f"  ⏭️ Ignorando {texto}")
                                    continue
                                
                                # Construir URL completa
                                if not href.startswith('http'):
                                    if href.startswith('/'):
                                        href = f"https://www.losmundialesdefutbol.com{href}"
                                    elif href.startswith('mundiales/'):
                                        href = f"https://www.losmundialesdefutbol.com/{href}"
                                
                                mundiales.append({
                                    'año': año,
                                    'nombre': texto,
                                    'url': href
                                })
                                print(f"  ✓ {texto}")
                    except:
                        continue
            
            mundiales.sort(key=lambda x: x['año'], reverse=True)
            print(f"\n✅ Total mundiales: {len(mundiales)}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return mundiales
    
    def extraer_planteles_por_mundial(self, mundial):
        """Extrae los planteles de un mundial con reintentos"""
        
        for intento in range(self.reintentos_globales):
            print(f"\n  📂 Procesando {mundial['año']} - {mundial['nombre']} (intento {intento + 1}/{self.reintentos_globales})")
            
            driver = self.obtener_con_tor(mundial['url'], f"mundial {mundial['año']}")
            
            if not driver:
                if intento < self.reintentos_globales - 1:
                    print(f"    ⏳ Esperando 20 segundos...")
                    time.sleep(20)
                continue
            
            planteles = []
            
            try:
                # Verificar bloqueo
                page_source = driver.page_source.lower()
                title = driver.title.lower()
                
                if "403" in title or "forbidden" in page_source:
                    print(f"    ⚠️ Página bloqueada - Reintento {intento + 1}")
                    driver.quit()
                    if intento < self.reintentos_globales - 1:
                        print(f"    ⏳ Esperando 30 segundos para cambiar IP...")
                        time.sleep(30)
                    continue
                
                # Buscar filas de grupos
                filas_grupo = driver.find_elements(By.CSS_SELECTOR, "tr.a-top")
                
                for fila in filas_grupo:
                    try:
                        celdas = fila.find_elements(By.TAG_NAME, "td")
                        if len(celdas) < 3:
                            continue
                        
                        grupo = celdas[0].text.strip()
                        
                        if not grupo or len(grupo) > 3:
                            continue
                        
                        paises_celda = celdas[2]
                        enlaces_paises = paises_celda.find_elements(By.CSS_SELECTOR, "a[href*='planteles/']")
                        
                        for enlace in enlaces_paises:
                            try:
                                href = enlace.get_attribute("href")
                                pais = enlace.text.strip()
                                
                                if pais and len(pais) > 2 and href:
                                    planteles.append({
                                        'mundial': mundial['año'],
                                        'pais': pais,
                                        'grupo': grupo,
                                        'url_plantel': href
                                    })
                                    print(f"      ✓ {pais} - Grupo {grupo}")
                            except:
                                continue
                    except:
                        continue
                
                print(f"    ✅ Total planteles: {len(planteles)}")
                return planteles
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                if intento < self.reintentos_globales - 1:
                    print(f"    ⏳ Reintentando en 20 segundos...")
                    time.sleep(20)
            finally:
                try:
                    driver.quit()
                except:
                    pass
        
        print(f"  ❌ No se pudo procesar {mundial['año']}")
        return []
    
    def extraer_jugadores_de_plantel(self, plantel):
        """Extrae los jugadores de un plantel con reintentos"""
        
        for intento in range(self.reintentos_globales):
            print(f"\n        📄 Procesando {plantel['pais']} ({plantel['mundial']}) - Intento {intento + 1}/{self.reintentos_globales}")
            
            driver = self.obtener_con_tor(
                plantel['url_plantel'], 
                f"plantel {plantel['pais']}"
            )
            
            if not driver:
                if intento < self.reintentos_globales - 1:
                    print(f"          ⏳ Reintentando en 15 segundos...")
                    time.sleep(15)
                continue
            
            jugadores = []
            
            try:
                # Verificar bloqueo
                page_source = driver.page_source.lower()
                title = driver.title.lower()
                
                if "403" in title or "forbidden" in page_source:
                    print(f"          ⚠️ Página bloqueada")
                    driver.quit()
                    if intento < self.reintentos_globales - 1:
                        print(f"          ⏳ Esperando 25 segundos...")
                        time.sleep(25)
                    continue
                
                # Buscar tablas de jugadores
                tablas = driver.find_elements(By.CSS_SELECTOR, "table.pad-y5")
                
                for tabla in tablas:
                    try:
                        # Determinar posición
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
                        
                        # Extraer jugadores
                        filas = tabla.find_elements(By.CSS_SELECTOR, "tr.a-top.bb-2")
                        
                        for fila in filas:
                            try:
                                celdas = fila.find_elements(By.TAG_NAME, "td")
                                if len(celdas) >= 2:
                                    camiseta = celdas[0].text.strip()
                                    
                                    enlace = celdas[1].find_element(By.TAG_NAME, "a")
                                    jugador = enlace.text.strip()
                                    href = enlace.get_attribute("href")
                                    
                                    referencia = href.split('/')[-1] if href else ""
                                    
                                    if jugador and camiseta:
                                        jugadores.append({
                                            'mundial': plantel['mundial'],
                                            'pais': plantel['pais'],
                                            'grupo': plantel['grupo'],
                                            'jugador': jugador,
                                            'referencia': referencia,
                                            'camiseta': camiseta,
                                            'posicion': posicion
                                        })
                                        print(f"            ✓ {jugador} - #{camiseta} ({posicion})")
                            except:
                                continue
                    except:
                        continue
                
                print(f"        ✅ Total jugadores: {len(jugadores)}")
                return jugadores
                
            except Exception as e:
                print(f"          ❌ Error: {e}")
                if intento < self.reintentos_globales - 1:
                    print(f"          ⏳ Reintentando en 15 segundos...")
                    time.sleep(15)
            finally:
                try:
                    driver.quit()
                except:
                    pass
        
        print(f"        ❌ No se pudo procesar {plantel['pais']}")
        return []
    
    def scrapear_todos(self, max_mundiales=None):
        """Proceso completo"""
        
        # Iniciar Tor
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return []
        
        try:
            # PASO 1: Mundiales
            mundiales = self.obtener_lista_mundiales()
            if not mundiales:
                return []
            
            if max_mundiales:
                mundiales = mundiales[:max_mundiales]
                print(f"\n📊 Procesando {max_mundiales} mundiales")
            
            # PASO 2: Planteles
            print("\n" + "="*60)
            print("📋 EXTRAYENDO PLANTELES")
            print("="*60)
            
            todos_planteles = []
            for i, mundial in enumerate(mundiales, 1):
                print(f"\n📁 [{i}/{len(mundiales)}] {mundial['año']}")
                planteles = self.extraer_planteles_por_mundial(mundial)
                todos_planteles.extend(planteles)
                
                if i < len(mundiales):
                    pausa = random.uniform(5, 8)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            print(f"\n✅ TOTAL PLANTELES: {len(todos_planteles)}")
            
            # PASO 3: Jugadores
            print("\n" + "="*60)
            print("📋 EXTRAYENDO JUGADORES")
            print("="*60)
            
            todos_jugadores = []
            for i, plantel in enumerate(todos_planteles, 1):
                print(f"\n  📁 [{i}/{len(todos_planteles)}] {plantel['pais']} ({plantel['mundial']}) - Grupo {plantel['grupo']}")
                
                jugadores = self.extraer_jugadores_de_plantel(plantel)
                todos_jugadores.extend(jugadores)
                
                if i < len(todos_planteles):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            return todos_jugadores
            
        finally:
            self.cerrar_tor_browser()
    
    def guardar_csv(self, jugadores, nombre='jugadores.csv'):
        """Guarda los datos en CSV"""
        if not jugadores:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'pais', 'grupo', 'jugador', 'referencia', 'camiseta', 'posicion']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for i, j in enumerate(jugadores, 1):
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

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("⚽ SCRAPER DEFINITIVO - CON GECKODRIVER LOCAL")
    print("="*60)
    print("\n📌 Características:")
    print("   • Usa geckodriver.exe local (sin descargas)")
    print("   • 3 reintentos por página")
    print("   • Espera automática cuando hay bloqueo")
    print("   • Tor Browser se inicia y cierra solo")
    print("   • Acepta cookies automáticamente")
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperJugadoresTor()
    
    if not scraper.ruta_tor:
        print("\n❌ No se encontró Tor Browser")
        exit()
    
    if not scraper.ruta_geckodriver:
        print("\n❌ No se encontró geckodriver.exe")
        print("💡 Debe estar en la misma carpeta que este script")
        exit()
    
    try:
        max_mundiales = input("\n¿Máximo de mundiales? (Enter para todos): ").strip()
        max_mundiales = int(max_mundiales) if max_mundiales else None
        
        nombre = input("Nombre CSV (Enter para 'jugadores.csv'): ").strip()
        nombre = nombre or 'jugadores.csv'
        
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING...")
        print("⏱️  Puede tomar varias horas - Déjalo correr")
        print("="*60)
        
        jugadores = scraper.scrapear_todos(max_mundiales)
        
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