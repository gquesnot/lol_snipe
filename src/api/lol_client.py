import os
import random
import string
import subprocess
from base64 import b64encode
from time import sleep
from typing import Optional

import psutil
import urllib3

from src.enums.client_api_endpoints import ClientApiEndpoints
from src.enums.client_config import ClientConfig
from src.enums.lol_mode import LolMode
from src.utils.env_functions import load_env, get_env
from src.utils.session import Session

CLIENT_PROCESS_NAME = "LeagueClientUX"
CLIENT_HOST_PROCESS_NAME = "LeagueClient"
GAME_PROCESS_NAME = "League of Legends"
CLIENT_EXECUTABLE_PATH = "League of Legends\\LeagueClient.exe"
CLIENT_PBE_EXECUTABLE_PATH = "League of Legends (PBE)\\LeagueClient.exe"
GAME_CONFIG_PATH = "League of Legends\\Config\\game.cfg"
PERSISTED_SETTINGS_PATH = "League of Legends\\Config\\PersistedSettings.json"
KEY_CONFIG_PATH = "League of Legends\\Config\\input.ini"
GAME_API_PORT = 2999
ADDRESS = "127.0.0.1"


class ClientApi:
    session: Optional[Session] = None
    pid: int = -1
    summoner_id: Optional[int] = None

    def __init__(self, mode: LolMode = LolMode.NORMAL):
        load_env()
        self.mode = mode
        self.session = Session()
        self.default_league_path = get_env("DEFAULT_LEAGUE_PATH")
        self.lock_path = os.path.join(self.default_league_path,
                                      "League of Legends\\lockfile" if self.mode == LolMode.NORMAL else "League of Legends (PBE)\\lockfile")

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def init_api(self):
        self._wait_for_client_to_open()

    def _wait_for_client_to_open(self):
        self._ensure_client_is_open()
        print("Waiting for API to be ready...")
        while not self.is_api_ready():
            sleep(0.5)
        print("API is ready\n")
        print("Waiting for client to be available...")
        while not self.is_available():
            sleep(0.5)
        print("Client is available\n")

    def _ensure_client_is_open(self):
        if not self._client_is_open():
            print("Client is not open, opening...")
            self._kill_client()
            self._open_client()
        print("Client is open\n")
        self._wait_until(self._initialize_session_from_lock_file)

    def _client_is_open(self):
        for proc in psutil.process_iter():
            try:
                process_name = proc.name()
                if process_name == ClientConfig.CLIENT_HOST_PROCESS_NAME + '.exe':
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return -1

    def _kill_client(self):
        for process in ClientConfig.CLIENT_PROCESS_LIST:
            try:
                subprocess.Popen(f"taskkill /f /im {process}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                pass
        sleep(0.1)

    def _open_client(self):
        print('-- STARTING CLIENT --')
        executable_path = ClientConfig.CLIENT_EXECUTABLE_PATH if self.mode == ClientConfig.NORMAL_MODE else ClientConfig.CLIENT_PBE_EXECUTABLE_PATH
        subprocess.call([os.path.join(self.default_league_path, executable_path)])

    def _initialize_session_from_lock_file(self):
        if not os.path.isfile(self.lock_path):
            return False
        with open(self.lock_path, "r+") as fd:
            lock_data = fd.read().split(':')
        self.session.init(
            lock_data[4], ClientConfig.ADDRESS,
            lock_data[2],
            {
                'Authorization': 'Basic ' + b64encode(bytes("riot:{}".format(lock_data[3]), 'utf-8')).decode('ascii')
            }
        )
        self.pid = int(lock_data[1])
        return True

    def is_api_ready(self):

        try:
            r = self.session.request(*ClientApiEndpoints.LOGIN_SESSION)
            if r.status_code != 200:
                return False
            data = r.json()
            if data['state'] == 'SUCCEEDED' and data['summonerId'] is not None:
                self.summoner_id = data['summonerId']
                return True
            return False
        except Exception:
            return False

    def _wait_until(self, condition, sleep_time=0.5):
        while not condition():
            sleep(sleep_time)

    def get_online_friends(self):
        r = self.session.request(*ClientApiEndpoints.FRIENDS)
        return [
            friend for friend in r.json()
            if friend['availability'] not in ('offline', 'mobile')
        ]

    def get_game_status(self):
        r = self.session.request(*ClientApiEndpoints.GAMEFLOW_SESSION)
        return r.json()

    def send_lock_action(self, action_id, data):
        r = self.session.request(*ClientApiEndpoints.CHAMP_SELECT_LOCK_PICK + str(action_id) + '/complete', data=data)
        return r.json()

    def send_action(self, action_id, data):
        method, url = ClientApiEndpoints.CHAMP_SELECT_PICK
        url += str(action_id)
        return self.session.request(method, url, data=data)

    def get_flow(self):
        r = self.session.request(*ClientApiEndpoints.GAMEFLOW_PHASE)
        return r.json()

    def create_lobby(self, queue_id):
        r = self.session.request(*ClientApiEndpoints.LOBBY_CREATE_LOBBY, data={"queueId": queue_id})
        return r.json()

    def create_custom_lobby(self, map_id, team_size: int = 5, is_practice_tool=False):
        lobby_name = random.choice(string.ascii_lowercase) + str(random.randint(0, 1000))
        print(f"Creating lobby {lobby_name}")
        data = {
            "customGameLobby": {
                "configuration": {
                    "gameMode": "PRACTICETOOL" if is_practice_tool else "CLASSIC",
                    "gameMutator": "",
                    "gameServerRegion": "",
                    "mapId": map_id,
                    "mutators": {
                        "id": 1
                    },
                    "spectatorPolicy": "AllAllowed",
                    "teamSize": team_size
                },
                "lobbyName": lobby_name,
                "lobbyPassword": None,
            },
            "isCustom": True
        }
        r = self.session.request(*ClientApiEndpoints.LOBBY_CREATE_LOBBY, data=data)
        return r.json()

    def stop_queue(self):
        self.session.request(*ClientApiEndpoints.LOBBY_STOP_SEARCH)

    def quit_lobby(self):
        self.session.request(*ClientApiEndpoints.LOBBY_QUIT_LOBBY)

    def get_lobby_status(self):
        r = self.session.request(*ClientApiEndpoints.LOBBY_GET_LOBBY)
        return r.json()

    def create_aram_lobby(self):
        return self.create_lobby(450)

    def start_queue(self):
        self.session.request(*ClientApiEndpoints.LOBBY_SEARCH)

    def in_aram_lobby(self):
        try:
            return self.get_lobby_status()['gameConfig']['queueId'] == 450
        except Exception:
            return False

    def is_available(self):
        r = self.session.request(*ClientApiEndpoints.GAMEFLOW_AVAILABILITY)
        return r.json()['isAvailable']
