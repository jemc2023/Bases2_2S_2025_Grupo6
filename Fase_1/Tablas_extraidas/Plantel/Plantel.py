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
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ============================================
# CONFIGURACIÓN DE PROXIES - PON AQUÍ TU LISTA COMPLETA DE PROXIES
# ============================================
PROXIES_LISTA = """
4.195.16.140:80
158.69.185.37:3129
103.65.237.92:5678
38.60.196.214:80
5.161.155.252:80
133.18.234.13:80
46.29.162.166:80
190.119.132.62:80
190.119.132.61:80
162.248.165.72:1080
194.213.18.200:443
46.183.25.8:443
35.225.22.61:80
51.79.135.131:8080
31.40.204.250:80
210.223.44.230:3128
94.176.3.43:7443
89.58.55.33:80
156.146.56.231:8081
23.88.88.105:443
81.10.234.234:80
8.212.177.126:8080
23.88.88.102:80
138.124.53.25:7443
147.75.34.105:443
102.223.9.53:80
34.44.49.215:80
109.236.88.82:80
217.217.249.160:8080
45.136.131.63:8443
45.136.130.191:8443
46.47.197.210:3128
197.221.249.198:80
103.84.95.54:7890
165.227.5.10:8888
97.74.87.226:80
95.3.9.78:3128
89.116.88.19:80
107.174.231.218:8888
32.223.6.94:80
190.58.248.86:80
50.122.86.118:80
211.171.114.154:3128
20.210.113.32:8123
192.73.244.36:80
175.138.231.145:80
89.58.57.45:80
213.157.6.50:80
213.33.126.130:80
194.158.203.14:80
45.136.131.47:8443
46.250.251.246:80
91.107.141.42:8081
139.178.90.204:443
176.126.164.213:80
23.95.242.79:3128
62.99.138.162:80
219.65.73.81:80
27.34.242.98:80
103.125.31.222:80
45.136.130.175:8443
46.249.100.124:80
47.56.110.204:8989
0.0.0.0:80
127.0.0.7:80
138.91.159.185:80
171.237.180.135:2102
197.221.240.247:80
43.250.54.139:60000
197.221.240.178:80
81.169.213.169:8888
103.180.118.184:8080
144.31.25.69:21064
139.162.200.213:80
152.42.213.210:8080
52.142.253.29:80
45.122.122.71:8080
45.123.142.69:8181
41.220.16.213:80
200.174.198.32:8888
147.45.60.34:1082
35.209.198.222:80
147.91.22.150:80
8.220.204.92:8080
39.109.113.97:4090
46.17.47.48:80
37.27.6.46:80
8.213.215.187:8443
154.65.39.7:80
213.230.110.191:3128
35.180.127.14:1001
41.139.234.127:8080
103.159.249.145:8080
196.1.97.198:80
41.220.16.210:80
171.251.172.78:5110
163.5.128.177:14270
103.141.180.254:8080
45.10.69.113:8888
154.127.219.242:999
58.137.174.101:8080
103.188.169.95:8080
175.158.63.166:1111
103.224.125.38:2024
124.106.116.34:1337
160.25.180.35:8080
45.190.76.100:999
45.175.232.75:999
119.93.206.217:8081
217.76.245.80:999
47.89.184.18:3128
205.209.118.30:3138
8.209.255.13:3128
101.47.73.135:3128
1.231.81.166:3128
195.158.8.123:3128
144.124.227.90:21074
8.219.97.248:80
47.91.120.190:1080
175.139.233.76:80
176.61.151.123:80
173.249.210.102:80
175.101.240.38:80
202.155.12.161:443
211.38.188.120:9080
45.136.130.188:8443
174.138.54.65:80
124.108.6.20:8085
147.231.163.133:80
160.251.142.232:80
189.7.145.111:3128
203.223.89.185:8080
178.217.168.164:55443
62.149.165.171:80
150.107.140.238:3128
159.65.245.255:80
86.53.183.16:1080
118.193.37.241:3129
138.68.235.51:80
150.136.163.51:80
179.96.28.58:80
172.193.178.226:80
163.5.128.33:14270
188.213.165.38:80
121.126.185.63:25152
69.48.201.94:80
88.216.98.251:53983
103.148.39.50:82
185.200.38.221:8085
103.171.240.77:8080
190.6.54.12:6969
202.133.88.173:80
197.221.234.252:80
45.136.130.223:8443
157.120.34.237:3128
14.232.228.80:8080
181.204.81.178:999
212.3.186.67:8080
112.198.18.206:8080
203.95.198.153:8080
190.2.214.137:9992
165.16.46.215:8080
23.247.136.254:80
85.208.108.43:2094
47.237.2.245:8081
158.160.215.167:8123
195.114.209.50:80
85.214.204.79:80
85.214.107.177:80
202.58.77.114:8080
201.77.110.245:999
37.238.63.39:8080
185.225.40.184:8080
151.242.153.8:80
203.205.49.2:10110
8.220.204.215:8443
62.113.119.14:8080
72.56.104.188:1080
38.159.36.83:999
103.166.90.165:8090
167.99.236.14:80
47.251.73.54:64
41.220.16.218:80
122.160.30.99:80
219.93.101.63:80
178.156.224.42:3128
219.93.101.60:80
202.51.214.81:8080
41.220.22.7:80
12.50.107.217:80
74.48.130.93:1080
14.143.130.210:1111
116.50.169.2:8088
212.15.47.50:8080
187.19.200.217:8090
38.156.236.186:999
41.59.115.217:8081
195.26.224.135:80
154.90.48.76:80
219.93.101.62:80
87.76.1.80:8080
181.118.150.28:9992
103.39.75.123:8080
84.39.112.144:3128
174.138.119.88:80
139.99.237.62:80
47.251.87.74:5060
108.161.135.118:80
38.7.195.50:999
49.148.138.194:8082
104.232.211.14:5627
23.94.7.23:5710
31.57.41.70:5646
86.38.236.216:6500
179.61.245.253:7032
38.154.205.109:5377
31.58.16.99:6066
104.239.13.25:6654
50.114.8.82:7067
138.128.153.108:5142
185.226.207.20:5569
89.116.78.250:5861
104.143.224.55:5916
69.58.12.200:8205
82.27.240.156:6964
31.56.137.112:6188
179.61.245.161:6940
23.27.196.130:6499
146.103.3.168:7221
198.105.111.219:6897
64.64.127.145:6098
104.238.38.220:6488
31.58.30.196:6778
45.135.139.52:6355
45.43.64.82:6340
45.43.81.187:5834
104.168.25.17:5699
209.242.203.165:6880
38.154.224.194:6735
31.58.21.202:6473
23.26.94.119:6101
145.223.46.141:5691
198.105.111.193:6871
86.38.154.21:5664
82.27.240.130:6938
45.39.4.110:5535
31.59.33.97:6673
23.95.244.204:6157
45.39.115.106:5517
146.103.3.243:7296
31.59.33.6:6582
172.120.119.162:5822
50.114.117.3:6986
104.168.118.7:5963
172.120.119.203:5863
45.127.250.84:5693
45.39.17.90:5513
31.58.30.219:6801
104.252.149.83:5497
162.220.247.177:6772
45.43.70.122:6409
23.27.75.25:6105
38.154.204.59:8100
45.59.161.88:5880
45.61.96.82:6062
23.94.246.104:8057
31.58.18.4:6273
45.39.75.36:5950
104.245.244.24:6464
89.116.78.213:5824
172.121.235.39:8194
107.181.154.132:5810
50.114.82.189:7173
191.101.121.78:6352
198.105.111.42:6720
89.249.193.93:5831
103.47.53.80:8378
198.105.100.127:6378
31.56.137.252:6328
23.236.170.141:9174
84.46.204.242:6545
107.181.154.38:5716
45.41.179.226:6761
162.220.247.83:6678
86.38.154.107:5750
45.61.97.184:6710
31.59.20.53:6631
31.57.42.248:6518
23.26.94.231:6213
45.61.122.251:6543
31.59.20.205:6783
23.236.196.216:6306
23.27.210.168:6538
46.202.67.228:8235
104.143.224.116:5977
31.58.18.214:6483
66.78.34.34:5653
89.249.192.198:6597
45.43.70.143:6430
23.95.255.62:6646

"""

