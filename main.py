import requests
from tqdm import tqdm
import json


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.url = 'https://api.vk.com/method/'
    def users_info(self):
        """Функция получения информации о пользователе VK"""
        url = self.url + 'users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_photo_vk(self, count_f, alboum = 'wall'):
        """Функция получения фотограций у пользователя self.id на его стене album_id' = "wall" количесто фото 'count_f' """
        url = self.url + 'photos.get'
        params = {'owner_id': -self.id, 'album_id': alboum, 'count': count_f, 'extended':1}
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
        """Метод загружает файлы по списку file_path на яндекс диск"""
        href = self._get_upload_link(disk_file_path=file_path_to).get("href", "")
        #response = requests.put(href, data=open(file_path_from, 'rb'))
        response = requests.put(href, data=file_path_from)
        response.raise_for_status()
        #print(response)

    def md(self, path1):
        """Метод создает папку path1 на яндекс диске"""
        href = 'https://cloud-api.yandex.net/v1/disk/resources'
        h = self.get_headers()
        param = {"path": path1, "overwrite": True}
        response = requests.put(href, headers=h, params=param)
    
    def dd(self, path1):
        """Метод создает удаляет папку path1 на яндекс диске"""
        href = 'https://cloud-api.yandex.net/v1/disk/resources'
        h = self.get_headers()
        param = {"path": path1, "overwrite": True}
        response = requests.delete(href, headers=h, params=param)

def  get_maxsize_photo(serch_data):
    """Функция поиска максимального размера фото. Выход размер, url, количество лайков"""
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

def read_token(file_name):
    """Функция чтения токена из файла file_name."""
    with open(file_name,'r', encoding='utf8') as file:
        for line in file:
            res =  line.strip()
    return res

def Serch_req(mane):
    result = 0
    with open("param.ini",'r', encoding='utf8') as file:
        """Функция поиска параметра mane в файле param.ini"""
        res = file.readlines()
        for x in res:
            str = x.strip()
            if str.find(mane) == 0:
                result = str[len(mane)+1:]
    return result

def read_parametrs():
    """чтение параметров программы из param.ini"""
    global user_id
    global count_file
    global dir_mane
    global album_i
    global vk_token
    global yd_token
    dir_mane = str(Serch_req('dir_mane'))
    dir_mane = str(Serch_req('dir_mane'))
    album_i = str(Serch_req('album_id'))
    vk_token = str(Serch_req('vk_token'))
    yd_token = str(Serch_req('yd_token'))

    try:
        user_id = int(input('Введи ID пользователя>'))
    except ValueError:
        print('Введено не корректное значения')
        user_id = int(Serch_req('user_id'))
        print(f'Присвоенно значение по умолчанию :{user_id}')
    else:
        if user_id < 1:
            print('Введено не корректное значения')
            user_id = int(Serch_req('user_id'))
            print(f'Присвоенно значение по умолчанию :{user_id}')

    try:
        count_file = int(input('Введите количество выгружаемых файлов>'))
    except ValueError:
        print('Введено не корректное значения')
        count_file = int(Serch_req('count_file'))
        print(f'Присвоенно значение по умолчанию :{count_file}')
    else:
        if count_file < 1:
            print('Введено не корректное значения')
            count_file = int(Serch_req('count_file'))
            print(f'Присвоенно значение по умолчанию :{count_file}')

def main_function(main_res):
    """Основная функция которая получает данные из ВК и записывает на ЯДиск"""
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
        json.dump(main_result, f)

if __name__ == "__main__":

    read_parametrs()
    vk = VK(vk_token, user_id)
    uploader = YaUploader(yd_token)
    main_result = []
    main_function(main_result)
    print("Конец работы программы")