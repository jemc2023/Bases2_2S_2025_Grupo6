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
# SCRAPER DE RESULTADOS - VERSIÓN CORREGIDA
# ============================================

class ScraperResultados:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        self.resultados_procesados = set()
        self.archivo_checkpoint = "resultados_checkpoint.csv"
        self.start_id = 1
        print("🚀 Inicializando scraper de Resultados...")
        
        # Mapeo de tipos de fase
        self.tipos_fase = {
            '1ra Ronda': '1ra Ronda',
            'Grupo': '1ra Ronda',
            'Octavos': 'Octavos de final',
            'Octavos de final': 'Octavos de final',
            'Cuartos': 'Cuartos de final',
            'Cuartos de final': 'Cuartos de final',
            'Semis': 'Semifinales',
            'Semifinales': 'Semifinales',
            'Final': 'Final',
            '2da Ronda': '2da Ronda',
            'Ronda final': 'Ronda final',
            '3er Puesto': '3er puesto',
            '3er puesto': '3er puesto'
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
        """Carga los resultados ya procesados desde archivos existentes"""
        archivos_posibles = [
            "resultados_ERROR.csv",
            "resultados_PARCIAL.csv",
            self.archivo_checkpoint
        ]
        
        for archivo in archivos_posibles:
            if os.path.exists(archivo):
                print(f"📂 Cargando checkpoint desde: {archivo}")
                try:
                    with open(archivo, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if 'mundial' in row and 'fecha' in row and 'pais1' in row and 'pais2' in row:
                                clave = f"{row['mundial']}_{row['fecha']}_{row['pais1']}_{row['pais2']}"
                                self.resultados_procesados.add(clave)
                    
                    print(f"  ✅ Cargados {len(self.resultados_procesados)} resultados ya procesados")
                    
                    max_id = 0
                    with open(archivo, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if 'id' in row and row['id'].isdigit():
                                max_id = max(max_id, int(row['id']))
                    
                    if max_id > 0:
                        self.start_id = max_id + 1
                        print(f"  ✅ Continuando desde ID: {self.start_id}")
                    
                    return True
                except Exception as e:
                    print(f"  ⚠️ Error cargando checkpoint: {e}")
        
        print("  📝 No se encontró checkpoint, comenzando desde cero")
        return False
    
    def guardar_checkpoint(self, resultados, es_parcial=False):
        """Guarda checkpoint con los resultados procesados hasta ahora"""
        if not resultados:
            return
        
        nombre_archivo = self.archivo_checkpoint if not es_parcial else "resultados_PARCIAL.csv"
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'pais1', 'pais2', 'grupo_pais1', 'grupo_pais2', 'fecha', 
                     'tipo_fase', 'mundial', 'hubo_tiempo_extra', 'hubo_penales']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for i, r in enumerate(resultados, self.start_id):
                writer.writerow({
                    'id': i,
                    'pais1': r.get('pais1', ''),
                    'pais2': r.get('pais2', ''),
                    'grupo_pais1': r.get('grupo_pais1', ''),
                    'grupo_pais2': r.get('grupo_pais2', ''),
                    'fecha': r.get('fecha', ''),
                    'tipo_fase': r.get('tipo_fase', ''),
                    'mundial': r.get('mundial', ''),
                    'hubo_tiempo_extra': r.get('hubo_tiempo_extra', False),
                    'hubo_penales': r.get('hubo_penales', False)
                })
        
        print(f"💾 Checkpoint guardado: {len(resultados)} resultados en '{nombre_archivo}'")
    
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
            print(f"\n✅ Total mundiales: {len(mundiales)}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return mundiales
    
    def extraer_resultados_de_mundial(self, mundial):
        """Extrae los resultados de un mundial específico - VERSIÓN CORREGIDA"""
        
        for intento in range(self.reintentos_globales):
            print(f"\n  📂 Procesando resultados de {mundial['año']} (intento {intento + 1}/{self.reintentos_globales})")
            
            driver = self.obtener_con_tor(mundial['url_resultados'], f"resultados {mundial['año']}")
            
            if not driver:
                if intento < self.reintentos_globales - 1:
                    print(f"    ⏳ Esperando 20 segundos...")
                    time.sleep(20)
                continue
            
            resultados = []
            resultados_nuevos = 0
            
            try:
                # Buscar TODOS los contenedores de fechas (div con clase max-1 margen-b8 bb-2)
                contenedores_fecha = driver.find_elements(By.CSS_SELECTOR, "div.max-1.margen-b8.bb-2")
                print(f"    📅 Encontrados {len(contenedores_fecha)} contenedores de fecha")
                
                for contenedor in contenedores_fecha:
                    try:
                        # Extraer la fecha del h3 dentro de este contenedor
                        fecha_elem = contenedor.find_element(By.CSS_SELECTOR, "h3.t-enc-2")
                        fecha_texto = fecha_elem.text.strip()
                        match = re.search(r'Fecha:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})', fecha_texto)
                        if not match:
                            continue
                        
                        fecha = match.group(1)
                        print(f"      📅 Procesando fecha: {fecha}")
                        
                        # Dentro de este contenedor, buscar TODOS los partidos
                        # Los partidos están en divs con clase "margen-y3 pad-y5"
                        partidos = contenedor.find_elements(By.CSS_SELECTOR, "div.margen-y3.pad-y5")
                        
                        # También los que tienen bt-2 (borde superior)
                        partidos_con_borde = contenedor.find_elements(By.CSS_SELECTOR, "div.margen-y3.pad-y5.bt-2")
                        partidos = partidos + partidos_con_borde
                        
                        print(f"        📊 {len(partidos)} partidos encontrados para esta fecha")
                        
                        for partido in partidos:
                            try:
                                # Extraer número de partido
                                num_elem = partido.find_element(By.CSS_SELECTOR, "div.wpx-30")
                                num_partido = num_elem.text.strip()
                                
                                # Extraer etapa
                                etapa_elem = partido.find_element(By.CSS_SELECTOR, "div.wpx-170 a")
                                etapa_texto = etapa_elem.text.strip()
                                tipo_fase = self.tipos_fase.get(etapa_texto, '1ra Ronda')
                                
                                # Buscar el contenedor del resultado
                                resultado_container = partido.find_element(By.CSS_SELECTOR, "div.right-sm.a-right")
                                resultado_div = resultado_container.find_element(By.CSS_SELECTOR, "div.rd-100")
                                
                                # Buscar el div que contiene los países
                                game_div = resultado_div.find_element(By.CSS_SELECTOR, "div.game")
                                
                                # Extraer los dos países
                                paises = game_div.find_elements(By.CSS_SELECTOR, "div[style*='width: 129px']")
                                if len(paises) >= 2:
                                    pais1 = paises[0].text.strip()
                                    pais2 = paises[1].text.strip()
                                else:
                                    print(f"          ⚠️ No se encontraron países en partido {num_partido}")
                                    continue
                                
                                # Crear clave única para checkpoint
                                clave = f"{mundial['año']}_{fecha}_{pais1}_{pais2}"
                                
                                # Verificar si ya fue procesado
                                if clave in self.resultados_procesados:
                                    print(f"          ⏭️ Partido {num_partido} ya procesado: {pais1} vs {pais2}")
                                    continue
                                
                                # Extraer grupo del enlace de etapa
                                grupo_pais1 = ''
                                grupo_pais2 = ''
                                try:
                                    enlace_grupo = etapa_elem.get_attribute("href")
                                    if 'grupo_' in enlace_grupo:
                                        match_grupo = re.search(r'grupo_([a-zA-Z0-9]+)', enlace_grupo.lower())
                                        if match_grupo:
                                            grupo = match_grupo.group(1).upper()
                                            grupo_pais1 = grupo
                                            grupo_pais2 = grupo
                                except:
                                    pass
                                
                                # Detectar tiempo extra y penales
                                hubo_tiempo_extra = False
                                hubo_penales = False
                                
                                try:
                                    # Buscar todos los divs con clase margen-b3 después del game_div
                                    extra_divs = resultado_div.find_elements(By.CSS_SELECTOR, "div.margen-b3")
                                    
                                    for extra_div in extra_divs:
                                        texto_extra = extra_div.text.lower()
                                        if "en tiempo extra" in texto_extra:
                                            hubo_tiempo_extra = True
                                        if "por penales" in texto_extra:
                                            hubo_penales = True
                                except:
                                    pass
                                
                                resultado = {
                                    'pais1': pais1,
                                    'pais2': pais2,
                                    'grupo_pais1': grupo_pais1,
                                    'grupo_pais2': grupo_pais2,
                                    'fecha': fecha,
                                    'tipo_fase': tipo_fase,
                                    'mundial': mundial['año'],
                                    'hubo_tiempo_extra': hubo_tiempo_extra,
                                    'hubo_penales': hubo_penales
                                }
                                
                                resultados.append(resultado)
                                self.resultados_procesados.add(clave)
                                resultados_nuevos += 1
                                
                                indicadores = []
                                if hubo_tiempo_extra:
                                    indicadores.append("TE")
                                if hubo_penales:
                                    indicadores.append("P")
                                
                                indicador_str = f" [{'+'.join(indicadores)}]" if indicadores else ""
                                print(f"          ✓ Partido {num_partido}: {pais1} vs {pais2}{indicador_str}")
                                
                            except Exception as e:
                                # Si falla un partido, continuamos con el siguiente
                                continue
                                
                    except Exception as e:
                        print(f"      ⚠️ Error procesando contenedor de fecha: {e}")
                        continue
                
                print(f"    ✅ Resultados para {mundial['año']}: {resultados_nuevos} nuevos, {len(resultados)} total")
                return resultados
                    
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
        
        print(f"  ❌ No se pudo procesar resultados de {mundial['año']}")
        return []
    
    def scrapear_todos(self, max_mundiales=None):
        """Proceso completo con checkpoint"""
        
        self.cargar_checkpoint()
        
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return []
        
        try:
            mundiales = self.obtener_lista_mundiales()
            if not mundiales:
                return []
            
            if max_mundiales:
                mundiales = mundiales[:max_mundiales]
                print(f"\n📊 Procesando {max_mundiales} mundiales")
            
            print("\n" + "="*60)
            print("📋 EXTRAYENDO RESULTADOS")
            print("="*60)
            
            todos_resultados = []
            mundiales_procesados = 0
            
            for i, mundial in enumerate(mundiales, 1):
                print(f"\n📁 [{i}/{len(mundiales)}] {mundial['año']}")
                
                resultados = self.extraer_resultados_de_mundial(mundial)
                
                if resultados:
                    todos_resultados.extend(resultados)
                    mundiales_procesados += 1
                    self.guardar_checkpoint(todos_resultados, es_parcial=True)
                    print(f"  ✅ Checkpoint guardado después de {mundial['año']}")
                
                if i < len(mundiales):
                    pausa = random.uniform(3, 5)
                    print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                    time.sleep(pausa)
            
            print(f"\n✅ Mundiales procesados exitosamente: {mundiales_procesados}/{len(mundiales)}")
            return todos_resultados
            
        finally:
            self.cerrar_tor_browser()
    
    def guardar_csv(self, resultados, nombre='resultados.csv'):
        """Guarda los datos en CSV"""
        if not resultados:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre, 'w', newline='', encoding='utf-8-sig') as f:
            campos = ['id', 'pais1', 'pais2', 'grupo_pais1', 'grupo_pais2', 'fecha', 
                     'tipo_fase', 'mundial', 'hubo_tiempo_extra', 'hubo_penales']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for i, r in enumerate(resultados, self.start_id):
                writer.writerow({
                    'id': i,
                    'pais1': r.get('pais1', ''),
                    'pais2': r.get('pais2', ''),
                    'grupo_pais1': r.get('grupo_pais1', ''),
                    'grupo_pais2': r.get('grupo_pais2', ''),
                    'fecha': r.get('fecha', ''),
                    'tipo_fase': r.get('tipo_fase', ''),
                    'mundial': r.get('mundial', ''),
                    'hubo_tiempo_extra': r.get('hubo_tiempo_extra', False),
                    'hubo_penales': r.get('hubo_penales', False)
                })
        
        print(f"\n💾 Guardados {len(resultados)} resultados en '{nombre}'")
        print(f"📊 IDs desde {self.start_id} hasta {self.start_id + len(resultados) - 1}")

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("⚽ SCRAPER DE RESULTADOS DE MUNDIALES - VERSIÓN FINAL")
    print("="*60)
    print("\n📌 Características:")
    print("   • Extrae resultados de TODOS los mundiales (1930-2022)")
    print("   • Detecta tiempo extra y penales")
    print("   • Sistema de checkpoint")
    print("   • 3 reintentos por mundial")
    print("\n📊 Datos a extraer por partido:")
    print("   • País 1 y País 2")
    print("   • Grupo (si disponible)")
    print("   • Fecha del partido")
    print("   • Tipo de fase")
    print("   • Año del mundial")
    print("   • Si hubo tiempo extra (True/False)")
    print("   • Si hubo penales (True/False)")
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperResultados()
    
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
        
        nombre = input("Nombre CSV (Enter para 'resultados.csv'): ").strip()
        nombre = nombre or 'resultados.csv'
        
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING...")
        print("="*60)
        
        resultados = scraper.scrapear_todos(max_mundiales)
        
        if resultados:
            scraper.guardar_csv(resultados, nombre)
            print(f"\n✅ COMPLETADO!")
            print(f"📁 Archivo: {nombre}")
            print(f"📊 Total resultados: {len(resultados)}")
        else:
            print("\n❌ No hay datos")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido")
        if 'resultados' in locals() and resultados:
            scraper.guardar_checkpoint(resultados, es_parcial=True)
        scraper.cerrar_tor_browser()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'resultados' in locals() and resultados:
            scraper.guardar_checkpoint(resultados, es_parcial=True)
        scraper.cerrar_tor_browser()