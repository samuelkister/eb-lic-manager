import unittest
from eb_lic_manager.flex_lm.config import Server


class TestServer(unittest.TestCase):
    def testGoodParameters(self):
        host_computer = "host_computer"
        host_port = "1324"
        host_id = "host_id"

        server = Server(host_computer, host_id)
        self.assertEqual(server.host, host_computer)
        self.assertEqual(server.host_id, host_id)

        server = Server(host_computer, host_id, host_port)
        self.assertEqual(server.host, host_computer)
        self.assertEqual(server.host_id, host_id)
        self.assertEqual(server.port, int(host_port))

        server = Server(host_computer, host_id, host_port, "PRIMARY_IS_MASTER")
        self.assertEqual(server.host, host_computer)
        self.assertEqual(server.host_id, host_id)
        self.assertEqual(server.port, int(host_port))

        server = Server(host_computer, host_id, host_port, "PRIMARY_IS_MASTER", HEARTBAT_INTERVAL="132")
        self.assertEqual(server.host, host_computer)
        self.assertEqual(server.host_id, host_id)
        self.assertEqual(server.port, int(host_port))

        server = Server(host_computer, host_id, host_port, HEARTBAT_INTERVAL="132")
        self.assertEqual(server.host, host_computer)
        self.assertEqual(server.host_id, host_id)
        self.assertEqual(server.port, int(host_port))

    def testWrongParameters(self):
        wrong_parameters = [
            ((), "No Parameters"),
            (("host_computer",), "Only one parameter"),
            (("host", "id", "port"), "No numerical port"),
        ]

        for params, info in wrong_parameters:
            with self.subTest(infos=info):
                with self.assertRaises(Exception):
                    server = Server(*params)