"""TCP client for the raspi-gpio GPIO API at 192.168.0.142:5555."""

import json
import socket

DEFAULT_HOST = "192.168.0.142"
DEFAULT_PORT = 5555
DEFAULT_TIMEOUT = 5.0


class GpioClient:
    """Wraps TCP socket communication with the raspi-gpio API server."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
                 timeout: float = DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _send(self, cmd: str) -> str:
        """Send a command and return the raw response string."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect((self.host, self.port))
            s.sendall((cmd + "\n").encode())
            data = s.recv(4096).decode().strip()
            return data
        finally:
            s.close()

    def send_json(self, cmd: str):
        """Send a command and parse the response as JSON."""
        data = self._send(cmd)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    def ping(self) -> bool:
        """Check if the GPIO API is responsive."""
        try:
            resp = self._send("ping")
            return "pong" in resp
        except Exception:
            return False

    def read_all(self) -> dict:
        """Read all GPIO pin states. Returns {pin: value} dict."""
        return self.send_json("read_all")

    def read(self, pin: int):
        """Read a single GPIO pin state."""
        return self.send_json(f"read {pin}")

    def write(self, pin: int, value: int) -> str:
        """Set a GPIO pin as OUTPUT and drive HIGH (1) or LOW (0)."""
        return self._send(f"write {pin} {value}")

    def reset(self, pin: int) -> str:
        """Reset a GPIO pin back to INPUT with pull-up."""
        return self._send(f"reset {pin}")

    def reset_all(self) -> str:
        """Reset all GPIO pins to INPUT with pull-up."""
        return self._send("reset_all")

    def setup_inputs(self) -> str:
        """Configure all monitor pins as INPUT with pull-up."""
        return self._send("setup_inputs")

    def setup_outputs(self) -> str:
        """Configure drive pins as OUTPUT."""
        return self._send("setup_outputs")
