from dataclasses import dataclass
from typing import Optional, Union

from database.base import db


@dataclass
class VkAudio:
    id: int
    access_key: str
    ads: dict
    artist: str
    duration: int
    date: int
    is_explicit: bool
    is_focus_track: bool
    is_licensed: bool
    owner_id: int
    short_videos_allowed: bool
    stories_allowed: bool
    stories_cover_allowed: bool
    title: str
    track_code: str
    url: str
    album: Optional[dict] = None
    album_id: Optional[int] = None
    content_restricted: Optional[int] = None
    featured_artists: Optional[list] = None
    genre_id: Optional[int] = None
    lyrics_id: Optional[int] = None
    main_artists: Optional[Union[dict, list]] = None
    no_search: Optional[int] = None
    subtitle: Optional[str] = None

    def db_update(self, filter_dict, upsert=True):
        db['vk_music'].find_one_and_update(
            filter=filter_dict,
            update={'$set': self.__dict__},
            upsert=upsert
        )

    @classmethod
    def db_find_one(cls, filter_dict):
        project = {
            '_id': 0
        }
        data = db['vk_music'].find_one(filter_dict, project)
        if not data:
            return None
        return cls(**data)
