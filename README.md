# Scrapper de Strava.com

## Enunciado

1. El programa en python recibirá una lista de ids de usuarios, debe acceder a cada perfil
del usuario y devolver: Nombre, ubicación, descripción y url de la imagen del usuario.
2. Implementar una función que dado un nombre, extraiga una lista de usuarios con ese
nombre y sus IDs.
3. El proyecto se debe ejecutar a través de un Dockerfile y tener control de versiones,
preferiblemente que nos llegue en un link de github o similar.

Para los puntos 1 y 2 es necesario loguearse en strava.com, idealmente mediante cookies.

Puntos extra:
- Búsquedas paginadas para la parte 2.
- Orientación a objetos.
- Documentación.
- Buenas prácticas.
- Exportar los resultados en un json.

## Requerimientos del proyecto
- Antes de montar la imagen, el proyecto requiere de la cookie de inicio de sesión de Strava.
El proyecto lee la cookie de sesión de la variable de entorno `STRAVA_COOKIE_SESSION`.

- El programa lee las variables de entorno del fichero `.env`, el cual tiene que ir en la carpeta `app`

## Ejecución del proyecto

Para iniciar el proyecto, se requiere tener instalado Docker. En Windows, hay que tener Docker Desktop iniciado.

Para construir la imagen, se debe de ejecutar el siguiente comando:
```
docker build -t strava-scraper . 
```
Para ejecutar el programa, se debe de ejecutar el siguiente comando:
```
docker run --name strava-scraper strava-scraper
```
Al finalizar la ejecución, mostrará por consola el resultado.
También guardará en el contenedor los resultados en la carpeta `ouput`.

Se pueden recuperar los datos generados con el comando:
```
docker cp strava-scraper:/app/output .
```

## Documentación técnica
Para resolver los ejercicios de Web Scraping, he utilizado las librerías **requests** (para la petición de los datos por ID), **BeautifulSoup4** (para el parseo del string HTML a un objeto Soap, el cual nos permite buscar los datos por etiquetas) y **Playwright** (para peticiones que requieren la ejecución de JavaScript).

He decidido utilizar Playwright debido a que tiene menor consumo de recursos que otras librerías, como Selenium.

Las librerías requeridas se encuentran dentro del fichero `requirements.txt`.