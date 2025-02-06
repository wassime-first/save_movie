from bs4 import BeautifulSoup
import requests
import pandas as pd
from websocket import isEnabledForDebug


def response(page):
    url = f"https://fr.youporn.com/pornstars/?page={page}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.text
    return data


def search_ps(search):
    p_list = []

    for page in range(1, 101):
        site = response(page)
        soup = BeautifulSoup(site, "lxml")
        shit_list = []
        for i in soup.select('.recommended-pornstar-list .porn-star-list a  .image-wrapper img'):
            name = i.get('alt')
            link = i.get("data-src")
            data = (name, link)
            shit_list.append(data)
        for i in soup.select(".porn-star-list a  .image-wrapper img"):

            name = i.get('alt')
            link = i.get("data-src")
            data = (name, link)
            split_name = name.lower().split()
            split_name_alpha = []
            for n in split_name:
                split_name_alpha.append(list(n))
            split_search = search.lower().split()
            split_search_alpha = []
            for n in split_search:
                split_search_alpha.append(list(n))
            test = False
            for a in split_name_alpha:
                for b in split_search_alpha:
                    if b[0] == a[0]:
                        test = True

            if (search.lower() not in split_name) and test == False:
                pass
            elif data in shit_list:
                pass
            else:
                p_list.append(data)
    return p_list


def all_p():
    p_list = []
    for page in range(1, 101):
        site = response(page)
        soup = BeautifulSoup(site, "html5lib")
        shit_list = []
        for i in soup.select('.recommended-pornstar-list .porn-star-list a  .image-wrapper img'):
            name = i.get('alt')
            link = i.get("data-src")
            data = (name, link, str(page))
            shit_list.append(data)
        for i in soup.select(".porn-star-list a  .image-wrapper img"):

            name = i.get('alt')
            link = i.get("data-src")
            data = (name, link, str(page))

            if data in shit_list:
                pass
            else:
                p_list.append(data)
    return p_list


def search_offline(data, search, page):
    p_list = []
    full_world_list = []
    one_character_list = []
    p = 1
    c = 1
    for i in data:
        name = i[0]
        split_name = name.lower().split()
        split_name_alpha = []
        for n in split_name:
            split_name_alpha.append(list(n))
        split_search = search.lower().split()
        split_search_alpha = []
        for n in split_search:
            split_search_alpha.append(list(n))
        test = False
        for a in split_name_alpha:
            for b in split_search_alpha:
                if b[0] == a[0]:
                    test = True

        if (search.lower()  in split_name):
            name = i[0]
            url = i[1]
            full_world_list.append((name, url))
        elif test and  (search.lower() not in split_name):
            name = i[0]
            url = i[1]
            one_character_list.append((name, url, p))
        else:
            pass
        for i in full_world_list:
            p_list.append(i)
        for i in one_character_list:
            p_list.append(one_character_list)
    requested_data = []
    p = 1
    c = 1
    for i in p_list:
        name = i[0]
        url = i[1]
        p = p
        if c == 10:
            p += 1
            c = 1
        else:
            c += 1
        requested_data.append((name,url,p))
    r = []
    for i in  requested_data:
        if i[2] == page:
            r.append(i)

    return r


# with open("porn_stars.csv", mode="r") as data:
#     df = pd.DataFrame(data)
#     df.to_json("porn_star.json", index=False)


def all_porn_stars(page=None):
    df = pd.read_csv("porn_stars.csv")
    names = []
    urls = []
    pages = []
    for i in range(len(df["name"])) :
        names.append(df["name"][i])
        urls.append(df["url"][i])
        pages.append((df["page"][i]))

    final_data = []
    for i in range(len(df)):
        final_data.append((names[i],urls[i],pages[i]))
    if page:
        p = page
        requested_data = []
        for i in final_data:
            if i[2] == p:
                requested_data.append(i)
        return requested_data
    else:
        return final_data



# print(all_porn_stars())
