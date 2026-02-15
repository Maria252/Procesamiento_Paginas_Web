import os
import pandas as pd
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse
import re
import json
import time
import asyncio
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import aiohttp
from datetime import datetime
import google.generativeai as genai
from getpass import getpass

# ========== CONFIGURACIÓN ==========
print("🔐 Configuración de Google Gemini API Key")
print("Necesitas una API Key de Google AI Studio para usar Gemini")
print("Puedes obtenerla en: https://makersuite.google.com/app/apikey")
print()

gemini_api_key = "PON_AQUI_TU_API_KEY"  # Reemplaza con tu API Key o usa getpass para ingresarla de forma segura

genai.configure(api_key=gemini_api_key)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_CSV = os.environ.get("COMPANY_XLSX", os.path.join(DATA_DIR, "companies_demo.xlsx"))
HTML_DIR = os.environ.get("COMPANY_HTML", os.path.join(DATA_DIR, "htmls"))
OUTPUT_DIR = HTML_DIR
OUTPUT_FILE = os.environ.get("COMPANY_OUT", os.path.join(DATA_DIR, "processed", "company_info_V5.csv"))
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "checkpoint.json")
CACHE_FILE = os.path.join(OUTPUT_DIR, "gpt_cache.json")
BLOCKED_SITES_FILE = os.path.join(OUTPUT_DIR, "blocked_sites.json")

# Configuración de procesamiento
MAX_CONCURRENT_COMPANIES = int(os.environ.get("MAX_CONCURRENT", "5"))
GPT_RATE_LIMIT_DELAY = float(os.environ.get("GPT_DELAY", "1.0"))
URL_VALIDATION_TIMEOUT = int(os.environ.get("URL_TIMEOUT", "10"))

# Crea las carpetas si no existen
for path in [HTML_DIR, OUTPUT_DIR, os.path.dirname(OUTPUT_FILE)]:
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, 'processing.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

KEYWORDS = [
    # CONTACTO Y GENERAL
    'contact', 'contact-us', 'get-in-touch', 'contacts', 'contact-info', 'contact-information',
    'reach-us', 'connect', 'contactus', 'inquiries', 'support', 'customer-support', 'customer-service',

    # ACERCA DE/QUIÉNES SOMOS
    'about', 'about-us', 'who-we-are', 'our-story', 'company-overview', 'company-info', 'company-information',
    'overview', 'mission', 'our-mission', 'vision', 'our-vision', 'history', 'our-history', 'background',
    'values', 'our-values', 'core-values', 'what-we-do', 'who-we-are',

    # EQUIPO / LIDERAZGO
    'team', 'our-team', 'leadership', 'leadership-team', 'management', 'management-team', 'executives',
    'executive-team', 'board', 'board-of-directors', 'directors', 'board-members', 'founders', 'co-founders',
    'partners', 'partner-team', 'staff', 'employees', 'people', 'our-people',

    # CARRERAS / EMPLEO
    'careers', 'career', 'jobs', 'job-openings', 'work-with-us', 'join-our-team', 'opportunities', 'vacancies',
    'employment', 'job-listings', 'internships', 'internship-opportunities',

    # SERVICIOS / PRODUCTOS
    'services', 'service', 'our-services', 'products', 'our-products', 'solutions', 'what-we-offer',
    'offerings', 'capabilities', 'portfolio',

    # PARTNERS / SOCIOS
    'partners', 'our-partners', 'partnerships', 'alliances', 'affiliates', 'collaborators',

    # RESPONSABILIDAD / SOSTENIBILIDAD
    'sustainability', 'sustainable', 'corporate-social-responsibility', 'csr', 'responsibility',
    'annual-report', 'esg', 'environment', 'sustainability-report', 'impact',

    # HISTORIA / TRAYECTORIA
    'history', 'our-history', 'story', 'company-story', 'background', 'trajectory', 'track-record',

    # OTROS CORPORATIVOS
    'directory', 'directory-board', 'governance', 'governance-structure', 'advisors', 'advisory-board',
    'committee', 'committees', 'executive-board', 'leadership-structure',

    # ESPAÑOL ÚTIL SI OCUPAS WEBS BILINGÜES O LATAM
    'empresa', 'servicio', 'servicios', 'quienes', 'quiénes', 'acerca', 'nosotros', 'equipo',
    'contacto', 'trayectoria', 'historia', 'mision', 'misión', 'valores', 'directorio', 'gerencia', 'fundadores'
]



