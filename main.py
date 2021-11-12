import json
import codecs
import bs4
import requests
from bs4 import BeautifulSoup

URL = 'https://www.transportstyrelsen.se/'
vagmarken_url = URL + '/sv/vagtrafik/Vagmarken/'

json_data_for_question = []
json_data_for_incorrect_answers = []


# {
#       "category": "Vägmärken",
#       "type": "multiple",
#       "difficulty": "easy",
#       "img": "https://www.transportstyrelsen.se/globalassets/global/vag/vagmarken/vagmarken-nedladdning/a1-1.png",
#       "question": "Märket på bilden står för?",
#       "correct_answer": "Märket anger en farlig kurva samt kurvans riktning.",
#       "incorrect_answers": [
#         "Märket anger flera farliga kurvor samt den första farliga kurvans riktning.",
#         "Märket anger brant ned förslutning. Siffran anger lutningen i procent och är anpassad till förhållandena på platsen.",
#         "Varning för avsmalnande väg"
#       ]
#     }

def get_html(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup


def get_roadsignlink(url):
    html = get_html(url)
    roadsignlinks = html.find_all('a', {'class': 'roadsignlink'})
    return roadsignlinks


def get_names_and_urls(elements: bs4.element.ResultSet):
    arr = []
    for element in elements:
        arr.append({
            'url': element['href'].strip(),
            'name': element.text.strip()
        })
    return arr


def get_vagmarken_image_url(url):
    html = get_html(url)
    try:
        list_group = html.find_all('div', {'class': 'list-group'})[0]
        list_group_item = list_group.find_all('a', {'class': 'list-group-item'})
        if '.png' in list_group_item[0]['href']:
            return list_group_item[0]['href']
        elif '.png' in list_group_item[1]['href']:
            image_url = list_group_item[1]['href']
            return image_url
        elif '.png' in list_group_item[2]['href']:
            image_url = list_group_item[2]['href']
            return image_url
        elif '.png' in list_group_item[3]['href']:
            image_url = list_group_item[3]['href']
            return image_url
        elif '.png' in list_group_item[4]['href']:
            image_url = list_group_item[4]['href']
            return image_url
        else:
            alt_image = html.find_all('img', {'class': 'roadsign'})[0]['src']
            return alt_image
    except IndexError:
        try:
            alt_image = html.find_all('img', {'class': 'roadsign'})[0]['src']
            return alt_image
        except IndexError:
            content_primary = html.find_all('div', {'id': 'content-primary'})[0]
            image_url = content_primary.find_all('a')[4]['href']
            return image_url


def get_image_file_name_from_url(url):
    img_name = url.split('/')[-1].split('-')[0].upper()
    img_format = url.split('/')[-1].split('.')[-1]
    file_name = img_name + '.' + img_format
    return file_name


def download_and_save_image(url):
    img_data = requests.get(url).content
    with open('img\\' + get_image_file_name_from_url(url), 'wb') as handler:
        handler.write(img_data)


def create_json_data(data_list: []):
    for category in data_list:
        vagmarke_list = get_names_and_urls(get_roadsignlink(URL + category['url']))
        for vagmarke in vagmarke_list:
            img_url = get_vagmarken_image_url(URL + vagmarke['url'])
            json_data_q = {
                "category": category['name'].split('.')[-1],
                "type": "multiple",
                "img_url": URL + img_url,
                "img_file_name": get_image_file_name_from_url(img_url),
                "question": vagmarke['name'].split('.')[-1]
            }
            json_data_a = {
                "category": category['name'].split('.')[-1],
                "question": vagmarke['name'].split('.')[-1]
            }
            json_data_for_question.append(json_data_q)
            json_data_for_incorrect_answers.append(json_data_a)


def write_json_to_file():
    with open('incorrect_answers.json', 'w', encoding='utf-8') as outfile:
        json.dump(json_data_for_incorrect_answers, outfile)

    with open('question.json', 'w', encoding='utf-8') as outfile:
        json.dump(json_data_for_question, outfile)


if __name__ == '__main__':
    vagmarken_list = get_names_and_urls(get_roadsignlink(vagmarken_url))
    create_json_data(vagmarken_list)
    write_json_to_file()
