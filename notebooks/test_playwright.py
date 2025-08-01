#!/usr/bin/env python3
"""
Script de verificación específico para Playwright en MyBinder.
Ejecuta este script para verificar que Playwright esté funcionando correctamente.
"""

import sys
import subprocess
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    """Test básico de Playwright"""
    print("🌐 Probando Playwright...")
    
    try:
        async with async_playwright() as p:
            print("   ✅ Playwright importado correctamente")
            
            # Intentar lanzar navegador
            browser = await p.chromium.launch(headless=True)
            print("   ✅ Chromium lanzado exitosamente")
            
            # Crear página de prueba
            page = await browser.new_page()
            print("   ✅ Página creada exitosamente")
            
            # Navegar a una página simple
            await page.goto('https://example.com')
            print("   ✅ Navegación exitosa")
            
            # Obtener título
            title = await page.title()
            print(f"   ✅ Título obtenido: {title}")
            
            await browser.close()
            print("   ✅ Navegador cerrado correctamente")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Playwright: {e}")
        return False

def check_system_dependencies():
    """Verificar dependencias del sistema"""
    print("🔍 Verificando dependencias del sistema...")
    
    dependencies = [
        'libnspr4', 'libnss3', 'libdbus-1-3', 'libatk1.0-0',
        'libatk-bridge2.0-0', 'libatspi2.0-0', 'libxcomposite1',
        'libxdamage1', 'libxfixes3', 'libxrandr2', 'libgbm1',
        'libxkbcommon0', 'libasound2'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            result = subprocess.run(['dpkg', '-l', dep], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(dep)
        except:
            missing.append(dep)
    
    if missing:
        print(f"   ❌ Faltan dependencias: {', '.join(missing)}")
        return False
    else:
        print("   ✅ Todas las dependencias del sistema están instaladas")
        return True

async def main():
    """Función principal"""
    print("🔍 Verificación de Playwright para MyBinder")
    print("=" * 50)
    
    # Verificar dependencias del sistema
    sys_deps_ok = check_system_dependencies()
    
    # Verificar Playwright
    playwright_ok = await test_playwright()
    
    print("\n" + "=" * 50)
    if sys_deps_ok and playwright_ok:
        print("🎉 ¡Playwright está funcionando correctamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecuta: python 0_html_processing.py")
        print("   2. El script debería funcionar sin errores de navegador")
    else:
        print("❌ Hay problemas con Playwright")
        print("\n🔧 Soluciones:")
        if not sys_deps_ok:
            print("   1. Las dependencias del sistema faltan")
            print("   2. Esto debería solucionarse automáticamente en MyBinder")
            print("   3. Si persiste, reporta el problema en el repositorio")
        if not playwright_ok:
            print("   4. Hay un problema con la instalación de Playwright")
            print("   5. Intenta ejecutar: python -m playwright install chromium")
    
    return sys_deps_ok and playwright_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
