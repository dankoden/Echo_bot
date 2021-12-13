from unittest import TestCase
from unittest.mock import Mock, patch, ANY

from vk_api.bot_longpoll import  VkBotMessageEvent

from generate_ticket import generate_ticket
from vk_bot import Bot



class MyTest(TestCase):
    """
    test for vk_bot
    """
    ROW_EVENT = {'type': 'message_new',
                 'object': {'message':
                                {'date': 1637166213,
                                 'from_id': 673207418,
                                 'id': 148, 'out': 0,
                                 'peer_id': 673207418,
                                 'text': 'привет',
                                 'attachments': [],
                                 'conversation_message_id': 139,
                                 'fwd_messages': [],
                                 'important': False,
                                 'is_hidden': False,
                                 'random_id': 0},
                            'client_info':
                                {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'open_photo', 'callback', 'intent_subscribe', 'intent_unsubscribe'],
                                 'keyboard': True,
                                 'inline_keyboard': True,
                                 'carousel': True,
                                 'lang_id': 0}},
                 'group_id': 208609334,
                 'event_id': 'ef6da18f7f419fffac227282faf14e2e07dd87a4'}


    def test_ok_run(self):
        """
            test for function run
            """
        count = 5
        event = [{}]*count  # [{},{}.....]
        long_poller_mock = Mock(return_value=event)
        long_poller_mock_listen = Mock()
        long_poller_mock_listen.listen = long_poller_mock
        with patch("vk_bot.vk_api.VkApi"):
            with patch("vk_bot.VkBotLongPoll",return_value = long_poller_mock_listen):
                bot = Bot("","")
                bot.on_event = Mock()
                bot.run()
                bot.on_event.assert_any_call({})
                assert bot.on_event.call_count == count

    def test_ok_event(self):
        """
        test for function on_event
        """
        event = VkBotMessageEvent(raw = self.ROW_EVENT)
        with patch("vk_bot.vk_api.VkApi"):
            with patch("vk_bot.VkBotLongPoll"):
                bot = Bot("","")
                bot.api.messages.send = Mock()
                bot.on_event(event)

        bot.api.messages.send.assert_called_once_with(message = self.ROW_EVENT["object"]["message"]["text"],
                             peer_id = self.ROW_EVENT["object"]["message"]["peer_id"],
                             random_id = ANY)



    def test_ok_generate_ticket(self):
        """
        Test for function generate_ticket
        """
        with open("Files/logo_ticket.png","rb") as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()

        with patch("requests.get",return_value=avatar_mock):
            tickets_file = generate_ticket("Ihor", "i.ok.danko@gmail.com")

        with open("Files/tickets-example.png","rb") as expected_file:
            expected_bytes = expected_file.read()
        assert tickets_file.read() == expected_bytes




