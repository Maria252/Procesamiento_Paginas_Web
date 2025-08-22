# 🏢 Extractor Automático de Información de Empresas

[![Abrir en Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Maria252/Procesamiento_Paginas_Web/HEAD)

## 🤔 ¿Qué hace este programa?

Imagina que tienes una lista de 100 empresas y necesitas conocer información específica de cada una (ciudad donde están ubicadas, en qué sector trabajan, si tienen presencia en Latinoamérica, etc.). 

**En lugar de visitar manualmente cada página web y tomar notas**, este programa automatiza todo el proceso:

1. **📋 Toma una lista** de empresas con sus páginas web (desde un archivo Excel)
2. **🌐 Visita automáticamente** cada página web
3. **🤖 Lee y entiende** el contenido usando Inteligencia Artificial
4. **📊 Extrae la información** que necesitas de forma organizada
5. **💾 Guarda todo** en un archivo que puedes abrir con Excel

## 🎯 ¿Para qué sirve?

### ✅ Perfecto para:
- **Investigación de mercado**: Conocer empresas competidoras
- **Análisis sectorial**: Entender qué hacen las empresas de un sector
- **Prospección comercial**: Obtener datos de contacto y ubicación
- **Estudios académicos**: Recopilar información empresarial para investigaciones
- **Due diligence**: Verificar información de empresas antes de hacer negocios

### ❌ NO es recomendable para:
- Obtener información confidencial o privada
- Hacer muchas consultas simultáneas (puede saturar los servidores)
- Usar sin permiso en sitios web que lo prohíban

## 🚀 ¿Cómo usarlo? (Sin instalar nada)

### Opción 1: Usar en la nube (RECOMENDADO) 🌟

**No necesitas instalar nada en tu computadora!**

1. **Haz clic en el botón "launch binder"** ⬆️ (arriba)
2. **Espera 3-5 minutos** mientras se prepara el entorno virtual
3. **Cuando esté listo**, verás una pantalla como Jupyter
4. **Abre la carpeta "notebooks"**
5. **Ejecuta el archivo principal** `0_html_processing.py`

### Opción 2: Si eres técnico y quieres instalarlo localmente

```bash
# Descargar el código
git clone https://github.com/Maria252/Procesamiento_Paginas_Web.git
cd Procesamiento_Paginas_Web

# Instalar todo lo necesario
pip install -r binder/requirements.txt
python -m playwright install chromium

# Ejecutar
cd notebooks
python 0_html_processing.py
```

## 📁 ¿Qué archivos incluye?

```
📂 Tu proyecto
├── 📂 data/                          # Aquí van los datos
│   ├── 📄 companies_demo.xlsx        # Lista de empresas de ejemplo
│   ├── 📂 htmls/                     # Páginas web descargadas
│   └── 📂 processed/                 # Resultados finales
├── 📂 notebooks/                     # El programa principal
│   └── 📄 0_html_processing.py       # Archivo que hace toda la magia
└── 📄 README.md                      # Este archivo que estás leyendo
```

## 📊 ¿Qué información extrae?

El programa busca y organiza esta información de cada empresa:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **🏙️ Ciudad sede** | Dónde está ubicada la empresa | "Bogotá" |
| **🌎 Estado/Región** | Región o departamento | "Cundinamarca" |
| **📝 Descripción** | Qué hace la empresa (máximo 60 palabras) | "Empresa líder en servicios financieros..." |
| **🏭 Sector** | A qué industria pertenece | "Servicios Financieros" |
| **🌎 Presencia LATAM** | Si opera en otros países de Latinoamérica | "Sí - Colombia, Perú, México" |
| **♻️ Sostenibilidad** | Si publica reportes ambientales | "Sí - Reporte anual 2024" |
| **📞 Teléfonos** | Números de contacto | ["+57 1 234 5678"] |

## 🛠️ ¿Qué necesitas para empezar?

### Requisitos básicos:
1. **📱 Conexión a internet** (para descargar las páginas web)
2. **🔑 API Key de Google AI** (es gratis - te explico cómo conseguirla abajo)
3. **📄 Lista de empresas** en formato Excel con estas columnas:
   - `Company Name` (Nombre de la empresa)
   - `Website` (Página web)

### 🔑 Cómo conseguir tu API Key de Google AI (GRATIS):

1. **Ve a** https://makersuite.google.com/app/apikey
2. **Inicia sesión** con tu cuenta de Google
3. **Haz clic en "Create API Key"**
4. **Copia la clave** que te aparece
5. **Pégala cuando el programa te la pida**

⚠️ **IMPORTANTE**: La API Key es como una contraseña, no la compartas con nadie.

## 📋 Ejemplo de archivo de entrada

Tu archivo Excel debe verse así:

| Company Name | Website |
|--------------|---------|
| ProColombia | https://procolombia.co |
| Bancolombia | https://www.bancolombia.com |
| Avianca | https://www.avianca.com |
| Ecopetrol | https://www.ecopetrol.com.co |

## 🎯 ¿Cómo funciona internamente? (Explicación simple)

### Paso 1: Preparación 📋
- Lee tu archivo Excel con la lista de empresas
- Verifica que las páginas web sean accesibles

### Paso 2: Navegación web 🌐
- Abre cada página web como si fuera una persona con un navegador
- Espera a que cargue completamente (incluso contenido dinámico)
- Busca secciones importantes: "Acerca de", "Contacto", "Servicios", etc.

### Paso 3: Análisis inteligente 🤖
- Envía el contenido de la página a Google AI (Gemini)
- La IA "lee" y "entiende" el texto como lo haría una persona
- Extrae la información específica que necesitas

### Paso 4: Organización 📊
- Guarda toda la información en un formato ordenado
- Crea un archivo CSV que puedes abrir con Excel
- Mantiene un registro de qué empresas ya procesó (para no repetir trabajo)

## ⚡ Configuración y rendimiento

### ⏱️ ¿Cuánto tiempo toma?
- **Por empresa**: 30-60 segundos
- **50 empresas**: 30-50 minutos aproximadamente
- **Depende de**: velocidad de internet, complejidad de las páginas web

### 🔧 Configuraciones que puedes cambiar:
```python
MAX_CONCURRENT_COMPANIES = 5    # Cuántas empresas procesar al mismo tiempo
GPT_RATE_LIMIT_DELAY = 1.0      # Pausa entre consultas a la IA (en segundos)
URL_VALIDATION_TIMEOUT = 10     # Tiempo máximo para verificar si una página funciona
```

## 🚨 Problemas comunes y soluciones

### "No encuentro mi API Key" 🔑
- **Solución**: Ve a https://makersuite.google.com/app/apikey y créala de nuevo
- Asegúrate de copiar todo el texto sin espacios extra

### "El programa se detiene con errores" ⚠️
- **Solución**: Es normal que algunos sitios web no funcionen
- El programa automáticamente salta esos sitios y continúa con los demás
- Revisa el archivo de log para ver qué pasó

### "Los resultados no están completos" 📊
- **Solución**: Algunas empresas no publican toda su información en la web
- El programa marca "No Information" cuando no encuentra datos
- Es normal y no es un error

### "Va muy lento" 🐌
- **Solución**: Es normal, el programa es cuidadoso para no saturar las páginas web
- **NO cambies** las configuraciones de tiempo para ir más rápido (puede causar bloqueos)

## 📈 ¿Qué hacer con los resultados?

Una vez que termine, tendrás un archivo CSV con toda la información. Puedes:

1. **📊 Abrirlo en Excel** para analizarlo
2. **📈 Crear gráficos** para visualizar patrones
3. **🔍 Filtrar empresas** por sector, ubicación, etc.
4. **📧 Usar los datos de contacto** para outreach comercial
5. **📋 Crear reportes** para presentaciones

## ⚖️ Consideraciones éticas y legales

### ✅ Uso responsable:
- **Respeta** los términos de servicio de las páginas web
- **No hagas** muchas consultas seguidas al mismo sitio
- **Usa** la información de forma ética y legal
- **Verifica** la información importante manualmente

### ❌ NO hagas:
- Extraer información personal o confidencial
- Usar los datos para spam o actividades ilegales
- Ignorar las políticas de robots.txt de los sitios web
- Hacer muchas consultas simultáneas (puede parecer un ataque)

## 🆘 ¿Necesitas ayuda?

### Si algo no funciona:
1. **📋 Revisa** que tu archivo Excel tenga las columnas correctas
2. **🔑 Verifica** que tu API Key sea válida
3. **🌐 Confirma** que tengas internet estable
4. **📝 Revisa** los mensajes que aparecen en pantalla

### Archivos de log:
El programa guarda registros detallados en:
- `data/htmls/processing.log` - Registro completo de lo que hace
- `data/htmls/blocked_sites.json` - Sitios que no pudieron procesarse

## 🎓 ¿Quieres aprender más?

Este proyecto combina varias tecnologías modernas:
- **Web Scraping**: Extraer información de páginas web
- **Inteligencia Artificial**: Google Gemini para análisis de texto
- **Automatización**: Python para orquestar todo el proceso
- **Análisis de datos**: Pandas para organizar la información

## � Contacto y soporte

- **📧 Problemas técnicos**: Revisa la sección de troubleshooting arriba
- **💡 Sugerencias**: Abre un "Issue" en GitHub
- **🤝 Colaborar**: Haz un "Pull Request" con mejoras

---

## 🎉 ¡Listo para empezar!

**Recuerda**: Este es un programa poderoso pero requiere paciencia. La automatización inteligente toma tiempo, pero te ahorrará horas de trabajo manual.

**🚀 Haz clic en "launch binder" arriba para comenzar tu primera extracción automatizada de datos empresariales!**
---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - Puedes usarlo libremente para fines educativos y comerciales.

## �‍💻 Creado por

Desarrollado para el Workshop de IA Empresarial - ProColombia 2025

**🔥 ¡Automatiza tu investigación empresarial y ahorra tiempo valioso!**
