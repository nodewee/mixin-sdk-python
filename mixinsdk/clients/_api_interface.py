from ..api import (AssetApi, ConversationApi, MessageApi, NetworkApi, PinApi,
                   TransferApi, UserApi)


class ApiInterface:
    def __init__(
        self,
        user_api: UserApi = None,
        message_api: MessageApi = None,
        asset_api: AssetApi = None,
        pin_api: PinApi = None,
        conversation_api: ConversationApi = None,
        transfer_api: TransferApi = None,
        network_api: NetworkApi = None,
    ):
        if user_api:
            self.user = user_api
        if message_api:
            self.message = message_api
        if asset_api:
            self.asset = asset_api
        if pin_api:
            self.pin = pin_api
        if conversation_api:
            self.conversation = conversation_api
        if transfer_api:
            self.transfer = transfer_api
        if network_api:
            self.network = network_api
