import base64

from ..clients._requests import HttpRequest
from ..clients._sign import generate_ed25519_keypair


class UserApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    def get_me(self):
        """
        Get the current user's personal information.
        """
        return self._http.get("/me")

    def get_user(self, user_id: str):
        return self._http.get(f"/users/{user_id}")

    def get_users(self, user_ids: list):
        return self._http.post("/users/fetch", user_ids)

    def search_user(self, query: str):
        """
        Search user by Mixin ID or Phone Number.

        params:
            query: str, Mixin ID or Phone Number
        """
        return self._http.get("/search/" + query)

    def get_friends(self):
        """
        Obtaining the contact list of the user.
        The list contains users and bots.
        You can judge whether it is a bot user by whether there is an app field.
        """
        return self._http.get("/friends")

    def add_friend(self, user_id: str, alias_name: str = None):
        """
        Add a friend and set an alias
        """
        payload = {"action": "ADD", "user_id": user_id, "full_name": alias_name}
        return self._http.post("/relationships", payload)

    def delete_friend(self, user_id: str):
        """
        Delete a friend
        """
        payload = {"action": "REMOVE", "user_id": user_id}
        return self._http.post("/relationships", payload)

    def block_user(self, user_id: str):
        """Block a user"""
        payload = {"action": "BLOCK", "user_id": user_id}
        return self._http.post("/relationships", payload)

    def unblock_user(self, user_id: str):
        """Unblock a user"""
        payload = {"action": "UNBLOCK", "user_id": user_id}
        return self._http.post("/relationships", payload)

    def get_blocking_users(self):
        """Get the list of users that have been blocked"""
        return self._http.get("/blocking_users")

    def create_network_user(self):
        """Create a network user. Only application user can create network users."""

        pk, sk = generate_ed25519_keypair()
        pk_b64 = base64.b64encode(pk).decode()
        sk_b64 = base64.b64encode(sk).decode()

        payload = {
            "session_secret": pk_b64,
            "full_name": "A name",
        }
        r = self._http.post("/users", payload)

        r["keypair"] = {"public_key": pk_b64, "private_key": sk_b64}

        return r