def normalize_url(url):
    if not url:
        return ""
    
    url = url.strip()
    
    # Remove any trailing slash first to normalize
    url = url.rstrip('/')
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Convert http to https
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    
    # Ensure it starts with www. after the protocol
    if url.startswith('https://') and not url.startswith('https://www.'):
        # Check if it already has www.
        domain_part = url[8:]  # Remove 'https://'
        if not domain_part.startswith('www.'):
            url = 'https://www.' + domain_part
    
    # Add trailing slash
    if not url.endswith('/'):
        url += '/'
    
    return url

def safe_filename(s, default="file"):
    s = str(s)
    s = re.sub(r'[<>:"/\\|?*\']', '_', s)
    s = re.sub(r'\s+', '_', s)
    return s if s not in ("", ".", "..") else default

def extract_visible_text(html, max_length=14000):
    """Extraer texto visible mejorado, simulando lo que ve un usuario"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remover elementos que no son visibles o no son útiles
    for element in soup(['script', 'style', 'noscript', 'meta', 'link', 'head']):
        element.decompose()
    
    # Remover comentarios HTML
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remover elementos comúnmente ocultos
    for element in soup.find_all(attrs={'style': lambda x: x and 'display:none' in x.replace(' ', '')}):
        element.decompose()
    
    for element in soup.find_all(attrs={'class': lambda x: x and any(hidden in str(x).lower() for hidden in ['hidden', 'hide', 'invisible', 'sr-only'])}):
        element.decompose()
    
    # Priorizar contenido importante
    important_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'p', 'div', 'section', 'article', 'main']
    important_classes = ['content', 'main', 'body', 'description', 'about', 'info', 'text', 'mission', 'vision', 'company', 'business']
    
    important_text = []
    regular_text = []
    
    # Extraer texto de elementos importantes primero
    for tag_name in important_tags:
        for element in soup.find_all(tag_name):
            element_text = element.get_text(separator=' ', strip=True)
            if element_text and len(element_text) > 10:  # Filtrar texto muy corto
                # Verificar si es contenido importante por clase
                element_classes = element.get('class', [])
                if any(important_class in str(element_classes).lower() for important_class in important_classes):
                    important_text.append(element_text)
                else:
                    regular_text.append(element_text)
    
    # Si no hay texto importante suficiente, usar todo el texto
    if not important_text:
        text = soup.get_text(separator=' ', strip=True)
    else:
        # Combinar texto importante primero, luego regular si hay espacio
        text = ' '.join(important_text)
        if len(text) < max_length // 2:
            remaining_length = max_length - len(text)
            additional_text = ' '.join(regular_text)[:remaining_length]
            text = text + ' ' + additional_text
    
    # Limpiar texto
    text = ' '.join(text.split())  # Normalizar espacios
    text = text.replace('\n', ' ').replace('\t', ' ')
    
    return text[:max_length]

def merge_htmls_for_company(company, html_dir):
    prefix = safe_filename(company)
    htmls = []
    for fname in os.listdir(html_dir):
        if fname.startswith(prefix) and fname.endswith('.html'):
            try:
                with open(os.path.join(html_dir, fname), encoding="utf-8") as f:
                    htmls.append(f.read())
            except Exception as e:
                logger.warning(f"Ignorado {fname}: {e}")
    return "\n".join(htmls) if htmls else ""

def build_prompt(text):
    return f"""
Eres un experto en extracción de datos empresariales. Analiza el siguiente texto de un sitio web empresarial y responde ÚNICAMENTE con un JSON que contenga:

