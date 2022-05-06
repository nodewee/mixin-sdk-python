# Mixin SDK for Python (Unofficial)

This is the [Mixin Network](https://mixin.one) SDK for Python.

## Notice

Referring to existing projects, redesign the code structure to improve ease of use and readability.

Based on:

- <https://github.com/includeleec/mixin-python3-sdk>
- <https://github.com/learnforpractice/mixin-python>

Runtime support: Python 3.9

**It is still in development, please do not use it in production environment.**

## Progress

- [x] Support for Ed25519 and RS512 for signature and encryption
- [x] Support for client initialize from keystore, user OAuth token and without auth
- [x] HTTP Client
- [x] Blaze(Websocket) Client
  - [x] Support for multi-threading to process messages
- [x] User API
- [ ] User Data Types
- [x] PIN API
- [x] Asset API
- [ ] Asset and Chain Data Types
- [x] Transfer API
- [ ] Transfer, Transaction and Snapshot Data Types
- [x] Network API
- [ ] Conversation API
- [x] Message API
- [x] Message Data Types
- [ ] Circles API
- [ ] Sharing Bots
- [ ] Messenger Schema Data Types
- [ ] Upload Album
- [ ] Withdrawal API
- [ ] Multi-Signature API
- [ ] Collectibles API
- [ ] Mainnet RPC API and Client

## Getting started

1. Clone the repository, or download code.

2. Set up and activate virtual environment, like this:

```bash
cd mixin-sdk-python-main
python3.9 -m venv env
. env/bin/activate
```

3. Install dependencies:

`python3.9 -m pip install -r requirements.txt`

4. Than see "examples" folder, and run the example.

## Contributing

Thanks for taking the time to contribute! Welcome to pull requests and open issues to improve the code and the documentation. The project need your help.✨

## References

- <https://developers.mixin.one/docs/api>
- <https://github.com/MixinNetwork/bot-api-go-client/>
