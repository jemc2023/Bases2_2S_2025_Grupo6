from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tu lista de proxies (la que me pasaste)
PROXIES_LISTA = """
137.184.96.68:80
47.251.73.54:64
158.160.215.167:8123
172.237.73.24:80
113.160.132.26:8080
188.213.165.38:80
197.221.240.178:80
20.81.205.173:80
150.230.249.50:1080
35.225.22.61:80
8.212.165.164:999
103.30.30.6:20326
124.108.6.20:8085
46.250.251.246:80
139.162.200.213:80
81.10.234.234:80
113.11.64.137:20326
38.145.208.135:8443
197.221.234.252:80
138.124.53.25:7443
46.8.233.226:3128
38.145.208.102:8443
147.75.34.105:443
116.203.139.209:5678
165.227.5.10:8888
8.219.97.248:80
118.193.37.241:3129
138.91.159.185:80
147.91.22.150:80
152.230.215.123:80
39.109.113.97:4090
167.99.236.14:80
4.195.16.140:80
150.107.140.238:3128
103.65.237.92:5678
41.220.16.218:80
165.227.118.27:80
159.65.245.255:80
103.113.70.189:1081
62.84.245.79:80
219.93.101.62:80
107.174.231.218:8888
32.223.6.94:80
23.247.136.254:80
190.58.248.86:80
50.122.86.118:80
46.29.162.166:80
210.177.178.148:80
190.119.132.61:80
20.210.113.32:8123
82.65.220.152:80
144.124.227.90:21074
112.198.22.122:80
210.223.44.230:3128
89.58.55.33:80
156.146.56.231:8081
81.169.213.169:8888
89.58.57.45:80
103.133.26.119:8080
43.167.227.161:1080
213.157.6.50:80
213.33.126.130:80
194.158.203.14:80
219.93.101.63:80
23.88.88.105:443
197.221.249.196:80
34.81.160.132:80
66.111.113.34:80
23.88.88.102:80
62.99.138.162:80
1.225.116.115:1080
27.34.242.98:80
103.125.31.222:80
34.44.49.215:80
109.236.88.82:80
46.47.197.210:3128
219.93.101.60:80
46.249.100.124:80
160.251.142.232:80
0.0.0.0:80
127.0.0.7:80
79.137.17.104:80
174.138.119.88:80
5.161.155.252:80
133.18.234.13:80
141.147.9.254:80
86.53.183.16:1080
85.198.96.242:3128
8.212.177.126:8080
219.65.73.81:80
41.220.22.7:80
41.220.16.213:80
41.220.16.208:80
213.230.110.191:3128
81.177.160.200:80
69.48.201.94:80
203.76.98.21:45958
75.84.71.14:80
185.85.111.18:80
82.165.20.115:80
66.135.16.53:80
1.1.220.100:8080
222.252.97.26:8008
170.80.95.10:11211
179.49.237.6:999
103.153.149.140:8181
182.53.202.208:8080
103.144.90.75:8081
82.165.61.217:8085
149.88.94.216:7890
45.136.130.220:8443
193.23.200.251:10808
195.158.8.123:3128
35.209.198.222:80
95.3.9.78:3128
46.17.47.48:80
138.68.235.51:80
12.50.107.220:80
174.138.54.65:80
12.50.107.222:80
64.188.90.36:1080
45.136.130.234:8443
38.145.220.219:8443
38.145.220.189:8443
38.145.220.206:8443
38.145.220.221:8443
38.145.220.244:8443
45.136.130.236:8443
38.145.220.192:8443
38.145.220.191:8443
38.145.220.209:8443
38.145.203.135:8443
146.19.128.135:1080
102.223.9.53:80
217.217.249.160:8080
197.221.249.198:80
103.84.95.54:7890
200.174.198.32:8888
57.128.188.167:9157
139.99.237.62:80
37.27.6.46:80
41.173.7.82:8080
89.116.88.19:80
38.60.196.214:80
143.198.135.176:80
103.94.52.70:3128
192.73.244.36:80
51.79.135.131:8080
62.60.177.204:34094
45.136.130.235:8443
45.136.130.237:8443
38.145.220.243:8443
197.221.234.149:80
147.231.163.133:80
47.56.110.204:8989
85.214.204.79:80
47.238.130.212:8004
143.208.57.59:8080
139.177.190.161:3128
103.137.218.233:83
85.117.56.115:8080
201.220.112.98:999
47.91.120.190:1080
160.248.7.177:80
41.220.16.210:80
35.224.171.0:80
47.237.107.41:135
175.139.233.76:80
34.140.137.151:80
150.136.163.51:80
38.145.203.162:8443
38.145.220.220:8443
38.145.220.9:8443
176.126.164.213:80
38.145.208.93:8443
38.145.208.98:8443
38.145.203.246:8443
38.145.208.95:8443
45.136.130.227:8443
38.145.220.13:8443
38.145.208.96:8443
121.126.185.63:25152
97.74.87.226:80
193.32.178.160:57329
38.145.208.37:8443
38.145.208.137:8443
38.145.203.235:8443
38.145.208.141:8443
45.136.130.233:8443
114.111.151.41:80
154.65.39.7:80
190.119.132.62:80
45.207.200.120:1080
38.145.203.161:8443
69.70.244.34:80
34.122.187.196:80
38.145.208.94:8443
38.145.208.99:8443
116.80.49.156:3172
171.233.34.80:8080
176.61.151.123:80
175.101.240.38:80
45.136.130.219:8443
52.142.253.29:80
172.193.178.226:80
212.47.232.28:80
195.26.224.135:80
150.136.254.73:443
144.31.137.23:8080
198.111.166.184:80
103.151.20.131:80
181.78.107.139:999
47.91.121.127:50
38.34.183.130:8443
183.110.216.128:8090
168.121.222.230:80
41.220.16.215:80
108.170.12.14:80
103.253.145.138:6980
38.146.28.249:40000
37.26.86.206:47464
58.147.190.145:8181
180.211.179.126:8080
103.156.233.63:8080
43.243.172.186:83
170.245.132.82:9000
203.150.166.170:8080
103.169.189.202:9090
112.203.122.13:8082
103.51.122.253:3125
212.108.115.172:8080
115.247.115.38:8080
154.19.38.169:8080
197.221.240.247:80
154.90.48.76:80
168.235.110.63:3128
167.71.196.28:8080
12.50.107.221:80
38.145.208.145:8443
178.156.224.42:3128
38.145.208.181:8443
45.136.130.163:8443
38.145.220.11:8443
38.145.208.138:8447
47.238.203.170:50000
203.175.127.240:8080
202.58.64.67:1111
103.246.1.146:8080
154.6.116.121:6090
86.38.236.56:6340
31.58.21.197:6468
162.220.246.204:6488
199.180.9.145:6165
45.151.161.150:6241
206.206.119.209:6120
136.0.182.184:6254
45.43.70.200:6487
145.223.46.112:5662
45.41.179.18:6553
50.114.82.123:7107
38.154.197.79:6745
136.0.118.20:6392
209.127.127.163:7261
161.123.101.5:6631
217.69.121.186:5851
31.57.42.221:6491
136.0.127.254:5963
107.173.36.219:5674
104.233.12.64:6615
67.227.113.40:5580
216.173.120.23:6315
199.180.10.119:6490
23.229.19.75:8670
136.0.180.146:6167
103.84.177.30:8083
107.173.137.209:6463
198.23.239.188:6594
136.0.188.158:6121
198.12.112.246:5257
107.174.215.31:7972
64.64.127.251:6204
191.101.181.185:6938
31.57.82.158:6739
209.127.143.134:8233
86.38.26.47:6212
136.0.189.98:6825
173.211.8.161:6273
191.101.25.37:6434
23.94.246.239:8192
46.203.96.188:6312
104.245.244.69:6509
191.96.202.39:6085
31.58.18.131:6400
192.154.250.243:5823
198.23.128.130:5758
161.123.131.106:5711
198.105.111.91:6769
136.0.194.2:6739
86.38.154.15:5658
185.216.106.195:6272

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
    """Prueba si un proxy funciona"""
    try:
        # Intentar conectar a Google a través del proxy
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
            print(f"✅ Proxy funciona: {proxy}")
            return proxy
        else:
            print(f"❌ Proxy devuelve {response.status_code}: {proxy}")
            return None
    except Exception as e:
        print(f"❌ Proxy falla: {proxy} - {str(e)[:50]}")
        return None

def probar_proxies_en_paralelo(proxies, max_workers=20):
    """Prueba múltiples proxies en paralelo"""
    proxies_funcionales = []
    
    print(f"🔍 Probando {len(proxies)} proxies...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(probar_proxy, proxy): proxy for proxy in proxies}
        
        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                proxies_funcionales.append(resultado)
    
    return proxies_funcionales

class ScraperConProxies:
    def __init__(self, proxies_list):
        self.proxies_funcionales = proxies_list
        self.proxies_usados = set()
        print(f"📊 Inicializado con {len(self.proxies_funcionales)} proxies funcionales")
    
    def obtener_proxy_disponible(self):
        """Obtiene un proxy aleatorio que no se haya usado recientemente"""
        proxies_disponibles = [p for p in self.proxies_funcionales if p not in self.proxies_usados]
        
        if not proxies_disponibles:
            # Si todos se usaron, reiniciar el conjunto
            self.proxies_usados.clear()
            proxies_disponibles = self.proxies_funcionales
        
        proxy = random.choice(proxies_disponibles)
        self.proxies_usados.add(proxy)
        return proxy
    
    def obtener_html_con_selenium(self, url, nombre_archivo, max_intentos=5):
        """
        Intenta obtener el HTML usando diferentes proxies
        """
        for intento in range(max_intentos):
            print(f"\n{'='*60}")
            print(f"🔄 INTENTO {intento + 1} de {max_intentos}")
            
            # Obtener proxy
            proxy = self.obtener_proxy_disponible()
            print(f"🌍 Usando proxy: {proxy}")
            
            options = Options()
            
            # Configuración anti-detección
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User-agent aleatorio
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Configurar proxy
            options.add_argument(f'--proxy-server=http://{proxy}')
            
            # Opciones para rendimiento
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-images')
            options.add_argument('--window-size=1920,1080')
            
            # Modo headless (oculto) - opcional, quitar si quieres ver el navegador
            # options.add_argument('--headless')
            
            try:
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
                
                print(f"📡 Accediendo a: {url}")
                driver.set_page_load_timeout(30)
                driver.get(url)
                
                # Espera aleatoria
                time.sleep(random.uniform(5, 10))
                
                # Verificar bloqueo
                if "403" in driver.title or "forbidden" in driver.page_source.lower():
                    print(f"⚠️ Proxy {proxy} bloqueado (403)")
                    driver.quit()
                    continue
                
                # Guardar HTML
                html = driver.page_source
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                print(f"✅ ÉXITO con proxy {proxy}")
                print(f"📌 Título: {driver.title}")
                print(f"📊 Tamaño: {len(html):,} caracteres")
                
                driver.quit()
                return html
                
            except Exception as e:
                print(f"❌ Error con proxy {proxy}: {str(e)[:100]}")
                if 'driver' in locals():
                    driver.quit()
                continue
            
            finally:
                # Pequeña pausa entre intentos
                time.sleep(random.uniform(2, 5))
        
        print("\n❌ No se pudo acceder con ningún proxy")
        return None

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("🕷️  SCRAPER CON PROXIES GRATUITOS")
    print("="*60)
    
    # 1. Obtener lista de proxies
    todos_proxies = obtener_lista_proxies()
    print(f"📋 Total proxies en lista: {len(todos_proxies)}")
    
    # 2. Preguntar si probar proxies
    probar = input("\n¿Probar qué proxies funcionan primero? (s/n): ").strip().lower()
    
    proxies_funcionales = []
    if probar == 's':
        print("\n🔍 Probando proxies (puede tomar 1-2 minutos)...")
        # Probar solo los primeros 50 para no tardar demasiado
        proxies_a_probar = todos_proxies[:50]
        proxies_funcionales = probar_proxies_en_paralelo(proxies_a_probar)
        
        print(f"\n✅ Proxies funcionales encontrados: {len(proxies_funcionales)}")
        if proxies_funcionales:
            print("Proxies que funcionan:")
            for p in proxies_funcionales[:10]:  # Mostrar solo los primeros 10
                print(f"   - {p}")
    else:
        # Usar todos sin probar (menos fiable pero más rápido)
        proxies_funcionales = todos_proxies
        print("⚠️ Usando todos los proxies sin probar (muchos fallarán)")
    
    if not proxies_funcionales:
        print("❌ No hay proxies funcionales. ¿Quieres continuar con tu IP normal?")
        continuar = input("(s/n): ").strip().lower()
        if continuar != 's':
            exit()
    
    # 3. Pedir URL
    print("\n" + "="*60)
    url = input("URL a scrapear: ").strip()
    nombre = input("Nombre archivo (ej: pagina.html): ").strip()
    
    if not nombre.endswith('.html'):
        nombre += '.html'
    
    # 4. Ejecutar scraping
    if proxies_funcionales:
        scraper = ScraperConProxies(proxies_funcionales)
        resultado = scraper.obtener_html_con_selenium(url, nombre)
    else:
        # Fallback a tu código original sin proxy
        print("⚠️ Usando método sin proxy (tu IP original)")
        resultado = obtener_html_con_selenium_original(url, nombre)  # Tu función original
    
    if resultado:
        print(f"\n✅ Archivo guardado: {nombre}")
    else:
        print("\n❌ No se pudo obtener la página")