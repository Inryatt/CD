import asyncio
loop = asyncio.get_event_loop()

async def hello():
    print('Hello')
    await asyncio.sleep(3)
    print('World')

async def mainloop():
    t = []
    for _ in range(3):
        t.append(hello())
    await asyncio.gather(*t)

if __name__ == '__main__':
    loop.run_until_complete(mainloop())