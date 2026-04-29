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
# SCRAPER DE PREMIOS PARA TODOS LOS MUNDIALES
# ============================================

class ScraperPremios:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        print("🚀 Inicializando scraper de premios...")
        
        # Diccionario de IDs de premios (solo los del CSV)
        self.id_premio = {
            'Balón de Oro': 1,
            'Balón de Plata': 2,
            'Balón de Bronce': 3,
            'Botín de Oro': 4,
            'Botín de Plata': 5,
            'Botín de Bronce': 6,
            'Guante de Oro': 7,
            'Mejor Jugador Joven': 8,
            'FIFA Fair Play': 9,
            'Equipo Más Entretenido': 10
        }
        
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
    
    def extraer_premios_de_mundial(self, mundial):
        """Extrae los premios de un mundial específico (solo IDs 1-10)"""
        print(f"\n  📂 Procesando premios de {mundial['año']}")
        
        driver = self.obtener_con_tor(mundial['url_premios'], f"premios {mundial['año']}")
        
        if not driver:
            print(f"  ❌ No se pudo acceder")
            return []
        
        premios = []
        
        try:
            # Buscar todos los contenedores de premios
            contenedores = driver.find_elements(By.CSS_SELECTOR, "div[style*='border: 1px solid #BEA388']")
            
            for contenedor in contenedores:
                try:
                    # Buscar el título del premio
                    titulo_elem = contenedor.find_element(By.CSS_SELECTOR, "p.negri")
                    titulo = titulo_elem.text.strip()
                    
                    # Verificar si el premio está en nuestro diccionario
                    if titulo not in self.id_premio:
                        continue  # Ignorar premios no listados (como Equipo Ideal)
                    
                    id_premio = self.id_premio[titulo]
                    
                    # Buscar enlaces (jugadores o países)
                    enlaces = contenedor.find_elements(By.TAG_NAME, "a")
                    
                    if not enlaces:
                        # Si no hay enlaces, es un guión "-" (sin premio)
                        continue
                    
                    for enlace in enlaces:
                        try:
                            texto = enlace.text.strip()
                            href = enlace.get_attribute("href")
                            
                            # Determinar si es jugador o país
                            if "/jugadores/" in href:
                                # Es un jugador
                                referencia = href.split('/')[-1]
                                premios.append({
                                    'mundial': mundial['año'],
                                    'id_premio': id_premio,
                                    'jugador': referencia,
                                    'pais': ''
                                })
                                print(f"      ✓ {titulo}: {referencia}")
                            
                            elif "/selecciones/" in href:
                                # Es un país
                                pais = texto
                                premios.append({
                                    'mundial': mundial['año'],
                                    'id_premio': id_premio,
                                    'jugador': '',
                                    'pais': pais
                                })
                                print(f"      ✓ {titulo}: {pais}")
                            
                        except:
                            continue
                            
                except Exception as e:
                    continue
            
            print(f"    ✅ Total premios encontrados: {len(premios)}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return premios
    
    def scrapear_todos(self):
        """Proceso completo de scraping de premios"""
        
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
            
            # PASO 2: Extraer premios de cada mundial
            print("\n" + "="*60)
            print("📋 EXTRAYENDO PREMIOS (solo IDs 1-10)")
            print("="*60)
            
            todos_premios = []
            
            for i, mundial in enumerate(mundiales, 1):
                print(f"\n📁 [{i}/{len(mundiales)}] {mundial['año']}")
                
                premios = self.extraer_premios_de_mundial(mundial)
                todos_premios.extend(premios)
                
                if i < len(mundiales):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            return todos_premios
            
        finally:
            self.cerrar_tor_browser()
    
    def guardar_csv(self, premios, nombre='premios.csv'):
        """Guarda los premios en CSV"""
        if not premios:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'mundial', 'id_premio', 'jugador', 'pais']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for i, p in enumerate(premios, 1):
                writer.writerow({
                    'id': i,
                    'mundial': p.get('mundial', ''),
                    'id_premio': p.get('id_premio', ''),
                    'jugador': p.get('jugador', ''),
                    'pais': p.get('pais', '')
                })
        
        print(f"\n💾 Guardados {len(premios)} premios en '{nombre}'")

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🏆 SCRAPER DE PREMIOS DE MUNDIALES")
    print("="*60)
    print("\n📌 Características:")
    print("   • Extrae premios de TODOS los mundiales (1930-2022)")
    print("   • SOLO los premios de tu CSV (IDs 1-10)")
    print("   • Ignora 'Equipo Ideal' y otros no listados")
    print("   • Usa la misma lógica que funcionó antes")
    print("\n📊 IDs de premios (según tu CSV):")
    print("   1 - Balón de Oro")
    print("   2 - Balón de Plata")
    print("   3 - Balón de Bronce")
    print("   4 - Botín de Oro")
    print("   5 - Botín de Plata")
    print("   6 - Botín de Bronce")
    print("   7 - Guante de Oro")
    print("   8 - Mejor Jugador Joven")
    print("   9 - FIFA Fair Play")
    print("   10 - Equipo Más Entretenido")
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperPremios()
    
    if not scraper.ruta_tor:
        print("\n❌ No se encontró Tor Browser")
        exit()
    
    if not scraper.ruta_geckodriver:
        print("\n❌ No se encontró geckodriver.exe")
        print("💡 Debe estar en la misma carpeta que este script")
        exit()
    
    try:
        nombre = input("\nNombre CSV (Enter para 'premios.csv'): ").strip()
        nombre = nombre or 'premios.csv'
        
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING...")
        print("⏱️  Procesando todos los mundiales...")
        print("="*60)
        
        premios = scraper.scrapear_todos()
        
        if premios:
            scraper.guardar_csv(premios, nombre)
            print(f"\n✅ COMPLETADO!")
            print(f"📁 Archivo: {nombre}")
            print(f"📊 Total registros: {len(premios)}")
        else:
            print("\n❌ No hay datos")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido")
        scraper.cerrar_tor_browser()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        scraper.cerrar_tor_browser()