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
# CONFIGURACIÓN DE PROXIES (la misma lista)
# ============================================

PROXIES_LISTA = """
195.158.8.123:3128
47.91.115.179:8081
47.76.144.139:3128
167.71.182.192:80
41.220.16.210:80
176.61.151.123:80
85.214.204.79:80
31.40.204.250:80
174.138.54.65:80
91.107.141.42:8081
152.42.213.210:8080
8.212.177.126:8080
176.126.164.213:80
104.225.220.233:80
183.110.216.159:8090
197.221.234.253:80
34.135.166.24:80
45.136.130.191:8443
45.136.130.188:8443
219.93.101.60:80
57.128.188.167:9157
118.193.37.241:3129
37.59.110.73:80
175.138.231.145:80
156.146.56.231:8081
81.10.234.234:80
66.135.16.53:80
23.88.88.102:80
41.220.22.7:80
147.231.163.133:80
171.237.180.135:2102
190.6.54.12:6969
213.230.110.191:3128
178.156.224.42:3128
8.219.97.248:80
46.17.47.48:80
4.195.16.140:80
158.69.185.37:3129
37.27.6.46:80
115.127.178.50:6969
195.133.64.177:3128
183.98.143.134:8086
174.138.119.88:80
89.116.88.19:80
38.60.196.214:80
5.161.155.252:80
154.43.62.22:80
219.93.101.62:80
107.174.231.218:8888
133.18.234.13:80
32.223.6.94:80
37.139.33.145:1080
23.247.136.254:80
190.58.248.86:80
46.29.162.166:80
20.210.113.32:8123
192.73.244.36:80
202.155.12.161:443
194.213.18.200:443
46.183.25.8:443
35.225.22.61:80
51.79.135.131:8080
210.223.44.230:3128
94.176.3.43:7443
89.58.55.33:80
81.169.213.169:8888
89.58.57.45:80
116.254.118.180:80
213.157.6.50:80
213.33.126.130:80
194.158.203.14:80
124.108.6.20:8085
23.88.88.105:443
45.136.131.47:8443
45.136.130.223:8443
197.221.234.252:80
138.124.53.25:7443
23.95.242.79:3128
62.99.138.162:80
1.225.116.115:1080
219.65.73.81:80
89.117.130.19:80
172.193.178.226:80
27.34.242.98:80
103.125.31.222:80
102.223.9.53:80
34.44.49.215:80
109.236.88.82:80
217.217.249.160:8080
45.136.130.175:8443
45.136.131.63:8443
41.220.16.215:80
46.47.197.210:3128
200.174.198.32:8888
151.242.153.8:80
46.249.100.124:80
160.251.142.232:80
0.0.0.0:80
97.74.87.226:80
127.0.0.7:80
85.214.107.177:80
47.56.110.204:8989
186.167.112.91:999
116.80.49.172:3172
36.92.24.12:9100
103.112.45.43:8085
103.154.230.74:8090
103.169.254.75:6080
45.188.167.25:999
201.77.110.33:999
103.102.12.105:8080
150.107.140.238:3128
144.124.227.90:21074
139.178.90.204:443
121.126.185.63:25152
165.227.5.10:8888
172.237.73.24:80
190.119.132.62:80
190.119.132.61:80
43.208.16.199:30756
219.93.101.63:80
197.221.249.196:80
159.65.245.255:80
202.133.88.173:80
162.248.165.72:1080
72.56.104.188:1080
175.139.233.76:80
110.74.206.40:8181
38.156.72.10:8080
139.162.200.213:80
183.110.216.128:8090
1.234.153.14:80
158.160.215.167:8123
87.255.196.143:80
167.99.236.14:80
157.20.204.40:8080
175.101.240.38:80
103.253.145.138:6980
103.251.232.40:8090
202.58.77.9:8080
103.105.76.19:8080
181.78.197.235:999
38.123.220.190:8080
95.3.9.78:3128
107.172.125.217:3128
41.220.16.213:80
45.140.147.82:1081
190.97.239.40:999
38.190.100.104:999
140.245.66.105:8081
47.77.193.180:1080
128.140.113.110:8081
41.220.16.208:80
88.216.98.251:53983
31.220.78.244:80
197.221.240.178:80
47.238.134.126:8081
173.181.143.245:80
8.213.134.213:55443
190.153.237.6:37453
209.141.54.136:5555
129.213.162.27:17777
168.235.110.63:3128
103.46.8.85:8080
203.115.101.58:82
187.62.241.136:8080
202.47.185.178:8085
2.139.62.85:3128
161.132.39.58:8080
103.227.187.13:6080
204.199.202.133:999
186.0.144.81:9797
102.211.216.18:8080
109.197.153.25:8888
195.87.136.2:5331
115.245.89.250:8080
84.201.138.232:3128
181.209.107.154:999
42.96.16.158:1311
95.167.29.50:8080
103.164.231.243:8080
45.229.17.130:999
197.248.37.31:8104
83.239.34.82:8080
47.237.92.86:8080
186.215.87.194:30005
167.172.253.162:4857
147.91.22.150:80
47.90.167.27:8443
35.224.171.0:80
43.231.249.145:9090
41.220.16.218:80
185.85.111.18:80
163.5.128.131:14270
89.238.200.81:80
46.250.251.246:80
163.5.128.177:14270
103.76.149.67:8080
207.180.254.198:8080
196.1.93.16:80
181.94.197.37:8080
197.221.234.149:80
15.204.151.149:3128
116.80.64.41:7777
103.166.91.138:8090
103.247.13.75:8181
160.19.19.9:8080
193.38.224.169:8081
103.166.90.50:8090
202.154.18.56:8080
206.84.104.126:8080
190.60.48.212:999
152.70.84.108:8080
163.61.55.173:1111
64.181.240.152:3128
152.230.215.123:80
195.26.224.135:80
47.250.159.65:9098
8.211.195.173:80
120.50.11.225:5555
103.65.237.92:5678
182.53.202.208:8080
197.221.249.198:80
84.39.112.144:3128
185.233.203.191:4555
196.251.222.86:8104
116.80.49.166:3172
122.3.77.27:8082
103.175.46.162:8080
116.0.54.25:8080
180.191.32.233:8081
181.119.67.133:999
104.251.81.87:14270
64.176.6.165:13920
200.116.198.222:9812
197.221.240.247:80
163.5.128.117:14270
97.213.92.28:80
116.203.139.209:5678
196.1.97.198:80
67.169.98.211:443
95.213.247.248:1080
211.171.114.154:3128
204.199.140.25:999
196.251.223.29:8103
201.159.97.109:8081
35.209.198.222:80
138.91.159.185:80
139.99.237.62:80
62.149.165.171:80
47.237.107.41:135
116.99.49.187:10002
108.161.135.118:80
45.22.209.157:8888
147.75.34.105:443
160.20.38.102:8080
103.188.173.152:8080
210.87.74.71:8080
181.209.122.117:999
41.189.171.186:8080
92.180.22.224:8081
200.39.137.137:999
47.91.120.190:1080
8.219.229.53:84
65.21.201.149:8080
20.210.76.175:8561
110.44.115.83:8080
138.68.235.51:80
82.148.13.136:80
103.113.70.189:1081
173.249.210.102:80
103.180.123.229:8080
35.180.127.14:1001
110.171.40.132:8080
200.10.30.19:999
36.95.61.186:8080
110.232.87.251:8080
103.162.221.165:3125
85.208.108.43:2094
164.90.215.49:3128
86.102.77.67:1080
162.220.247.224:6819
67.227.112.16:6056
172.121.235.132:8287
45.41.160.190:6172
31.59.20.218:6796
104.165.66.155:7310
84.46.204.119:6422
172.245.7.160:5213
192.227.131.134:6718
82.26.208.145:5452
140.99.197.174:7051
84.46.204.23:6326
103.178.21.104:3125
120.28.216.101:8080
103.209.88.75:8080
125.26.4.219:8080
45.230.169.5:999
103.167.229.147:8080
98.154.21.253:4228
"""