def obtener_lista_proxies():
    """Convierte el texto en una lista de proxies"""
    proxies = []
    for linea in PROXIES_LISTA.strip().split('\n'):
        proxy = linea.strip()
        if proxy and not proxy.startswith('#') and proxy != '0.0.0.0:80' and proxy != '127.0.0.7:80':
            proxies.append(proxy)
    return proxies

def probar_proxy(proxy, timeout=5):
    """Prueba si un proxy funciona conectando a Google"""
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get(
            'https://www.google.com',
            proxies=proxies,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        if response.status_code == 200:
            return proxy
    except:
        pass
    return None

def probar_proxies_en_paralelo(proxies, max_workers=20):
    """Prueba múltiples proxies en paralelo"""
    proxies_funcionales = []
    
    print(f"🔍 Probando {len(proxies)} proxies (esto puede tomar 1-2 minutos)...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(probar_proxy, proxy): proxy for proxy in proxies[:50]}
        
        for i, future in enumerate(as_completed(futures), 1):
            resultado = future.result()
            if resultado:
                proxies_funcionales.append(resultado)
                print(f"  ✓ {resultado}")
    
    return proxies_funcionales

# ============================================
# CLASE PRINCIPAL DEL SCRAPER DE PLANTELES - VERSIÓN MEJORADA
# ============================================

class ScraperPlanteles:
    def __init__(self, proxies_list=None):
        self.proxies_funcionales = proxies_list if proxies_list else []
        self.proxies_usados = set()
        self.proxies_fallidos = set()  # Nuevo: proxies que definitivamente no funcionan
        print(f"📊 Inicializado con {len(self.proxies_funcionales)} proxies funcionales")
    
    def obtener_proxy_disponible(self):
        """Obtiene un proxy aleatorio que no se haya usado recientemente ni haya fallado"""
        if not self.proxies_funcionales:
            return None
        
        # Excluir proxies que ya fallaron
        proxies_disponibles = [p for p in self.proxies_funcionales 
                              if p not in self.proxies_usados and p not in self.proxies_fallidos]
        
        if not proxies_disponibles:
            # Si no hay disponibles, resetear usados pero mantener fallidos
            self.proxies_usados.clear()
            proxies_disponibles = [p for p in self.proxies_funcionales if p not in self.proxies_fallidos]
        
        if not proxies_disponibles:
            # Si todos han fallado, limpiar fallidos y reintentar
            print("  ⚠️ Todos los proxies han fallado, reiniciando lista...")
            self.proxies_fallidos.clear()
            proxies_disponibles = self.proxies_funcionales
        
        proxy = random.choice(proxies_disponibles)
        self.proxies_usados.add(proxy)
        return proxy
    
    def marcar_proxy_fallido(self, proxy):
        """Marca un proxy como fallido para no volver a usarlo"""
        if proxy:
            self.proxies_fallidos.add(proxy)
            print(f"  ⚠️ Proxy marcado como fallido: {proxy}")
    
    def configurar_driver_con_proxy(self, proxy=None):
        """Configura el driver de Chrome con proxy opcional"""
        options = Options()
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--lang=es')
        options.add_argument('--window-size=1920,1080')
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        if proxy:
            options.add_argument(f'--proxy-server=http://{proxy}')
        
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Timeouts más largos
        options.add_argument('--connection-timeout=30')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Configurar timeouts
        driver.set_page_load_timeout(100)
        driver.set_script_timeout(100)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def obtener_lista_mundiales(self, url_principal="https://www.losmundialesdefutbol.com/mundiales.php"):
        """Obtiene todos los links a los mundiales desde la página principal"""
        print(f"\n🌍 Accediendo a página principal: {url_principal}")
        
        mundiales = []
        intentos = 0
        max_intentos = 3
        
        while intentos < max_intentos and not mundiales:
            proxy = self.obtener_proxy_disponible() if self.proxies_funcionales else None
            driver = None
            
            try:
                driver = self.configurar_driver_con_proxy(proxy)
                driver.get(url_principal)
                print("  ⏳ Esperando que cargue la página...")
                time.sleep(random.uniform(4, 7))
                
                # Buscar en la tabla principal
                print("  🔍 Buscando en tabla principal...")
                
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
                                    
                                    if not href.startswith('http'):
                                        if href.startswith('/'):
                                            href = f"https://www.losmundialesdefutbol.com{href}"
                                        elif href.startswith('mundiales/'):
                                            href = f"https://www.losmundialesdefutbol.com/{href}"
                                    
                                    if not any(m['año'] == año for m in mundiales):
                                        mundiales.append({
                                            'año': año,
                                            'nombre': texto,
                                            'url': href
                                        })
                                        print(f"  ✓ {texto} - {año}")
                        except:
                            continue
                
                if mundiales:
                    mundiales.sort(key=lambda x: x['año'], reverse=True)
                    print(f"\n✅ TOTAL MUNDIALES ENCONTRADOS: {len(mundiales)}")
                else:
                    print(f"  ⚠️ No se encontraron mundiales (intento {intentos + 1}/{max_intentos})")
                    intentos += 1
                    time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                error_str = str(e)
                if "ERR_CONNECTION_RESET" in error_str or "ERR_PROXY_CONNECTION_FAILED" in error_str:
                    print(f"  ❌ Error de conexión con proxy {proxy}. Marcando como fallido...")
                    self.marcar_proxy_fallido(proxy)
                else:
                    print(f"  ❌ Error: {e}")
                
                intentos += 1
                time.sleep(random.uniform(3, 5))
            finally:
                if driver:
                    driver.quit()
        
        return mundiales
    
    def extraer_planteles_por_mundial(self, url_mundial, año, max_reintentos=5):
        """
        Extrae los planteles (país y grupo) de la página de un mundial
        Reintenta con diferentes proxies hasta lograr conexión exitosa
        """
        print(f"\n  📂 Procesando planteles del mundial {año}")
        print(f"  📡 URL: {url_mundial}")
        
        planteles = []
        intentos = 0
        ultimo_error = None
        
        while intentos < max_reintentos:
            proxy = self.obtener_proxy_disponible() if self.proxies_funcionales else None
            driver = None
            
            try:
                if proxy:
                    print(f"  🌍 Intento {intentos + 1}/{max_reintentos} con proxy: {proxy}")
                else:
                    print(f"  🌍 Intento {intentos + 1}/{max_reintentos} sin proxy")
                
                driver = self.configurar_driver_con_proxy(proxy)
                driver.get(url_mundial)
                time.sleep(random.uniform(3, 5))
                
                # Verificar que la página cargó correctamente
                if "403" in driver.title or "Forbidden" in driver.page_source:
                    print(f"  ⚠️ Página bloqueada (403) con proxy {proxy}")
                    self.marcar_proxy_fallido(proxy)
                    intentos += 1
                    continue
                
                # --- BUSCAR LA TABLA DE GRUPOS Y PLANTELES ---
                print(f"    🔍 Buscando tabla de grupos y planteles...")
                
                # Estrategia 1: Buscar por la clase específica
                grupo_elements = driver.find_elements(By.CSS_SELECTOR, "td.w-1-12.negri.pad-t2")
                
                if grupo_elements:
                    print(f"    ✓ Encontrados {len(grupo_elements)} grupos")
                    
                    for grupo_elem in grupo_elements:
                        try:
                            grupo = grupo_elem.text.strip()
                            
                            # Buscar la fila padre
                            fila_grupo = grupo_elem.find_element(By.XPATH, "./..")
                            
                            # Buscar la celda que contiene los países
                            celdas = fila_grupo.find_elements(By.TAG_NAME, "td")
                            if len(celdas) >= 3:
                                paises_celda = celdas[2]
                                
                                # Buscar enlaces a planteles
                                enlaces_paises = paises_celda.find_elements(By.CSS_SELECTOR, "a[href*='planteles/']")
                                
                                for enlace in enlaces_paises:
                                    try:
                                        pais = enlace.text.strip()
                                        if pais and len(pais) > 2:
                                            planteles.append({
                                                'mundial': año,
                                                'pais': pais,
                                                'grupo': grupo
                                            })
                                            print(f"      ✓ {pais} - Grupo {grupo}")
                                    except:
                                        continue
                        except Exception as e:
                            continue
                
                # Estrategia 2: Si no encontró, buscar por estructura alternativa
                if not planteles:
                    print(f"    🔍 Usando estrategia alternativa...")
                    
                    tablas = driver.find_elements(By.TAG_NAME, "table")
                    
                    for tabla in tablas:
                        if "Grupo" in tabla.text or "Planteles" in tabla.text:
                            filas = tabla.find_elements(By.TAG_NAME, "tr")
                            
                            for fila in filas:
                                try:
                                    celdas = fila.find_elements(By.TAG_NAME, "td")
                                    
                                    if len(celdas) >= 2:
                                        posible_grupo = celdas[0].text.strip()
                                        
                                        if posible_grupo and len(posible_grupo) == 1 and posible_grupo.isalpha():
                                            grupo = posible_grupo
                                            
                                            for celda in celdas[1:]:
                                                enlaces = celda.find_elements(By.CSS_SELECTOR, "a[href*='planteles/']")
                                                
                                                for enlace in enlaces:
                                                    pais = enlace.text.strip()
                                                    if pais and len(pais) > 2:
                                                        planteles.append({
                                                            'mundial': año,
                                                            'pais': pais,
                                                            'grupo': grupo
                                                        })
                                                        print(f"      ✓ {pais} - Grupo {grupo}")
                                except:
                                    continue
                
                # Si llegamos aquí, la conexión fue exitosa (haya encontrado datos o no)
                print(f"    ✅ Total planteles encontrados para {año}: {len(planteles)}")
                return planteles  # Salir del bucle de reintentos
                
            except Exception as e:
                error_str = str(e)
                ultimo_error = error_str
                
                if "ERR_CONNECTION_RESET" in error_str or "ERR_PROXY_CONNECTION_FAILED" in error_str:
                    print(f"    ❌ Error de conexión con proxy {proxy}. Intentando con otro...")
                    if proxy:
                        self.marcar_proxy_fallido(proxy)
                elif "timeout" in error_str.lower():
                    print(f"    ❌ Timeout con proxy {proxy}. Intentando con otro...")
                    if proxy:
                        self.marcar_proxy_fallido(proxy)
                else:
                    print(f"    ❌ Error inesperado: {error_str[:100]}")
                    if proxy:
                        self.marcar_proxy_fallido(proxy)
                
                intentos += 1
                
                if intentos < max_reintentos:
                    print(f"    ⏳ Reintentando en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"    ❌ Se agotaron los reintentos para {año}")
            
            finally:
                if driver:
                    driver.quit()
        
        # Si salimos del bucle sin éxito
        print(f"    ⚠️ No se pudo conectar para {año} después de {max_reintentos} intentos")
        return planteles
    
    def scrapear_todos_planteles(self, url_principal=None, max_mundiales=None):
        """Proceso completo de scraping de planteles para todos los mundiales"""
        if not url_principal:
            url_principal = "https://www.losmundialesdefutbol.com/mundiales.php"
        
        print("\n" + "="*60)
        print("📋 PASO 1: OBTENER LISTA DE MUNDIALES")
        print("="*60)
        
        mundiales = self.obtener_lista_mundiales(url_principal)
        
        if not mundiales:
            print("❌ No se pudo obtener la lista de mundiales")
            return []
        
        if max_mundiales and max_mundiales < len(mundiales):
            mundiales = mundiales[:max_mundiales]
            print(f"\n📊 Limitando a {max_mundiales} mundiales")
        
        print(f"\n✅ Mundiales a procesar: {len(mundiales)}")
        for m in mundiales:
            print(f"  • {m['año']}: {m['nombre']}")
        
        print("\n" + "="*60)
        print("📋 PASO 2: EXTRAYENDO PLANTELES DE CADA MUNDIAL")
        print("="*60)
        
        todos_planteles = []
        mundiales_fallidos = []
        
        for i, mundial in enumerate(mundiales, 1):
            print(f"\n📁 [{i}/{len(mundiales)}] Procesando {mundial['año']} - {mundial['nombre']}")
            
            planteles = self.extraer_planteles_por_mundial(mundial['url'], mundial['año'])
            
            if planteles:
                todos_planteles.extend(planteles)
                print(f"  ✅ {len(planteles)} planteles extraídos")
            else:
                print(f"  ⚠️ No se pudieron extraer planteles para {mundial['año']}")
                mundiales_fallidos.append(mundial['año'])
            
            # Pausa entre mundiales
            if i < len(mundiales):
                pausa = random.uniform(3, 5)
                print(f"  ⏳ Pausa de {pausa:.1f} segundos...")
                time.sleep(pausa)
        
        # Mostrar resumen de fallos
        if mundiales_fallidos:
            print(f"\n⚠️ Mundiales que fallaron: {', '.join(mundiales_fallidos)}")
        
        return todos_planteles
    
    def guardar_csv(self, planteles, nombre_archivo='planteles.csv'):
        """Guarda los datos en un archivo CSV con ID autoincremental"""
        if not planteles:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['id', 'mundial', 'pais', 'grupo']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, p in enumerate(planteles, 1):
                writer.writerow({
                    'id': i,
                    'mundial': p.get('mundial', ''),
                    'pais': p.get('pais', '').strip(),
                    'grupo': p.get('grupo', '').strip()
                })
        
        print(f"\n💾 Datos guardados en '{nombre_archivo}'")
        print(f"📊 Total de registros: {len(planteles)}")
    
    def mostrar_resumen(self, planteles):
        """Muestra un resumen de los datos recolectados"""
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL - PLANTELES")
        print("="*60)
        
        if not planteles:
            print("No hay datos para mostrar")
            return
        
        print(f"Total de planteles procesados: {len(planteles)}")
        
        # Contar por mundial
        mundiales = {}
        for p in planteles:
            año = p['mundial']
            mundiales[año] = mundiales.get(año, 0) + 1
        
        print("\n📌 Cantidad de planteles por mundial:")
        for año, count in sorted(mundiales.items(), reverse=True):
            print(f"  • {año}: {count} planteles")
        
        # Mostrar algunos ejemplos
        print("\n📌 Primeros 10 registros:")
        print("-" * 50)
        print(f"{'ID':<5} {'Mundial':<8} {'Grupo':<6} {'País'}")
        print("-" * 50)
        
        for p in planteles[:10]:
            print(f"{p.get('id', ''):<5} {p.get('mundial', ''):<8} {p.get('grupo', ''):<6} {p.get('pais', '')}")

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🏆 SCRAPER DE PLANTELES DE MUNDIALES - VERSIÓN MEJORADA")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Antes de ejecutar, asegúrate de haber")
    print("   puesto tu lista completa de proxies en la variable PROXIES_LISTA")
    
    # 1. Configurar proxies
    print("\n" + "-"*40)
    print("🔧 CONFIGURACIÓN DE PROXIES")
    print("-"*40)
    
    usar_proxies = input("¿Usar proxies para evitar bloqueos? (s/n): ").strip().lower()
    
    proxies_funcionales = []
    if usar_proxies == 's':
        todos_proxies = obtener_lista_proxies()
        
        if not todos_proxies:
            print("❌ No hay proxies configurados. Por favor, añade los proxies en PROXIES_LISTA")
            exit()
        
        print(f"📋 Total proxies en lista: {len(todos_proxies)}")
        
        probar = input("¿Probar qué proxies funcionan primero? (s/n): ").strip().lower()
        if probar == 's':
            proxies_funcionales = probar_proxies_en_paralelo(todos_proxies)
            print(f"\n✅ Proxies funcionales: {len(proxies_funcionales)}")
        else:
            proxies_funcionales = todos_proxies
            print("⚠️ Usando todos los proxies sin probar")
    
    # 2. Crear scraper
    scraper = ScraperPlanteles(proxies_funcionales if usar_proxies == 's' else None)
    
    # 3. Configurar
    print("\n" + "-"*40)
    print("⚙️  CONFIGURACIÓN")
    print("-"*40)
    
    try:
        max_mundiales = input("Número máximo de mundiales a procesar (Enter para todos): ").strip()
        max_mundiales = int(max_mundiales) if max_mundiales else None
    except:
        max_mundiales = None
    
    nombre_archivo = input("Nombre del archivo CSV (Enter para 'planteles.csv'): ").strip()
    if not nombre_archivo:
        nombre_archivo = 'planteles.csv'
    elif not nombre_archivo.endswith('.csv'):
        nombre_archivo += '.csv'
    
    # 4. Ejecutar
    print("\n" + "="*60)
    print("🚀 INICIANDO SCRAPING DE PLANTELES...")
    print("="*60)
    
    try:
        planteles = scraper.scrapear_todos_planteles(max_mundiales=max_mundiales)
        
        if planteles:
            scraper.guardar_csv(planteles, nombre_archivo)
            scraper.mostrar_resumen(planteles)
            print(f"\n✅ PROCESO COMPLETADO!")
        else:
            print("\n❌ No se obtuvieron resultados")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        if 'planteles' in locals() and planteles:
            scraper.guardar_csv(planteles, 'planteles_PARCIAL.csv')
            print("💾 Datos parciales guardados")
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()