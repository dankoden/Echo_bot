from settingsloc import TOKEN,ID_GROUP
TOKEN = TOKEN
ID_GROUP = ID_GROUP
# greate your TOKEN and ID_GROUP

INITENTS = [
        {
        "name":"Дата проведения",
        "tokens":("когда","сколько","дата","дату"),
        "scenario":None,
        "answer":"Конференция проходит 15-го Апреля. Регистрация доступна с 12 числа"},

        {"name":"Место проведения",
        "tokens":("где","Место","Локация","Метро","Адрес"),
        "scenario":None,
        "answer":"Конференция будет проведена по адресу: г.Одесса ул. Лиманская 3"},

        {"name":"Cколько стоит",
        "tokens":("денег","сколько","дорого","дешево","гривен"),
        "scenario":None,
        "answer":"Это вообще не дорого , я уверена что вы сможете себе позволить"},

        {
        "name":"Регистрация",
        "tokens":("регистр","добав"),
        "scenario":"Registration",
        "answer":None
        }
        ]
SCENARIOS = {
        "Registration":{
                "first_step":"step_1",
                "steps":{
                        "step_1":{
                                "text":"Чтобы зарегистрироватся введите ваше имя. Оно будет написано на бейджике",
                                "failure_text":"Попробуйте еще раз ,имя должно состоять минимум из 3 символов и начинатся с заглавной буквы",
                                "handler":"handler_name",
                                "next_step":"step_2"
                         },
                        "step_2":{
                                "text":"Введите почту, мы отправим на нее все данные",
                                "failure_text":"Попробуйте еще раз ,во введенном адресе ошибка , попробуйте еще раз",
                                "handler":"handle_email",
                                "next_step":"step_3"
                        },
                        "step_3":{
                                "text":"Спасибо за регистрацию {name}. Мы отправим вам ниже билет. И продублируем всю информацию на почту"
                                       " почту {email} все данные",
                                "image":"generate_ticket_handler",
                                "failure_text":None,
                                "handler":None,
                                "next_step":None
                        }
                }
        }
}

DEFAULT_ANSWER = "Незнаю как ответить на это сообщение," \
                 "могу вам предложить регистрацию на мероприятие"
DB_CONFIG = dict(
    provider="postgres",
    user = "postgres" ,
    host = "localhost",
    database = "vk_chat_bot"
)