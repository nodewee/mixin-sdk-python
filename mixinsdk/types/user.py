class UserSession:
    def __init__(self, user_id=None, session_id=None, publick_key=None) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.publick_key = publick_key


class UserProfile:
    def __init__(
        self,
        user_id: str,
        mixin_number: str = "",
        name: str = "",
        avatar_url: str = "",
        is_app: bool = False,
    ):
        self.user_id = user_id
        self.mixin_number = mixin_number
        self.name = name
        self.avatar_url = avatar_url
        self.is_app = is_app
