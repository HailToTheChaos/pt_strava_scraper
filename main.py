import os
from typing import Optional
from warnings import warn
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

    users_data = {}
    for id in list_ids:
        response = get(f"{url}/{id}", cookies=COOKIE)

        bs_user_page = BS(response.text, features="html.parser")

        users_data[id] = _extract_user_info(bs_user_page)

    return users_data


def _search_ids_by_name(name: str) -> Optional[BS]:
    ENDPOINT = f"{BASE_URL}/athletes/search"
    user_url = f"{ENDPOINT}?query={quote(name)}"

    athlete_ids = []
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()

        # Se configura la cookie de playwright para poder iniciar sesión
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
        response = page.goto(user_url)

        if response and response.status == 200:
            # Se obtienen todos los elementos que contienen enlaces a atletas
            athlete_links = page.locator(
                "li.AthleteList_athleteListItem__egbVo div.Athlete_athleteInfo__rVPKN a[href^='/athletes/']"
            ).all()

            # Se extraen los IDs de los hrefs
            for link in athlete_links:
                href = link.get_attribute("href")
                if href and "/athletes/" in href:
                    athlete_id = href.split("/athletes/")[-1]
                    athlete_ids.append(athlete_id)

    return athlete_ids


def get_user_ids_by_name(list_names: list[str]) -> dict:
    """
    La Función `get_user_ids_by_name` obtiene los ids de los nombre que se pasan por parámetro.

    Es decir, al pasar un nombre se buscan los IDs de las cuentas que tienen ese nombre.

    Args:
        list_names (list[str]): listado de nombres a buscar
    """
    users_data = {}
    for name in list_names:
        response = _search_ids_by_name(name)
        if not response:
            continue

        users_data[name] = response
    # for name in
    return users_data


def main():
    list_ids = ["1854350", "113191718", "6830469"]
    list_usernames = ["Miguel Ángel Durán", "Leon Parkes", "Javi Guerrero"]

    dict_users_data_by_id = get_users_data_by_ids(list_ids)
    dict_users_ids_by_name = get_user_ids_by_name(list_usernames)

    print(dict_users_data_by_id)
    print(dict_users_ids_by_name)


if __name__ == "__main__":
    main()
