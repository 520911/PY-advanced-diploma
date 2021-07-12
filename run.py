from random import randrange
import vk_api
from sqlalchemy.orm import declarative_base
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_class.class_user import VkUser, user_token
from db.orm_diploma import add_user_to_db, add_to_black_list, save_matches
from bot_constraint import statuses, sexes, profile_status, yes, no, choose_str, status_str
from vk_tokens import grup_token

Base = declarative_base()

vk1 = vk_api.VkApi(token=grup_token)
longpoll = VkLongPoll(vk1, group_id=205558812)


def write_msg(user_id, message, attachment=None):
    vk1.method('messages.send', {'user_id': user_id, 'message': message, 'attachment': attachment,
                                 'random_id': randrange(10 ** 7)})


def main(den: VkUser = None):
    count = 0  # Счетчик пользователей
    user_count = 1
    black_list = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.message != '':

            if event.to_me:
                msg = event.text

                if msg == "старт":
                    add_user_to_db(den)  # Add user in table user
                    write_msg(event.user_id,
                              message=f"hi, {den.get_user_info()['first_name']} Хочешь найти людей?\nДа / Нет?")
                    statuses['status'] = 'input_country'
                elif msg in yes['yes'] and statuses['status'] == 'input_country':
                    write_msg(event.user_id,
                              message="Введите страну поиска с большой буквы, например - Россия\n "
                                      "При неправильном вводе выбора страны не произойдет")
                elif msg in den.get_country():
                    den.country = den.get_country()[msg]
                    write_msg(event.user_id, message="Введите город поиска с большой буквы, например - Самара\n"
                                                     "При неправильном вводе выбора города не произойдет")
                elif msg in den.get_city(den.country):
                    den.city = msg
                    write_msg(event.user_id, message="Введите пол:\n1 - женщина\n2 - мужчина\n0 - любой")
                    statuses['status'] = 'input_sex'
                elif msg in sexes and statuses['status'] == 'input_sex':
                    den.sex = int(msg)
                    write_msg(event.user_id, message="Введите от какого возраста вести поиск")
                    statuses['status'] = 'input_age_from'
                elif msg and statuses['status'] == 'input_age_from':
                    den.age_from = int(msg)
                    write_msg(event.user_id, message="Введите до какого возраста вести поиск")
                    statuses['status'] = 'input_age_to'
                elif msg and statuses['status'] == 'input_age_to':
                    den.age_to = int(msg)
                    write_msg(event.user_id, message=status_str)
                    statuses['status'] = 'input_profile_status'
                elif msg in profile_status and statuses['status'] == 'input_profile_status':
                    den.status = int(msg)
                    write_msg(event.user_id, message="Найдено {} результатов".format(len(den.get_search_info())))
                    write_msg(event.user_id,
                              message="Показать имя, фамилию и ссылку на профиль первого человека? Да/Нет")
                    statuses['status'] = 'show_first'
                elif msg in yes['yes'] and statuses['status'] == 'show_first':
                    user = den.get_search_info()
                    top_photos = den.get_top_photos(owner_id=user[count]['id'])

                    write_msg(event.user_id, f"Имя: {user[0]['first_name']},\n"
                                             f"Фамилия: {user[0]['last_name']},\n"
                                             f"Профиль: https://vk.com/id{user[count]['id']},\n"
                                             f"Фото: ", den.prepare_photos(top_photos))
                    write_msg(event.user_id, message=choose_str)
                    statuses['status'] = 'black_list'
                elif msg in no['no'] and statuses['status'] == 'black_list':
                    black = den.get_search_info()
                    add_to_black_list(user_id=user_count, match_id=black[count]['id'])
                    write_msg(event.user_id, message='Показать следующего человека? Введите - показать\n')
                elif msg in 'сохранить':
                    save_matches(den, count=count)
                    write_msg(event.user_id, message='Показать следующего человека? Введите - показать\n')
                elif msg in 'показать':
                    while count < len(den.get_search_info()):
                        count += 1
                        user = den.get_search_info()
                        if user[count]['id'] not in black_list:
                            top_photos = den.get_top_photos(owner_id=user[count]['id'])
                            write_msg(event.user_id, f"Имя: {user[count]['first_name']},\n"
                                                     f"Фамилия: {user[count]['last_name']},\n"
                                                     f"Профиль: https://vk.com/id{user[count]['id']},\n"
                                                     f"Фото: ", den.prepare_photos(top_photos))
                            write_msg(event.user_id, message="Для начала нового поиска введите 'старт'\n"
                                                             "Для выхода введите 'ку'")
                            write_msg(event.user_id, message=choose_str)
                        else:
                            write_msg(event.user_id, message="Закончились люди, для повтора поиска наберите: старт")
                        black_list.append(user[count]['id'])
                        break
                elif msg == 'старт':
                    statuses['status'] = 200
                    count = 0
                    user_count += 1
                elif msg == 'ку':
                    count = 0
                    break


if __name__ == '__main__':
    user = VkUser(token=user_token)
    main(user)
