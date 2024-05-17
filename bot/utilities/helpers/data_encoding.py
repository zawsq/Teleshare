import base64
import binascii
import json
from json.decoder import JSONDecodeError
from typing import Any


class DataValidationError(Exception):
    """
    Raised when an invalid or corrupted encoded data is received.
    """

    def __init__(self, data_link: str) -> None:
        super().__init__(f"Invalid data link: {data_link}")


class DataEncoder:
    """
    A class providing methods for encoding and decoding data or file links using JSON and Base64.
    """

    @staticmethod
    def encode_data(data_to_encode: Any) -> str:  # noqa: ANN401
        """
        Encode data to a Base64-encoded JSON string.

        Parameters:
            data_to_encode (Any): The data to be encoded.

        Returns:
            str: The Base64-encoded JSON string representing the data.
        """
        json_string = json.dumps(data_to_encode)
        base64_bytes = base64.b64encode(json_string.encode())
        return base64_bytes.decode()

    @staticmethod
    def decode_data(base64_string: str) -> Any:  # noqa: ANN401
        """
        Decode a Base64-encoded JSON string back to the original data.

        Parameters:
            base64_string (str): The Base64-encoded JSON string to be decoded.

        Returns:
            Any: Decoded data.

        Raises:
            DataValidationError: If the input data is invalid or corrupted.
        """
        try:
            base64_bytes = base64_string.encode()
            decoded_bytes = base64.b64decode(base64_bytes)
            return json.loads(decoded_bytes)
        except (JSONDecodeError, binascii.Error) as exc:
            raise DataValidationError(base64_string) from exc
