from mixinsdk.types import message

response_of_sent_single_message = {
    "data": {
        "type": "message",
        "representative_id": "",
        "quote_message_id": "",
        "conversation_id": "xx-xx-xx-xx-xx",
        "user_id": "xx-xx-xx-xx-xx",
        "session_id": "xx-xx-xx-xx-xx",
        "message_id": "xx-xx-xx-xx-xx",
        "category": "PLAIN_TEXT",
        "data": "SGVsbG8sIHdvcmxkIQ==",
        "data_base64": "SGVsbG8sIHdvcmxkIQ",
        "status": "",
        "source": "CREATE_MESSAGE",
        "silent": False,
        "created_at": "2022-02-12T02:39:10.672507091Z",
        "updated_at": "2022-02-12T02:39:10.672507091Z",
    }
}


def test_show_message():
    mv = message.MessageView.from_dict(response_of_sent_single_message["data"])
    print("decoded message data:", mv.data_decoded)
    print("message struct:", mv.data_struct)
    print("created_at:", mv.created_at)
