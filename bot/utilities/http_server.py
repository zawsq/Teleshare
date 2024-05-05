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
        request = await reader.readline()
        rq = f"Received request: {request.decode()}"
        self.logger.info(rq)
        writer.write(b"HTTP/1.1 200 OK\r\n")
        writer.write(b"Content-type: text/html\r\n")
        writer.write(b"\r\n")
        writer.write(b"<html><body>Hello, World!</body></html>")

        try:
            await writer.drain()
        except ConnectionResetError:
            self.logger.info("Connection Lost")
        writer.close()

    async def run_server(self) -> None:
        """
        Run the HTTP server.
        """
        server = await asyncio.start_server(self.handle_request, self.host, self.port)
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    server = HTTPServer("127.0.0.1", 8080)
    asyncio.run(server.run_server())
