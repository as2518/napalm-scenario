import unittest
from router import Router

class TestRouter(unittest.TestCase):
    def setUp(self):
        router = Router(
        hostname    = 'router1',
        model       = 'model1',
        os          = 'junos',
        ipaddress   = '192.168.0.1',
        username    = 'user1',
        password    = 'passwrod1')

    def test_open(self):
        expected = 1
        actual = 2
        self.assertEqual(expected, actual)
    
    def test_close(self):
        expected = 1
        actual = 2
        self.assertEqual(expected, actual)

    def test_commit(self):
        expected = 1
        actual = 2
        self.assertEqual(expected, actual)

    def test_compare_config(self):
        expected = 1
        actual = 2
        self.assertEqual(expected, actual)

    def test_check_hostname(self):
        expected = 1
        actual = 2
        self.assertEqual(expected, actual)

    def test_load_config(self):
        expected = 1
        actual = 2
        self.assertEqual(expected, actual)


    def tearDown(self):
        pass

if __name__ == "__main__":
        unittest.main()