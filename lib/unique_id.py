import uuid
import hashlib


def generate_uuid():
    try:
        uuid_value = uuid.uuid4()
        assert uuid.UUID(str(uuid_value), version=4)
    except ValueError:
        uuid_value = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
    return uuid_value
