import os.path
import logging

import vk_api
from vk_api.bot_longpoll import VkBotEventType,VkBotLongPoll

import handlers
import settings

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

class UserState():
    """
    Состояние пользователя внутри сценария.
    """
    def __init__(self,scenario_name,step_name,context = None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}




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
        self.user_states = dict()



    def run(self):
        """
        run bot
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception("Ошибка в оброботчике событий")

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
        if user_id in self.user_states:
            # continue scenario
            text_to_send = self.continue_scenario(user_id,text =text)

        else:
            # search scenario
            for intent in settings.INITENTS:
                log.debug(f"User gets intent - {intent}")
                if any(token in text.lower() for token in intent["tokens"]):
                    if intent["answer"]:
                        text_to_send = intent["answer"]
                    else:
                        text_to_send = self.run_scenario(intent["scenario"],user_id)
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER

        self.api.messages.send(message=text_to_send,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id,
                               )
    def run_scenario(self, scenario_name,user_id):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario["first_step"]
        step = scenario["steps"][first_step]
        text_to_send = step["text"]
        self.user_states[user_id] = UserState(scenario_name = scenario_name,step_name= first_step)
        return text_to_send


    def continue_scenario(self,user_id,text):
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]["steps"]
        step = steps[state.step_name]

        handler = getattr(handlers, step["handler"])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step["next_step"]]
            text_to_send = next_step["text"].format(**state.context)
            if next_step["next_step"]:
            # switch to next step
                state.step_name = step["next_step"]
            else:
                # finish scenario
                self.user_states.pop(user_id)
                log.info(f"Зарегистрировали пользователя с данными {state.context}")

        else:
            # retry current step
            text_to_send = step["failure_text"].format(**state.context)



        return text_to_send



if __name__ == "__main__":
    config_logging()
    bot = Bot(ID_GROUP, TOKEN)
    bot.run()
