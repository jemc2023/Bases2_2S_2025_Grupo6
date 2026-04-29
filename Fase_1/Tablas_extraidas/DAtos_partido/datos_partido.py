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
# SCRAPER DE LINKS DE PARTIDOS - VERSIÓN SIMPLE
# ============================================

class ScraperLinksPartidos:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        print("🚀 Inicializando scraper de links de partidos...")
        
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
        """Obtiene una página con reintentos usando Tor"""
        
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
    
    def obtener_lista_mundiales(self):
        """Obtiene todos los mundiales desde la página principal"""
        print("\n" + "="*60)
        print("📋 OBTENIENDO LISTA DE MUNDIALES")
        print("="*60)
        
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
                                    print(f"  ⏭️ Excluyendo {texto}")
                                    continue
                                
                                url_resultados = f"https://www.losmundialesdefutbol.com/mundiales/{año}_resultados.php"
                                
                                mundiales.append({
                                    'año': año,
                                    'nombre': texto,
                                    'url_resultados': url_resultados
                                })
                                print(f"  ✓ {texto}")
                    except:
                        continue
            
            mundiales.sort(key=lambda x: x['año'], reverse=True)
            print(f"\n✅ Mundiales encontrados: {len(mundiales)}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return mundiales
    
    def extraer_partidos_de_mundial(self, mundial):
        """Extrae todos los partidos de un mundial desde su página de resultados"""
        
        partidos = []
        
        print(f"\n  📂 Procesando {mundial['año']} - {mundial['nombre']}")
        
        driver = self.obtener_con_tor(mundial['url_resultados'], f"resultados {mundial['año']}")
        
        if not driver:
            print(f"  ❌ No se pudo acceder a resultados de {mundial['año']}")
            return partidos
        
        try:
            # Buscar TODOS los contenedores de partidos
            contenedores_partido = driver.find_elements(By.CSS_SELECTOR, "div.margen-y3.pad-y5")
            contenedores_con_borde = driver.find_elements(By.CSS_SELECTOR, "div.margen-y3.pad-y5.bt-2")
            contenedores_partido.extend(contenedores_con_borde)
            
            print(f"    📊 Encontrados {len(contenedores_partido)} partidos")
            
            for contenedor in contenedores_partido:
                try:
                    # Extraer link del partido
                    enlace_partido = contenedor.find_element(By.CSS_SELECTOR, "a[href*='partidos/']")
                    url_partido = enlace_partido.get_attribute("href")
                    
                    # Extraer etapa/tipo de ronda
                    try:
                        etapa_elem = contenedor.find_element(By.CSS_SELECTOR, "div.wpx-170 a")
                        etapa = etapa_elem.text.strip()
                    except:
                        etapa = ""
                    
                    # Extraer equipos
                    paises = contenedor.find_elements(By.CSS_SELECTOR, "div[style*='width: 129px']")
                    if len(paises) >= 2:
                        pais1 = paises[0].text.strip()
                        pais2 = paises[1].text.strip()
                    else:
                        continue
                    
                    # Extraer grupo (si está en la etapa)
                    grupo = ""
                    if "Grupo" in etapa:
                        match_grupo = re.search(r'Grupo\s+([A-Za-z0-9])', etapa)
                        if match_grupo:
                            grupo = match_grupo.group(1)
                    
                    partidos.append({
                        'mundial': mundial['año'],
                        'pais1': pais1,
                        'pais2': pais2,
                        'tipo_ronda': etapa,
                        'grupo': grupo,
                        'url': url_partido
                    })
                    
                except Exception as e:
                    continue
            
            print(f"    ✅ Partidos extraídos: {len(partidos)}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return partidos
    
    def ejecutar(self, max_mundiales=None):
        """Ejecuta el proceso completo"""
        
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return []
        
        try:
            # Obtener mundiales
            mundiales = self.obtener_lista_mundiales()
            
            if max_mundiales and max_mundiales < len(mundiales):
                mundiales = mundiales[:max_mundiales]
                print(f"\n📊 Procesando {max_mundiales} mundiales")
            
            todos_partidos = []
            
            # Procesar cada mundial
            for i, mundial in enumerate(mundiales, 1):
                print(f"\n📁 [{i}/{len(mundiales)}] {mundial['año']}")
                
                partidos = self.extraer_partidos_de_mundial(mundial)
                todos_partidos.extend(partidos)
                
                # Pausa entre mundiales
                if i < len(mundiales):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            return todos_partidos
            
        finally:
            self.cerrar_tor_browser()
    
    def guardar_csv(self, partidos, nombre='todos_los_partidos.csv'):
        """Guarda la lista de partidos en CSV"""
        if not partidos:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'url']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for p in partidos:
                writer.writerow(p)
        
        print(f"\n💾 Guardados {len(partidos)} partidos en '{nombre}'")

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("⚽ SCRAPER DE LINKS DE PARTIDOS - VERSIÓN SIMPLE")
    print("="*60)
    print("\n📌 Este script generará un CSV con:")
    print("   • Año del mundial")
    print("   • País 1")
    print("   • País 2")
    print("   • Tipo de ronda (ej: 1ra Ronda Grupo A, Octavos, etc.)")
    print("   • Grupo (si aplica)")
    print("   • URL del partido")
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperLinksPartidos()
    
    if not scraper.ruta_tor:
        print("\n❌ No se encontró Tor Browser")
        exit()
    
    if not scraper.ruta_geckodriver:
        print("\n❌ No se encontró geckodriver.exe")
        print("💡 Debe estar en la misma carpeta que este script")
        exit()
    
    try:
        max_mundiales = input("\n¿Máximo de mundiales a procesar? (Enter para todos): ").strip()
        max_mundiales = int(max_mundiales) if max_mundiales else None
        
        nombre = input("Nombre del CSV (Enter para 'todos_los_partidos.csv'): ").strip()
        nombre = nombre or 'todos_los_partidos.csv'
        
        print("\n" + "="*60)
        print("🚀 INICIANDO EXTRACCIÓN...")
        print("="*60)
        
        partidos = scraper.ejecutar(max_mundiales)
        
        if partidos:
            scraper.guardar_csv(partidos, nombre)
            print(f"\n✅ COMPLETADO!")
            print(f"📁 Archivo: {nombre}")
            print(f"📊 Total partidos: {len(partidos)}")
        else:
            print("\n❌ No se encontraron partidos")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido")
        scraper.cerrar_tor_browser()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        scraper.cerrar_tor_browser()