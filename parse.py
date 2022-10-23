import datetime
import json
import logging
from functools import lru_cache
from pprint import pprint
from time import sleep
from typing import List, Tuple, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag

from config import logindata
from utils import Auditorium, WeekDay, Lesson, Week, Session, month_to_int

groups_names_to_requests = dict()
teachers_names_to_requests = dict()


def update_global_dicts() -> bool:
    global groups_names_to_requests
    global teachers_names_to_requests
    try:
        document = \
            BeautifulSoup(requests.get('https://guap.ru/rasp/').text, 'lxml').select_one('.rasp').select_one('.form')
        groups_names_to_requests = {
            el.text: el.attrs['value']
            for el in document.select_one('span:-soup-contains("группа:")').select('option')
        }
        teachers_names_to_requests = {
            el.text: el.attrs['value']
            for el in document.select_one('span:-soup-contains("преподаватель:")').select('option')
        }
        return True
    except IndexError:
        return False


def get_group_rasp(group_name: str | int) -> Optional[List[Lesson]]:
    group_name = str(group_name)
    for i in range(3):  # tries count
        if group_name in groups_names_to_requests:
            break
        if not update_global_dicts():
            sleep(1)
            print('Wait')
    else:
        return None  # Internet errors or group_name invalid
    children = \
        BeautifulSoup(requests.get(f'https://guap.ru/rasp/?g={groups_names_to_requests[group_name]}').text,
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
                lesson = Lesson(
                    name=child.select_one('span').text.split(' – ')[1].strip(),
                    type=child.select('span>b')[-1].text,  # для week.all
                    number=child.find_previous_sibling('h4').text.split()[0],
                    day=WeekDay(child.find_previous_sibling('h3').text),
                    week=week,
                    auditorium=Auditorium(
                        address=child.select('span>em')[0].text.split(', ')[0].replace(' – ', ''),
                        number=child.select_one('span>em').text.split(', ')[1].replace('ауд. ', '')
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


def get_teachers() -> pd.DataFrame:
    logging.critical('[parse.get_teachers] Not implemented')
    return None


sess_groups_names_to_requests = dict()
sess_teachers_names_to_requests = dict()


def update_session_dicts() -> bool:
    global sess_groups_names_to_requests
    global sess_teachers_names_to_requests
    try:
        document = \
            BeautifulSoup(requests.get('https://raspsess.guap.ru/').text, 'lxml').select_one('.rasp').select_one(
                '.form')
        sess_groups_names_to_requests = {
            el.text: el.attrs['value']
            for el in document.select_one('span:-soup-contains("группа:")').select('option')
        }
        sess_teachers_names_to_requests = {
            el.text: el.attrs['value']
            for el in document.select_one('span:-soup-contains("преподаватель:")').select('option')
        }
        return True
    except IndexError:
        return False


def get_sessions(group_name: str | int) -> Optional[List[Session]]:
    group_name = str(group_name)
    for i in range(3):  # tries count
        if group_name in sess_groups_names_to_requests:
            break
        if not update_session_dicts():
            sleep(1)
            print('Wait')
    else:
        return None  # Internet errors or group_name invalid
    children = \
        BeautifulSoup(requests.get(f'https://raspsess.guap.ru/?g={sess_groups_names_to_requests[group_name]}').text,
                      'lxml').select_one('.result').children
    # next(children)  # skip legend with div tag
    result = []
    for child in children:
        # h3 is week day, h4 is shift
        if child.name == 'div':
            child: Tag
            date = child.find_previous_sibling('h3').text.split()
            session = Session(
                name=child.select_one('span').text.split(' – ')[0].strip(),
                date=datetime.date(datetime.date.today().year, month_to_int.get(date[1], 1), int(date[0])),
                number=child.find_previous_sibling('h4').text.split()[0],
                auditorium=Auditorium(
                    address=child.select('span>em')[0].text.split('. ')[0].replace(' – ', ''),
                    number=child.select_one('span>em').text.split('. ')[1]
                ),
                teacher=child.select_one('div').select_one('.preps').select_one('a').text,
            )
            result.append(session)
    return result


def get_tasks(session_token: str, labels: Tuple[str] = ('id', 'user_id', 'type_name', 'name')) -> pd.DataFrame:
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
            )>
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
        return pd.DataFrame(
            columns=labels,
            data=([task[label] for label in labels] for task in
                  json_obj['tasks']))


def get_materials(session_token: str, labels: Tuple[str] = ('name', 'url', 'filelink')) -> pd.DataFrame:
    """
    getstudentmaterials: {
        materials: [
            <material-objects list(
                id         material id
                datecreate create date
                name       material name and description
                semester   material semester id
                isPublic   "1" if public
                url        external link
                filelink   guap /get-material/* file link (may be "/get-material/" if empty)
                subject    <subject-id list>
                groups     <??? list>
            )>
        ]
      }
    """
    with requests.Session() as sess:
        sess.cookies['PHPSESSID'] = session_token
        json_obj = json.loads(
            sess.post(
                url='https://pro.guap.ru/getstudentmaterials/'
            ).content.decode(encoding='unicode_escape', errors='ignore').replace(r'\/', '/'),
            strict=False)
        return pd.DataFrame(
            columns=labels,
            data=([material[label] if label != 'filelink' else
                   None if material[label] == '/get-material/' else
                   'https://pro.guap.ru' + material[label]
                   for label in labels] for material in
                  json_obj['materials'])
        )


@lru_cache(maxsize=4)
def get_session_token(login: str, password: str) -> str:
    with requests.Session() as sess:
        for _ in range(2):  # simulate redirection with session token
            sess.post(url='https://pro.guap.ru/user/login_check', data={
                '_username': login,
                '_password': password
            }, allow_redirects=False)
        return sess.cookies['PHPSESSID']


def main():
    pprint(get_sessions('4142'))
    ...


if __name__ == '__main__':
    main()
