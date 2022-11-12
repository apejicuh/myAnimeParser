import requests as rq
from bs4 import BeautifulSoup
from time import sleep
from math import ceil
import csv

# Заголовок для дополнительного аргумента библиотеки requests
headers = {"User-Agent":
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}


def main():

    print('path: data.csv results') # Файл, куда будет выводиться результат парсинга
    _path = 'data.csv'
    animes = 0
    with open(_path, 'w', encoding='cp1251', newline='') as file:  # Написание заголовков в .csv файл
        writer = csv.writer(file, delimiter=',')
        writer.writerow(
            (
                'title_name',
                'title_type',
                'title_genres',
                'title_rate',
                'title_score',
                'opinion',
                'commentator_review_rate',
                'user_name',
                'sex',
                'age',
                'start_year'
            )
        )

    url = "https://shikimori.one/animes"  # Главная ссылка, парсинг по которой осуществляем
    pages = int(BeautifulSoup(rq.get(url, headers=headers).text, "lxml").find('span',
                                                                              class_='link-total').text)  # Узнаём кол-во страниц с аниме
    for page in range(1, pages):  # Цикл по всем страницам в пагинации
        sleep(0.5)  # Idle для программы. Слишком быстрые запросы приведут к защите сайта от запросов
        soup = BeautifulSoup(rq.get(f"https://shikimori.one/animes/page/{page}", headers=headers).text, "lxml")  # Делаем запрос на каждую страницу и делаем из неё BeautifulSoup
        try:
            data = soup.find_all("article")
        except:
            print('animes on page error!')
        url_list = []  # Список аниме на одной странице

        for i in data:
            try:
                url_list.append(i.find("a").get("href"))
            except:
                print('url_list error!')
        # На текущей странице ссылки на все тайтлы

        for item in url_list:
            animes+=1
            print(f'[INFO] anime: {animes}')

            sleep(0.5)

            soup = BeautifulSoup(rq.get(item, headers=headers).text, "lxml")  # Делаем запрос на страницу каждого аниме из списка
            try:
                local_text = soup.find("h1").text  # Тут название RU / EN
                title_name = local_text[local_text.find("/") + 2:]  # Получаем название анивэ EN
                title_type = soup.find('div', class_='value').text  # Получаем тип анимэ
            except:
                print('title_name error!')

            title_genres_tmp = soup.find_all('span', class_='genre-en')  # Получаем список жанров на англ. языке
            title_genres = []

            for a in title_genres_tmp:
                title_genres.append(a.text)

            title_genres = ', '.join(title_genres)  # Тут получили string с жанрами

            title_rate = ''

            for a in soup.find_all('div', class_='line-container'):
                if a.text.find('Рейтинг: ') != -1:
                    title_rate = a.text[11:-2]
                    break

            try:
                title_score_all = soup.find('div', class_='text-score').text
                title_score_text = soup.find('div', class_='score-notice').text
                title_score = title_score_all.replace(title_score_text, '')
            except:
                print('title score error!')

            soup = BeautifulSoup(rq.get(item + '/reviews', headers=headers).text, "lxml")
            reviews_count = int(soup.find("div", class_="count").text)

            if reviews_count != 0:
                pages_with_reviews = ceil(reviews_count / 8)

                for page in range(1, pages_with_reviews + 1):
                    print('[INFO] reviews page: ' + str(page) + '/' + str(pages_with_reviews))

                    sleep(0.5)
                    current_anime_reviews_page = item + '/reviews' + f"/page/{page}"  # Заходим на каждую страницу с отзывами
                    new_response = rq.get(current_anime_reviews_page,
                                          headers=headers)  # Делаем запрос на каждую страницу с отзывами

                    souper = BeautifulSoup(new_response.text, "lxml").find_all("article")

                    for review in souper:  # Цикл по каждому отзыву
                        # Отработка отзыва
                        try:
                            opinion = 'neutral'
                            if review.find('div', class_='opinion positive') is not None:
                                opinion = 'positive'
                            elif review.find('div', class_='opinion negative') is not None:
                                opinion = 'negative'
                            else:
                                opinion = 'neutral'
                        except:
                            print('opinion error!')

                        commentator_review_rate = -1 # Оценка, которую пользователь оставил в отзыве
                        try:
                            if review.find('div', class_='stars score score-10') is not None:
                                commentator_review_rate = 10
                            elif review.find('div', class_='stars score score-9') is not None:
                                commentator_review_rate = 9
                            elif review.find('div', class_='stars score score-8') is not None:
                                commentator_review_rate = 8
                            elif review.find('div', class_='stars score score-7') is not None:
                                commentator_review_rate = 7
                            elif review.find('div', class_='stars score score-6') is not None:
                                commentator_review_rate = 6
                            elif review.find('div', class_='stars score score-5') is not None:
                                commentator_review_rate = 5
                            elif review.find('div', class_='stars score score-4') is not None:
                                commentator_review_rate = 4
                            elif review.find('div', class_='stars score score-3') is not None:
                                commentator_review_rate = 3
                            elif review.find('div', class_='stars score score-2') is not None:
                                commentator_review_rate = 2
                            elif review.find('div', class_='stars score score-1') is not None:
                                commentator_review_rate = 1
                            elif review.find('div', class_='stars score score-0') is not None:
                                commentator_review_rate = 0
                        except:
                            print('commentator_review_rate error!')

                        try:
                            commentator = review.find('a', class_='author-link').get('href')  # Получение ссылки на пользователя
                        except:
                            print('author link error!')

                        sleep(0.5)

                        soup = BeautifulSoup(rq.get(commentator, headers=headers).text,
                                             'lxml')  # Заходим на профиль комментатора

                        # Отработка параметров комментатора
                        try:
                            user_name = soup.find('h1').text  # Име пользователя
                        except:
                            print('user name error!')

                        try:
                            commentator_info = soup.find("div", class_="notice").text
                        except:
                            print('commentator info error')

                        sex = ''  # Пол
                        age = ''  # Возраст
                        start_year = -1  # Год регистрации

                        if commentator_info.find('муж') != -1:
                            sex = 'муж'
                        elif commentator_info.find('жен') != -1:
                            sex = 'жен'
                        else:
                            sex = '-'

                        if commentator_info.find(' лет') != -1:
                            age = commentator_info[commentator_info.find(' лет') - 2: commentator_info.find(' лет')]
                        elif commentator_info.find(' год') != -1:
                            age = commentator_info[commentator_info.find(' год') - 2: commentator_info.find(' год')]
                        elif commentator_info.find(' года') != -1:
                            age = commentator_info[commentator_info.find(' года') - 2: commentator_info.find(' года')]
                        else:
                            age = '-'

                        if commentator_info.find(' г.') != -1:
                            start_year = int(
                                commentator_info[commentator_info.find(' г.') - 4: commentator_info.find(' г.')])
                        else:
                            start_year = 0
                        # print(title_name, title_type, title_genres, title_rate, title_score, user_name, sex, age,
                        #       start_year, opinion, commentator_review_rate)

                        # Записываем результаты в .csv файл
                        with open(_path, 'a', encoding='utf-8', newline='') as file:
                            writer = csv.writer(file, delimiter=',')
                            writer.writerow(
                                (
                                    title_name,
                                    title_type,
                                    title_genres,
                                    title_rate,
                                    title_score,
                                    opinion,
                                    commentator_review_rate,
                                    user_name,
                                    sex,
                                    age,
                                    start_year
                                )
                            )
            else:
                continue


if __name__ == '__main__':
    main()
