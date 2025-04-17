import asyncio
import websockets
import websockets.asyncio
import websockets.asyncio.server

from game import handle

async def main():
    async with websockets.asyncio.server.serve(handle, "0.0.0.0", 8080) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())