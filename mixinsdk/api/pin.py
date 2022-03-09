from ..clients._requests import HttpRequest


class PinApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    def verify(self, encrypted_pin):
        """
        Verify a user's PIN, is valid or not. For example,
        you can verify PIN before updating it.
        Notice the iterator of the pin will increment also.

        params:
        - encrypted_pin: use .encrypt() method to make it
        """
        body = {"pin": encrypted_pin}

        return self._http.post("/pin/verify", body)

    def update(self, old_pin, new_pin):
        """
        Change the PIN of the user, or setup a new PIN if it is not set yet.

        params:
        - old_pin: Encrypted old PIN or empty for setup a new PIN
        - new_pin": Encrypted new PIN

        PIN is used to manage user's addresses, assets and etc.
        There's no default PIN for a Mixin Network user (except APP).
        To set an initial PIN, set old_pin to an empty string.
        """
        body = {"old_pin": old_pin, "pin": new_pin}

        return self._http.post("/pin/update", body)

    def get_error_logs(self, limit: int = 10, offset: str = None):
        """Query the user PIN error log records,
        based on which developers can remind
        the user of the number of errors within 24 hours.

        params:
        - limit, Pagination limit, maximally 100.
        - offset, Pagination start time, e.g. `2020-12-12T12:12:12.999999999Z`
        """
        # - category, Log type, please set to `PIN_INCORRECT`

        params = {"limit": limit, "offset": offset, "category": "PIN_INCORRECT"}
        return self._http.get("/logs", params)
