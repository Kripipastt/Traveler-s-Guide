import requests
import sqlite3


def get_info(info):
    edited_info = []
    for parameter in ("name", "address", "url", "Phones", "Hours"):
        if parameter in info.keys():
            if parameter == "Phones":
                edited_info.append(info[parameter][0]["formatted"])
            elif parameter == "Hours":
                edited_info.append(info[parameter]["text"])
            else:
                edited_info.append(info[parameter])
        else:
            edited_info.append("Не указано")
    return edited_info


def search(coords, type, results):
    new_coords = []
    info = []
    search_api_sercer = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": "281788be-187b-428c-bb91-52c7c96a2979",
        "format": "json",
        "lang": "ru_RU",
        "ll": coords,
        "type": "biz",
        "text": type,
        "results": results
    }
    get_req = requests.get(search_api_sercer, params=search_params).json()
    orgs = get_req["features"]
    for org in orgs:
        info.append(get_info(org["properties"]["CompanyMetaData"]))
        new_coords.append(",".join(map(str, org["geometry"]["coordinates"])))
    return new_coords, info


def geocode(toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        return None
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    return toponym


def get_coords(adress):
    toponym = geocode(adress)
    coords = ",".join(toponym["Point"]["pos"].split())
    return coords


def map_show(coords, ll, z):
    points = []
    for i in range(len(coords)):
        points.append(f"{coords[i]},pm2rdm{i + 1}")
    map_params = {
        "pt": "~".join(points),
        "l": "map",
        "ll": ll,
        "z": z
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    map_file = "image/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)


def fill_database(info: list):
    con = sqlite3.connect("database/places_db.db")
    cur = con.cursor()
    cur.execute("DELETE from places")
    for i in range(len(info)):
        if i < 14:
            info[i].append("1")
        elif 14 <= i < 21:
            info[i].append("2")
        else:
            info[i].append("3")
        cur.execute(f'''INSERT INTO places VALUES ({i + 1}, "{info[i][0]}", "{info[i][1]}", "{info[i][2]}", "{info[i][3]}", "{info[i][4]}", {info[i][5]})''')
    con.commit()
    con.close()


def main():
    coords, info = search(get_coords("Рязань"), "музей", 14) # 14
    theaters = search(get_coords("Рязань"), "театр", 7) # 7
    for i in range(len(theaters[0])):
        coords.append(theaters[0][i]), info.append(theaters[1][i])
    monuments = search(get_coords("Рязань"), "памятник", 7) # 7
    for i in range(len(monuments[0])):
        coords.append(monuments[0][i]), info.append(monuments[1][i])
    map_show(coords, "39.741914,54.629565", 13)
    fill_database(info)
    for i in info:
        print(i)


if __name__ == '__main__':
    main()
