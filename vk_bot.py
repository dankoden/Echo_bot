import os.path
import logging

import requests
import vk_api
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotEventType,VkBotLongPoll

import handlers
import settings
from models import Registration, UserState

try:
    from settings import TOKEN,ID_GROUP
except ImportError:
    exit("cp your ID_GROUP and TOKEN from your vk api")

import random
def config_logging():
    """
    Config logger
    :return: None
    """
    global log
    log = logging.getLogger("bot")
    log.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("bot_logging.log",mode="w")

    formater_stream = logging.Formatter("%(asctime)s %(levelname)s %(message)s",datefmt="%d-%m-%Y %H:%M")
    formater_file = logging.Formatter("%(asctime)s %(levelname)s %(message)s",datefmt="%d-%m-%Y %H:%M")

    stream_handler.setFormatter(formater_stream)
    file_handler.setFormatter(formater_file)
    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)


class Bot():
    """
    Echo bot
    use Python 3.9
    """
    ROW_EVENT = {
        'type': 'message_typing_state',
        'object': {'state': 'typing', 'from_id': 673207418, 'to_id': -208609334},
        'group_id': 208609334,
        'event_id': '0f29fe489577eeee72ffb729cc01c3b092c7f084'
    }
    def __init__(self,id_group,token):
        """

        :param id_group: id group vk.com
        :param token: secret token
        """
        self.id_group = id_group
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.long_poller = VkBotLongPoll(self.vk,group_id=self.id_group)
        self.api = self.vk.get_api()



    def run(self):
        """
        run bot
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception("Ошибка в оброботчике событий")
    @db_session
    def on_event(self,event):
        """
        send message if it is text
        :param event:
        :return None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug("Мы еще не научились работать с этими событиями %s",event.type)
            return
        user_id = event.message.peer_id
        text = event.message.text
        state = UserState.get(user_id=str(user_id))
        if state is not None:
            # continue scenario
            self.continue_scenario(text =text,state=state,user_id=user_id)

        else:
            # search scenario
            for intent in settings.INITENTS:
                log.debug(f"User gets intent - {intent}")
                if any(token in text.lower() for token in intent["tokens"]):
                    if intent["answer"]:
                        self.send_text(intent["answer"], user_id)
                    else:
                        self.run_scenario(intent["scenario"],user_id,text)
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER,user_id)

    def send_text(self,text,user_id):
        """
        send only text
        used in send_step

        """
        self.api.messages.send(message=text,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id,
                               )
    def send_image(self,image,user_id):
        """
        send image to messages
        used in send_step
        """
        upload_url = self.api.photos.getMessagesUploadServer()["upload_url"]
        upload_data = requests.post(url=upload_url,files={"photo":("image.png",image,"image/png")}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)

        owner_id = image_data[0]["owner_id"]
        media_id = image_data[0]["id"]
        attachment = f"photo{owner_id}_{media_id}"

        self.api.messages.send(attachment=attachment,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id,
                               )
        log.info("Отправили билет")

    def send_step(self,step,user_id,text,context):
        """
        we send a message to the user through this function, it will determine whether
        it is necessary to send the text itself or a text with a picture

        """
        if "text" in step:
            self.send_text(step["text"].format(**context),user_id)
        if "image" in step:
            handler = getattr(handlers,step["image"])
            image = handler(context)
            self.send_image(image,user_id)


    def run_scenario(self, scenario_name,user_id,text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario["first_step"]
        step = scenario["steps"][first_step]
        self.send_step(step , user_id,text,context = {})
        UserState(user_id = str(user_id),scenario_name = scenario_name,step_name= first_step,context = {})



    def continue_scenario(self,text,state,user_id):
        steps = settings.SCENARIOS[state.scenario_name]["steps"]
        step = steps[state.step_name]

        handler = getattr(handlers, step["handler"])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step["next_step"]]
            self.send_step(next_step,user_id,text,state.context)
            if next_step["next_step"]:
            # switch to next step
                state.step_name = step["next_step"]
            else:
                # finish scenario
                state.delete()
                Registration(name = state.context["name"],email = state.context["email"])
                log.info(f"Зарегистрировали пользователя с данными {state.context}")

        else:
            # retry current step
            self.send_text(step["failure_text"].format(**state.context), user_id)



if __name__ == "__main__":
    config_logging()
    bot = Bot(ID_GROUP, TOKEN)
    bot.run()
