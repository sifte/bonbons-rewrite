import asyncio

from helpers.bot import Bonbons

bot = Bonbons()


async def main() -> None:
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
