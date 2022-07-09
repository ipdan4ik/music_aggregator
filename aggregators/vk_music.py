import math
import time

from tqdm import tqdm

import requests
import webbrowser
from urllib.parse import urlparse, parse_qs

from models.vk_audio import VkAudio
from models.vk_auth import VkAuth
from utils.decorators import request_reconnect

URL_AUTH = 'https://oauth.vk.com/authorize'
URL = 'https://api.vkontakte.ru/method/'


class VkMusic:

    def __init__(self, client_id=6121396):
        self.client_id = client_id
        self.auth = self.update_auth_token()

    def update_auth_token(self):
        auth = VkAuth.db_find_one(self.client_id)
        if auth and auth.timestamp > time.time():
            return auth

        params = {
            'client_id': self.client_id,
            'scope': '1',
            'redirect_uri': ['https://oauth.vk.com/blank.html', 'close.html'],
            'display': 'page',
            'response_type': 'token',
            'revoke': 0,
        }
        url = requests.get(URL_AUTH.format(app_id=self.client_id), params=params).url
        webbrowser.open_new(url)

        init_time = int(time.time())

        response = input('Open this link and paste the result url\n')
        parsed_response = urlparse(response)
        parsed_response_qs = parse_qs(parsed_response.fragment)
        access_token = parsed_response_qs['access_token'][0]
        expires_in = parsed_response_qs['expires_in'][0]
        user_id = parsed_response_qs['user_id'][0]
        data = VkAuth(
            token=access_token,
            user_id=user_id,
            client_id=self.client_id,
            timestamp=init_time + int(expires_in),
        ).db_update(upsert=True)
        return data

    def vk_request(self, url, params):
        response = requests.get(url, params=params)
        response_json = response.json()
        if 'error' in response_json:
            error_code = response_json['error']['error_code']
            if error_code == 14:
                params['captcha_sid'] = response_json['error']['captcha_sid']
                webbrowser.open_new(response_json['error']['captcha_img'])
                params['captcha_key'] = input('\nВведите символы, изображённые на картинке: ')
                return self.vk_request(url, params=params)
            elif error_code == 100:
                return None
            else:
                print(response_json)
                return None
        return response_json

    def get_audio_list(self, owner_id):
        # audio.get.json?uid={uid}&access_token={atoken}
        limit = 100
        audio_list = []
        params = {
            'owner_id': owner_id,
            'access_token': self.auth.token,
            'v': '5.131',
            'count': 1,
            'offset': 0
        }

        # first request to check total count
        response = self.vk_request(URL + 'audio.get', params=params)
        count = response['response']['count']

        params['count'] = limit
        total_pages = math.ceil(count / limit)
        for page in range(total_pages):
            params['offset'] = page * limit
            response = self.vk_request(URL + 'audio.get', params=params)
            audio_list.extend(response['response']['items'])

        assert response['response']['count'] == len(audio_list), 'wrong count of items'
        return audio_list

    @request_reconnect
    def get_audio(self, track_id, owner_id):
        params = {
            'audios': f'{owner_id}_{track_id}',
            'access_token': self.auth.token,
            'v': '5.131'
        }
        response = self.vk_request(URL + 'audio.getById', params=params)
        if response is None:
            return None
        return VkAudio(**response['response'][0])

    def parse_user_audio(self, user_id=None):
        if not user_id:
            user_id = self.auth.user_id
        audio_list = self.get_audio_list(user_id)

        new_n = 0
        old_n = 0
        print(audio_list[:30])
        for track in tqdm(audio_list):
            track_id = track['id']
            owner_id = track['owner_id']
            audio_obj = VkAudio.db_find_one({'id': track_id, 'owner_id': owner_id})

            old_n += 1
            if not audio_obj:
                audio_obj = self.get_audio(track_id, owner_id)
                new_n += 1
                old_n -= 1

                if not audio_obj:
                    new_n -= 1
                    continue

            audio_obj.db_update({'id': track_id, 'owner_id': owner_id})
        err_n = len(audio_list) - new_n - old_n
        print(f'Добавлено: {new_n}; Пропущено: {old_n}; Ошибок: {err_n}\n')


if __name__ == '__main__':
    vkmusic = VkMusic()
    vkmusic.parse_user_audio(323291031)
