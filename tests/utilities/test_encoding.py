from bot.utilities.helpers import Encoding


def test_encoding() -> None:
    file_ids = [1, 2, 3, 4, 5]
    encoded_string = Encoding.encode(file_ids)
    assert encoded_string == "WzEsIDIsIDMsIDQsIDVd"
    decoded_ids = Encoding.decode(encoded_string)
    assert decoded_ids == file_ids
