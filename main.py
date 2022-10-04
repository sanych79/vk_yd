import requests
from tqdm import tqdm
import json
import configparser


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.url = 'https://api.vk.com/method/'

    def get_photo_vk(self, count_f, alboum = 'wall'):
        """Функция получения фотограций у пользователя self.id в альбоме album_id' = "wall" количесто фото'count_f' """
        url = self.url + 'photos.get'
        params = {'owner_id': -self.id, 'album_id': alboum, 'count': count_f, 'extended':1}
        response = requests.get(url, params={**self.params, **params}).json()
        return response
    def serch_user_vk(self, user_name):
        """Функция поиска пользователя """
        url = self.url + 'users.search'
        params = {'q': user_name}
        response = requests.get(url, params={**self.params, **params}).json()
        return response

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def _get_upload_link(self, disk_file_path):
        up_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        h = self.get_headers()
        param = {"path": disk_file_path, "overwrite": True}
        response = requests.get(up_url, headers=h, params=param)
        return response.json()

    def upload(self, file_path_from: str, file_path_to: str):
        """Метод загружает файлы c file_path_from в file_path_to на ЯДиск"""
        href = self._get_upload_link(disk_file_path=file_path_to).get("href", "")
        response = requests.put(href, data=file_path_from)
        response.raise_for_status()

    def md(self, path1):
        """Метод создает папку path1 на яндекс диске"""
        href = 'https://cloud-api.yandex.net/v1/disk/resources'
        h = self.get_headers()
        param = {"path": path1, "overwrite": True}
        response = requests.put(href, headers=h, params=param)

def  get_maxsize_photo(serch_data):
    """Функция поиска максимального размера фото. Выход размер, url, количество лайков, тип размера фото"""
    size = 0
    size_type = 0
    m_url = 0
    m_like = 0
    count = 1
    for y in serch_data['sizes']:
        if size < y['width']*y['height'] or count == 1:
            size = y['width']*y['height']
            m_url = y['url']
            m_like = serch_data['likes']['count']
            size_type = y['type']
        count = 0
    return size, m_url, m_like, size_type

def read_parametrs():
    """чтение параметров программы из settings.ini"""
    global count_file
    global dir_mane
    global album_i
    global vk_token
    global yd_token

    config = configparser.ConfigParser()
    config.read("settings.ini")

    dir_mane = config["VKtoYD"]["dir_mane"]
    album_i = config["VKtoYD"]["album_id"]
    vk_token = config["VKtoYD"]["vk_token"]
    yd_token = config["VKtoYD"]["yd_token"]
    count_file = int(config["VKtoYD"]["count_file"])

def enter_param():
    global user_id
    global user_name

    config = configparser.ConfigParser()
    config.read("settings.ini")

    try:
        user_id = int(input('Введи ID пользователя>'))
    except ValueError:
        print('Введено не корректное значения')
        user_id = config["VKtoYD"]["user_id"]
        print(f'Присвоенно значение по умолчанию :{user_id}')
    else:
        if user_id < 1:
            print('Введено не корректное значения')
            user_id = config["VKtoYD"]["user_id"]
            print(f'Присвоенно значение по умолчанию :{user_id}')

    try:
        user_name = str(input('Введи Имя и Фамилию пользователя>'))
    except ValueError:
        print('Введено не корректное значения')
        user_id = config["VKtoYD"]["user_name"]
        print(f'Присвоенно значение по умолчанию :{user_name}')
    else:
        if len(user_name) < 4:
            print('Введено не корректное значения')
            user_id = config["VKtoYD"]["user_name"]
            print(f'Присвоенно значение по умолчанию :{user_name}')


def main_function():
    """Основная функция которая получает данные из ВК и записывает на ЯДиск"""
    main_res = []
    Count_step_statusbar = int(100/count_file)
    last_max_like = 0
    with tqdm(total=100) as pbar:
        for x in vk.get_photo_vk(count_f=count_file, alboum=album_i)['response']['items']:
            like_count = x['likes']['count']
            size, max_url, max_like, size_type = get_maxsize_photo(x)
            if max_like == last_max_like:
                file_name = f'{max_like}_{x["date"]}'
            else:
                file_name = max_like
            last_max_like = max_like
            url = max_url
            result = uploader.md(dir_mane)
            result = uploader.upload(url, f'BackUp_Photo/{file_name}.jpg')
            main_res.append({"file_name": f'{file_name}.jpg', "size": size_type})
            pbar.update(Count_step_statusbar)

    """ запись результата в файл result.json """
    with open('result.json', 'w') as f:
        json.dump(main_res, f)

def comp_username_user_id(username, user_id):
    """Проверка совпадения имени пользователя и его идентификатора"""
    for x in vk.serch_user_vk(username)['response']['items']:
        if x['id']==user_id:
            return True

if __name__ == "__main__":

    read_parametrs()
    enter_param()
    vk = VK(vk_token, user_id)

    flag = 0
    while flag == 0:
        if comp_username_user_id(user_name, user_id) == True:
            flag = 1
        else:
            print(f'Идентификатор {user_id} не пренадлежит пользователю {user_name}')
            enter_param()

    vk = VK(vk_token, user_id)
    uploader = YaUploader(yd_token)
    main_function()

    print("Конец работы программы")