import requests
from dotenv import load_dotenv
import os

load_dotenv()
IMG = os.getenv("IMG")
API_KEY = os.getenv("API_KEY")
API_LONG_KEY = os.getenv("API_LONG_KEY")
API_LONG_KEY_VIDEO = os.getenv("API_LONG_KEY_VIDEO")
api_key = API_KEY
api_long_key = API_LONG_KEY
IMG_LINK = os.getenv("IMG_LINK")
url = f"https://api.themoviedb.org/3/authentication"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_long_key}",
}


def search_tv(title, page):
    url_searsh = "https://api.themoviedb.org/3/search/tv"
    params = {
        "query": title,
        # "api_key": api_key,
        "language": "en-US",
        "page": page,
        "include_adult": True,
    }

    response_search = requests.get(url_searsh, headers=headers, params=params)
    data = response_search.json()
    tv_list = []
    for title in data["results"]:
        d = (f"{title['name']} -  {title['first_air_date']}", f"{IMG_LINK}{title['backdrop_path']}", title["id"])
        tv_list.append(d)
    return tv_list


def tv_data(id):
    url = f"https://api.themoviedb.org/3/tv/{id}"
    response_movie = requests.get(url, headers=headers)
    data = response_movie.json()
    title = data["original_name"]
    overview = data["overview"]
    release_date = data["last_air_date"]
    img_url = f'{IMG_LINK}{data["poster_path"]}'
    rating = data["vote_average"]
    return (title, release_date, img_url, overview, rating)

def tv_image_data(id):
    url = f"https://api.themoviedb.org/3/tv/{id}/images"
    headers = {
        "accept": "application/json",
        "Authorization": f"{API_LONG_KEY_VIDEO}",
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()
    images = []
    for i in data["backdrops"]:
        image_link = f"{IMG_LINK}{i['file_path']}"
        images.append(image_link)
    return images

def tv_video_data(id):
    url = f"https://api.themoviedb.org/3/tv/{id}/videos?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"{API_LONG_KEY_VIDEO}",
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()
    videos = []
    for i in data["results"]:
        youtube_link = f"https://www.youtube.com/embed/{i['key']}"
        videos.append(youtube_link)
    return videos

def search_movies(title, page):
    url_searsh = "https://api.themoviedb.org/3/search/movie"
    params = {
        "query": title,
        # "api_key": api_key,
        "language": "en-US",
        "page": page,
        "include_adult": True,
    }

    response_search = requests.get(url_searsh, headers=headers, params=params)
    data = response_search.json()
    movies_list = []
    for title in data["results"]:
        movies_list.append((f"{title['title']}-{title['release_date']}", f"{IMG_LINK}{title['backdrop_path']}",title["id"]))
    return (movies_list)


def movie_data(id):
    url_movie = f"https://api.themoviedb.org/3/movie/{id}"
    response_movie = requests.get(url_movie, headers=headers)
    data = response_movie.json()
    title = data["original_title"]
    release_date = data["release_date"]
    overview = data["overview"]
    img_url = f'{IMG_LINK}{data["backdrop_path"]}'
    rating = data["vote_average"]
    return (title, release_date, overview, img_url, rating)

def movie_video_data(id):
    url = f"https://api.themoviedb.org/3/movie/{id}/videos?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"{API_LONG_KEY_VIDEO}",
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()
    videos = []
    for i in data["results"]:
        youtube_link = f"https://www.youtube.com/embed/{i['key']}"
        videos.append(youtube_link)
    return videos

def movie_image_data(id):
    url = f"https://api.themoviedb.org/3/movie/{id}/images"
    headers = {
        "accept": "application/json",
        "Authorization": f"{API_LONG_KEY_VIDEO}",
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()
    images = []
    for i in data["backdrops"]:
        image_link = f"{IMG_LINK}{i['file_path']}"
        images.append(image_link)
    return images



def search_all(title, page):
    url_all = "https://api.themoviedb.org/3/search/multi"
    params = {
        "query": title,
        # "api_key": api_key,
        "language": "en-US",
        "page": page,
        "include_adult": True,
    }
    response_all = requests.get(url=url_all, headers=headers, params=params)
    data = response_all.json()
    all_results = []
    for i in data["results"]:
        try:
            add = (i["id"], i["name"], f'{IMG_LINK}{i["profile_path"]}', "pp")
            all_results.append(add)
        except IndexError:
            add = (i["id"], i["name"], f'{IMG}', "pp")
            all_results.append(add)
        except KeyError:
            try:
                add = (i["id"], i["title"], f"{IMG_LINK}{i['backdrop_path']}", i["media_type"])
                all_results.append(add)
            except KeyError:
                add = (i["id"], i["name"], f"{IMG_LINK}{i['backdrop_path']}", i["media_type"])
                all_results.append(add)
    return all_results


def search_ppl(title, page):
    url_searsh = "https://api.themoviedb.org/3/search/person"
    params = {
        "query": title,
        # "api_key": api_key,
        "language": "en-US",
        "page": page,
        "include_adult": True,
    }

    response_search = requests.get(url_searsh, headers=headers, params=params)
    data = response_search.json()
    actor_list = []
    for title in data["results"]:
        d = (f"{title['name']}", f"{IMG_LINK}{title['profile_path']}", title["id"])
        actor_list.append(d)
    return actor_list


def ppl_data(id):
    url_movie = f"https://api.themoviedb.org/3/person/{id}"
    response_movie = requests.get(url_movie, headers=headers)
    data = response_movie.json()
    name = data["name"]
    img_url = f'{IMG_LINK}{data["profile_path"]}'
    return (name, img_url)

def ppl_image_data(id):
    url_movie = f"https://api.themoviedb.org/3/person/{id}/images"
    response_movie = requests.get(url_movie, headers=headers)
    data = response_movie.json()
    images = []
    for i in data["profiles"]:
        image_link = f"{IMG_LINK}{i['file_path']}"
        images.append(image_link)
    return images

def discover_movies(page):
    url = f"https://api.themoviedb.org/3/discover/movie?include_adult=true&include_video=false&language=en-US&page={page}&sort_by=popularity.desc"
    response = requests.get(url=url, headers=headers)
    data = response.json()
    dicovery_list = []
    for i in data["results"]:
        title = i["title"]
        id = i["id"]
        rating = i["vote_average"]
        img = f'{IMG_LINK}{i["backdrop_path"]}'
        d = (title, img, id, rating, "movie")
        dicovery_list.append(d)
    return dicovery_list

def discover_tv(page):
    url = f"https://api.themoviedb.org/3/discover/tv?include_adult=true&include_video=false&language=en-US&page={page}&sort_by=popularity.desc"
    response = requests.get(url=url, headers=headers)
    data = response.json()
    dicovery_list = []
    for i in data["results"]:
        title = i["name"]
        id = i["id"]
        rating = i["vote_average"]
        img = f'{IMG_LINK}{i["backdrop_path"]}'
        d = (title, img, id, rating, "tv")
        dicovery_list.append(d)
    return dicovery_list

# print(tv_data(94605))
# print(movie_video_data(939243))
# print(movie_data("109445"))
# print(discover_movies(1))
# print(ppl_image_data(11701))