import decimal
import uuid
from typing import Union

from ..clients._requests import HttpRequest


class TransferApi:
    def __init__(self, http: HttpRequest, get_encrypted_pin: callable):
        self._http = http
        self.get_encrypted_pin = get_encrypted_pin

    def read_by_trace_id(self, trace_id: str):
        """Read transfer by trace ID.
        This API is only for reading transfers,
        not deposits or withdrawals
        """
        return self._http.get(f"/transfers/trace/{trace_id}")

    def send_to_user(
        self,
        opponent_id: str,
        asset_id: str,
        amount: Union[str, float, decimal.Decimal],
        memo: str = "",
        trace_id: str = None,
    ):
        """Transfer to specific user.

        parmas:
            - opponent_id, *required*, user id of the receiver
            - asset_id, *required*
            - amount, *required*, e.g.: "0.01",
                supports up to 8 digits after the decimal point
            - memo, optional, maximally 140 characters
            - trace_id, optional, used to prevent duplicate payment.
                If not specified, a random UUID will be generated.
        """
        encrypted_pin = self.get_encrypted_pin()
        trace_id = trace_id if trace_id else str(uuid.uuid4())
        amount = amount if isinstance(amount, str) else format(amount, ".8f")
        body = {
            "asset_id": asset_id,
            "opponent_id": opponent_id,
            "amount": amount,
            "pin": encrypted_pin,
            "trace_id": trace_id,
            "memo": memo,
        }
        # TODO: pre-process error response
        return self._http.post("/transfers", body)

    # TODO TEST
    def send_to_mainnet_address(
        self,
        opponent_id,
        asset_id,
        amount: Union[str, float, decimal.Decimal],
        memo: str = "",
        trace_id: str = None,
    ):
        """Transfer to a specified mainnet address.

        params:
            - opponent_id, the mainnet address which you are transferring
            - amount, e.g.: "0.01", supports up to 8 digits after the decimal point
            - memo, Optional, maximally 140 characters
            - trace_id, Optional, used to prevent duplicate payment
        """

        encrypted_pin = self.get_encrypted_pin()
        trace_id = trace_id if trace_id else str(uuid.uuid4())
        amount = amount if isinstance(amount, str) else format(amount, ".8f")

        body = {
            "pin": encrypted_pin,
            "opponent_id": opponent_id,
            "asset_id": asset_id,
            "amount": f"{amount:.8f}",
            "memo": memo,
            "trace_id": trace_id,
        }
        return self._http.post("/transactions", body)

    # TODO TEST
    def send_to_multisig_address(
        self,
        user_ids,
        threshold,
        asset_id,
        amount: Union[str, float, decimal.Decimal],
        memo: str = "",
        trace_id: str = None,
    ):
        """Transfer to a Multi-signature Address

        params:
            - user_ids, list of receivers user id.
                identify the address which you are transferring
            - threshold, the number of signatures required to confirm the transaction
            - amount, e.g.: "0.01", supports up to 8 digits after the decimal point
            - memo, Optional, maximally 140 characters
            - trace_id, Optional, used to prevent duplicate payment
        """

        encrypted_pin = self.get_encrypted_pin()
        trace_id = trace_id if trace_id else str(uuid.uuid4())
        amount = amount if isinstance(amount, str) else format(amount, ".8f")

        body = {
            "pin": encrypted_pin,
            "opponent_multisig": {"receivers": user_ids, "threshold": threshold},
            "asset_id": asset_id,
            "amount": f"{amount:.8f}",
            "memo": memo,
            "trace_id": trace_id,
        }
        return self._http.post("/transactions", body)

    # TODO: offset, support for more types: datetime, unix timestamp
    def get_snapshots_list(
        self,
        offset: str,
        limit: int,
        order: str = None,
        asset_id: str = None,
        opponent_id: str = None,
        description: str = None,
    ):
        """Get the snapshots by several filters.

        Parameters:
            !opponent and destination, tag can't use together,
            both of them don't support order.

            - offset: *required*, pagination start time,
                e.g. `2020-12-12T12:12:12.999999999Z`.
            - limit: *required*, the number of results to return,
                pagination limit, maximally 500.
            - order: Order snapshots e.g. `ASC or DESC`.
            - asset_id: Optional, get transfers by asset.
            - opponent_id: Optional, get transfers by opponent (user or bot).
            - destination_id: Optional, get transfers by destination, only withdrawals.
        """
        params = {"offset": offset, "limit": limit}
        if order:
            params["order"] = order
        if asset_id:
            params["asset_id"] = asset_id
        if opponent_id:
            params["opponent_id"] = opponent_id
        if description:
            params["description"] = description

        return self._http.get("/snapshots", params)

    def get_snapshot(self, snapshot_id: str):
        """Get the snapshot of a user by snapshot id"""
        return self._http.get(f"/snapshots/{snapshot_id}")
