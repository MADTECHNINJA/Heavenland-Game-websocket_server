from websocketserver.heavenland.api import HeavenLandAPI
from websocketserver.heavenland.exceptions import JWTDecodeError


def game_login(username: str, password: str) -> dict:
    refresh_token, access_token, payload = HeavenLandAPI().game_login(username, password)
    user_id = payload.get('sub')
    return {
        "refresh_token": refresh_token,
        "access_token": access_token,
        "user_id": user_id
    }


def validate_heavenland_token(access_token: str) -> dict:
    try:
        valid_data = HeavenLandAPI().validate_token(access_token)
    except Exception:
        raise JWTDecodeError
    return valid_data


def get_inventory(access_token: str, user_id: str) -> dict:
    try:
        response = HeavenLandAPI().get_user_inventory(access_token, user_id)
    except Exception:
        raise JWTDecodeError
    return response


def add_to_inventory(access_token: str, user_id: str, item_id: int) -> dict:
    try:
        response = HeavenLandAPI().add_to_user_inventory(access_token, user_id, item_id)
    except Exception:
        raise JWTDecodeError
    return response


def remove_from_inventory(access_token: str, user_id: str, item_id: int) -> dict:
    try:
        response = HeavenLandAPI().remove_from_user_inventory(access_token, user_id, item_id)
    except Exception:
        raise JWTDecodeError
    return response


def list_assets(limit: int, offset: int) -> dict:
    try:
        print(limit, offset)
        response = HeavenLandAPI().get_game_assets(limit, offset)
    except Exception:
        raise JWTDecodeError
    return response
