"""
Handler - функция , которая принимает на вход текст(текст входящего сообщения ) и context (dict) а возвращает bool:
True если шаг пройден ,False если данные введены неверно
"""
import re
re_name = re.compile(r"^[\w+\s\-]{3,40}$")

def handler_name(text,context):
    match = re.match(re_name,text)
    if match:
        context["name"] = text
        return True
    else:
        return False

def handle_email(text,context = None):
    match = re.search(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+',text)
    if match is not None:
        context["email"] = match.group()
        return True
    else:
        return False



