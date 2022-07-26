# CHANGELOG

### unreleased v0.1.6-dev

New

- Skeleton of the code structure
  > Reinventing the wheel for ease of use and readability.
- Support for Ed25519 and RS512 for signature and encryption
- Implemented HTTP client, and Blaze(Websocket) client
  - Support for client initialize from keystore, user OAuth token and without auth
  - Blaze client, support for multi-threading to process messages
- Implemented some Mixin API: User, PIN, Asset, Transfer, Message, Network APIs
- Message data structures packer
- Messenger schema packer: sharing schema,
