""""
Ensure that you have inserted the api key and secret in .env file
"""


from bot import Bot

if __name__ == '__main__':
    bot = Bot()
    bot.set_sandbox_mode(is_testnet=False, is_fake_orders=False)
    bot.load_markets()

    bot.show_all_prices_update(False)
    bot.show_last_price_update(False)
    bot.show_pairs_update(False)
    bot.show_positions_update(False)
    bot.show_trades(True)

    bot.set_base_currency('USDT')

    bot.set_percent_size(25)  # 2 to 5 percent is recommended
    # or
    # bot.set_fixed_size(100)

    bot.set_leverage(8)  # 20 maximum because some limitation
    bot.run()
