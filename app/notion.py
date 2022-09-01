import logging
import os
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)


class Notion:
    def __init__(self):
        self.birthday_dict = {}
        self.congrat_text = (
            "Необходимо поздравить с подарком!",
            "Необходимо поздравить!",
            "Напоминаем о покупке подарка",
        )
        self.message_day = ("Сегодня день рождения:", "Сегодня день рождения:", "Через 5 дней день рождения:")

    def _load(self, url, auth_head):
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        try:
            r = session.post(url, headers=auth_head)
        except Exception as exc:
            raise RuntimeError("couldn't open url") from exc
        return r.json()

    def get_data(self):
        url = f"https://api.notion.com/v1/databases/{os.environ['NOTION_DATABASE_ID']}/query"
        headers = {"Authorization": f"Bearer {os.environ['NOTION_TOKEN']}", "Notion-Version": "2021-08-16"}
        result_dict = self._load(url, headers)

        birthdays = []
        pr_birthdays_5d = []
        pr_birthdays = []

        hb_list_result = result_dict["results"]
        for birthday in hb_list_result:
            self.birthday_dict = self.get_values(birthday)

            if self.birthday_dict["date"] != "":
                if self.check_birthday(self.birthday_dict["date"]):
                    if self.birthday_dict["status"] != "Поздравление":
                        pr_birthdays.append(self.form_text(0))
                    else:
                        birthdays.append(self.form_text(1))
                elif self.check_birthday(self.birthday_dict["date"], 5):
                    pr_birthdays_5d.append(self.form_text(2))
        return birthdays + pr_birthdays + pr_birthdays_5d

    def check_birthday(self, birthday, difference=0):
        a = datetime.today() + timedelta(days=difference)
        dr = datetime.strptime(birthday, "%Y-%m-%d")
        return True if a.month == dr.month and a.day == dr.day else False

    def form_text(self, index):
        return (
            f"{self.message_day[index]} <b> {self.birthday_dict['fio']} </b>\n {self.birthday_dict['workplace']},"
            f" {self.birthday_dict['company']}\n Телефон: {self.birthday_dict['phone']}\n "
            f"Telegram: {self.birthday_dict['tg']}\n Email: {self.birthday_dict['email']}\n "
            f"{self.congrat_text[index]}\n {self.birthday_dict['notes']}\n "
            f"Ответственный: {self.birthday_dict['responsible']} "
        )

    def check_values(self, condition, end_part, end=""):
        if condition and condition[end_part]:
            return condition[end_part]
        return end

    def get_values(self, result):
        properties = result["properties"]
        return {
            "fio": properties["ФИО"]["title"][0]["text"]["content"],
            "date": self.check_values(properties["ДР"]["date"], "start"),
            "workplace": self.check_values(properties["Тип"]["select"], "name"),
            "company": self.check_values(properties["Компания"]["select"], "name"),
            "phone": self.check_values(properties["Телефон"], "phone_number"),
            "tg": self.check_values(properties["Telegram"], "url"),
            "email": self.check_values(properties["Email"], "email"),
            "status": self.check_values(properties["Статус для ДР"]["select"], "name", "Поздравление"),
            "responsible": properties["Ответственный"]["rollup"]["array"][0]["url"]
            if properties["Ответственный"]["rollup"]["array"] != []
            else "",
            "notes": properties["Заметки"]["rich_text"][0]["text"]["content"]
            if len(properties["Заметки"]["rich_text"]) > 0
            else "",
        }
