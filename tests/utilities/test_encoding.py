from bot.utilities.helpers import DataEncoder


def test_data_encoder() -> None:
    file_ids = [1, 2, 3, 4, 5]
    encoded_string = DataEncoder.encode_data(file_ids)
    assert encoded_string == "WzEsIDIsIDMsIDQsIDVd"
    decoded_ids = DataEncoder.decode_data(encoded_string)
    assert decoded_ids == file_ids


def test_codex_decoder() -> None:
    backup_channel = -1002136107017
    base64_string_batch = "Z2V0LTU3NzIzMDM5NzY0MTc5Mi01ODQyNDUzNTAzOTA5MTE"
    base64_string_solo = "Z2V0LTM1Mzc1NDA0NTc3NzAwMQ"
    expected_batch = [576, 577, 578, 579, 580, 581, 582, 583]
    expected_solo = [353]

    assert DataEncoder.codex_decode(base64_string_batch, backup_channel) == expected_batch
    assert DataEncoder.codex_decode(base64_string_solo, backup_channel) == expected_solo
