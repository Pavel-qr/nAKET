from dataclasses import dataclass
from enum import Enum
from pprint import pprint
from time import sleep
from typing import Optional, List
import warnings
import requests
from bs4 import BeautifulSoup, Tag
import json
from tmp import logindata  # Tuple[login, password]
import pandas as pd

groups_names_to_requests = dict()
teachers_names_to_requests = dict()

nuber_to_time = {
    '1': '(9:30 – 11:00)',
    '2': '(11:10 – 12:40)',
    '3': '(13:00 – 14:30)',
    '4': '(15:00 - 16:30)',
    '5': '(16:40 - 18:10)',
    '6': '(18:30 - 20:00)',
    '7': '(21:10 - 21:40)',
}


class WeekDay(Enum):
    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    Thursday = 'Четверг'
    Friday = 'Пятница'
    Saturday = 'Суббота'
    Sunday = 'Воскресенье'


class Week(Enum):
    all = '🔶'
    up = 'верхняя (нечетная) ▲🔺'
    dn = 'нижняя (четная) ▼🔻'
    # out = 'вне сетки расписания (—)'


@dataclass
class Auditorium:
    address: str
    number: str


@dataclass
class Lesson:
    name: str
    type: str
    day: WeekDay
    number: str
    auditorium: Auditorium
    teachers: Optional[list[str]]
    groups: Optional[list[str]]
    week: Week


def update_global_dicts() -> bool:
    global groups_names_to_requests
    global teachers_names_to_requests
    global ids_to_teacher_names
    try:
        document = \
            BeautifulSoup(requests.get('https://rasp.guap.ru/').text, 'lxml').select_one('.rasp').select_one('.form')
        groups_names_to_requests = {
            el.text: el.attrs['value']
            for el in document.select_one('span:-soup-contains("группа:")').select('option')
            # 'span:contains(группа:)'
        }
        teachers_names_to_requests = {
            el.text: el.attrs['value']
            for el in document.select_one('span:-soup-contains("преподаватель:")').select('option')
            # 'span:contains(преподаватель:)'
        }
        return True
    except IndexError:
        return False


def get_group_rasp(group_name: str) -> List[Lesson]:
    for i in range(3):  # tries count
        if group_name in groups_names_to_requests:
            break
        if not update_global_dicts():
            sleep(1)
            print('Wait')
    else:
        # Internet errors or group_name invalid
        # todo raise
        raise
    children = \
        BeautifulSoup(requests.get(f'https://rasp.guap.ru/?g={groups_names_to_requests[group_name]}').text,
                      'lxml').select_one('.result').children
    next(children)  # skip legend with div tag
    result = []
    for child in children:
        # h3 is week day, h4 is time and couple number
        if child.name == 'div':
            if child.find_previous_sibling('h3').text == 'Вне сетки расписания':
                continue
                # todo add this
            else:
                if child.select('.dn'):
                    week = Week.dn
                elif child.select('.up'):
                    week = Week.up
                else:
                    week = Week.all
                child: Tag
                # print(child.select_one('span').find_all(text=True, recursive=False))
                lesson = Lesson(
                    name=child.select_one('span').text.split(' – ')[1].strip(),
                    type=child.select('span>b')[0].text,
                    number=child.find_previous_sibling('h4').text.split()[0],
                    day=WeekDay(child.find_previous_sibling('h3').text),
                    week=week,
                    auditorium=Auditorium(
                        address=child.select('span>em')[0].text.split(', ')[0],
                        number=child.select_one('span>em').text.split(', ')[1]
                    ),
                    groups=None,
                    teachers=None,
                )
                try:
                    lesson.groups = [a.text for a in child.select_one('div').select_one('.groups').select('a')]
                except AttributeError:
                    pass
                try:
                    lesson.teachers = [a.text for a in child.select_one('div').select_one('.preps').select('a')]
                except AttributeError:
                    pass
                result.append(lesson)
    return result


def get_tasks(session_token: str) -> pd.DataFrame:
    """
    all fields are strings or nulls
    get-student-tasksdictionaries: {
        tasks: [
            <task-objects list(
                id             task id
                user_id        teacher id
                datecreate     creation date
                dateupdate     last update date (not sure)
                name           task title
                description    task description
                type           task type id
                tt_name        task type name
                public         ???
                semester       task semester id
                markpoint      task maximum grade
                reportRequired ???
                url            attached link (by teacher)
                ordernum       for identical subjects, this field increases from one
                expulsionLine  ???
                plenty         ???
                harddeadline   hard deadline data
                grid           ???
                subject        task subject id
                subject_name   task subject name
                hash           ???
                filename       attached file (by teacher)
                semester_name  task semester name
                type_name      task type name
                status         task status id
                curPoints      received grade
                status_name    task status name
            )
        ],
        dictionaries: {
            status: [<verification stages list (id, name)>],
            subjects: [<subjects list (id, text, semester)>],
            semester: [<semesters list (id, name)>], # names starts with space
            types: [<task types list (id, name)>],
            values: [...], offset and limit   # IDK what is this
        }
    }
    """
    with requests.Session() as sess:
        sess.cookies['PHPSESSID'] = session_token
        json_obj = json.loads(
            sess.post(
                url='https://pro.guap.ru/get-student-tasksdictionaries/'
            ).content.decode(encoding='unicode_escape', errors='ignore').replace(r'\/', '/'),
            strict=False)
        labels = ['id', 'user_id', 'type_name', 'name']
        table = pd.DataFrame(columns=labels,
                             data=([task[label] for label in labels] for task in
                                   json_obj['tasks']))
        return table


def get_session_token(login: str, password: str) -> str:
    with requests.Session() as sess:
        for _ in range(2):  # <- lol
            sess.post(url='https://pro.guap.ru/user/login_check', data={
                '_username': login,
                '_password': password
            }, allow_redirects=False)
        return sess.cookies['PHPSESSID']


def main():
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(get_tasks(get_session_token(*logindata)))


if __name__ == '__main__':
    main()
