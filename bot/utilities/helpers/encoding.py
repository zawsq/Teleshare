import base64
import json


class Encoding:
    """
    A class providing methods for encoding and decoding lists of file IDs using JSON and Base64.
    """

    @staticmethod
    def encode(file_ids: list[int]) -> str:
        """
        Encode a list of file IDs to a Base64-encoded JSON string.

        Parameters:
            file_ids (list[int]): A list of file IDs to be encoded.

        Returns:
            str: The Base64-encoded JSON string representing the file IDs.
        """
        json_string = json.dumps(file_ids)
        base64_bytes = base64.b64encode(json_string.encode())
        return base64_bytes.decode()

    @staticmethod
    def decode(base64_string: str) -> list[int]:
        """
        Decode a Base64-encoded JSON string back to a list of file IDs.

        Parameters:
            base64_string (str): The Base64-encoded JSON string to be decoded.

        Returns:
            list[int]: The decoded list of file IDs.

        Format:
            expected output:
                [channel id, message ids here]
        """
        base64_bytes = base64_string.encode()
        decoded_bytes = base64.b64decode(base64_bytes)
        return json.loads(decoded_bytes)
