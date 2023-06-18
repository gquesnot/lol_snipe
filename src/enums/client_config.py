from enum import Enum

from src.utils.env_functions import get_env


class ClientConfig():
    ADDRESS = "127.0.0.1"
    CLIENT_PROCESS_NAME = "LeagueClientUX"
    CLIENT_HOST_PROCESS_NAME = "LeagueClient"
    GAME_PROCESS_NAME = "League of Legends"
    CLIENT_EXECUTABLE_PATH = "League of Legends\\LeagueClient.exe"
    CLIENT_PBE_EXECUTABLE_PATH = "League of Legends (PBE)\\LeagueClient.exe"
    NORMAL_MODE = "NORMAL"
    PBE_MODE = "PBE"
    CLIENT_PROCESS_LIST = ['LeagueClientUxRender.exe', 'LeagueClient.exe', 'LeagueClientUx.exe', 'RiotClientServices.exe']



