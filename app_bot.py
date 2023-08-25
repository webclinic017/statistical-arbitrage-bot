from bot import Bot

if __name__ == '__main__':
    bot = Bot()
    bot.set_sandbox_mode(False)
    bot.load_markets()

    bot.show_all_prices_update(False)
    bot.show_last_price_update(False)
    bot.show_pairs_update(False)
    bot.show_positions_update(False)
    bot.show_trades(True)

    bot.set_base_currency('USDT')
    bot.set_percent_size(10)  # or bot.set_fixed_size(50)
    bot.set_leverage(10)
    bot.run()
