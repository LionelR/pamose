import unittest

import pamose


class PamoseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = pamose.app.test_client()

    def test_index(self):
        rv = self.app.get('/')
        self.assertIn('Welcome to PAssive MOnitoring SErver', rv.data.decode())


if __name__ == '__main__':
    unittest.main()
