# Cabutos Backend
Web Site administrador Cabuto Market

## Sobre el proyecto
Rest Api Cabuto es un proyecto que se encarga de la administración, funcionalidad, seguridad y optimización de recursos de la empresa Minimarket Cabutos.

## Tecnologías

El proyecto esta desarrollador totalmente en Django framework de Python. Conecta a una base de datos relacional en MySQL.

Se encuentra desplegado en [PythonAnywhere](https://www.pythonanywhere.com/)

Repositorio en [GitHub](https://github.com/CabutoMarket/CabutoBack)

## Instalación

Clonar el proyecto

```bash
git clone https://github.com/CabutoMarket/CabutoBack.git
```

Crear un entorno virtual para que las dependencias instaladas y sus versiones se manejen dentro del contexto del proyecto y no de forma global.

> IMPORTANTE: Usar una versión adecuada de Python, se ha realizado con Python 3.8.x
```bash
python -m venv myvenv
```

Activar entorno virtual

```bash
myenv\Scripts\activate
```

El proyecto cuenta con un archivo requirements.txt donde se encuentran listadas todas las dependencias que requiere el proyecto para su correcta ejecución.

```bash
pip install -r requirements.txt
```

> NOTA: Si se instalan nuevas depedencias actualizar 'requirements.txt'

Para actualizar requirements.txt se debe ejecutar:

```bash
pip freeze > requirements.txt
```
Una vez instaladas todas las dependencias procedemos a cambiar la conexión a la base de datos por nuestra versión en local.
Para ello nos dirigimos a la ruta `./cabuto/settings.py`. Aquí buscaremos el siguiente bloque codigo:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'CabutoShop$marketdb',
        'USER': 'CabutoShop',
        'PASSWORD': 'market2020',
        'HOST': 'CabutoShop.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'traditional',
        }

    }
}
```

y lo reemplazamos por la conexión a nuestra base de datos en local, por ejemplo con postgresql:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'CabutoShop',
        'USER': 'postgres',
        'PASSWORD': '124356*/',
        'HOST': '127.0.0.1',
        'PORT': 5432,
    }
}
```