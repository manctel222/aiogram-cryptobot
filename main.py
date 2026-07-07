import asyncio
import aiohttp
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from handlers.routes import router
from bases.database import init_db, get_active_alarms, deactivate_alarm

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)

async def crypto_price_checker(bot: Bot):
    await asyncio.sleep(2)
    while True:
        try:
            active_alarms = get_active_alarms()
            if active_alarms:
                async with aiohttp.ClientSession() as session:
                    prices = {}
                    for coin in ["BTC", "ETH"]:
                        async with session.get(f"https://api.coinbase.com/v2/prices/{coin}-USD/spot") as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                prices[coin] = float(data["data"]["amount"])

                    for alarm_id, user_id, coin, target_price, condition in active_alarms:
                        current_price = prices.get(coin)
                        if not current_price:
                            continue
                            
                        is_triggered = False
                        if condition == "above" and current_price >= target_price:
                            is_triggered = True
                        elif condition == "below" and current_price <= target_price:
                            is_triggered = True
                            
                        if is_triggered:
                            direction = "вырос выше" if condition == "above" else "упал ниже"
                            try:
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=f"🚨 *КРИПТО-БУДИЛЬНИК СРАБОТАЛ!*\n\n"
                                         f"🪙 Монета: *{coin}*\n"
                                         f"📈 Текущая цена: *${current_price:,.2f}*\n"
                                         f"Курс {direction} вашего лимита *${target_price:,.2f}*.",
                                    parse_mode="Markdown"
                                )
                                deactivate_alarm(alarm_id)
                            except Exception as tg_err:
                                print(f"Пользователь {user_id} заблокировал бота: {tg_err}")
                                deactivate_alarm(alarm_id)

        except Exception as e:
            print(f"Ошибка в фоновом мониторинге: {e}")
            
        await asyncio.sleep(60)



async def main():
    init_db() 

    bot = Bot(token=TOKEN)

    asyncio.create_task(crypto_price_checker(bot))

    print("Бот запущен...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())