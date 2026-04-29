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
# SCRAPER DE EQUIPO IDEAL PARA TODOS LOS MUNDIALES
# ============================================

class ScraperEquipoIdeal:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        print("🚀 Inicializando scraper de Equipo Ideal...")
        
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
                                
                                # Construir URL de premios
                                url_premios = f"https://www.losmundialesdefutbol.com/mundiales/{año}_premios.php"
                                
                                mundiales.append({
                                    'año': año,
                                    'nombre': texto,
                                    'url_premios': url_premios
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
    
    def extraer_equipo_ideal(self, mundial):
        """Extrae los jugadores del Equipo Ideal de un mundial"""
        print(f"\n  📂 Procesando Equipo Ideal de {mundial['año']}")
        
        driver = self.obtener_con_tor(mundial['url_premios'], f"premios {mundial['año']}")
        
        if not driver:
            print(f"  ❌ No se pudo acceder")
            return []
        
        jugadores = []
        
        try:
            # Buscar el contenedor de Equipo Ideal
            # Estrategia 1: Buscar por el texto "Equipo Ideal"
            equipo_ideal = None
            
            # Buscar por el encabezado
            encabezados = driver.find_elements(By.XPATH, "//p[contains(text(), 'Equipo Ideal')]")
            if encabezados:
                # Encontrar el contenedor padre
                equipo_ideal = encabezados[0].find_element(By.XPATH, "../../..")
            
            if not equipo_ideal:
                # Estrategia 2: Buscar por la estructura típica
                contenedores = driver.find_elements(By.CSS_SELECTOR, "div[style*='border: 1px solid #BEA388']")
                for contenedor in contenedores:
                    try:
                        if "Equipo Ideal" in contenedor.text:
                            equipo_ideal = contenedor
                            break
                    except:
                        continue
            
            if not equipo_ideal:
                print(f"    ⚠️ No se encontró Equipo Ideal para {mundial['año']}")
                return []
            
            # Buscar todos los enlaces a jugadores dentro del contenedor
            enlaces = equipo_ideal.find_elements(By.TAG_NAME, "a")
            
            for enlace in enlaces:
                try:
                    href = enlace.get_attribute("href")
                    
                    # Solo nos interesan los enlaces a jugadores
                    if "/jugadores/" in href:
                        referencia = href.split('/')[-1]
                        jugadores.append({
                            'mundial': mundial['año'],
                            'jugador': referencia
                        })
                        print(f"      ✓ {referencia}")
                except:
                    continue
            
            print(f"    ✅ Total jugadores en Equipo Ideal: {len(jugadores)}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return jugadores
    
    def scrapear_todos(self):
        """Proceso completo de scraping de Equipo Ideal"""
        
        # Iniciar Tor
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return []
        
        try:
            # PASO 1: Obtener lista de mundiales
            mundiales = self.obtener_lista_mundiales()
            if not mundiales:
                return []
            
            print(f"\n✅ Mundiales a procesar: {len(mundiales)}")
            
            # PASO 2: Extraer Equipo Ideal de cada mundial
            print("\n" + "="*60)
            print("📋 EXTRAYENDO EQUIPO IDEAL")
            print("="*60)
            
            todos_jugadores = []
            
            for i, mundial in enumerate(mundiales, 1):
                print(f"\n📁 [{i}/{len(mundiales)}] {mundial['año']}")
                
                jugadores = self.extraer_equipo_ideal(mundial)
                todos_jugadores.extend(jugadores)
                
                if i < len(mundiales):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            return todos_jugadores
            
        finally:
            self.cerrar_tor_browser()
    
    def guardar_csv(self, jugadores, nombre='equipo_ideal.csv'):
        """Guarda los jugadores en CSV"""
        if not jugadores:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'jugador']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for i, j in enumerate(jugadores, 1):
                writer.writerow({
                    'id': i,
                    'mundial': j.get('mundial', ''),
                    'jugador': j.get('jugador', '')
                })
        
        print(f"\n💾 Guardados {len(jugadores)} jugadores en '{nombre}'")

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🏆 SCRAPER DE EQUIPO IDEAL")
    print("="*60)
    print("\n📌 Características:")
    print("   • Extrae Equipo Ideal de TODOS los mundiales (1930-2022)")
    print("   • Guarda: mundial (año) y jugador (referencia PHP)")
    print("   • Usa la misma lógica que funcionó antes")
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperEquipoIdeal()
    
    if not scraper.ruta_tor:
        print("\n❌ No se encontró Tor Browser")
        exit()
    
    if not scraper.ruta_geckodriver:
        print("\n❌ No se encontró geckodriver.exe")
        print("💡 Debe estar en la misma carpeta que este script")
        exit()
    
    try:
        nombre = input("\nNombre CSV (Enter para 'equipo_ideal.csv'): ").strip()
        nombre = nombre or 'equipo_ideal.csv'
        
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING...")
        print("⏱️  Procesando todos los mundiales...")
        print("="*60)
        
        jugadores = scraper.scrapear_todos()
        
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