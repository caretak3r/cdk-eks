import unittest
import uuid


class TestUUID(unittest.TestCase):
    def test_generate_uuid(self):
        uuid_value = uuid.uuid4()
        self.assertIsInstance(uuid_value, uuid.UUID)
        self.assertEqual(uuid_value.version, 4)


if __name__ == "__main__":
    unittest.main()
