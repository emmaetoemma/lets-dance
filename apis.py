import requests
import json
import os


def get_coordinates_by_address(address):
    """
    Используем API геокодера для определения координат по адресу.
    Возвращает координаты в формате x,y, где x и y - широта и долгота в виде
    десятичных дробей с разделением дробной части от целой при помощи точки.
    None, если адрес не найден
    """
    if address is None:
        return
    url = 'https://geocode-maps.yandex.ru/1.x'
    params = {
        'geocode': address,
        'apikey': os.environ.get('YA_GEOCODER_KEY', ''),
        'format': 'json',
        'results': 1,
        'lang': os.environ.get('YA_REGION', 'ru_RU')
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    found = res.json()['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found']
    # искомого адреса нет, предложим пользователю повторить попытку
    if int(found) == 0:
        return
    return res.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].replace(' ', ',')

def get_organizations_by_coordinates(coordinates):
    """
    Используем API поиска по организациям для поиска школ танцев.
    Возвращает список, состоящий из одного или нескольких адресов в формате {'address': <str>, 'name': <str>}.
    None, если не один адрес не найден.
    """
    if coordinates is None:
        return
    url = 'https://search-maps.yandex.ru/v1'
    params = {
        'apikey': os.environ.get('YA_SEARCH_KEY', ''),
        'text': 'школа танцев',
        'results': os.environ.get('YA_SEARCH_RESULTS_COUNT', 3),
        'lang': os.environ.get('YA_REGION', 'ru_RU'),
        'type': 'biz',
        'll': coordinates,
        'spn': os.environ.get('YA_SEARCH_RANGE', '0.015, 0.015'),
        'rspn': 0
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    found = res.json()['properties']['ResponseMetaData']['SearchResponse']['found']
    if int(found) == 0:
        return
    schools = list()
    count_to_find = 0
    for school in res.json()['features']:
        schools.append({
            'name': school['properties']['CompanyMetaData']['name'],
            'address': school['properties']['CompanyMetaData']['address'],
            })
    return schools

def get_schools_by_address(address):
    if address is None:
        return
    coordinates = get_coordinates_by_address(address)
    if coordinates is None:
        return
    schools = get_organizations_by_coordinates(coordinates)
    return schools