- hq_city: Ciudad de la sede principal (string)
- hq_state: Estado/provincia de la sede principal (string) 
- company_description: Descripción breve de la empresa (máximo 60 palabras)
- sector: Sector industrial (ej: 'Tecnología', 'Servicios Financieros', 'Manufactura')
- rol_empresa: Rol en la cadena de suministro (ej: 'Productor', 'Distribuidor', 'Retailer', 'Mayorista', 'Importador', 'Exportador', 'Fabricante', 'Proveedor de Servicios')
- presence_in_latam: Presencia en Latinoamérica (True/False + lista países si se mencionan)
- contact_phone: Números de teléfono de contacto (lista de strings)
- productos_comercializan: Descripción de los principales productos que comercializa la empresa

Si falta algún campo, usa "No Information".

Responde únicamente con el JSON, sin explicaciones adicionales.

Texto:
{text}
"""

def call_gemini(prompt, model_name="gemini-2.0-flash", cache=None):
    """Llamar a Gemini con caché y rate limiting."""
    if cache is None:
        cache = {}
    
    cache_key = create_cache_key(prompt)
    if cache_key in cache:
        logger.info("Usando respuesta desde caché de Gemini")
        return cache[cache_key]
    
    model = genai.GenerativeModel(model_name)
    
    # Rate limiting
    time.sleep(GPT_RATE_LIMIT_DELAY)
    
    try:
        response = model.generate_content(prompt)
        result = response.text
        
        cache[cache_key] = result
        
        logger.info("Respuesta de Gemini obtenida y guardada en caché")
        return result
        
    except Exception as e:
        logger.error(f"Error en Gemini: {e}")
        return "{}"

def normalize_response(data):
    """Normalize the AI response dictionary."""
    if not isinstance(data, dict):
        # If data is not a dictionary, it's likely an error message or unexpected format.
        # Return a dictionary with all fields set to 'No Information'
        keys = [
            'hq_city', 'hq_state', 'company_description', 'sector', 'rol_empresa',
            'presence_in_latam', 'contact_phone', 'productos_comercializan'
        ]
        return {key: 'No Information' for key in keys}

    normalized_data = {}
    key_mapping = {
        'hq_city': ['hq_city', 'city', 'headquarters_city'],
        'hq_state': ['hq_state', 'state', 'headquarters_state'],
        'company_description': ['company_description', 'description'],
        'sector': ['sector', 'industry'],
        'rol_empresa': ['rol_empresa', 'company_role'],
        'presence_in_latam': ['presence_in_latam', 'latam_presence'],
        'contact_phone': ['contact_phone', 'phone', 'contact'],
        'productos_comercializan': ['productos_comercializan', 'products_sold']
    }

    for standard_key, possible_keys in key_mapping.items():
        found = False
        for key in possible_keys:
            if key in data and data[key] is not None:
                value = data[key]
                # Basic cleaning for string values
                if isinstance(value, str):
                    value = value.strip()
                    if value.lower() in ['null', 'none', 'n/a', 'na', '']:
                        value = "No Information"
                # Ensure lists are not empty
                elif isinstance(value, list) and not value:
                    value = "No Information"
                
                normalized_data[standard_key] = value
                found = True
                break
        if not found:
            normalized_data[standard_key] = 'No Information'
            
    # Specific normalizations
    latam_presence = normalized_data.get('presence_in_latam', "No Information")
    if isinstance(latam_presence, str):
        latam_lower = latam_presence.lower().strip()
        if latam_lower in ['true', 'yes', 'sí', 'si']:
            normalized_data['presence_in_latam'] = "True"
        elif latam_lower in ['false', 'no']:
            normalized_data['presence_in_latam'] = "False"

    return normalized_data

def parse_response_to_dict(response_text):
    """Extracts a JSON object from a string and normalizes it."""
    try:
        # Find the start of the JSON object
        json_start = response_text.find('{')
        # Find the end of the JSON object
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            # Attempt to parse the JSON
            data = json.loads(json_str)
            return normalize_response(data)
        else:
            logging.warning(f"No JSON object found in the response: {response_text}")
            return normalize_response(None)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON from response: {e}")
        logging.error(f"Response text was: {response_text}")
        return normalize_response(None)
    except Exception as e:
        logging.error(f"An unexpected error occurred in parse_response_to_dict: {e}")
        return normalize_response(None)

def find_internal_links(html, base_url, keywords=KEYWORDS, max_links=8):
    soup = BeautifulSoup(html, 'html.parser')
    found, seen = [], set()
    for a in soup.find_all('a', href=True):
        href, text = a['href'], (a.get_text() or "").lower()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc != urlparse(base_url).netloc: continue
        if full_url in seen: continue
        if any(kw in href.lower() for kw in keywords) or any(kw in text for kw in keywords):
            found.append(full_url)
            seen.add(full_url)
        if len(found) >= max_links: break
    return found

async def get_rendered_html_async(url, timeout=20000, max_retries=3):
    """Obtener HTML renderizado con mejor manejo de contenido dinámico"""
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    ignore_https_errors=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                # Configurar timeouts más largos para contenido dinámico
                page.set_default_timeout(30000)
                page.set_default_navigation_timeout(30000)
                
                # Navegar a la página
                await page.goto(url, timeout=timeout, wait_until='networkidle')
                
                # Esperar a que se cargue el contenido dinámico
                await page.wait_for_timeout(5000)
                
                # Intentar hacer scroll para activar lazy loading
                try:
                    await page.evaluate("""
                        async () => {
                            await new Promise((resolve) => {
                                let totalHeight = 0;
                                const distance = 100;
                                const timer = setInterval(() => {
                                    const scrollHeight = document.body.scrollHeight;
                                    window.scrollBy(0, distance);
                                    totalHeight += distance;
                                    
                                    if(totalHeight >= scrollHeight){
                                        clearInterval(timer);
                                        resolve();
                                    }
                                }, 100);
                            });
                        }
                    """)
                    await page.wait_for_timeout(2000)
                except:
                    pass  # Si falla el scroll, continuar
                
                # Volver al inicio de la página
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(1000)
                
                # Obtener el HTML final renderizado
                html = await page.content()
                await browser.close()
                
                logger.info(f"    HTML renderizado obtenido para {url} (intento {attempt+1})")
                return html
                
        except Exception as e:
            logger.error(f"Error intento {attempt+1} para {url}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3 * (attempt + 1))
    
    logger.error(f"No se pudo obtener HTML después de {max_retries} intentos para {url}")
    return None


def save_checkpoint(processed):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()

async def download_sections(sections, company, base_output_dir, timeout=20000):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) 
        tasks, results = [], {}
        for link in sections:
            tasks.append(_fetch_and_save_section(browser, link, company, base_output_dir, timeout))
        results_list = await asyncio.gather(*tasks)
        for url, html, fname in results_list:
            if html:
                results[url] = fname
        await browser.close()
        return results

async def _fetch_and_save_section(browser, link, company, base_output_dir, timeout):
    """Descargar sección con mejor renderizado"""
    extra = urlparse(link).path.strip("/").replace("/", "_") or "extra"
    extra_filename = safe_filename(company + "_" + extra) + ".html"
    
    try:
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Configurar timeouts
        page.set_default_timeout(25000)
        page.set_default_navigation_timeout(25000)
        
        # Navegar y esperar contenido
        await page.goto(link, timeout=timeout, wait_until='networkidle')
        await page.wait_for_timeout(3000)
        
        # Scroll rápido para activar lazy loading
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(500)
        except:
            pass
        
        html_section = await page.content()
        
        # Guardar archivo
        with open(os.path.join(base_output_dir, extra_filename), "w", encoding="utf-8") as f:
            f.write(html_section)
        
        await page.close()
        await context.close()
        
        logger.info(f"    Descargado: {link} -> {extra_filename}")
        return (link, html_section, extra_filename)
        
    except Exception as e:
        logger.error(f"    Error descargando {link}: {e}")
        return (link, None, extra_filename)

# ========== FUNCIONES DE VALIDACIÓN Y CACHÉ ==========

def create_cache_key(text):
    """Crear clave única para caché basada en el contenido"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def load_gpt_cache():
    """Cargar caché de respuestas GPT"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error cargando caché GPT: {e}")
    return {}

def save_gpt_cache(cache):
    """Guardar caché de respuestas GPT"""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando caché GPT: {e}")

def load_blocked_sites():
    """Cargar lista de sitios bloqueados/inaccesibles"""
    if os.path.exists(BLOCKED_SITES_FILE):
        try:
            with open(BLOCKED_SITES_FILE, encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"Error cargando sitios bloqueados: {e}")
    return set()

def save_blocked_sites(blocked_sites):
    """Guardar lista de sitios bloqueados"""
    try:
        with open(BLOCKED_SITES_FILE, "w", encoding="utf-8") as f:
            json.dump(list(blocked_sites), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando sitios bloqueados: {e}")

async def validate_url(url, use_fallback=True):
    """Validar si una URL es accesible antes del procesamiento con múltiples métodos"""
    try:
        # Primer intento: HEAD request
        timeout = aiohttp.ClientTimeout(total=URL_VALIDATION_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.head(url) as response:
                    if response.status < 400:
                        return True
            except:
                pass  # Si HEAD falla, intentar GET
            
            # Segundo intento: GET request (algunos sitios bloquean HEAD)
            if use_fallback:
                try:
                    async with session.get(url) as response:
                        return response.status < 400
                except:
                    pass
        
        return False
        
    except Exception as e:
        logger.warning(f"URL no accesible {url}: {e}")
        return False

def review_blocked_sites(blocked_sites, df):
    """Revisar y mostrar estadísticas de sitios bloqueados"""
    if not blocked_sites:
        logger.info("No hay sitios bloqueados")
        return
    
    logger.info(f"=== SITIOS BLOQUEADOS: {len(blocked_sites)} ===")
    
    # Contar empresas afectadas
    affected_companies = []
    for idx, row in df.iterrows():
        url = str(row.get("Website", "")).strip()
        if url and normalize_url(url) in blocked_sites:
            company_name = row.get('Company Name', f"empresa_{idx}")
            affected_companies.append((company_name, normalize_url(url)))
    
    logger.info(f"Empresas afectadas: {len(affected_companies)}")
    
    # Mostrar algunos ejemplos
    for i, (company, url) in enumerate(affected_companies[:10]):
        logger.info(f"  {i+1}. {company}: {url}")
    
    if len(affected_companies) > 10:
        logger.info(f"  ... y {len(affected_companies) - 10} más")
    
    return affected_companies

def clear_blocked_sites_file():
    """Limpiar archivo de sitios bloqueados"""
    try:
        if os.path.exists(BLOCKED_SITES_FILE):
            os.remove(BLOCKED_SITES_FILE)
            logger.info("Archivo de sitios bloqueados eliminado")
        else:
            logger.info("No existe archivo de sitios bloqueados")
    except Exception as e:
        logger.error(f"Error eliminando archivo de sitios bloqueados: {e}")

def normalize_gpt_response(data):
    """This function is deprecated and will be removed. Use normalize_response instead."""
    # This function is kept for backward compatibility during transition,
    # but it just calls the new function.
    return normalize_response(data)

async def process_single_company(idx, row, total, blocked_sites, gpt_cache):
    """Procesar una sola empresa de manera asíncrona"""
    company = row.get('Company Name', f"empresa_{idx}")
    url = str(row.get("Website", "")).strip()
    
    if not url:
        logger.warning(f"[{idx+1}/{total}] {company}: URL vacía, saltando")
        return None
    
    # Normalizar URL
    url = normalize_url(url)
    
    # Verificar si está en sitios bloqueados
    if url in blocked_sites:
        logger.warning(f"[{idx+1}/{total}] {company}: Sitio previamente bloqueado, saltando")
        return None
    
    # Validar URL antes de procesar (validación menos estricta)
    if not await validate_url(url, use_fallback=True):
        logger.warning(f"[{idx+1}/{total}] {company}: URL no accesible después de validación completa, agregando a sitios bloqueados")
        blocked_sites.add(url)
        return None
    
    prefix = safe_filename(company)
    already_extracted = any(fname.startswith(prefix) and fname.endswith(".html") for fname in os.listdir(HTML_DIR))
    
    # Descargar HTMLs solo si no existen
    if not already_extracted:
        logger.info(f"[{idx+1}/{total}] Descargando HTMLs de {company}: {url}")
        
        try:
            html_home = await get_rendered_html_async(url)
            if html_home:
                home_filename = safe_filename(company, "home") + ".html"
                with open(os.path.join(OUTPUT_DIR, home_filename), "w", encoding="utf-8") as f:
                    f.write(html_home)
                
                links = find_internal_links(html_home, url)
                if links:
                    logger.info(f"    Secciones relevantes encontradas: {len(links)}")
                    await download_sections(links, company, OUTPUT_DIR, timeout=20000)
            else:
                logger.error(f"    Error al procesar {company} ({url}), agregando a sitios bloqueados")
                blocked_sites.add(url)
                return None
                
        except Exception as e:
            logger.error(f"Error descargando {company}: {e}")
            blocked_sites.add(url)
            return None
        
        # Pequeña pausa para evitar sobrecargar el servidor
        await asyncio.sleep(2)
    else:
        logger.info(f"[{idx+1}/{total}] {company}: HTMLs ya descargados, extrayendo datos...")

    logger.info(f"--- Extrayendo y analizando para {company} ---")
    
    try:
        all_html_text = merge_htmls_for_company(company, HTML_DIR)
        if not all_html_text:
            logger.warning(f"No se encontró contenido HTML para {company}")
            return None
            
        visible_text = extract_visible_text(all_html_text, max_length=14000)
        prompt = build_prompt(visible_text)
        response = call_gemini(prompt, cache=gpt_cache)
        data = parse_response_to_dict(response)

        result = {
            'company_name': company,
            'website': url,
            'hq_city': data.get('hq_city', 'No Information'),
            'hq_state': data.get('hq_state', 'No Information'),
            'company_description': data.get('company_description', 'No Information'),
            'sector': data.get('sector', 'No Information'),
            'rol_empresa': data.get('rol_empresa', 'No Information'),
            'presence_in_latam': data.get('presence_in_latam', 'No Information'),
            'contact_phone': data.get('contact_phone', 'No Information'),
            'productos_comercializan': data.get('productos_comercializan', 'No Information')
        }

        logger.info(f"-> Procesado exitosamente {company}")
        return result, url
        
    except Exception as e:
        logger.error(f"Error procesando {company}: {e}")
        return None


# ========== FLUJO PRINCIPAL MEJORADO ==========

async def main():
    """Flujo principal con procesamiento en paralelo mejorado"""
    start_time = datetime.now()
    logger.info("Iniciando procesamiento de empresas")
    
    # Cargar datos y caches
    processed = load_checkpoint()
    blocked_sites = load_blocked_sites()
    gpt_cache = load_gpt_cache()

    df = pd.read_excel(INPUT_CSV)
    total = len(df)
    header_written = os.path.exists(OUTPUT_FILE)
    
    # Revisar sitios bloqueados
    if blocked_sites:
        logger.info("\n" + "="*50)
        review_blocked_sites(blocked_sites, df)
        logger.info("="*50 + "\n")
        
        # Opcional: Si hay muchos sitios bloqueados, considera limpiar la lista
        if len(blocked_sites) > 50:
            logger.warning(f"ATENCIÓN: Hay {len(blocked_sites)} sitios bloqueados.")
            logger.warning("Si quieres reintentar sitios bloqueados, puedes limpiar el archivo:")
            logger.warning(f"rm {BLOCKED_SITES_FILE}")
    
    # Filtrar empresas que necesitan procesamiento
    companies_to_process = []
    companies_with_html = 0
    companies_already_processed = 0
    companies_blocked = 0
    
    for idx, row in df.iterrows():
        url = str(row.get("Website", "")).strip()
        company_name = row.get('Company Name', f"empresa_{idx}")
        
        if not url:
            continue
            
        normalized_url = normalize_url(url)
        
        # Verificar si está bloqueado
        if normalized_url in blocked_sites:
            companies_blocked += 1
            continue
        
        # Verificar si tiene archivos HTML descargados
        prefix = safe_filename(company_name)
        has_html_files = any(fname.startswith(prefix) and fname.endswith(".html") for fname in os.listdir(HTML_DIR))
        
        if has_html_files:
            companies_with_html += 1
            # Si ya tiene HTMLs Y está en processed, no procesar
            if normalized_url in processed:
                companies_already_processed += 1
                continue
        
        # Procesar si:
        # 1. No tiene HTMLs descargados, O
        # 2. Tiene HTMLs pero no está en processed (para extraer datos con GPT)
        companies_to_process.append((idx, row))
    
    logger.info(f"Total empresas: {total}")
    logger.info(f"Empresas con HTMLs existentes: {companies_with_html}")
    logger.info(f"Empresas completamente procesadas: {companies_already_processed}")
    logger.info(f"Empresas bloqueadas: {companies_blocked}")
    logger.info(f"Empresas por procesar: {len(companies_to_process)}")
    
    if not companies_to_process:
        logger.info("No hay empresas nuevas para procesar")
        return
    
    # Procesar en lotes para control de concurrencia
    batch_size = MAX_CONCURRENT_COMPANIES
    successful_count = 0
    failed_count = 0
    
    for i in range(0, len(companies_to_process), batch_size):
        batch = companies_to_process[i:i+batch_size]
        logger.info(f"Procesando lote {i//batch_size + 1} de {(len(companies_to_process)-1)//batch_size + 1}")
        
        # Crear tareas asíncronas para el lote
        tasks = []
        for idx, row in batch:
            task = process_single_company(idx, row, total, blocked_sites, gpt_cache)
            tasks.append(task)
        
        # Ejecutar tareas en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error en tarea: {result}")
                failed_count += 1
                continue
                
            if result is None:
                failed_count += 1
                continue
                
            try:
                result_data, url = result
                processed.add(url)
                
                # Guardar resultado
                out_df = pd.DataFrame([result_data])
                out_df.to_csv(OUTPUT_FILE, mode='a', index=False, header=not header_written)
                header_written = True
                successful_count += 1
                
            except Exception as e:
                logger.error(f"Error guardando resultado: {e}")
                failed_count += 1
        
        # Guardar progreso después de cada lote
        save_checkpoint(processed)
        save_blocked_sites(blocked_sites)
        save_gpt_cache(gpt_cache)
        
        # Pausa entre lotes para respetar rate limits
        if i + batch_size < len(companies_to_process):
            await asyncio.sleep(2)
    
    # Estadísticas finales
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 50)
    logger.info("ESTADÍSTICAS FINALES")
    logger.info(f"Tiempo total: {duration}")
    logger.info(f"Empresas procesadas exitosamente: {successful_count}")
    logger.info(f"Empresas fallidas: {failed_count}")
    logger.info(f"Sitios bloqueados total: {len(blocked_sites)}")
    logger.info(f"Entradas en caché GPT: {len(gpt_cache)}")
    logger.info("¡Extracción finalizada!")

if __name__ == "__main__":
    import sys
    
    # Agregar opción para limpiar sitios bloqueados
    if len(sys.argv) > 1 and sys.argv[1] == "--clear-blocked":
        logger.info("Limpiando archivo de sitios bloqueados...")
        clear_blocked_sites_file()
        logger.info("Reinicia el script sin --clear-blocked para procesar empresas")
        sys.exit(0)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--show-blocked":
        logger.info("Mostrando sitios bloqueados...")
        df = pd.read_excel(INPUT_CSV)
        blocked_sites = load_blocked_sites()
        review_blocked_sites(blocked_sites, df)
        sys.exit(0)
    
    # Ejecutar el flujo principal asíncrono
    asyncio.run(main())