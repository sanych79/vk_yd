import requests
import os
import shutil
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
        #print(response.json())
        return response.json()

    def upload(self, file_path_from: str, file_path_to: str):
        """Метод загружает файлы по списку file_path на яндекс диск"""
        href = self._get_upload_link(disk_file_path=file_path_to).get("href", "")
        response = requests.put(href, data=open(file_path_from, 'rb'))
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
    for y in x['sizes']:
        if size < y['width']*y['height'] or count == 1:
            size = y['width']*y['height']
            m_url = y['url']
            m_like = x['likes']['count']
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
    album_i = str(Serch_req('album_id'))
    vk_token = str(Serch_req('vk_token'))
    yd_token = str(Serch_req('yd_token'))



if __name__ == "__main__":

    read_parametrs()
    user_id = int(input('Введи ID пользователя'))
    count_file = int(input('Введите количество выгружаемых файлов'))

    vk = VK(vk_token, user_id)
    uploader = YaUploader(yd_token)

    """ создаем временную папку для фото"""
    path1 = os.getcwd()
    path2 = path1 +f'\{dir_mane}'
    access_rights = 0o755
    
    try:
       os.makedirs(path2)
    except OSError:
       print ("Создать директорию %s не удалось" % path2)
    else:
       print ("Успешно создана директория %s " % path2)

    os.chdir(path2)
    main_result = []

    Count_step_statusbar = int(100/count_file)
    with tqdm(total=100) as pbar:
        for x in vk.get_photo_vk(count_f= count_file, alboum=album_i)['response']['items']:
            like_count = x['likes']['count']

            size, max_url, max_like, size_type = get_maxsize_photo(x['sizes'])
            url = max_url
            r = requests.get(url)
            result = uploader.md(dir_mane)
            with open(f'{max_like}.jpg', 'wb') as f:
                f.write(r.content)  
                result = uploader.upload(f'{max_like}.jpg', f'BackUp_Photo/{max_like}.jpg')
                main_result.append({"file_name": f'{max_like}.jpg', "size": size_type})
                pbar.update(Count_step_statusbar)

    os.chdir(path1)

    """ удаляем временную папку """
    shutil.rmtree(path2)

    """ запись результата в файл result.json """
    with open('result.json', 'w') as f:
        json.dump(main_result, f)