from dataclasses import dataclass
from database.base import db


@dataclass
class VkAuth:
    token: str
    user_id: str
    client_id: int
    timestamp: int

    def db_update(self, upsert=True):
        db['vk_auth'].find_one_and_update(
            filter={'client_id': self.client_id},
            update={'$set': self.__dict__},
            upsert=upsert
        )

    @classmethod
    def db_find_one(cls, client_id):
        find = {
            'client_id': client_id
        }
        project = {
            '_id': 0
        }
        data = db['vk_auth'].find_one(find, project)
        if not data:
            return None
        return cls(**data)
