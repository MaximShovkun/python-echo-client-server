import socket
import time


class ClientError(Exception):
    """General class of client exceptions"""
    pass


class ClientSocketError(ClientError):
    """Exception thrown by client on network error"""
    pass


class ClientProtocolError(ClientError):
    """Exception thrown by client on protocol error"""
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        # class encapsulates socket creation
        # create a client socket, remember the object socket in self
        self.host = host
        self.port = port
        try:
            self.connection = socket.create_connection((host, port), timeout)
        except socket.error as err:
            raise ClientSocketError("error create connection", err)

    def _read(self):
        """Method for reading server response"""
        data = b""
        # accumulate the buffer until we meet "\n\n" at the end of the command
        while not data.endswith(b"\n\n"):
            try:
                data += self.connection.recv(1024)
            except socket.error as err:
                raise ClientSocketError("error recv data", err)

        # convert bytes to str objects for further work
        decoded_data = data.decode()

        status, payload = decoded_data.split("\n", 1)
        payload = payload.strip()

        # if an error - throw an exception ClientError
        if status == "error":
            raise ClientProtocolError(payload)

        return payload

    def put(self, key, value, timestamp=None):
        timestamp = timestamp or int(time.time())

        # send put command request
        try:
            self.connection.sendall(
                f"put {key} {value} {timestamp}\n".encode()
            )
        except socket.error as err:
            raise ClientSocketError("error send data", err)

        # parsing the answer
        self._read()

    def get(self, key):
        # form and send get command request
        try:
            self.connection.sendall(
                f"get {key}\n".encode()
            )
        except socket.error as err:
            raise ClientSocketError("error send data", err)

        # read the answer
        payload = self._read()

        data = {}
        if payload == "":
            return data

        # parsing the answer for the get command
        for row in payload.split("\n"):
            key, value, timestamp = row.split()
            if key not in data:
                data[key] = []
            data[key].append((int(timestamp), float(value)))

        return data

    def close(self):
        try:
            self.connection.close()
        except socket.error as err:
            raise ClientSocketError("error close connection", err)


def _main():
    # client for testing
    client = Client("127.0.0.1", 8888, timeout=5)
    client.put("test", 0.5, timestamp=1)
    client.put("test", 2.0, timestamp=2)
    client.put("test", 0.5, timestamp=3)
    client.put("load", 3, timestamp=4)
    client.put("load", 4, timestamp=5)
    print(client.get("load"))

    client.close()


if __name__ == "__main__":
    _main()
