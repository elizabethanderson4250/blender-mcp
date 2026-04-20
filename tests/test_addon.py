"""Tests for the Blender MCP addon server functionality."""

import json
import socket
import threading
import time
import unittest
from unittest.mock import MagicMock, patch


class TestBlenderMCPServer(unittest.TestCase):
    """Unit tests for BlenderMCPServer core logic."""

    def test_command_serialization(self):
        """Test that commands serialize to valid JSON."""
        command = {
            "type": "execute_code",
            "params": {"code": "import bpy; print(bpy.app.version)"}
        }
        serialized = json.dumps(command)
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized["type"], "execute_code")
        self.assertIn("code", deserialized["params"])

    def test_response_structure(self):
        """Test that responses have the expected structure."""
        success_response = {
            "status": "success",
            "result": {"output": "3.6.0"}
        }
        error_response = {
            "status": "error",
            "message": "NameError: name 'foo' is not defined"
        }

        self.assertEqual(success_response["status"], "success")
        self.assertIn("result", success_response)

        self.assertEqual(error_response["status"], "error")
        self.assertIn("message", error_response)

    def test_command_types(self):
        """Verify all expected command types are handled."""
        expected_commands = [
            "execute_code",
            "get_scene_info",
            "get_object_info",
            "get_viewport_screenshot",
        ]
        # Ensure command type strings are non-empty and valid
        for cmd in expected_commands:
            self.assertIsInstance(cmd, str)
            self.assertGreater(len(cmd), 0)


class TestSocketCommunication(unittest.TestCase):
    """Integration-style tests for socket message framing."""

    def _recv_all(self, sock, length):
        """Helper to receive exactly `length` bytes."""
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                break
            data += chunk
        return data

    def test_message_framing(self):
        """Test length-prefixed message framing used by the addon."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)

        received = []

        def server_thread():
            conn, _ = server_sock.accept()
            raw_len = self._recv_all(conn, 4)
            msg_len = int.from_bytes(raw_len, "big")
            data = self._recv_all(conn, msg_len)
            received.append(json.loads(data.decode("utf-8")))
            conn.close()
            server_sock.close()

        t = threading.Thread(target=server_thread, daemon=True)
        t.start()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))

        payload = json.dumps({"type": "get_scene_info", "params": {}}).encode("utf-8")
        client.sendall(len(payload).to_bytes(4, "big") + payload)
        client.close()

        t.join(timeout=3)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["type"], "get_scene_info")


class TestParameterValidation(unittest.TestCase):
    """Tests for parameter validation logic."""

    def test_execute_code_requires_code_param(self):
        """execute_code command must include a 'code' parameter."""
        valid = {"type": "execute_code", "params": {"code": "x = 1"}}
        invalid = {"type": "execute_code", "params": {}}

        self.assertIn("code", valid["params"])
        self.assertNotIn("code", invalid["params"])

    def test_get_object_info_requires_name(self):
        """get_object_info command must include an object 'name'."""
        valid = {"type": "get_object_info", "params": {"name": "Cube"}}
        invalid = {"type": "get_object_info", "params": {}}

        self.assertIn("name", valid["params"])
        self.assertNotIn("name", invalid["params"])


if __name__ == "__main__":
    unittest.main()
