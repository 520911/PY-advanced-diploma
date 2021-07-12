from datetime import datetime
from urllib.parse import urlencode
import vk_api
from dateutil.relativedelta import relativedelta
from vk_tokens import user_token

vk = vk_api.VkApi(token=user_token).get_api()


class VkUser:
    def __init__(self, token=user_token):
        self.token = token
        self._sex = None
        self._relation = None
        self._city = None
        self._age_from = None
        self._age_to = None
        self._country_id = None
        self.black_list = []

    @property
    def country(self):
        return self._country_id

    @country.setter
    def country(self, value):
        self._country_id = value

    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, value):
        self._city = value

    @property
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, value):
        self._sex = value

    @property
    def relation(self):
        return self._relation

    @relation.setter
    def relation(self, value):
        self._relation = value

    @property
    def age_from(self):
        return self._age_from

    @age_from.setter
    def age_from(self, value):
        self._age_from = value

    @property
    def age_to(self):
        return self._age_to

    @age_to.setter
    def age_to(self, value):
        self._age_to = value

    @staticmethod
    def get_auth_link(app_id: int = 7892875, scope='status'):
        url = 'https://oauth.vk.com/authorize'
        redirect_uri = 'https://oauth.vk.com/blank.html'
        params = {
            "client_id": app_id,  # app id 7892875
            "redirect_uri": redirect_uri,
            "response_type": "token",
            "scope": scope
        }
        url_requests = '?'.join((url, urlencode(params)))
        return url_requests

    @staticmethod
    def get_user_info(ids: str = None):
        user = vk.users.get(user_ids=ids, fields='sex,bdate,city,relation,domain')[0]
        return user

    @staticmethod
    def get_date_from_str(date_str: str = None):
        bdate = date_str.split('.') if date_str else []
        bdate.extend([None, None, None])
        birth_day = int(bdate[0]) if bdate[0] else bdate[0]
        birth_month = int(bdate[1]) if bdate[1] else bdate[1]
        birth_year = int(bdate[2]) if bdate[2] else bdate[2]
        age = None
        if birth_year:
            birth_date = datetime(birth_year, birth_month, birth_day)
            now = datetime.utcnow()
            now = now.date()
            age = relativedelta(now, birth_date).years
        return age

    @staticmethod
    def get_age(ids: str = None):
        try:
            age = VkUser.get_date_from_str(VkUser.get_user_info(ids)['bdate'])
        except KeyError:
            age = None
        return age

    @staticmethod
    def get_user_city(ids: str = None):
        try:
            city = VkUser.get_user_info(ids)['city']['title']
        except KeyError:
            city = None
        return city

    @staticmethod
    def get_relations(ids: str = None):
        relations = VkUser.get_user_info(ids)['relation']
        return relations

    @staticmethod
    def get_search_sex(ids: str = None):
        sex = VkUser.get_user_info(ids)['sex']
        return sex

    @staticmethod
    def get_country():
        country = vk.database.getCountries(need_all=1, count=235)['items']
        result_dict = {}
        for i in country:
            result_dict[i['title']] = i['id']
        return result_dict

    @staticmethod
    def get_city(country_id=1, count=1000, need_all=0):
        country = vk.database.getCities(country_id=country_id, count=count, need_all=need_all)['items']
        result_list = []
        for result in country:
            result_list.append(result['title'])
        return result_list

    def get_search_info(self, count=10, has_photo=1):
        result_list = []
        users = vk.users.search(access_token=self.token, sex=self._sex, count=count,
                                hometown=self._city, country=self._country_id, status=self._relation,
                                age_from=self._age_from,
                                age_to=self._age_to, has_photo=has_photo, fields='id, is_closed, bdate, domain')
        for user in users['items']:
            if user['is_closed'] is False:
                result_list.append(user)
        return result_list

    @staticmethod
    def get_top_photos(owner_id: int = None, album_id='profile', extended=1):
        result_dict = {}
        photos = vk.photos.get(access_token=user_token, owner_id=owner_id, extended=extended, album_id=album_id)[
            'items']
        for photo_ in photos:
            media_id_ = 'photo' + str(photo_['owner_id']) + '_' + str(photo_['id'])
            popularity = photo_['likes']['count'] + photo_['comments']['count']
            result_dict[media_id_] = popularity
        sorted_tuple = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_tuple[:3]

    @staticmethod
    def prepare_photos(photos_list: list = None):
        links = [i[0] for i in photos_list]
        photos_ = ','.join(links)
        return photos_
