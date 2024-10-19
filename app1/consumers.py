from channels.generic.websocket import AsyncWebsocketConsumer
import json

# Store a dictionary to keep track of players per room
rooms = {}

class GameRoom(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        
        # Initialize room in the dictionary if not already created
        if self.room_group_name not in rooms:
            rooms[self.room_group_name] = {
                "players": 0  # Keep track of the number of connected players
            }

        # Check player count
        if rooms[self.room_group_name]["players"] < 2:
            # Add player to the room
            rooms[self.room_group_name]["players"] += 1
            self.player_number = rooms[self.room_group_name]["players"]

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Inform the player of their role (player 1 or player 2)
            await self.send(text_data=json.dumps({
                'type': 'player_role',
                'player_number': self.player_number
            }))
        else:
            # If two players are already connected, reject additional connections
            await self.close()

    async def disconnect(self, close_code):
        # Decrease player count on disconnect
        if rooms[self.room_group_name]["players"] > 0:
            rooms[self.room_group_name]["players"] -= 1

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast message to the other player
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
