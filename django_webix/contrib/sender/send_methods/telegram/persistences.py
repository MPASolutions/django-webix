
from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, Dict, Any, Tuple, Optional

from telegram.ext import BasePersistence
from telegram.utils.types import ConversationDict

from django_webix.contrib.sender.models import TelegramPersistence


class ReMapKeys:
    @staticmethod
    def encode(mapping):
        _result = []
        for k, v in mapping.items():
            if isinstance(v, dict):
                v = ReMapKeys.encode(v)
            _result.append({'key': k, 'value': v})
        return _result

    @staticmethod
    def decode(mapping):
        _result = {}
        for i in mapping:
            if isinstance(i['value'], list) and all(isinstance(n, dict) for n in i['value']):
                i['value'] = ReMapKeys.decode(i['value'])
            if isinstance(i['key'], list) and all(isinstance(n, int) for n in i['key']):
                i['key'] = tuple(i['key'])
            _result[i['key']] = i['value']
        return _result


class DatabaseTelegramPersistence(BasePersistence):
    def __init__(
        self,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
    ):
        super().__init__(
            store_user_data=store_user_data,
            store_chat_data=store_chat_data,
            store_bot_data=store_bot_data,
        )
        self._user_data = None
        self._chat_data = None
        self._bot_data = None
        self._conversations = None

        self._user_data = defaultdict(
            dict,
            TelegramPersistence.objects.filter(typology='user_data').values_list('data', flat=True).first() or {}
        )
        self._chat_data = defaultdict(
            dict,
            TelegramPersistence.objects.filter(typology='chat_data').values_list('data', flat=True).first() or {}
        )
        self._bot_data = defaultdict(
            dict,
            TelegramPersistence.objects.filter(typology='bot_data').values_list('data', flat=True).first() or {}
        )
        self._conversations = defaultdict(
            dict,
            ReMapKeys.decode(TelegramPersistence.objects.filter(
                typology='conversations'
            ).values_list('data', flat=True).first() or {})
        )

    def get_user_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the user_data if stored, or an empty
        ``defaultdict(dict)``.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self._user_data:
            pass
        else:
            self._user_data = defaultdict(dict)
        return deepcopy(self._user_data)  # type: ignore[arg-type]

    def update_user_data(self, user_id: int, data: Dict) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data` [user_id].
        """
        if self._user_data is None:
            self._user_data = defaultdict(dict)
        if self._user_data.get(user_id) == data:
            return
        self._user_data[user_id] = data
        TelegramPersistence.objects.update_or_create(typology='user_data', defaults={"data": self._user_data})

    def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        """ "Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the chat_data if stored, or an empty
        ``defaultdict(dict)``.

        Returns:
            :obj:`defaultdict`: The restored chat data.
        """
        if self._chat_data:
            pass
        else:
            self._chat_data = defaultdict(dict)
        return deepcopy(self._chat_data)  # type: ignore[arg-type]

    def update_chat_data(self, chat_id: int, data: Dict) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """
        if self._chat_data is None:
            self._chat_data = defaultdict(dict)
        if self._chat_data.get(chat_id) == data:
            return
        self._chat_data[chat_id] = data
        TelegramPersistence.objects.update_or_create(typology='chat_data', defaults={"data": self._chat_data})

    def get_bot_data(self) -> Dict[Any, Any]:
        """ "Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the bot_data if stored, or an empty
        :obj:`dict`.

        Returns:
            :obj:`dict`: The restored bot data.
        """
        if self._bot_data:
            pass
        else:
            self._bot_data = {}
        return deepcopy(self._bot_data)  # type: ignore[arg-type]

    def update_bot_data(self, data: Dict) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.bot_data` .
        """
        if self._bot_data == data:
            return
        self._bot_data = data.copy()
        TelegramPersistence.objects.update_or_create(typology='bot_data', defaults={"data": self._bot_data})

    def get_conversations(self, name: str) -> ConversationDict:
        """ "Will be called by :class:`telegram.ext.Dispatcher` when a
        :class:`telegram.ext.ConversationHandler` is added if
        :attr:`telegram.ext.ConversationHandler.persistent` is :obj:`True`.
        It should return the conversations for the handler with `name` or an empty :obj:`dict`

        Args:
            name (:obj:`str`): The handlers name.

        Returns:
            :obj:`dict`: The restored conversations for the handler.
        """

        if self._conversations:
            pass
        else:
            self._conversations = {}
        return self._conversations.get(name, {}).copy()  # type: ignore[union-attr]

    def update_conversation(
        self, name: str, key: Tuple[int, ...], new_state: Optional[object]
    ) -> None:
        """Will be called when a :attr:`telegram.ext.ConversationHandler.update_state`
        is called. This allows the storage of the new state in the persistence.

        Args:
            name (:obj:`str`): The handler's name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """
        if not self._conversations:
            self._conversations = {}
        if self._conversations.setdefault(name, {}).get(key) == new_state:
            return
        self._conversations[name][key] = new_state
        if new_state is None:
            del self._conversations[name][key]

        TelegramPersistence.objects.update_or_create(
            typology='conversations',
            defaults={"data": ReMapKeys.encode(self._conversations)}
        )
