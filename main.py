import requests
import os
import shutil
from tqdm import tqdm

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
    
    

   def get_photo_vk(self, count_f):
        """Функция получения фотограций у пользователя self.id на его стекне album_id' = "wall" количесто фото 'count_f' """
        url = self.url + 'photos.get'
        params = {'owner_id': -self.id, 'album_id': "wall", 'count': count_f, 'extended':1}
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

if __name__ == "__main__":

    def  get_maxsize_photo(serch_data={}):
        """Функция поиска максимального размера фото. Выход размер, url, количество лайков"""
        size = 0
        m_url = 0
        m_like = 0
        count = 1
        for y in x['sizes']:
            if size < y['width']*y['height'] or count == 1:
                size = y['width']*y['height']
                m_url = y['url']
                m_like = x['likes']['count']
            count = 0
        return size, m_url, m_like

    def read_token(file_name):
        """Функция чтения токена из файлаfile_name."""
        with open(file_name,'r', encoding='utf8') as file:
            for line in file:
                res =  line.strip()
        return res

    vk_token = read_token('token_vk.txt')
    yd_token = read_token('token_yadisk.txt')

    "user_id - id пользоватля в VK"
    user_id = 1
    "count_file - количество скачиваемых фото VK"
    count_file = 3
    vk = VK(vk_token, user_id)
    uploader = YaUploader(yd_token)


    # создаем временную папку для фото
    dir_mane = 'BackUp_Photo'
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


    Count_step_statusbar = int(100/count_file)
    with tqdm(total=100) as pbar:
        for x in vk.get_photo_vk(count_f= count_file)['response']['items']:
            like_count = x['likes']['count']

            size, max_url, max_like = get_maxsize_photo(x['sizes'])

            url = max_url
            r = requests.get(url)
            result = uploader.md(dir_mane)
            with open(f'{max_like}.jpg', 'wb') as f:
                f.write(r.content)  
                result = uploader.upload(f'{max_like}.jpg', f'BackUp_Photo/{max_like}.jpg')
                pbar.update(Count_step_statusbar)

    os.chdir(path1)

    shutil.rmtree(path2) # удаляем временную папку



     

