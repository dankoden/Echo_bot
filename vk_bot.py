import os.path
import logging
import vk_api
from vk_api.bot_longpoll import VkBotEventType,VkBotLongPoll
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

    def on_event(self,event):
        """
        send message if it is text
        :param event:
        :return None
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.info("Отправляем сообщение назад")
            self.api.messages.send(message=event.message.text,
                                    random_id=random.randint(0, 2 ** 20),
                                    peer_id=event.message.peer_id,
                                    )
        else:
            log.debug("Мы еще не научились работать с этими событиями %s",event.type)



if __name__ == "__main__":
    config_logging()
    bot = Bot(ID_GROUP, TOKEN)
    bot.run()
