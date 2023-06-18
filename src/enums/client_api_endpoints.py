from enum import Enum


class ClientApiEndpoints():
    LOGIN_SESSION = ("GET", "/lol-login/v1/session")

    MATCHMAKING_ACCEPT = ("POST", "/lol-matchmaking/v1/ready-check/accept")

    GAMEFLOW_SESSION = ("GET", "/lol-gameflow/v1/session")
    GAMEFLOW_PHASE = ("GET", "/lol-gameflow/v1/gameflow-phase")
    GAMEFLOW_AVAILABILITY = ("GET", "/lol-gameflow/v1/availability")

    CHAMP_SELECT_LOCK_PICK = ("POST", "/lol-champ-select/v1/session/actions/")
    CHAMP_SELECT_PICK = ("PATCH", "/lol-champ-select/v1/session/actions/")
    CHAMP_SELECT_SESSION = ("GET", "/lol-champ-select/v1/session")
    CHAMP_SELECT_PICKABLE_CHAMPIONS = ("GET", "/lol-champ-select/v1/pickable-champions")
    CHAMP_SELECT_MY_SELECTION = ("PATCH", "/lol-champ-select/v1/session/my-selection")
    CHAMP_SELECT_CURRENT_CHAMPION = ("GET", "/lol-champ-select/v1/current-champion")

    LOBBY_CUSTOM_GAMES = ("GET", "/lol-lobby/v1/custom-games")
    LOBBY_CREATE_LOBBY = ("POST", "/lol-lobby/v2/lobby")
    LOBBY_QUIT_LOBBY = ("DELETE", "/lol-lobby/v2/lobby")
    LOBBY_GET_LOBBY = ("GET", "/lol-lobby/v2/lobby")
    LOBBY_ADD_BOTS = ("POST", "/lol-lobby/v1/lobby/custom/bots")
    LOBBY_SEARCH = ("POST", "/lol-lobby/v2/lobby/matchmaking/search")
    LOBBY_STOP_SEARCH = ("DELETE", "/lol-lobby/v2/lobby/matchmaking/search")
    LOBBY_SWITCH_TEAM = ("POST", "/lol-lobby/v1/lobby/custom/switch-teams")
    LOBBY_START_CUSTOM = ("POST", "/lol-lobby/v1/lobby/custom/start-champ-select")

    CURRENT_SUMMONER = ("GET", "/lol-summoner/v1/current-summoner")

    HONOR_PLAYER = ("POST", "/lol-honor-v2/v1/honor-player")

    KILL_UX = ("POST", "/riotclient/kill-ux")

    FRIENDS = ("GET", "/lol-chat/v1/friends")
