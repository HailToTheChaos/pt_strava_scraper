import json
import os
from typing import Optional
from dotenv import load_dotenv
from requests import get
from bs4 import BeautifulSoup as BS
from urllib.parse import quote
from playwright.sync_api import sync_playwright

load_dotenv()

BASE_URL = "https://www.strava.com"
COOKIE = {"_strava4_session": os.getenv("STRAVA_COOKIE_SESSION")}


def _extract_user_info(soup: BS) -> dict[Optional[str]]:
    """
    La función `_extract_user_info` extrae datos de la página del usuario.

    Los datos que obtiene son `nombre`, `localización`, `descripción` e `imagen del perfil`.

    Si no encuentra las etiquetas, devuelve los datos nulos.

    Args:
        soup (bs4.BeautifulSoup): Objeto que parsea el HTML y permite obtener los datos buscando las etiquetas.

    Returns:
        user_data (dict[Optional[str]]): Diccionario con los datos del usuario.
    """
    user_data = {}

    user_name_element = soup.find("h1", {"class": "text-title1 athlete-name"})
    user_data["name"] = user_name_element.text if user_name_element else None

    user_location_element = soup.find("div", {"class": "location"})
    user_data["location"] = (
        user_location_element.text.replace("\n", "") if user_location_element else None
    )

    user_description = soup.find("div", {"class": "description-content"})
    user_data["description"] = (
        user_description.find("p").text if user_description else None
    )

    user_image = soup.find("div", {"class": "avatar-img-wrapper"})
    user_data["profile_image"] = (
        user_image.find("img").get("src") if user_image else None
    )

    return user_data


def get_users_data_by_ids(list_ids: list[str]) -> dict[Optional[str]]:
    """
    La función `get_users_data_by_ids` busca los perfiles de los IDs que se han pasado por parámetro.

    Una vez extraidos los datos, devuelve un diccionario con los datos de los usuarios.

    Los datos que obtiene son `nombre`, `localización`, `descripción` e `imagen del perfil`.

    Args:
        list_ids (list[str]): Listado de IDs a buscar.

    Returns:
        users_data (dict[Optional[str]]): Diccionario con los datos de los usuarios.
    """
    url = f"{BASE_URL}/athletes"

    users_data = []
    for id in list_ids:
        data = {}
        response = get(f"{url}/{id}", cookies=COOKIE)

        bs_user_page = BS(response.text, features="html.parser")

        data["id"] = id
        data["data"] = _extract_user_info(bs_user_page)
        users_data.append(data)

    return users_data


def _search_ids_by_name(name: str) -> list[str]:
    """
    La función `_search_ids_by_name` obtiene todos los IDs bucando un nombre
    en el buscador de Strava.

    Una vez se obtiene el soap con los datos, se van extrayendo los IDs de las etiquetas.

    Args:
        name (str): Nombre a buscar

    Returns:
        athlete_ids ()
    """
    ENDPOINT = f"{BASE_URL}/athletes/search"
    athlete_ids = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()

        context.add_cookies(
            [
                {
                    "name": list(COOKIE.keys())[0],
                    "value": list(COOKIE.values())[0],
                    "domain": "www.strava.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                }
            ]
        )

        page = context.new_page()

        # Buscamos los resultados en todas las páginas hasta que nos salga
        # que no se han encontrado más resultados
        page_num = 1
        while True:
            user_url = f"{ENDPOINT}?query={quote(name)}&page={page_num}"
            response = page.goto(user_url)

            if not response or response.status != 200:
                break  # Error de conexión

            if page.locator("text=No se han encontrado resultados para").is_visible():
                break

            athlete_links = page.locator(
                "li.AthleteList_athleteListItem__egbVo div.Athlete_athleteInfo__rVPKN a[href^='/athletes/']"
            ).all()

            if not athlete_links:
                break

            for link in athlete_links:
                href = link.get_attribute("href")
                if href and "/athletes/" in href:
                    athlete_id = href.split("/athletes/")[-1]
                    if athlete_id not in athlete_ids:
                        athlete_ids.append(athlete_id)

            page_num += 1  # Siguiente página

        browser.close()

    return athlete_ids


def get_user_ids_by_name(list_names: list[str]) -> dict:
    """
    La Función `get_user_ids_by_name` obtiene los ids de los nombre que se pasan por parámetro.

    Es decir, al pasar un nombre se buscan los IDs de las cuentas que tienen ese nombre.

    Args:
        list_names (list[str]): listado de nombres a buscar
    """
    users_data = []
    for name in list_names:
        user_data = {}
        response = _search_ids_by_name(name)
        if not response:
            continue

        user_data["name"] = name
        user_data["IDs"] = response

        users_data.append(user_data)

    return users_data


def _save_dicto_to_json_file(file_name: str, data: dict) -> None:
    """
    La función `_save_dicto_to_json_file` guarda los resultados en un json,
    dentro de la carpeta output.

    Args:
        file_name (str): nombre del fichero donde se van a guardar los datos.
        data (dict): datos a guardar.
    """
    file_path = "output"
    os.makedirs(file_path, exist_ok=True)

    with open(f"{file_path}/{file_name}", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def main():
    list_ids = ["1854350", "113191718", "6830469"]
    list_usernames = ["Miguel Ángel Durán", "Leon Parkes"]

    print("Obteniendo datos de los usuarios...")
    dict_users_data_by_id = get_users_data_by_ids(list_ids)
    print("--> Datos Obtenidos")
    print("Obteniendo IDs por nombre de usuario...")
    dict_users_ids_by_name = get_user_ids_by_name(list_usernames)
    print("-->IDs obtenidos")

    print("Datos de usuarios:", dict_users_data_by_id)
    print("IDs de usuarios:", dict_users_ids_by_name)

    _save_dicto_to_json_file(
        file_name="user_data_by_id.json", data=dict_users_data_by_id
    )
    _save_dicto_to_json_file(
        file_name="users_ids_by_name.json", data=dict_users_ids_by_name
    )


if __name__ == "__main__":
    main()
