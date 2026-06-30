"""
Finite State Machine state groups, used both by user and admin handlers.
"""
from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    waiting_query = State()


class AddAnimeStates(StatesGroup):
    poster = State()
    name = State()
    genre = State()
    episodes_count = State()
    dubbed_by = State()
    language = State()
    code = State()
    channel_link = State()
    confirm = State()


class DeleteAnimeStates(StatesGroup):
    waiting_identifier = State()


class AddEpisodeStates(StatesGroup):
    waiting_anime_code = State()
    waiting_episode_number = State()
    waiting_video = State()


class ChannelManageStates(StatesGroup):
    waiting_channel_id = State()
    waiting_channel_to_remove = State()


class VipManageStates(StatesGroup):
    waiting_add_id = State()
    waiting_remove_id = State()


class BroadcastStates(StatesGroup):
    waiting_content = State()
    waiting_confirm = State()


class ChannelPostStates(StatesGroup):
    waiting_anime_code = State()
    waiting_channel_choice = State()
