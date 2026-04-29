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
# SCRAPER DE PARTIDOS DESDE CSV - VERSIÓN FINAL
# ============================================

class ScraperPartidosDesdeCSV:
    def __init__(self):
        self.tor_process = None
        self.ruta_tor = self.encontrar_tor_browser()
        self.ruta_geckodriver = self.encontrar_geckodriver()
        self.puerto_tor = 9150
        self.puerto_proxy = 9150
        self.reintentos_globales = 3
        self.start_id = {
            'goles': 1,
            'tarjetas': 1,
            'cambios': 1,
            'jugadores': 1,
            'no_disponibles': 1,
            'capitanes': 1,
            'penales': 1
        }
        # Archivos de salida
        self.archivos = {
            'goles': 'goles_desde_csv.csv',
            'tarjetas': 'tarjetas_desde_csv.csv',
            'cambios': 'cambios_desde_csv.csv',
            'jugadores': 'jugadores_desde_csv.csv',
            'no_disponibles': 'no_disponibles_desde_csv.csv',
            'capitanes': 'capitanes_desde_csv.csv',
            'penales': 'penales_desde_csv.csv',
            'errores': 'errores_desde_csv.csv'
        }
        print("🚀 Inicializando scraper de partidos desde CSV...")
        
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
    
    def cargar_ids_desde_archivo(self, archivo):
        """Carga el último ID de un archivo CSV"""
        max_id = 0
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'id' in row and row['id'].isdigit():
                            max_id = max(max_id, int(row['id']))
                print(f"  ✅ {archivo} - último ID: {max_id}")
            except Exception as e:
                print(f"  ⚠️ Error leyendo {archivo}: {e}")
        return max_id + 1 if max_id > 0 else 1
    
    def cargar_checkpoints(self):
        """Carga los últimos IDs de todos los archivos"""
        print("\n📂 Cargando checkpoints...")
        for key in self.start_id:
            archivo = self.archivos[key]
            if os.path.exists(archivo):
                self.start_id[key] = self.cargar_ids_desde_archivo(archivo)
                print(f"  ✅ {key}: ID inicial {self.start_id[key]}")
    
    def guardar_en_csv(self, datos, key):
        """Guarda datos en el CSV correspondiente"""
        if not datos:
            return
        
        archivo = self.archivos[key]
        
        fieldnames = {
            'goles': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'minuto', 
                     'jugador', 'referencia', 'equipo', 'es_penal', 'fue_en_tiempo_extra'],
            'tarjetas': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'minuto',
                        'jugador', 'referencia', 'equipo', 'tipo'],
            'cambios': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'minuto', 'equipo',
                       'jugador_entra', 'referencia_entra', 'jugador_sale', 'referencia_sale', 'en_entretiempo'],
            'jugadores': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'equipo',
                         'jugador', 'referencia', 'posicion', 'camiseta', 'es_titular', 'ingreso'],
            'no_disponibles': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'equipo',
                              'jugador', 'referencia', 'detalle'],
            'capitanes': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'equipo',
                         'jugador', 'referencia'],
            'penales': ['id', 'mundial', 'pais1', 'pais2', 'tipo_ronda', 'grupo', 'turno', 'equipo',
                       'jugador', 'referencia', 'anotado', 'detalle']
        }
        
        modo = 'a' if os.path.exists(archivo) else 'w'
        with open(archivo, modo, newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames[key])
            if modo == 'w':
                writer.writeheader()
            
            for dato in datos:
                dato['id'] = self.start_id[key]
                writer.writerow(dato)
                self.start_id[key] += 1
        
        print(f"💾 Guardados {len(datos)} registros en '{archivo}' (IDs hasta {self.start_id[key]-1})")
    
    def guardar_error(self, fila, error):
        """Guarda un error en el archivo de errores"""
        archivo = self.archivos['errores']
        modo = 'a' if os.path.exists(archivo) else 'w'
        
        with open(archivo, modo, newline='', encoding='utf-8-sig') as f:
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
    
    def extraer_info_partido(self, driver, fila):
        """Extrae la información básica del partido desde la fila del CSV"""
        return {
            'mundial': fila['mundial'],
            'pais1': fila['pais1'],
            'pais2': fila['pais2'],
            'tipo_ronda': fila['tipo_ronda'],
            'grupo': fila['grupo']
        }
    
    def extraer_goles(self, driver, info):
        """Extrae goles del partido"""
        goles = []
        try:
            goles_divs = driver.find_elements(By.CSS_SELECTOR, "div.a-left.clearfix.clear.overflow-x-auto div[style*='min-height']")
            
            for gol_div in goles_divs:
                try:
                    texto = gol_div.text
                    if not texto or "Goles:" in texto:
                        continue
                    
                    match_min = re.search(r'(\d+)\'?', texto)
                    minuto = match_min.group(1) if match_min else ""
                    fue_en_tiempo_extra = 'ET' in texto
                    
                    try:
                        enlace = gol_div.find_element(By.TAG_NAME, "a")
                        jugador = enlace.text.strip()
                        referencia = enlace.get_attribute("href").split('/')[-1]
                    except:
                        lineas = texto.split('\n')
                        jugador = lineas[1].strip() if len(lineas) >= 2 else texto
                        referencia = ""
                    
                    estilo = gol_div.get_attribute("style") or ""
                    if "padding-right" in estilo:
                        equipo = info['pais1']
                    else:
                        equipo = info['pais2']
                    
                    es_penal = '(pen)' in texto.lower() or 'de penal' in texto.lower()
                    
                    goles.append({
                        'mundial': info['mundial'],
                        'pais1': info['pais1'],
                        'pais2': info['pais2'],
                        'tipo_ronda': info['tipo_ronda'],
                        'grupo': info['grupo'],
                        'minuto': minuto,
                        'jugador': jugador,
                        'referencia': referencia,
                        'equipo': equipo,
                        'es_penal': es_penal,
                        'fue_en_tiempo_extra': fue_en_tiempo_extra
                    })
                except:
                    continue
        except:
            pass
        return goles
    
    def extraer_tarjetas(self, driver, info):
        """Extrae tarjetas del partido"""
        tarjetas = []
        try:
            tabla = driver.find_element(By.XPATH, "//h3[contains(text(), 'Tarjetas')]/following::table[1]")
            filas = tabla.find_elements(By.CSS_SELECTOR, "tr.a-top, tr.color-alt-item")
            
            for fila in filas:
                try:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 3:
                        equipo_celda = celdas[0].text.strip()
                        match_equipo = re.search(r'([A-Za-z\s]+)$', equipo_celda)
                        equipo = match_equipo.group(1).strip() if match_equipo else equipo_celda
                        
                        try:
                            enlace = celdas[1].find_element(By.TAG_NAME, "a")
                            jugador = enlace.text.strip()
                            referencia = enlace.get_attribute("href").split('/')[-1]
                        except:
                            jugador = celdas[1].text.strip()
                            referencia = ""
                        
                        info_tarjeta = celdas[2].text.strip()
                        match_min = re.search(r'(\d+)\'?', info_tarjeta)
                        minuto = match_min.group(1) if match_min else ""
                        tipo = 'amarilla' if 'amarilla' in info_tarjeta.lower() else 'roja'
                        
                        tarjetas.append({
                            'mundial': info['mundial'],
                            'pais1': info['pais1'],
                            'pais2': info['pais2'],
                            'tipo_ronda': info['tipo_ronda'],
                            'grupo': info['grupo'],
                            'minuto': minuto,
                            'jugador': jugador,
                            'referencia': referencia,
                            'equipo': equipo,
                            'tipo': tipo
                        })
                except:
                    continue
        except:
            pass
        return tarjetas
    
    def extraer_cambios(self, driver, info):
        """Extrae cambios del partido"""
        cambios = []
        try:
            tabla = driver.find_element(By.XPATH, "//h3[contains(text(), 'Cambios')]/following::table[1]")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            equipo_actual = ""
            
            for fila in filas:
                try:
                    if fila.get_attribute("class") == "bt-2":
                        texto_fila = fila.text
                        match_equipo = re.search(r'([A-Za-z\s]+)$', texto_fila)
                        if match_equipo:
                            equipo_actual = match_equipo.group(1).strip()
                        continue
                    
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 5 and equipo_actual:
                        minuto_texto = celdas[0].text.strip()
                        match_min = re.search(r'(\d+)', minuto_texto)
                        minuto = match_min.group(1) if match_min else ""
                        en_entretiempo = 'entretiempo' in minuto_texto.lower()
                        
                        try:
                            enlace_entra = celdas[2].find_element(By.TAG_NAME, "a")
                            jugador_entra = enlace_entra.text.strip()
                            ref_entra = enlace_entra.get_attribute("href").split('/')[-1]
                        except:
                            jugador_entra = celdas[2].text.strip()
                            ref_entra = ""
                        
                        try:
                            enlace_sale = celdas[4].find_element(By.TAG_NAME, "a")
                            jugador_sale = enlace_sale.text.strip()
                            ref_sale = enlace_sale.get_attribute("href").split('/')[-1]
                        except:
                            jugador_sale = celdas[4].text.strip()
                            ref_sale = ""
                        
                        cambios.append({
                            'mundial': info['mundial'],
                            'pais1': info['pais1'],
                            'pais2': info['pais2'],
                            'tipo_ronda': info['tipo_ronda'],
                            'grupo': info['grupo'],
                            'minuto': minuto,
                            'equipo': equipo_actual,
                            'jugador_entra': jugador_entra,
                            'referencia_entra': ref_entra,
                            'jugador_sale': jugador_sale,
                            'referencia_sale': ref_sale,
                            'en_entretiempo': en_entretiempo
                        })
                except:
                    continue
        except:
            pass
        return cambios
    
    def extraer_jugadores(self, driver, info):
        """Extrae todos los jugadores del partido"""
        titulares = []
        no_disponibles = []
        capitanes = []
        
        try:
            tablas = driver.find_elements(By.CSS_SELECTOR, "table.a-center")
            
            for tabla in tablas:
                try:
                    equipo_elem = tabla.find_element(By.CSS_SELECTOR, "tr td[colspan='3'] strong")
                    equipo = equipo_elem.text.strip()
                    
                    filas = tabla.find_elements(By.TAG_NAME, "tr")
                    estado = None
                    
                    for fila in filas:
                        texto = fila.text.strip()
                        
                        if "Titulares" in texto:
                            estado = 'titular'
                            continue
                        elif "Ingresaron" in texto:
                            estado = 'suplente'
                            continue
                        elif "Otros Suplentes" in texto:
                            estado = 'suplente'
                            continue
                        elif "No Disponibles" in texto:
                            estado = 'no_disponible'
                            continue
                        
                        if estado and len(fila.find_elements(By.TAG_NAME, "td")) >= 3:
                            celdas = fila.find_elements(By.TAG_NAME, "td")
                            
                            posicion = celdas[0].text.strip()
                            if not posicion or posicion == "Pos":
                                continue
                            
                            camiseta = celdas[1].text.strip().replace('.', '')
                            
                            try:
                                enlace = celdas[2].find_element(By.TAG_NAME, "a")
                                jugador = enlace.text.strip()
                                referencia = enlace.get_attribute("href").split('/')[-1]
                                es_capitan = "(C)" in celdas[2].text
                            except:
                                jugador = celdas[2].text.strip()
                                referencia = ""
                                es_capitan = False
                            
                            if estado == 'no_disponible':
                                no_disponibles.append({
                                    'mundial': info['mundial'],
                                    'pais1': info['pais1'],
                                    'pais2': info['pais2'],
                                    'tipo_ronda': info['tipo_ronda'],
                                    'grupo': info['grupo'],
                                    'equipo': equipo,
                                    'jugador': jugador,
                                    'referencia': referencia,
                                    'detalle': 'suspendido' if 'suspendido' in texto.lower() else 'lesionado'
                                })
                            else:
                                titulares.append({
                                    'mundial': info['mundial'],
                                    'pais1': info['pais1'],
                                    'pais2': info['pais2'],
                                    'tipo_ronda': info['tipo_ronda'],
                                    'grupo': info['grupo'],
                                    'equipo': equipo,
                                    'jugador': jugador,
                                    'referencia': referencia,
                                    'posicion': posicion,
                                    'camiseta': camiseta,
                                    'es_titular': estado == 'titular',
                                    'ingreso': estado == 'suplente'
                                })
                                
                                if es_capitan:
                                    capitanes.append({
                                        'mundial': info['mundial'],
                                        'pais1': info['pais1'],
                                        'pais2': info['pais2'],
                                        'tipo_ronda': info['tipo_ronda'],
                                        'grupo': info['grupo'],
                                        'equipo': equipo,
                                        'jugador': jugador,
                                        'referencia': referencia
                                    })
                except:
                    continue
        except:
            pass
        
        return titulares, no_disponibles, capitanes
    
    def extraer_penales(self, driver, info):
        """Extrae penales del partido"""
        penales = []
        try:
            encabezado = driver.find_element(By.XPATH, "//h3[contains(text(), 'Definición por Penales')]")
            contenedor = encabezado.find_element(By.XPATH, "./following::div[contains(@class, 'left')]")
            
            try:
                primero = driver.find_element(By.XPATH, "//div[contains(text(), 'patea primero')]").text
                patea_primero = primero.replace('patea primero', '').strip()
            except:
                patea_primero = ""
            
            penales_local = contenedor.find_elements(By.CSS_SELECTOR, "div.left.a-right.w-50")
            penales_visitante = contenedor.find_elements(By.CSS_SELECTOR, "div.left.w-50")
            
            if patea_primero == info['pais1']:
                equipo_local = info['pais1']
                equipo_visitante = info['pais2']
            else:
                equipo_local = info['pais2']
                equipo_visitante = info['pais1']
            
            for i in range(max(len(penales_local), len(penales_visitante))):
                turno = i + 1
                
                if i < len(penales_local):
                    penal = self._procesar_penal(penales_local[i], turno, equipo_local)
                    if penal:
                        penal.update(info)
                        penales.append(penal)
                
                if i < len(penales_visitante):
                    penal = self._procesar_penal(penales_visitante[i], turno, equipo_visitante)
                    if penal:
                        penal.update(info)
                        penales.append(penal)
        except:
            pass
        
        return penales
    
    def _procesar_penal(self, div, turno, equipo):
        """Procesa un penal individual"""
        try:
            html = div.get_attribute("innerHTML")
            
            if 'background-color: green' in html or '#339966' in html:
                anotado = True
                detalle = ""
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
            
            try:
                enlace = div.find_element(By.TAG_NAME, "a")
                jugador = enlace.text.strip()
                referencia = enlace.get_attribute("href").split('/')[-1]
            except:
                texto = div.text.strip()
                jugador = re.sub(r'\([^)]*\)', '', texto).strip()
                referencia = ""
            
            return {
                'turno': turno,
                'equipo': equipo,
                'jugador': jugador,
                'referencia': referencia,
                'anotado': anotado,
                'detalle': detalle
            }
        except:
            return None
    
    def procesar_partido(self, fila):
        """Procesa un partido completo desde una fila del CSV"""
        
        url = fila['url']
        print(f"\n    📄 {fila['pais1']} vs {fila['pais2']} - {fila['tipo_ronda']} {fila['mundial']}")
        
        driver = self.obtener_con_tor(url, "partido")
        if not driver:
            self.guardar_error(fila, "No se pudo cargar la página")
            return False
        
        try:
            info = self.extraer_info_partido(driver, fila)
            
            goles = self.extraer_goles(driver, info)
            if goles:
                self.guardar_en_csv(goles, 'goles')
            
            tarjetas = self.extraer_tarjetas(driver, info)
            if tarjetas:
                self.guardar_en_csv(tarjetas, 'tarjetas')
            
            cambios = self.extraer_cambios(driver, info)
            if cambios:
                self.guardar_en_csv(cambios, 'cambios')
            
            titulares, no_disponibles, capitanes = self.extraer_jugadores(driver, info)
            if titulares:
                self.guardar_en_csv(titulares, 'jugadores')
            if no_disponibles:
                self.guardar_en_csv(no_disponibles, 'no_disponibles')
            if capitanes:
                self.guardar_en_csv(capitanes, 'capitanes')
            
            penales = self.extraer_penales(driver, info)
            if penales:
                self.guardar_en_csv(penales, 'penales')
            
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
        """Ejecuta el proceso completo desde un CSV"""
        
        self.cargar_checkpoints()
        
        if not self.iniciar_tor_browser():
            print("❌ No se pudo iniciar Tor")
            return
        
        try:
            with open(archivo_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                partidos = list(reader)
            
            print(f"\n📊 Partidos a procesar: {len(partidos)}")
            
            if max_partidos and max_partidos < len(partidos):
                partidos = partidos[:max_partidos]
                print(f"📊 Limitando a {max_partidos} partidos")
            
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
            for key, archivo in self.archivos.items():
                if os.path.exists(archivo):
                    size = os.path.getsize(archivo)
                    print(f"   • {archivo} ({size} bytes)")
            
        finally:
            self.cerrar_tor_browser()

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("⚽ SCRAPER DE PARTIDOS DESDE CSV")
    print("="*60)
    print("\n📌 Este script:")
    print("   1. Lee un CSV con la lista de partidos")
    print("   2. Para cada partido, extrae TODA la información")
    print("   3. Genera 7 archivos CSV con los datos")
    
    archivo_entrada = input("\n📂 Nombre del CSV de entrada (ej: 'todos_los_partidos.csv'): ").strip()
    if not archivo_entrada:
        archivo_entrada = "todos_los_partidos.csv"
    
    if not os.path.exists(archivo_entrada):
        print(f"❌ No se encontró el archivo {archivo_entrada}")
        exit()
    
    input("\n✅ Presiona ENTER para comenzar...")
    
    scraper = ScraperPartidosDesdeCSV()
    
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