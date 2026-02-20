# MiniProyecto1-Backend

# Descripción

Backend desarrollado con Django y Django Rest Framework para la gestión de actividades académicas.

Se implementó la configuración base del proyecto, conexión a base de datos PostgreSQL (Supabase), modelo principal y endpoints iniciales.

# Tecnologías utilizadas

- Python

- Django

- Django Rest Framework

- PostgreSQL (Supabase)

- SQLite (entorno de testing)

- dj-database-url

- python-dotenv

# Configuración del entorno
1. Clonar el repositorio
git clone <url-del-repositorio>
cd MP1-B
2. Crear entorno virtual
python -m venv .venv
3. Activar entorno virtual (Windows)
.venv\Scripts\activate
4. Instalar dependencias
pip install -r requirements.txt

# Variables de entorno
Crear un archivo .env en la raíz del proyecto con el siguiente contenido:

  DATABASE_URL=<cadena_de_conexion_supabase>
  DJANGO_SECRET_KEY=<clave_secreta>
  DJANGO_DEBUG=True

  # Aplicar migraciones
  
- python manage.py migrate
  
- Ejecutar el servidor
  
- python manage.py runserver

**El servidor estará disponible en:** http://127.0.0.1:8000/

# Ejecutar pruebas
python manage.py test


# Estado actual

- Configuración base del proyecto
- Conexión a Supabase
- Modelo Activity
- Endpoint de creación de actividades
- Endpoint de verificación (health)
- Pruebas automatizadas
