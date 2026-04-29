from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv
import time
import random
import os
import socket
import subprocess
import psutil

class ScraperJugadoresTor:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        self.jugadores_procesados = set()
        self.archivo_checkpoint = "jugadores_checkpoint.csv"
        print("🚀 Inicializando scraper de jugadores con Tor...")
        
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
        """Configura Firefox con proxy de Tor usando geckodriver local - CON NOSCRIPT DESHABILITADO"""
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
        
        # ===== CONFIGURACIÓN PARA EVITAR NOSCRIPT Y ERRORES DE SEGURIDAD =====
        
        # Deshabilitar NoScript completamente
        options.set_preference("extensions.noscript.enabled", False)
        options.set_preference("extensions.noscript.global", False)
        options.set_preference("extensions.noscript.permanent", False)
        
        # Deshabilitar protecciones de Tor Browser que bloquean scripts
        options.set_preference("privacy.resistFingerprinting", False)  # Deshabilitar anti-fingerprinting
        options.set_preference("privacy.trackingprotection.enabled", False)  # Deshabilitar protección de tracking
        options.set_preference("privacy.trackingprotection.pbmode.enabled", False)
        options.set_preference("privacy.firstparty.isolate", False)  # Deshabilitar aislamiento
        
        # Permitir scripts y contenido mixto
        options.set_preference("security.mixed_content.block_active_content", False)
        options.set_preference("security.mixed_content.block_display_content", False)
        options.set_preference("security.fileuri.strict_origin_policy", False)
        
        # Deshabilitar protección XSS de Firefox
        options.set_preference("security.xssfilter.enabled", False)
        options.set_preference("security.xssfilter.warn", False)
        
        # Permitir todas las cookies y scripts
        options.set_preference("network.cookie.cookieBehavior", 0)  # 0 = aceptar todas
        options.set_preference("network.cookie.lifetimePolicy", 2)  # 2 = aceptar todas
        
        # Anti-detección (más permisivo)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0")
        
        # Aumentar timeouts
        options.set_preference("dom.max_script_run_time", 60)
        options.set_preference("dom.max_chrome_script_run_time", 60)
        
        # Deshabilitar actualizaciones automáticas que puedan interferir
        options.set_preference("app.update.auto", False)
        options.set_preference("app.update.enabled", False)
        
        try:
            service = Service(executable_path=self.ruta_geckodriver)
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(180)  # Aumentado a 180 segundos
            driver.set_script_timeout(120)
            return driver
        except Exception as e:
            print(f"  ❌ Error configurando driver: {e}")
            return None
    
    def obtener_con_tor(self, url, descripcion, reintentos=5):  # Aumentado a 5 reintentos
        """Obtiene una página con reintentos usando Tor"""
        
        for intento in range(reintentos):
            driver = self.configurar_driver_con_tor()
            if not driver:
                time.sleep(5)
                continue
            
            try:
                print(f"    🌍 Intento {intento + 1}/{reintentos} - {descripcion}")
                
                # Estrategia: cargar primero con un timeout más largo
                driver.set_page_load_timeout(180)
                driver.get(url)
                time.sleep(8)  # Más tiempo para cargar
                
                self.aceptar_consentimiento(driver)
                
                # Verificar errores
                page_source = driver.page_source.lower()
                title = driver.title.lower()
                
                # Si hay error de NoScript o XSS, simplemente continuamos (ya lo deshabilitamos)
                if "noscript" in page_source or "xss" in page_source:
                    print(f"    ⚠️ Advertencia de seguridad ignorada, continuando...")
                
                if "tor exited" in page_source:
                    print(f"    ⚠️ Error de Tor, reintentando...")
                    driver.quit()
                    time.sleep(15)
                    continue
                
                if "403" in title or "forbidden" in page_source:
                    print(f"    ⚠️ Página bloqueada (403), esperando 30 segundos...")
                    driver.quit()
                    time.sleep(30)
                    continue
                
                print(f"    ✅ Página cargada")
                return driver
                
            except TimeoutException:
                print(f"    ⚠️ Timeout, reintentando con más tiempo...")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(15)  # Más tiempo entre reintentos
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Si es error de NoScript/XSS, lo ignoramos y continuamos
                if "xss" in error_str or "noscript" in error_str or "security" in error_str:
                    print(f"    ⚠️ Error de seguridad ignorado, continuando de todas formas...")
                    try:
                        # Intentar recuperar el driver
                        driver.get("about:blank")
                        time.sleep(2)
                        driver.get(url)
                        time.sleep(5)
                        return driver
                    except:
                        pass
                
                print(f"    ❌ Error: {str(e)[:100]}")
                try:
                    driver.quit()
                except:
                    pass
                
                if intento < reintentos - 1:
                    espera = 15 * (intento + 1)  # Espera progresiva
                    print(f"    ⏳ Reintentando en {espera} segundos...")
                    time.sleep(espera)
        
        return None
    
    def cargar_checkpoint(self):
        """Carga los jugadores ya procesados desde el archivo de error o checkpoint"""
        archivos_posibles = [
            "jugadores_detalles_ERROR.csv",
            "jugadores_detalles_PARCIAL.csv",
            self.archivo_checkpoint
        ]
        
        for archivo in archivos_posibles:
            if os.path.exists(archivo):
                print(f"📂 Cargando checkpoint desde: {archivo}")
                try:
                    with open(archivo, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if 'referencia' in row and row['referencia']:
                                self.jugadores_procesados.add(row['referencia'])
                    
                    print(f"  ✅ Cargados {len(self.jugadores_procesados)} jugadores ya procesados")
                    return True
                except Exception as e:
                    print(f"  ⚠️ Error cargando checkpoint: {e}")
        
        print("  📝 No se encontró checkpoint, comenzando desde cero")
        return False
    
    def guardar_checkpoint(self, jugadores, es_parcial=False):
        """Guarda checkpoint con los jugadores procesados hasta ahora"""
        if not jugadores:
            return
        
        nombre_archivo = self.archivo_checkpoint if not es_parcial else "jugadores_detalles_PARCIAL.csv"
        
        fieldnames = ['referencia', 'birth_place', 'nicknames', 'web_site',
                      'Ig', 'Face', 'YT', 'Twitter', 'TikTok']
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for jugador in jugadores:
                for field in fieldnames:
                    if field not in jugador:
                        jugador[field] = ''
                writer.writerow(jugador)
        
        print(f"💾 Checkpoint guardado: {len(jugadores)} jugadores en '{nombre_archivo}'")
    
    def obtener_paises(self, driver):
        """Obtiene todos los links de países desde la página principal"""
        url_base = "https://www.losmundialesdefutbol.com/jugadores.php"
        print(f"🌍 Accediendo a: {url_base}")
        
        # Intentar varias veces si hay error
        for intento in range(3):
            try:
                driver.get(url_base)
                time.sleep(8)
                break
            except:
                if intento == 2:
                    return []
                time.sleep(10)
        
        paises = []
        
        try:
            enlaces = driver.find_elements(By.TAG_NAME, "a")
            
            for enlace in enlaces:
                try:
                    href = enlace.get_attribute("href")
                    texto = enlace.text.strip()
                    
                    if href and "jugadores_indice/" in href:
                        imagenes = enlace.find_elements(By.TAG_NAME, "img")
                        tiene_bandera = False
                        for img in imagenes:
                            alt = img.get_attribute("alt") or ""
                            if "Bandera" in alt:
                                tiene_bandera = True
                                break
                        
                        if tiene_bandera or (texto and len(texto) > 2):
                            if not any(p['url'] == href for p in paises):
                                paises.append({
                                    'nombre': texto if texto else href.split('/')[-1].replace('.php', '').capitalize(),
                                    'url': href
                                })
                                print(f"  ✓ País encontrado: {texto}")
                except:
                    continue
        except Exception as e:
            print(f"  ⚠️ Error buscando países: {e}")
        
        print(f"📊 Total de países encontrados: {len(paises)}")
        return paises
    
    def obtener_jugadores_desde_pais(self, driver, url_pais, nombre_pais):
        """Obtiene todos los links de jugadores desde la página de un país"""
        print(f"\n  📂 Accediendo a país: {nombre_pais}")
        print(f"  📡 URL: {url_pais}")
        
        # Intentar varias veces
        for intento in range(3):
            try:
                driver.get(url_pais)
                time.sleep(6)
                break
            except:
                if intento == 2:
                    return []
                time.sleep(8)
        
        jugadores = []
        
        try:
            enlaces = driver.find_elements(By.TAG_NAME, "a")
            
            for enlace in enlaces:
                try:
                    href = enlace.get_attribute("href")
                    texto = enlace.text.strip()
                    
                    if href and "/jugadores/" in href and ".php" in href:
                        if (texto and len(texto) > 1 and 
                            texto not in ['Inicio', 'Estadísticas', 'Mundiales', 'Selecciones', 
                                        'Jugadores', 'por Apellido', 'por Selección'] and
                            not any(j['url'] == href for j in jugadores)):
                            
                            referencia = href.split('/')[-1]
                            
                            if referencia in self.jugadores_procesados:
                                print(f"    ⏭️ Ya procesado: {texto}")
                                continue
                            
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
        
        print(f"    📊 Total jugadores nuevos en {nombre_pais}: {len(jugadores)}")
        return jugadores
    
    def extraer_datos_jugador(self, driver, url_jugador, jugador_info):
        """Extrae los campos específicos de la página del jugador"""
        print(f"      ⏳ Accediendo a jugador: {jugador_info['nombre_referencia']}")
        
        # Intentar varias veces
        for intento in range(3):
            try:
                driver.get(url_jugador)
                time.sleep(4)
                break
            except:
                if intento == 2:
                    return None
                time.sleep(5)
        
        datos = {
            'referencia': jugador_info['referencia'],
            'birth_place': '',
            'nicknames': '',
            'web_site': '',
            'Ig': '',
            'Face': '',
            'YT': '',
            'Twitter': '',
            'TikTok': ''
        }
        
        try:
            tablas = driver.find_elements(By.TAG_NAME, "table")
            
            for tabla in tablas:
                texto_tabla = tabla.text
                if any(x in texto_tabla for x in ['Lugar de nacimiento', 'Apodo', 'Sitio Web Oficial', 'Redes Sociales']):
                    filas = tabla.find_elements(By.TAG_NAME, "tr")
                    
                    for fila in filas:
                        try:
                            celdas = fila.find_elements(By.TAG_NAME, "td")
                            if len(celdas) >= 2:
                                etiqueta = celdas[0].text.strip().replace(':', '')
                                
                                if "Lugar de nacimiento" in etiqueta:
                                    datos['birth_place'] = celdas[1].text.strip()
                                elif "Apodo" in etiqueta:
                                    apodos = celdas[1].text.strip()
                                    apodos = apodos.replace('  ', ' ').strip()
                                    datos['nicknames'] = apodos
                                elif "Sitio Web Oficial" in etiqueta:
                                    enlaces_web = celdas[1].find_elements(By.TAG_NAME, "a")
                                    if enlaces_web:
                                        datos['web_site'] = enlaces_web[0].get_attribute("href")
                                    else:
                                        datos['web_site'] = celdas[1].text.strip()
                                elif "Redes Sociales" in etiqueta:
                                    spans = celdas[1].find_elements(By.CLASS_NAME, "d-inline-block")
                                    
                                    for span in spans:
                                        texto_span = span.text.lower()
                                        enlaces_red = span.find_elements(By.TAG_NAME, "a")
                                        
                                        if enlaces_red:
                                            href = enlaces_red[0].get_attribute("href")
                                            
                                            if 'twitter' in texto_span or 'x.com' in href:
                                                datos['Twitter'] = href
                                            elif 'instagram' in texto_span:
                                                datos['Ig'] = href
                                            elif 'facebook' in texto_span:
                                                datos['Face'] = href
                                            elif 'youtube' in texto_span:
                                                datos['YT'] = href
                                            elif 'tiktok' in texto_span:
                                                datos['TikTok'] = href
                        except:
                            continue
                    break
            
            if datos['nicknames']:
                datos['nicknames'] = ', '.join([a.strip() for a in datos['nicknames'].split(',') if a.strip()])
            
            campos_encontrados = []
            if datos['birth_place']: campos_encontrados.append('lugar')
            if datos['nicknames']: campos_encontrados.append(f"apodos({len(datos['nicknames'].split(','))})")
            if datos['web_site']: campos_encontrados.append('web')
            if datos['Ig']: campos_encontrados.append('IG')
            if datos['Face']: campos_encontrados.append('FB')
            if datos['YT']: campos_encontrados.append('YT')
            if datos['Twitter']: campos_encontrados.append('TW')
            if datos['TikTok']: campos_encontrados.append('TK')
            
            print(f"      ✓ Encontrado: {', '.join(campos_encontrados) if campos_encontrados else 'nada'}")
            
        except Exception as e:
            print(f"      ⚠️ Error extrayendo datos: {e}")
        
        return datos
    
    def guardar_csv(self, jugadores, nombre_archivo='jugadores_detalles.csv'):
        """Guarda los datos en un archivo CSV"""
        if not jugadores:
            print("❌ No hay datos para guardar")
            return
        
        fieldnames = ['referencia', 'birth_place', 'nicknames', 'web_site',
                      'Ig', 'Face', 'YT', 'Twitter', 'TikTok']
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for jugador in jugadores:
                for field in fieldnames:
                    if field not in jugador:
                        jugador[field] = ''
                writer.writerow(jugador)
        
        print(f"\n💾 Guardados {len(jugadores)} jugadores en '{nombre_archivo}'")
        return True
    
    def mostrar_resumen(self, jugadores):
        """Muestra un resumen de los datos recolectados"""
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        print(f"Total de jugadores procesados: {len(jugadores)}")
        
        if jugadores:
            stats = {
                'birth_place': 0,
                'nicknames': 0,
                'web_site': 0,
                'Ig': 0,
                'Face': 0,
                'YT': 0,
                'Twitter': 0,
                'TikTok': 0
            }
            
            total_apodos = 0
            for j in jugadores:
                for campo in stats:
                    if j.get(campo):
                        stats[campo] += 1
                if j.get('nicknames'):
                    total_apodos += len(j['nicknames'].split(','))
            
            print(f"\n📊 Estadísticas de datos encontrados:")
            print(f"  • Lugar de nacimiento: {stats['birth_place']}/{len(jugadores)}")
            print(f"  • Apodos: {stats['nicknames']}/{len(jugadores)} (total {total_apodos} apodos)")
            print(f"  • Web site: {stats['web_site']}/{len(jugadores)}")
            print(f"  • Instagram: {stats['Ig']}/{len(jugadores)}")
            print(f"  • Facebook: {stats['Face']}/{len(jugadores)}")
            print(f"  • YouTube: {stats['YT']}/{len(jugadores)}")
            print(f"  • Twitter/X: {stats['Twitter']}/{len(jugadores)}")
            print(f"  • TikTok: {stats['TikTok']}/{len(jugadores)}")
    
    def ejecutar(self):
        """Ejecuta el proceso completo de scraping"""
        print("="*60)
        print("🚀 WEB SCRAPING DE JUGADORES CON TOR - MODO CONTINUACIÓN")
        print("="*60)
        
        self.cargar_checkpoint()
        
        if self.jugadores_procesados:
            print(f"\n📋 Se omitirán {len(self.jugadores_procesados)} jugadores ya procesados")
        
        driver = None
        todos_los_jugadores = []
        
        try:
            if not self.iniciar_tor_browser():
                print("❌ No se pudo iniciar Tor Browser")
                return
            
            print("\n📋 PASO 1: OBTENER PAÍSES")
            driver = self.obtener_con_tor(
                "https://www.losmundialesdefutbol.com/jugadores.php", 
                "Página principal de jugadores",
                reintentos=3
            )
            
            if not driver:
                print("❌ No se pudo cargar la página principal")
                return
            
            paises = self.obtener_paises(driver)
            driver.quit()
            
            if not paises:
                print("❌ No se pudieron obtener los países")
                return
            
            print(f"\n✅ Países disponibles ({len(paises)}):")
            for i, pais in enumerate(paises, 1):
                print(f"  {i}. {pais['nombre']}")
            
            print("\n" + "="*60)
            print("⚙️  CONFIGURACIÓN")
            print("="*60)
            
            try:
                num_paises = int(input(f"¿Cuántos países procesar? (1-{len(paises)}): ").strip() or str(len(paises)))
                num_paises = max(1, min(num_paises, len(paises)))
            except:
                num_paises = len(paises)
            
            try:
                num_jugadores = int(input("¿Cuántos jugadores por país? (0 para todos): ").strip() or "0")
            except:
                num_jugadores = 0
            
            print(f"\n📊 Procesando {num_paises} países")
            print(f"📊 {'Todos los' if num_jugadores == 0 else num_jugadores} jugadores por país")
            print(f"📊 Omitiendo {len(self.jugadores_procesados)} jugadores ya procesados")
            
            for i, pais in enumerate(paises[:num_paises], 1):
                print(f"\n📁 [{i}/{num_paises}] PROCESANDO PAÍS: {pais['nombre']}")
                
                driver_pais = self.obtener_con_tor(pais['url'], f"Página de {pais['nombre']}")
                if not driver_pais:
                    print(f"  ⚠️ No se pudo cargar la página de {pais['nombre']}")
                    continue
                
                jugadores_pais = self.obtener_jugadores_desde_pais(driver_pais, pais['url'], pais['nombre'])
                driver_pais.quit()
                
                if not jugadores_pais:
                    print(f"  ⚠️ No hay jugadores nuevos en {pais['nombre']}")
                    continue
                
                jugadores_procesar = jugadores_pais if num_jugadores == 0 else jugadores_pais[:num_jugadores]
                print(f"  📊 Procesando {len(jugadores_procesar)} jugadores nuevos")
                
                for j, jugador_info in enumerate(jugadores_procesar, 1):
                    print(f"    [{j}/{len(jugadores_procesar)}] ", end="")
                    
                    driver_jugador = self.obtener_con_tor(jugador_info['url'], jugador_info['nombre_referencia'])
                    if driver_jugador:
                        datos = self.extraer_datos_jugador(driver_jugador, jugador_info['url'], jugador_info)
                        if datos:
                            todos_los_jugadores.append(datos)
                            self.jugadores_procesados.add(jugador_info['referencia'])
                        driver_jugador.quit()
                    
                    if len(todos_los_jugadores) % 5 == 0 and len(todos_los_jugadores) > 0:  # Cada 5 jugadores
                        self.guardar_checkpoint(todos_los_jugadores, es_parcial=True)
                    
                    if j < len(jugadores_procesar):
                        time.sleep(random.uniform(3, 5))  # Más tiempo entre jugadores
                
                if i < num_paises:
                    print(f"  ⏳ Pausa de 8 segundos...")
                    time.sleep(8)
            
            if todos_los_jugadores:
                archivo_anterior = "jugadores_detalles_ERROR.csv"
                if os.path.exists(archivo_anterior):
                    try:
                        with open(archivo_anterior, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                if not any(j['referencia'] == row['referencia'] for j in todos_los_jugadores):
                                    todos_los_jugadores.append(row)
                        print(f"📦 Combinados con datos de {archivo_anterior}")
                    except:
                        pass
                
                self.guardar_csv(todos_los_jugadores)
                self.mostrar_resumen(todos_los_jugadores)
                
                for archivo in ["jugadores_detalles_PARCIAL.csv", "jugadores_checkpoint.csv"]:
                    if os.path.exists(archivo):
                        os.remove(archivo)
                
                print(f"\n✅ PROCESO COMPLETADO!")
                print(f"📁 Archivo final: jugadores_detalles.csv")
                print(f"📊 Total final: {len(todos_los_jugadores)} jugadores")
            else:
                print("\n⚠️ No se procesaron jugadores nuevos")
                if os.path.exists("jugadores_detalles_ERROR.csv"):
                    print(f"📁 Usa el archivo existente: jugadores_detalles_ERROR.csv")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Proceso interrumpido")
            if todos_los_jugadores:
                self.guardar_checkpoint(todos_los_jugadores, es_parcial=True)
                print("💾 Puedes reanudar ejecutando el script nuevamente")
        
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            if todos_los_jugadores:
                self.guardar_checkpoint(todos_los_jugadores, es_parcial=True)
        
        finally:
            self.cerrar_tor_browser()

# ============================================
# EJECUCIÓN
# ============================================
if __name__ == "__main__":
    from selenium import webdriver
    
    scraper = ScraperJugadoresTor()
    scraper.ejecutar()