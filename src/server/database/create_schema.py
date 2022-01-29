from tortoise import Tortoise, run_async
from connect_to_database import connectToDatabase


async def main():
    await connectToDatabase()
    await Tortoise.generate_schemas()
if __name__ == '__main__':
    run_async(main())