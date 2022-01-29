from asyncio import Queue
from typing import Any


class Resource:
    '''
    object representing resource that could be created in the future
    '''
    def __init__(self) -> None:
        self._resource = Queue()

    def get_nowait(self) -> Any:
        res = self._resource.get_nowait()
        self._resource.put_nowait(res)
        return res

    async def get(self) -> Any:
        res = await self._resource.get()
        self._resource.put_nowait(res)
        return res

    def put(self, value: Any):
        self._resource.put_nowait(value)