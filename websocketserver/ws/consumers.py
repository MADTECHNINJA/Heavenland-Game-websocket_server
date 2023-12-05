from threading import Timer
from channels.layers import get_channel_layer
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.conf import settings
from websocketserver.api import business


def broadcast_message(data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "HL", {
            "type": "broadcast",
            "json": data,
        }
    )


def admin_broadcast(data: dict, end_task: bool = False):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "HL", {
            "type": "admin_broadcast",
            "end_task": end_task,
            "json": data,
        }
    )


class HLConsumer(JsonWebsocketConsumer):

    authenticated = False
    admin = False
    admin_ready_for_task = True

    def authenticate(self, token):
        if settings.UE4_SECRET != token:
            self.send_json({"error": "token is not valid"})
            return
        self.authenticated = True
        async_to_sync(self.channel_layer.group_add)("HL", self.channel_name)
        self.send_json({"info": "connected"})

    def authenticate_admin(self, token):
        if settings.ADMIN_SECRET != token:
            self.send_json({"error": "token is not valid"})
            return
        self.authenticated = True
        self.admin = True
        async_to_sync(self.channel_layer.group_add)("HL", self.channel_name)
        self.send_json({"info": "connected"})

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("HL", self.channel_name)

    def receive_json(self, content, **kwargs):
        if not self.authenticated:
            if content.get('action') == 'login' and content.get('token'):
                token = content.get('token')
                self.authenticate(token)
            if content.get('action') == 'admin_login' and content.get('token'):
                token = content.get('token')
                self.authenticate_admin(token)
            else:
                self.send_json({'error': "you need to authenticate first"})
        elif content.get('action') == 'broadcast':
            self.send_group_message(self.channel_name, content.get('data', {}), **kwargs)
        elif content.get('action') == 'admin' and self.admin:
            if self.admin_ready_for_task:
                self.administration(content.get('data', {}))
            else:
                self.send_json({"error": "task already in progress"})
        return

    def send_group_message(self, user_id, content, **kwargs):
        async_to_sync(self.channel_layer.group_send)(
            "HL",
            {
                "type": "broadcast",
                "json": {
                    "user_id": user_id,
                    "data": content
                },
            },
        )

    def broadcast(self, data):
        self.send_json(data['json'])

    def admin_broadcast(self, data):
        if not self.admin:
            return
        if data.get('end_task', False):
            self.admin_ready_for_task = True
        self.broadcast(data)

    def administration(self, data: dict):
        self.admin_ready_for_task = False
        if data.get('action') == 'render_thumbnail':
            Timer(interval=0, function=business.admin_render_building, args=[data]).start()
            return
        if data.get('action') == 'delete_thumbnail':
            Timer(interval=0, function=business.admin_delete_unused_building_thumbnails()).start()
            return
        if data.get('action') == 'migrate_chars':
            Timer(interval=0, function=business.migrate_char_models_to_envs()).start()
            return
