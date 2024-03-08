import asyncio
from aiohttp import ClientSession, http_websocket

async def my_callback(msg):
    print("I am call back: " + msg)


class WebPubSubClient:

    def __init__(self) -> None:
        self.url = "ws://localhost:8765"
        self.connected = False
        self.ack_map = {}
        self._ack_id = 0
        self.handlers = []

    async def listen(self):
        while self.connected:
            message: http_websocket.WSMessage = await self.socket.receive()
            print(f"client receive message: {message}")
            if message.type == http_websocket.WSMsgType.TEXT:
                ack_id = int(message.data)
                self.ack_map[ack_id].set()
                for handler in self.handlers:
                    asyncio.create_task(handler(message.data))

    def set_call_back(self, handler):
        self.handlers.append(handler)

    @property
    def next_ack_id(self):
        self._ack_id += 1
        return self._ack_id

    async def open(self):
        self.seesion = ClientSession()
        self.socket = await self.seesion.ws_connect(self.url)
        asyncio.create_task(self.listen())

        self.connected = True

    async def send(self, num):
        print(num)
        ack_id = self.next_ack_id
        await self.socket.send_str(str(ack_id))
        self.ack_map[ack_id] = asyncio.Event()
        await self.ack_map[ack_id].wait()
        self.ack_map.pop(ack_id)

    async def close(self):
        await self.socket.close()
        await self.seesion.close()
        self.connected = False
        self._ack_id = 0


async def main():
    client = WebPubSubClient()
    await client.open()
    client.set_call_back(my_callback)
    await asyncio.gather(*[asyncio.create_task(client.send(i)) for i in range(3)])
    await client.close()


asyncio.run(main())
