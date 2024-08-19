import asyncio

async def print_number(number):
    print(number)

async def main():
    # Create multiple tasks
    tasks = [asyncio.create_task(print_number(i)) for i in range(5)]
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

asyncio.run(main())
