# Archivo de configuración para MyBinder
# Este archivo asegura que el entorno se configure correctamente

# Configurar Jupyter para mostrar archivos desde la raíz del proyecto
c.NotebookApp.notebook_dir = '.'

# Configuraciones adicionales para el entorno
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8888

# Permitir el uso de widgets y aumentar límites de datos
c.NotebookApp.iopub_data_rate_limit = 1.0e10
c.NotebookApp.iopub_msg_rate_limit = 1.0e6
