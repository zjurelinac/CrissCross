import asyncio
import json
import websockets


class WS:
    """Websocket wrapper class, abstracts common operations"""
    def __init__(self, websocket, close_handler=None):
        self.ws = websocket
        self.close_handler = close_handler

    async def send(self, data):
        return await self.ws.send(json.dumps(data))

    async def recv(self):
        msg = await self.ws.recv()
        return json.loads(msg)

    async def serve(self, handler):
        print('Starting to serve...')
        while True:
            try:
                request = await asyncio.wait_for(self.recv(), timeout=20)
            except asyncio.TimeoutError:
                # No data in 20 seconds, check the connection.
                try:
                    pong_waiter = await self.ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    # No response to ping in 10 seconds, disconnect.
                    break
            except websockets.ConnectionClosed:
                break
            else:
                try:
                    await handler(request, self)
                except Exception as exc:
                    import traceback
                    traceback.print_exc()
                    await self.send({'error': {'type': exc.__class__.__name__, 'description': str(exc)}})

        if self.close_handler is not None:
            await self.close_handler()
