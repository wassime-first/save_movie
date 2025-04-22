from dotenv import load_dotenv
import os
import requests
import re

load_dotenv()
GAME_API_KEY = os.getenv("GAME_API_KEY")

def search_games(title, page):
    url_search = "https://api.rawg.io/api/games"

    params = {
        "key": GAME_API_KEY,
        "page": page,
        "page_size": 10,
        "search": title,
    }

    response_search = requests.get(url_search, params=params)
    data = response_search.json()
    game_list = []
    for game in data["results"]:
        d = (f"{game['name']} - {game['released']}", game["background_image"], game["id"])
        game_list.append(d)
    return game_list

def game_data(id):
    url = f"https://api.rawg.io/api/games/{id}"
    params = {
        "key": GAME_API_KEY,
    }
    response_game = requests.get(url, params=params)
    data = response_game.json()
    title = data["name"]
    overview = re.sub(r'<[^>]*>', '', data["description"])
    release_date = data["released"]
    img_url = data["background_image"]
    metacritic = data["metacritic"]
    return (title, release_date, img_url, overview, metacritic)

def game_trailers(id):
    url = f"https://api.rawg.io/api/games/{id}/movies"
    params = {
        "key": GAME_API_KEY,
    }
    response_game = requests.get(url, params=params)
    data = response_game.json()
    trailers = []
    for i in data["results"]:
        d = (i["data"]["max"])
        trailers.append(d)
    return trailers

