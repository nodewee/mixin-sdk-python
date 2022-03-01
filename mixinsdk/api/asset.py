from ..clients._requests import HttpRequest


class AssetApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    def get_assets_list(self):
        """
        Get the asset list of current user.
        """
        return self._http.get("/assets")

    def get_asset(self, asset_id):
        """
        Read asset by asset ID.
            the ASSETS:READ permission is required.
        """
        return self._http.get("/assets/" + asset_id)

    def get_fee(self, asset_id):
        """
        Get the specified asset's fee.
        """
        return self._http.get("/assets/" + asset_id + "/fee")

    def get_fiat_exchange_rates(self):
        """
        Returns a list of all fiat exchange rates based on US Dollar.
        """
        return self._http.get("/fiats")
