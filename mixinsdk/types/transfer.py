import decimal
from dataclasses import asdict, dataclass
from typing import Any, Dict

import dacite

from ..utils import parse_rfc3339_to_datetime


@dataclass
class TransferView:
    type: str
    amount: str
    asset_id: str
    counter_user_id: str
    created_at: str
    memo: str
    opponent_id: str
    snapshot_id: str
    trace_id: str

    def __post_init__(self):
        self.created_at_dt = parse_rfc3339_to_datetime(self.created_at)
        self.amount_decimal = decimal.Decimal(self.amount)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferView":
        return dacite.from_dict(cls, data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
