# CHANGELOG

### ver 0.2.4

- change license to MIT
- add file data structure packer
- add some mixin safe supports: payment uri, snapshots list (#4)
- fix and add mixin uri schema: sharing uri, user uri
- add encryption support for sending message
- update examples:
  - add blaze client example (#4)
  - add safe example (#5)
  - improve examples structure
- update docs:
  - update README.md and improve CONTRIBUTING.md
  - include updated records in CHANGELOG.md.


### v0.2.1

Fix

- Fix mistake of blaze client reconnect
- Fix URL path in /api/network

New

- Support for parsing encrypted messages
- Add more APIs of conversation

Change

- Change class names and property names

### unreleased v0.1.6

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
