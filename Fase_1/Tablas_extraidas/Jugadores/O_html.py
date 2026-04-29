from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

def obtener_proxy_gratuito():
    """Obtiene un proxy gratuito de una lista (esto es solo un ejemplo)"""
    # Lista de proxies gratuitos (debes actualizarlos frecuentemente)
    proxies = [
        "187.190.190.90:8080",  # Estos son solo ejemplos, NO funcionarán
        "201.91.82.155:3128",    # Busca proxies gratuitos actualizados en:
        "177.93.45.162:999"      # https://free-proxy-list.net/
    ]
    return random.choice(proxies) if proxies else None

def obtener_html_con_selenium_proxy(url, nombre_archivo, usar_proxy=True):
    """
    Abre la página con Selenium usando proxy para cambiar la IP
    """
    options = Options()
    
    # Configuraciones para evitar detección
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Añadir user-agent aleatorio para parecer más humano
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    # Configurar proxy si se solicita
    if usar_proxy:
        proxy = obtener_proxy_gratuito()
        if proxy:
            print(f"🔄 Usando proxy: {proxy}")
            options.add_argument(f'--proxy-server=http://{proxy}')
        else:
            print("⚠️ No se encontró proxy, continuando sin proxy...")
    
    print("🌍 Abriendo navegador...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        print(f"📡 Navegando a: {url}")
        driver.get(url)
        
        # Esperar tiempo variable para parecer humano
        tiempo_espera = random.uniform(5, 10)
        time.sleep(tiempo_espera)
        
        # Verificar si hay bloqueo
        if "403" in driver.title or "Forbidden" in driver.page_source:
            print("⚠️ Detectado posible bloqueo (403)")
            # Podrías intentar con otro proxy aquí
        
        html = driver.page_source
        print(f"✅ HTML obtenido. Tamaño: {len(html):,} caracteres")
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 HTML guardado en: {nombre_archivo}")
        print(f"📌 Título de la página: {driver.title}")
        
        return html
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        print("🔒 Cerrando navegador...")
        driver.quit()