import asyncio
import logging


class HTTPServer:
    """
    A simple HTTP server class.

    Parameters:
    host (str): The host to bind the server to.
    port (int): The port to bind the server to.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handle an incoming HTTP request.

        Parameters:
        reader (asyncio.StreamReader): The reader object to read the request from.
        writer (asyncio.StreamWriter): The writer object to write the response to.
        """
        try:
            request = await reader.read(1024)
            if not request:
                return

            self.logger.info("Received request: %s", request.decode().splitlines()[0])

            path = request.decode().split(" ")[1]
            if path == "/":
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    "\r\n"
                    "<!DOCTYPE html>"
                    "<html lang='en'>"
                    "<head>"
                    "<meta charset='UTF-8'>"
                    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                    "<title>Teleshare</title>"
                    "<style>"
                    "body { font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; }"  # noqa: E501
                    ".container { text-align: center; }"
                    "a { text-decoration: none; color: #007bff; }"
                    "</style>"
                    "</head>"
                    "<body>"
                    "<div class='container'>"
                    "<h1>Teleshare</h1>"
                    "<p><a href='https://github.com/zawsq/Teleshare' target='_blank'>Visit the Teleshare GitHub Repository</a></p>"  # noqa: E501
                    "</div>"
                    "</body>"
                    "</html>"
                )
            else:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"

            writer.write(response.encode())
            await writer.drain()
        except ConnectionResetError:
            self.logger.info("Connection lost")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run_server(self) -> None:
        """
        Run the HTTP server.
        """
        server = await asyncio.start_server(self.handle_request, self.host, self.port)
        self.logger.info("Serving on %s:%d", self.host, self.port)
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = HTTPServer("127.0.0.1", 8080)
    asyncio.run(server.run_server())
