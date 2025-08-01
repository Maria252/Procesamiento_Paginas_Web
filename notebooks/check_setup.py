#!/usr/bin/env python3
"""
Script de verificación del entorno para el workshop de extracción de empresas.
Ejecuta este script para verificar que todas las dependencias estén instaladas correctamente.
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Verificar si un paquete está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print(f"   ✅ {package_name} - OK")
            return True
        else:
            print(f"   ❌ {package_name} - No encontrado")
            return False
    except ImportError:
        print(f"   ❌ {package_name} - Error de importación")
        return False

def check_playwright_browsers():
    """Verificar si los navegadores de Playwright están instalados"""
    print("🌐 Verificando navegadores de Playwright...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if "is already installed" in result.stdout or result.returncode == 0:
            print("   ✅ Chromium - OK")
            return True
        else:
            print("   ❌ Chromium - No instalado")
            print("   💡 Ejecuta: python -m playwright install chromium")
            return False
    except Exception as e:
        print(f"   ❌ Error verificando Playwright: {e}")
        return False

def check_data_files():
    """Verificar que los archivos de datos existan"""
    print("📁 Verificando archivos de datos...")
    import os
    
    # Obtener rutas dinámicamente
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    files_to_check = [
        (os.path.join(project_root, "data", "companies_demo.xlsx"), "Archivo de empresas demo"),
        (os.path.join(project_root, "data", "htmls"), "Directorio de HTMLs"),
        (os.path.join(project_root, "data", "processed"), "Directorio de resultados")
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {description} - OK")
        else:
            print(f"   ❌ {description} - No encontrado: {file_path}")
            # Intentar crear directorios si no existen
            if "Directorio" in description:
                try:
                    os.makedirs(file_path, exist_ok=True)
                    print(f"   ✅ {description} - Creado automáticamente")
                except Exception as e:
                    print(f"   ❌ Error creando directorio: {e}")
                    all_good = False
            else:
                all_good = False
    
    return all_good

def main():
    """Función principal de verificación"""
    print("🔍 Verificando configuración del entorno...")
    print("=" * 50)
    
    checks = []
    
    # Verificar Python
    checks.append(check_python_version())
    
    # Verificar paquetes principales
    print("\n📦 Verificando paquetes de Python...")
    required_packages = [
        ("pandas", "pandas"),
        ("beautifulsoup4", "bs4"),
        ("playwright", "playwright"),
        ("aiohttp", "aiohttp"),
        ("google-generativeai", "google.generativeai"),
        ("openpyxl", "openpyxl"),
        ("matplotlib", "matplotlib"),
        ("jupyter", "jupyter")
    ]
    
    for package_name, import_name in required_packages:
        checks.append(check_package(package_name, import_name))
    
    # Verificar navegadores
    checks.append(check_playwright_browsers())
    
    # Verificar archivos de datos
    checks.append(check_data_files())
    
    # Resumen final
    print("\n" + "=" * 50)
    if all(checks):
        print("🎉 ¡Todo listo! El entorno está configurado correctamente.")
        print("\n📝 Próximos pasos:")
        print("   1. Obtén tu API key de Google Gemini: https://makersuite.google.com/app/apikey")
        print("   2. Configura la variable de entorno: export GEMINI_API_KEY='tu-api-key'")
        print("   3. Ejecuta el script: python 0_html_processing.py")
    else:
        print("❌ Hay problemas con la configuración.")
        print("\n🔧 Para solucionarlos:")
        print("   1. Instala las dependencias: pip install -r ../binder/requirements.txt")
        print("   2. Instala navegadores: python -m playwright install chromium")
        print("   3. Los directorios de datos se crean automáticamente")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