def obtener_lista_proxies():
    proxies = []
    for linea in PROXIES_LISTA.strip().split('\n'):
        proxy = linea.strip()
        if proxy and not proxy.startswith('#') and proxy != '0.0.0.0:80' and proxy != '127.0.0.7:80':
            proxies.append(proxy)
    return proxies

def probar_proxy(proxy, timeout=5):
    try:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        response = requests.get('https://www.google.com', proxies=proxies, timeout=timeout,
                                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        if response.status_code == 200:
            return proxy
    except:
        pass
    return None

def probar_proxies_en_paralelo(proxies, max_workers=20):
    proxies_funcionales = []
    print(f"🔍 Probando {len(proxies)} proxies...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(probar_proxy, proxy): proxy for proxy in proxies[:50]}
        for i, future in enumerate(as_completed(futures), 1):
            resultado = future.result()
            if resultado:
                proxies_funcionales.append(resultado)
                print(f"  ✓ {resultado}")
    return proxies_funcionales

# ============================================
# CLASE PRINCIPAL DEL SCRAPER - VERSIÓN CORREGIDA
# ============================================

class ScraperMundiales:
    def __init__(self, proxies_list=None):
        self.proxies_funcionales = proxies_list if proxies_list else []
        self.proxies_usados = set()
        print(f"📊 Inicializado con {len(self.proxies_funcionales)} proxies funcionales")
    
    def obtener_proxy_disponible(self):
        if not self.proxies_funcionales:
            return None
        proxies_disponibles = [p for p in self.proxies_funcionales if p not in self.proxies_usados]
        if not proxies_disponibles:
            self.proxies_usados.clear()
            proxies_disponibles = self.proxies_funcionales
        proxy = random.choice(proxies_disponibles)
        self.proxies_usados.add(proxy)
        return proxy
    
    def configurar_driver_con_proxy(self, proxy=None):
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
        
        # Modo headless (opcional - descomentar si no quieres ver el navegador)
        # options.add_argument('--headless')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def obtener_lista_mundiales_desde_html(self, url_principal="https://www.losmundialesdefutbol.com/mundiales.php"):
        """
        Obtiene todos los mundiales analizando el HTML de dos maneras:
        1. Desde la tabla principal visible
        2. Desde el menú desplegable
        """
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
                
                # --- ESTRATEGIA 1: Buscar en la tabla principal (c0s5 color-alt) ---
                print("  🔍 Estrategia 1: Buscando en tabla principal...")
                
                # Buscar la tabla con clase c0s5
                tablas = driver.find_elements(By.CSS_SELECTOR, "table.c0s5")
                
                if tablas:
                    # Buscar todos los enlaces dentro de la tabla que contengan "mundial"
                    enlaces = tablas[0].find_elements(By.CSS_SELECTOR, "a[href*='mundial']")
                    
                    for enlace in enlaces:
                        try:
                            href = enlace.get_attribute("href")
                            texto = enlace.text.strip()
                            
                            if href and texto and "Mundial" in texto:
                                # Extraer año
                                match = re.search(r'\b(19|20)\d{2}\b', texto)
                                if match:
                                    año = match.group()
                                    
                                    # Construir URL completa
                                    if not href.startswith('http'):
                                        if href.startswith('/'):
                                            href = f"https://www.losmundialesdefutbol.com{href}"
                                        elif href.startswith('mundiales/'):
                                            href = f"https://www.losmundialesdefutbol.com/{href}"
                                    
                                    # Evitar duplicados
                                    if not any(m['año'] == año for m in mundiales):
                                        mundiales.append({
                                            'año': año,
                                            'nombre': texto,
                                            'url': href
                                        })
                                        print(f"  ✓ Tabla: {texto} - {año}")
                        except:
                            continue
                
                # --- ESTRATEGIA 2: Buscar en el menú desplegable (sub-menu) ---
                print("  🔍 Estrategia 2: Buscando en menú desplegable...")
                
                # Buscar el div con clase sub-menu
                sub_menus = driver.find_elements(By.CSS_SELECTOR, "div.sub-menu")
                
                for sub_menu in sub_menus:
                    items = sub_menu.find_elements(By.CSS_SELECTOR, "ul li a")
                    
                    for item in items:
                        try:
                            href = item.get_attribute("href")
                            texto = item.text.strip()
                            
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
                                        print(f"  ✓ Menú: {texto} - {año}")
                        except:
                            continue
                
                # --- ESTRATEGIA 3: Buscar en la lista de enlaces directos ---
                if len(mundiales) < 5:  # Si no encontró suficientes
                    print("  🔍 Estrategia 3: Buscando en enlaces directos...")
                    
                    # Buscar todos los enlaces que contengan "mundial" en el texto
                    todos_enlaces = driver.find_elements(By.XPATH, "//a[contains(text(), 'Mundial')]")
                    
                    for enlace in todos_enlaces:
                        try:
                            href = enlace.get_attribute("href")
                            texto = enlace.text.strip()
                            
                            match = re.search(r'\b(19|20)\d{2}\b', texto)
                            if match and href:
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
                                    print(f"  ✓ Directo: {texto} - {año}")
                        except:
                            continue
                
                if mundiales:
                    # Ordenar por año (descendente)
                    mundiales.sort(key=lambda x: x['año'], reverse=True)
                    print(f"\n✅ TOTAL MUNDIALES ENCONTRADOS: {len(mundiales)}")
                    for m in mundiales:
                        print(f"  • {m['año']}: {m['nombre']}")
                else:
                    print(f"  ⚠️ No se encontraron mundiales (intento {intentos + 1}/{max_intentos})")
                    intentos += 1
                    time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                intentos += 1
                time.sleep(random.uniform(3, 5))
            finally:
                if driver:
                    driver.quit()
        
        return mundiales
    
    def extraer_datos_mundial(self, url_mundial, año):
        """Extrae organizador y campeón de la página de un mundial"""
        print(f"\n  📂 Procesando {año}")
        print(f"  📡 URL: {url_mundial}")
        
        datos = {
            'id': None,
            'año': año,
            'pais_organizador': None,
            'pais_campeon': None,
            'url': url_mundial
        }
        
        # Diccionario de campeones conocidos por si no se encuentran
        campeones_conocidos = {
            '2022': 'Argentina', '2018': 'Francia', '2014': 'Alemania', '2010': 'España',
            '2006': 'Italia', '2002': 'Brasil', '1998': 'Francia', '1994': 'Brasil',
            '1990': 'Alemania', '1986': 'Argentina', '1982': 'Italia', '1978': 'Argentina',
            '1974': 'Alemania', '1970': 'Brasil', '1966': 'Inglaterra', '1962': 'Brasil',
            '1958': 'Brasil', '1954': 'Alemania', '1950': 'Uruguay', '1938': 'Italia',
            '1934': 'Italia', '1930': 'Uruguay'
        }
        
        # Diccionario de organizadores conocidos
        organizadores_conocidos = {
            '2022': 'Qatar', '2018': 'Rusia', '2014': 'Brasil', '2010': 'Sudáfrica',
            '2006': 'Alemania', '2002': 'Corea del Sur/Japón', '1998': 'Francia',
            '1994': 'Estados Unidos', '1990': 'Italia', '1986': 'México',
            '1982': 'España', '1978': 'Argentina', '1974': 'Alemania', '1970': 'México',
            '1966': 'Inglaterra', '1962': 'Chile', '1958': 'Suecia', '1954': 'Suiza',
            '1950': 'Brasil', '1938': 'Francia', '1934': 'Italia', '1930': 'Uruguay'
        }
        
        intentos = 0
        max_intentos = 2
        
        while intentos < max_intentos:
            proxy = self.obtener_proxy_disponible() if self.proxies_funcionales else None
            driver = None
            
            try:
                driver = self.configurar_driver_con_proxy(proxy)
                driver.get(url_mundial)
                time.sleep(random.uniform(3, 5))
                
                page_source = driver.page_source
                
                # --- EXTRAER ORGANIZADOR ---
                # Buscar en el breadcrumb
                try:
                    breadcrumb = driver.find_element(By.CSS_SELECTOR, ".breadcrumb")
                    if breadcrumb:
                        texto_bread = breadcrumb.text
                        partes = texto_bread.split('>')
                        if len(partes) >= 3:
                            posible_org = partes[-1].strip()
                            if not posible_org.isdigit() and len(posible_org) > 2:
                                datos['pais_organizador'] = posible_org
                except:
                    pass
                
                # Buscar texto "Organizador:"
                if not datos['pais_organizador']:
                    match = re.search(r'Organizador:\s*([^<]+)', page_source, re.IGNORECASE)
                    if match:
                        datos['pais_organizador'] = match.group(1).strip()
                
                # Si no se encuentra, usar valor conocido
                if not datos['pais_organizador'] and año in organizadores_conocidos:
                    datos['pais_organizador'] = organizadores_conocidos[año]
                
                # --- EXTRAER CAMPEÓN ---
                # Buscar en la estructura con imagen de copa
                try:
                    elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'Campeón')]")
                    for elem in elementos:
                        padre = elem.find_element(By.XPATH, "..")
                        enlaces = padre.find_elements(By.TAG_NAME, "a")
                        if enlaces:
                            datos['pais_campeon'] = enlaces[0].text.strip()
                            break
                except:
                    pass
                
                # Buscar por imagen de la copa
                if not datos['pais_campeon']:
                    try:
                        copa_imgs = driver.find_elements(By.XPATH, "//img[contains(@src, 'copa_del_mundo')]")
                        for img in copa_imgs:
                            try:
                                enlace = img.find_element(By.XPATH, "./following::a[1]")
                                if enlace:
                                    datos['pais_campeon'] = enlace.text.strip()
                                    break
                            except:
                                continue
                    except:
                        pass
                
                # Buscar en el texto
                if not datos['pais_campeon']:
                    match = re.search(r'Campeón[:\s]*([^<\n]+)', page_source, re.IGNORECASE)
                    if match:
                        datos['pais_campeon'] = match.group(1).strip()
                
                # Usar valor conocido
                if not datos['pais_campeon'] and año in campeones_conocidos:
                    datos['pais_campeon'] = campeones_conocidos[año]
                
                print(f"    ✓ Organizador: {datos['pais_organizador'] or 'No encontrado'}")
                print(f"    ✓ Campeón: {datos['pais_campeon'] or 'No encontrado'}")
                
                return datos
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                intentos += 1
                time.sleep(random.uniform(2, 3))
            finally:
                if driver:
                    driver.quit()
        
        # Si falló, al menos devolver los valores conocidos
        datos['pais_organizador'] = organizadores_conocidos.get(año)
        datos['pais_campeon'] = campeones_conocidos.get(año)
        return datos
    
    def scrapear_todos_mundiales(self, url_principal=None):
        """Proceso completo de scraping"""
        if not url_principal:
            url_principal = "https://www.losmundialesdefutbol.com/mundiales.php"
        
        print("\n" + "="*60)
        print("📋 PASO 1: OBTENER LISTA DE MUNDIALES")
        print("="*60)
        
        mundiales = self.obtener_lista_mundiales_desde_html(url_principal)
        
        if not mundiales:
            print("❌ No se pudo obtener la lista de mundiales")
            return []
        
        print(f"\n📊 Mundiales encontrados: {len(mundiales)}")
        
        # PASO 2: Procesar cada mundial
        print("\n" + "="*60)
        print("📋 PASO 2: EXTRAYENDO DATOS DE CADA MUNDIAL")
        print("="*60)
        
        resultados = []
        for i, mundial in enumerate(mundiales, 1):
            print(f"\n📁 [{i}/{len(mundiales)}] {mundial['año']} - {mundial['nombre']}")
            datos = self.extraer_datos_mundial(mundial['url'], mundial['año'])
            if datos:
                datos['id'] = i
                resultados.append(datos)
            
            if i < len(mundiales):
                pausa = random.uniform(2, 4)
                print(f"  ⏳ Pausa de {pausa:.1f}s...")
                time.sleep(pausa)
        
        return resultados
    
    def guardar_csv(self, datos, nombre_archivo='mundiales.csv'):
        if not datos:
            print("❌ No hay datos para guardar")
            return
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['id', 'año', 'pais_organizador', 'pais_campeon', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for mundial in datos:
                writer.writerow({
                    'id': mundial.get('id', ''),
                    'año': mundial.get('año', ''),
                    'pais_organizador': mundial.get('pais_organizador', '').strip() if mundial.get('pais_organizador') else '',
                    'pais_campeon': mundial.get('pais_campeon', '').strip() if mundial.get('pais_campeon') else '',
                    'url': mundial.get('url', '')
                })
        
        print(f"\n💾 Datos guardados en '{nombre_archivo}'")
        
        completos = sum(1 for m in datos if m.get('pais_campeon') and m.get('pais_organizador'))
        print(f"📊 Mundiales con datos completos: {completos}/{len(datos)}")
    
    def mostrar_resumen(self, datos):
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        
        if not datos:
            print("No hay datos para mostrar")
            return
        
        print(f"\nTotal de mundiales: {len(datos)}")
        print("\n📌 Datos extraídos:")
        print("-" * 70)
        print(f"{'ID':<3} {'Año':<6} {'Organizador':<25} {'Campeón':<20}")
        print("-" * 70)
        
        for m in datos:
            org = m.get('pais_organizador', '')[:23] if m.get('pais_organizador') else 'No encontrado'
            camp = m.get('pais_campeon', '')[:18] if m.get('pais_campeon') else 'No encontrado'
            print(f"{m.get('id', ''):<3} {m.get('año', ''):<6} {org:<25} {camp:<20}")

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🏆 SCRAPER DE MUNDIALES - VERSIÓN FINAL")
    print("="*60)
    
    # 1. Configurar proxies
    print("\n" + "-"*40)
    print("🔧 CONFIGURACIÓN DE PROXIES")
    print("-"*40)
    
    usar_proxies = input("¿Usar proxies para evitar bloqueos? (s/n): ").strip().lower()
    
    proxies_funcionales = []
    if usar_proxies == 's':
        todos_proxies = obtener_lista_proxies()
        print(f"📋 Total proxies en lista: {len(todos_proxies)}")
        
        probar = input("¿Probar qué proxies funcionan primero? (s/n): ").strip().lower()
        if probar == 's':
            proxies_funcionales = probar_proxies_en_paralelo(todos_proxies)
            print(f"\n✅ Proxies funcionales: {len(proxies_funcionales)}")
        else:
            proxies_funcionales = todos_proxies[:20]
            print("⚠️ Usando primeros 20 proxies sin probar")
    
    # 2. Crear scraper
    scraper = ScraperMundiales(proxies_funcionales if usar_proxies == 's' else None)
    
    # 3. Configurar archivo
    print("\n" + "-"*40)
    print("⚙️  CONFIGURACIÓN")
    print("-"*40)
    
    nombre_archivo = input("Nombre del archivo CSV (Enter para 'mundiales.csv'): ").strip()
    if not nombre_archivo:
        nombre_archivo = 'mundiales.csv'
    elif not nombre_archivo.endswith('.csv'):
        nombre_archivo += '.csv'
    
    # 4. Ejecutar
    print("\n" + "="*60)
    print("🚀 INICIANDO SCRAPING...")
    print("="*60)
    
    try:
        resultados = scraper.scrapear_todos_mundiales()
        
        if resultados:
            scraper.guardar_csv(resultados, nombre_archivo)
            scraper.mostrar_resumen(resultados)
            print(f"\n✅ PROCESO COMPLETADO!")
            print(f"📁 Revisa el archivo: {nombre_archivo}")
        else:
            print("\n❌ No se obtuvieron resultados")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        if 'resultados' in locals() and resultados:
            scraper.guardar_csv(resultados, 'mundiales_PARCIAL.csv')
            print("💾 Datos parciales guardados")
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()