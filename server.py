import asyncio


class Storage:
    """Class for storing metrics in memory"""

    def __init__(self):
        # use the dictionary to store metrics
        self._data = {}

    def put(self, key, value, timestamp):
        if key not in self._data:
            self._data[key] = {}

        self._data[key][timestamp] = value

    def get(self, key):
        data = self._data

        # we return the necessary metric if it is not *
        if key != "*":
            data = {
                key: data.get(key, {})
            }

        # for simplicity, we store metrics in a regular dictionary and
        # sort it with each request, in a real application you should choose
        # a data structure
        result = {}
        for key, timestamp_data in data.items():
            result[key] = sorted(timestamp_data.items())

        return result


class ParseError(ValueError):
    pass


class Parser:
    """Class for implementing the protocol"""

    def encode(self, responses):
        """Convert server response to string for transmission to socket."""
        rows = []
        for response in responses:
            if not response:
                continue
            for key, values in response.items():
                for timestamp, value in values:
                    rows.append(f"{key} {value} {timestamp}")

        result = "ok\n"

        if rows:
            result += "\n".join(rows) + "\n"

        return result + "\n"

    def decode(self, data):
        """
        Command parsing for further execution.
        Returns a list of commands to execute.
        """
        parts = data.split("\n")
        commands = []
        for part in parts:
            if not part:
                continue

            try:
                method, params = part.strip().split(" ", 1)
                if method == "put":
                    key, value, timestamp = params.split()
                    commands.append(
                        (method, key, float(value), int(timestamp))
                    )
                elif method == "get":
                    key = params
                    commands.append(
                        (method, key)
                    )
                else:
                    raise ValueError("unknown method")
            except ValueError:
                raise ParseError("wrong command")

        return commands


class ExecutorError(Exception):
    pass


class Executor:
    """
    The Executor class implements the run method,
    which knows how to execute server commands.
    """
    def __init__(self, storage):
        self.storage = storage

    def run(self, method, *params):
        if method == "put":
            return self.storage.put(*params)
        elif method == "get":
            return self.storage.get(*params)
        else:
            raise ExecutorError("Unsupported method")


class EchoServerClientProtocol(asyncio.Protocol):
    """Class for implementing a server using asyncio."""

    # Note that storage is an attribute of the class.
    # The self.storage object for all instances of the EchoServerClientProtocol
    # class will be the same object for storing metrics.
    storage = Storage()

    def __init__(self):
        super().__init__()

        self.parser = Parser()
        self.executor = Executor(self.storage)
        self._buffer = b''

    def process_data(self, data):
        """Server input processing"""

        # parse messages using self.parser
        commands = self.parser.decode(data)

        # execute commands and save execution results
        responses = []
        for command in commands:
            resp = self.executor.run(*command)
            responses.append(resp)

        # convert commands to string
        return self.parser.encode(responses)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        """
        The data_received method is called
        when data is received on the socket.
        """
        self._buffer += data
        try:
            decoded_data = self._buffer.decode()
        except UnicodeDecodeError:
            return

        # waiting for data if the command is not completed by the \n character
        if not decoded_data.endswith('\n'):
            return

        self._buffer = b''

        try:
            # process the received request
            resp = self.process_data(decoded_data)
        except (ParseError, ExecutorError) as err:
            # form an error in case of expected exceptions
            self.transport.write(f"error\n{err}\n\n".encode())
            return

        # form a successful response
        self.transport.write(resp.encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        EchoServerClientProtocol,
        host, port
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    # run server for testing
    run_server('127.0.0.1', 8888)
