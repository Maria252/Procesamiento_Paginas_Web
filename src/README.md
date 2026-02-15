# 🏢 Workshop: Extracción Automatizada de Información de Empresas

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/tu-usuario/repo-name/HEAD?labpath=notebooks%2Fcaptacion_info_empresas.ipynb)

## 📋 Descripción

Este repositorio contiene un taller interactivo para construir un sistema automatizado de extracción de información empresarial que combina web scraping avanzado con análisis de IA.

### 🎯 Objetivos del Taller

- Aprender web scraping moderno con **Playwright**
- Integrar **Google Gemini** para análisis de contenido con IA
- Implementar **procesamiento secuencial** para mayor estabilidad
- Gestionar errores y optimizar performance
- Exportar datos estructurados para análisis

## 🚀 Inicio Rápido

### Opción 1: MyBinder (Recomendado para el taller)

1. Haz clic en el botón **"launch binder"** arriba
2. Espera a que se construya el entorno (puede tomar 2-3 minutos)
3. Abre el notebook `notebooks/captacion_info_empresas.ipynb`
4. Sigue las instrucciones paso a paso

### Opción 2: Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/repo-name.git
cd repo-name

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r binder/requirements.txt

# Instalar navegadores de Playwright
python -m playwright install chromium

# Ejecutar Jupyter
jupyter lab notebooks/captacion_info_empresas.ipynb
```

## 📁 Estructura del Proyecto

```
├── binder/
│   ├── requirements.txt    # Dependencias Python
│   ├── runtime.txt        # Versión de Python
│   └── postBuild          # Script post-instalación
├── notebooks/
│   └── captacion_info_empresas.ipynb  # Notebook principal del taller
├── data/
│   ├── companies_demo.csv             # Datos de ejemplo
│   ├── htmls/                         # HTMLs descargados
│   └── processed/                     # Resultados procesados
├── README.md
└── 0_html_processing.py               # Código original de referencia
```

## 🛠️ Requisitos

### Dependencias Principales
- **Python 3.10+**
- **Google AI API Key** (obtener en https://makersuite.google.com/app/apikey)
- **Playwright** para web scraping
- **Pandas** para manipulación de datos
- **BeautifulSoup** para parsing HTML

### API Key de Google AI
```python
# Durante el taller, se te pedirá ingresar tu API key
# Alternativamente, puedes configurar la variable de entorno:
export GOOGLE_AI_API_KEY="tu-api-key-aqui"
```

## 📊 Datos de Entrada

El sistema procesa un archivo Excel con las siguientes columnas:
- `Company Name`: Nombre de la empresa
- `Website`: URL del sitio web

### Ejemplo de datos:
```
Company Name         | Website
ProColombia         | https://procolombia.co
Bancolombia         | https://www.bancolombia.com
Avianca             | https://www.avianca.com
```

## 📈 Datos de Salida

El sistema extrae la siguiente información de cada empresa:
- **hq_city**: Ciudad de la sede
- **hq_state**: Estado/provincia de la sede
- **company_description**: Descripción breve de la empresa
- **sector**: Sector industrial
- **presence_in_latam**: Presencia en Latinoamérica
- **sustainability_reports**: Reportes de sostenibilidad
- **contact_phone**: Teléfonos de contacto

## 🎭 Características Técnicas

### Web Scraping Avanzado
- **Renderizado JavaScript** con Playwright
- **Manejo de contenido dinámico** y lazy loading
- **Extracción inteligente** de enlaces relevantes
- **Gestión de errores** y reintentos automáticos

### Análisis con IA
- **Prompts optimizados** para extracción de datos empresariales con Google Gemini
- **Caché inteligente** para evitar llamadas repetidas a la API
- **Normalización automática** de respuestas
- **Rate limiting** para cumplir con límites de API

### Optimización de Performance
- **Procesamiento secuencial** para mayor estabilidad
- **Sistema de checkpoints** para recuperación de errores
- **Validación de URLs** antes del procesamiento
- **Gestión de sitios bloqueados**

## 📝 Flujo de Trabajo

1. **Configuración**: Instalación de dependencias y configuración de API
2. **Carga de datos**: Lectura del archivo Excel con empresas
3. **Validación**: Verificación de accesibilidad de sitios web
4. **Scraping**: Descarga de HTML con renderizado JavaScript
5. **Análisis**: Extracción de información con Google Gemini
6. **Exportación**: Guardado de resultados en CSV
7. **Visualización**: Análisis y gráficos de los datos obtenidos

## ⚡ Performance y Escalabilidad

### Configuraciones Recomendadas
- **Procesamiento**: Secuencial (una empresa a la vez)
- **Timeout de URLs**: 15 segundos
- **Rate limit Gemini**: 2 segundos entre llamadas
- **Secciones por empresa**: Máximo 3 secciones adicionales

### Optimizaciones Implementadas
- Caché de respuestas Gemini
- Reutilización de HTMLs descargados
- Validación previa de URLs
- Manejo inteligente de errores

## 🔧 Personalización

### Modificar Keywords de Búsqueda
```python
KEYWORDS = [
    'contact', 'about', 'team', 'services',
    'contacto', 'acerca', 'equipo', 'servicios'
    # Agregar más keywords según necesidades
]
```

### Ajustar Prompt de Gemini
```python
def build_prompt(text):
    return f"""
    Personaliza aquí el prompt según tus necesidades específicas...
    {text}
    """
```

## 🐛 Solución de Problemas

### Errores Comunes
1. **API Key inválida**: Verificar configuración de Google AI
2. **Timeout de navegador**: Aumentar timeout en configuración
3. **Sitios bloqueados**: Revisar user-agent y headers
4. **Memoria insuficiente**: Reducir número de secciones por empresa

### Logs y Debugging
Los logs se muestran en tiempo real durante la ejecución e incluyen:
- Estado de descarga de cada empresa
- Errores de conexión y timeout
- Estadísticas de caché y performance
- Resultados de extracción por empresa

## 📚 Recursos Adicionales

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Playwright Python](https://playwright.dev/python/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [MyBinder Documentation](https://mybinder.readthedocs.io/)

## 🤝 Contribuir

¿Mejoras o sugerencias? ¡Contribuciones bienvenidas!

1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 👨‍💻 Autor

Desarrollado para el Workshop de IA Empresarial - ProColombia 2025

---

**🎉 ¡Disfruta aprendiendo sobre extracción automatizada de datos empresariales!**
