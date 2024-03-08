#!/usr/bin/env python

import asyncio
from websockets import serve


async def send(websocket):
    async for message in websocket:
        print(f"server receive message: {message}")
        await websocket.send(message)


async def main():
    async with serve(send, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
