import asyncio


async def download_1():
    print(asyncio.get_event_loop().time())
    await asyncio.sleep(4)
    print("Task 1 completed")
    print(asyncio.get_event_loop().time())


async def download_2():
    print(asyncio.get_event_loop().time())
    await asyncio.sleep(5)
    print("Task 2 completed")
    print(asyncio.get_event_loop().time())

async def  download_3():
    print(asyncio.get_event_loop().time())
    await asyncio.sleep(4)   
    print("Task 3 completed") 
    print(asyncio.get_event_loop().time())



async def main():
    await asyncio.gather(
        download_1(),
        download_2(),
        download_3()
    )


asyncio.run(main())


# 1.First run download_1() -> hits await, control back to event loop
# 2.Run download_2()-> hits await control back to event loop
# 3. Run download_3()-> hits await control back to event loop