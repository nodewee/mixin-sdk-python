import uuid

from ..clients._requests import HttpRequest
from ..utils import get_conversation_id_of_two_users


class ConversationApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    @staticmethod
    def get_unique_id(user_id, recipient_id):
        """
        Get conversation id of single chat between two users, such as bot and user.
            Same as `common.utils.get_conversation_id_of_two_users`
        """
        return get_conversation_id_of_two_users(user_id, recipient_id)

    @staticmethod
    def generate_random_id():
        """
        Generate a random conversation id for group
        """
        return str(uuid.uuid4())

    def create(
        self, category: str, conversation_id: str, name: str, participants: list
    ):
        """
        To create a new group or to have a conversation with a user for the first time.

        The conversations you created are conversations
        between your bot/dApp and regular Mixin Messenger users.
        You cannot use the user's access_token to create them.
        Please use the bot/dApp's token to create conversations

        Parameters:
            - category: GROUP" or "CONTACT
            - conversation_id: Unique identifier.
                Can be got by `get_unique_id()` or `generate_random_id()` method
            - name: Group name, valid when category is 'GROUP', 512 characters at most
            - participants: Member list '[{ user_id: UUID }]', up to 256 people
        """
        body = {
            "category": category,
            "conversation_id": conversation_id,
            "name": name,
            "participants": participants,
        }

        return self._http.post("/conversations", body)

    def get_info(self, conversation_id: str):
        """
        Get conversation information by id
        """
        return self._http.get(f"/conversations/{conversation_id}")

    # TODO: manage groups
