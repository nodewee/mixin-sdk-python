from ..clients._requests import HttpRequest


class NetworkApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    def get_chains_list(self):
        """
        Get the list of all public chains supported by Mixin,
        no permission needed.
        """
        return self._http.get("/network/chains")

    def get_asset(self, asset_id: str):
        """Get public information of an asset,
        no permission needed.
        """
        return self._http.get("/network/assets/" + asset_id)

    def get_top_assets_list(self, kind: str = "ALL"):
        """
        Read top valuable assets of Mixin Network,
        no permission needed.

        params:
            kind: "ALL", "NORMAL", "BARREN", "ALL" by default
        """
        params = {}
        if kind:
            params["kind"] = kind
        return self._http.get("/network", params)

    def search_asset_by_symbol(self, query: str, kind: str = "ALL"):
        """Search for popular assets by symbol or name.
                This API only returns assets with icons or prices.
                no permission needed.

        Parameters:
            - query: *required*, symbol (such as "BTC") or name (such as "Bitcoin")
            - kind: optional, "ALL", "NORMAL", "BARREN", "ALL" by default
        """
        params = {}
        if kind:
            params["kind"] = kind
        return self._http.get(f"/network/assets/search/{query}", params)

    # TODO: offset support more types, and convert with utc time
    def get_snapshots_list(
        self, offset=None, limit: int = None, asset_id: str = None, order: str = None
    ):
        """
        Get a list of snapshot records public information,
        which including transfers, deposits, withdrawals, etc.,
        no permission needed.

        Parameters:
            - offset: optional, pagination start time,
                RFC3339Nano format, e.g. `2020-12-12T12:12:12.999999999Z`.
            - limit: optional, pagination per page data limit,
                500 by default, maximally 500.
            - asset_id: optional, transfer records of a certain asset.
            - order: optional, Sort in `ASC` or `DESC` order, `DESC` by default.
        """
        params = {}
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        if asset_id:
            params["asset_id"] = asset_id
        if order:
            params["order"] = order

        return self._http.get("/network/snapshots", params)

    def get_snapshot(self, snapshot_id):
        """
        Read snapshot details by id.
        No permission needed. If given permission "SNAPSHOT:READ",
        details will include the private fields like `user_id`,
        `opponent_id`, `trace_id` and `data`.
        """
        return self._http.get("/network/snapshots/" + snapshot_id)

    def get_historical_price(self, asset_id: str, offset=None):
        """
        Get the historical price of a given asset.
        No permission needed.

        Parameters:
        - asset_id, *required*
        - offset, optional, specify query time in RFC3339Nano format,
            e.g. `2020-12-12T12:12:12.999999999Z`
        """
        params = {"asset": asset_id}
        if offset:
            params["offset"] = offset
        return self._http.get("/network/ticker", params)

    def get_pending_deposits_list(
        self,
        offset=None,
        limit: int = None,
        asset_id: str = None,
        destination: str = None,
    ):
        """Get public network-wide deposit records.
            No permission needed.

        Parameters:
            - offset: optional, pagination start time,
            RFC3339Nano format, e.g. `2020-12-12T12:12:12.999999999Z`.
            - limit: optional, pagination per page data limit,
            500 by default, maximally 500.
            - asset_id: optional, transfer records of a certain asset.
            - destination: Optional, get the records of
                pending deposits for a certain address.
            - tag: Optional, mark the pending deposit records of an address,
                used with destination.
        """
        params = {}
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        if asset_id:
            params["asset_id"] = asset_id
        if destination:
            params["destination"] = destination

        return self._http.get("/external/transactions", params)
