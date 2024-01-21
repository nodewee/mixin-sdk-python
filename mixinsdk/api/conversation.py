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

    def read(self, conversation_id: str):
        """
        Get conversation information by id
        """
        return self._http.get(f"/conversations/{conversation_id}")

    def create(
        self,
        category: str,
        conversation_id: str,
        name: str = None,
        participants: list = None,
    ):
        """
        To create a new group or to have a conversation with a user for the first time.

        The conversations you created are conversations
        between your bot/dApp and regular Mixin Messenger users.
        You cannot use the user's access_token to create them.
        Please use the bot/dApp's token to create conversations

        Parameters:
            - category: "GROUP" or "CONTACT"
            - conversation_id: Unique identifier.
                Can be got by `get_unique_id()` or `generate_random_id()` method
            - name: Group name, valid when category is 'GROUP', 512 characters at most
            - participants: Member list '[{ user_id: UUID }]', up to 256 people
        """
        payload = {
            "category": category,
            "conversation_id": conversation_id,
        }
        if name:
            payload["name"] = name
        if participants:
            payload["participants"] = participants

        return self._http.post("/conversations", payload)

    def create_single(self, bot_id, user_id):
        """Create conversation between bot and user"""
        conv_id = get_conversation_id_of_two_users(bot_id, user_id)
        return self.create("CONTACT", conv_id, participants = [{"user_id": user_id}])

    def create_group(self, list_of_user_id: list, group_name: str = None):
        """
        Parameters:
            - list_of_user_id, user id of participants, up to 256 people
        """
        participants = []
        for user_id in list_of_user_id:
            participants.append({"user_id": user_id})
        if not group_name:
            group_name = "New Group"
        conv_id = self.generate_random_id()
        return self.create("GROUP", conv_id, group_name, participants)

    def update_name(self, conversation_id: str, name: str):
        """
        Parameter:
            - name: New group name, 512 characters at most
        """
        payload = {"name": name}
        return self._http.post(f"/conversations/{conversation_id}", payload)

    def update_announcement(self, conversation_id: str, announcement: str):
        """
        Parameter:
            - name: Group Announcements, 1024 characters at most.
        """
        payload = {"announcement": announcement}
        return self._http.post(f"/conversations/{conversation_id}", payload)

    def add_participants(self, conversation_id: str, list_of_user_id: list):
        """If you are the owner or admin of this group conversation, you can add other users to the group by calling this API."""
        payload = []
        for user_id in list_of_user_id:
            d = {"user_id": user_id}
            payload.append(d)
        return self._http.post(
            f"/conversations/{conversation_id}/participants/ADD", payload
        )

    def remove_participants(self, conversation_id: str, list_of_user_id: list):
        """If you are the owner or admin of this group conversation, you can remove a member from the group."""
        payload = []
        for user_id in list_of_user_id:
            d = {"user_id": user_id}
            payload.append(d)
        return self._http.post(
            f"/conversations/{conversation_id}/participants/REMOVE", payload
        )

    def add_admins(self, conversation_id: str, list_of_user_id: list):
        """Set admin privileges"""
        payload = []
        for user_id in list_of_user_id:
            d = {"user_id": user_id, "role": "ADMIN"}
            payload.append(d)
        return self._http.post(
            f"/conversations/{conversation_id}/participants/ROLE", payload
        )

    def remove_admins(self, conversation_id: str, list_of_user_id: list):
        """Revoke admin privileges"""
        payload = []
        for user_id in list_of_user_id:
            d = {"user_id": user_id, "role": ""}
            payload.append(d)
        return self._http.post(
            f"/conversations/{conversation_id}/participants/ROLE", payload
        )
