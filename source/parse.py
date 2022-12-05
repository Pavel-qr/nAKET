import datetime
import json
from functools import lru_cache
from time import sleep
from typing import List, Tuple, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag

from source.utils import Auditorium, WeekDay, Lesson, Week, Session, month_to_int, decode_unicode

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
                # todo add off grid schedule items
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


def get_teacher_names() -> List[str]:
    while not teachers_names_to_requests:  # todo better internet errors handle
        update_global_dicts()
    return [
        teacher.split(' - ')[0]
        for teacher in teachers_names_to_requests.keys()
    ]


def get_teachers(session_token, searchtext, labels: Tuple[str] = ('firstname', 'lastname', 'reslink'),
                 role=1, people=0, post=0, chair=0, subdivision=0, limit=10, offset=0) \
        -> Optional[tuple[pd.DataFrame, bool]]:
    """
    Teacher Series can include:
        chair         -- ???.\n
        depname       -- ???.\n
        depname_short -- ???.\n
        faculty       -- ???.\n
        faculty_short -- ???.\n
        firstname     -- ???.\n
        id            -- ???.\n
        image         -- Image url.\n
        lastname      -- ???.\n
        middlename    -- ???.\n
        pluralist     -- ???.\n
        post          -- ???.\n
        reslink       -- guap.ru teacher link (short: without https://pro.guap.ru/).\n
        subdivision   -- ???.\n
        works         -- list of ???.\n
    :param session_token: ???
    :param searchtext: search by name
    :param labels: ???
    :param role: ???
    :param people: ids of teachers
    :param post: Должность
    :param chair: Подразделение
    :param subdivision: Факультет/Институт
    :param limit: ???
    :param offset: ???
    :return Teachers and is any teachers left
    """
    with requests.Session() as sess:
        sess.cookies['PHPSESSID'] = session_token
        response = sess.post(
            'https://pro.guap.ru/getpeoples/',
            data={'role': role, 'people': people, 'post': post,
                  'chair': chair, 'subdivision': subdivision,
                  'searchtext': searchtext, 'limit': limit, 'offset': offset})
        if response.status_code == 401:
            return None  # Invalid login/password
        json_obj = json.loads(
            decode_unicode(response.content),
            strict=False)
        return pd.DataFrame(
            columns=labels,
            data=([task[label] for label in labels] for task in
                  json_obj['people'])), json_obj['isyetitems']


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
                number=int(child.find_previous_sibling('h4').text.split()[0]),
                auditorium=Auditorium(
                    address=child.select('span>em')[0].text.split('. ')[0].replace(' – ', ''),
                    number=child.select_one('span>em').text.split('. ')[1]
                ),
                teacher=child.select_one('div').select_one('.preps').select_one('a').text,
            )
            result.append(session)
    return result


def get_tasks(session_token: str, labels: Tuple[str] = ('id', 'user_id', 'type_name', 'name')) \
        -> Optional[pd.DataFrame]:
    """
    Task Series can include:    todo sort by utility
        id             --  task id\n
        user_id        --  teacher id\n
        datecreate     --  creation date\n
        dateupdate     --  last update date (not sure)\n
        name           --  task title\n
        description    --  task description\n
        type           --  task type id\n
        tt_name        --  task type name\n
        public         --  ???\n
        semester       --  task semester id\n
        markpoint      --  task maximum grade\n
        reportRequired --  ???\n
        url            --  attached link (by teacher)\n
        ordernum       --  for identical subjects, this field increases from one\n
        expulsionLine  --  ???\n
        plenty         --  ???\n
        harddeadline   --  hard deadline data\n
        grid           --  ???\n
        subject        --  task subject id\n
        subject_name   --  task subject name\n
        hash           --  ???\n
        filename       --  attached file (by teacher)\n
        semester_name  --  task semester name\n
        type_name      --  task type name\n
        status         --  task status id\n
        curPoints      --  received grade\n
        status_name    --  task status name\n
    all fields are strings or nulls.
    """
    with requests.Session() as sess:
        sess.cookies['PHPSESSID'] = session_token
        response = sess.post(url='https://pro.guap.ru/get-student-tasksdictionaries/')
        if response.status_code == 401:
            return None  # Invalid login/password
        json_obj = json.loads(
            decode_unicode(response.content),
            strict=False)
        return pd.DataFrame(
            columns=labels,
            data=([task[label] for label in labels] for task in
                  json_obj['tasks']))


def get_materials(session_token: str, labels: Tuple[str] = ('name', 'url', 'filelink')) -> Optional[pd.DataFrame]:
    """
    Materials Series can include:
        id         -- material id.\n
        datecreate -- create date.\n
        name       -- material name and description.\n
        semester   -- material semester id.\n
        isPublic   -- "1" if public.\n
        url        -- external link.\n
        filelink   -- guap /get-material/* file link (may be "/get-material/" if empty).\n
        subject    -- <subject-id list>.\n
        groups     -- <??? list>.\n
    """
    with requests.Session() as sess:
        sess.cookies['PHPSESSID'] = session_token
        response = sess.post(url='https://pro.guap.ru/getstudentmaterials/')
        if response.status_code == 401:
            return None  # Invalid login/password
        json_obj = json.loads(
            decode_unicode(response.content),
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
    ...


if __name__ == '__main__':
    main()
