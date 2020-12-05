import urllib3
from bs4 import BeautifulSoup
import os


# Функция принимает строку(string) в виде url адреса и создает директории анализируя /  в ссылке
# В качестве ответа возращаеться строка в адреса созданной директории
def Create_url_name(url):
    t = url.find("//") + 2
    name = "\\"
    while url.find("/", t) > 0 and url.find("/", t) != (len(url) - 1):
        k = url.find("/", t)
        name = name + url[t:k] + "\\"
        t = k + 1
        try:
            os.mkdir(name)
        except:
            pass
    if url.find("/", t) != len(url) - 1:
        return name + url[t:]
    else:
        return name + url[t:len(url) - 1]


# Функция принимает строку(string) в виде html кода и ищет вхождение url ссылки в него
# В качестве ответа возращаеться строка в виде url ссылки в квадратных скобках и их начало их первого вхождения в код
def get_hyper_link(work):
    t = 0
    link = []
    while work.find("https", work.find("href=", t)) != (-1):
        k = work.find("https", work.find("href=", t))
        t = work.find("\"", work.find("\"", k))
        link.append([k, f"[{work[k:t]}]"])
    return link


# Функция принимает название файла и строку(string), функция записывает в файл строки разбиваю их на слова
def beatiful_string(url, Text, job):
    try:
        file = open(url + ".txt", "a")
    except:
        file = open(url + ".txt", "w")
    t = 0
    while (Text[t:(t + job[0] - 1)].rfind(" ") or Text[t:].find("]")) > 0 and len(Text) - t > 80:
        if t == 0:
            for i in range(job[2]):
                file.write(" ")
        if Text[t:(t + job[0] - 1)].rfind(" ") > 0:
            file.write(Text[t:(t + Text[t:(t + job[0] - 1)].rfind(" "))] + "\n")
            t += Text[t:(t + job[0] - 1)].rfind(" ")
        elif Text[t:].find("]") > 0:
            file.write(Text[t:(t + 1 + Text[t:].find("]"))] + "\n")
            t += Text[t:].find("]") + 1
    file.write(Text[t:] + "\n")
    for i in range(job[1]):
        file.write("\n")
    file.close()


# Функция принимает массив url ссылок и индекс нахождения их в коде и возращает слово перед который необходимо вставить ссылку
# Функция возращает массив слов перед которыми необходимо вставить ссылку
def mesto(link):
    vstr = []
    for i in range(len(link)):
        k = str(work).find("</a>", link[i][0]) - 1
        t = str(work).rfind(">", 0, k) + 1
        vstr.append(str(work)[t:k + 1])
    return vstr


# Функция получает путь к файлу по образцу которого ей нужно редактировать файл с которым мы работаем
# Функция возращает массив где 1 элемент максимальная длина строки, следущая кол-во строк отступов
# и последняя кол-во отступов в красной строке
def sample_file(name):
    sample = open(name, "r",encoding="utf-8")
    max = 0
    redstring = 0
    flag = 0
    text = sample.readlines()
    for i in range(len(list(text))):
        if len(text[i]) > 0 and len(text[i]) > max:
            max = len(text[i])
            if flag == 0:
                paragraph = 0
                while text[i][paragraph] == " ":
                    paragraph += 1
            flag = 1
        elif text[i].find("\n") == 0:
            redstring += 1
            flag = 0
        else:
            redstring = 0
    return [max, redstring, paragraph]


# Чтение названия url ссылки
if __name__ == "__main__":
    url = input()
    # Отправка get запроса на получения html кода со страницы
    try:
        resp = urllib3.PoolManager().request("GET", url)
    except:
        print("Ошибка url ссылки")
        exit()
    file = open("text1.txt", "w",encoding="utf-8")

    # Декодинг и запись в файл html кода
    try:
        file.write(resp.data.decode('utf-8').encode('windows-1251', 'replace').decode('windows-1251'))
    except:
        try:
            file.write(resp.data.decode('windows-1251'))
        except:
            print("Ошибка декодинга файла")
            exit()
    file.close()

    # Чтение кода из файла
    with open("text1.txt", 'r',encoding="utf-8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
        # Поиск текста по основным тегам для него
        work = soup.body.find_all(["h1", "article", "p"])
        # Вызов функций для поиска ссылок и массива перед которым их вставить
        link = get_hyper_link(str(work))
        vstr = mesto(link)
        # Проход по ответам запроса по тегам и извлечение текста из них
        text = [work[i].text for i in range(len(work))]
        # создание директории согласно анализу url ссылки и возращения пути к обекту
        url = Create_url_name(str(url))

        # Выбор форматирования
        try:
            if int((input(
                    "Использовать стандартную форму обработки сайта?" + "\n" + "0)НЕТ" + "\n" + "1)ДА" + "\n"))) == 1:
                # Запрос на директория где находиться файл по образцу которого сделать форматирование,
                # Если директория не доступна то используеться стандартное формотирование
                try:
                    directory = input("\n" + "Введите путь к файлу образцу:")
                    job = sample_file(directory)
                except:
                    print("Ошибка пути файла будет использованана стандартная обработка")
                    job = [80, 1, 3]
            else:
                job = [80, 1, 3]
        except:
            print("Введен неверный символ будет использоваться стандарный ввод")
            job = [80, 1, 3]

        # Проход по массиву текста
        for i in range(len(text)):
            for j in range(len(vstr)):
                # Поиск места для вставки ссылок
                k = text[i].find(" ", text[i].find(vstr[j]))
                if k != -1:
                    k = text[i].rfind(" ", 0, k - 1)
                    text[i] = text[i][:k] + link[j][1] + " " + text[i][k:]
            # Вывод текста в файл по формату
            beatiful_string(str(url), text[i], job)
    f.close()
    os.remove(os.getcwd() + "\\" + "text1.txt")
