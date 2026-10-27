import logging

import states
from aiogram import Bot, Dispatcher, executor, types
from db_bot import *
from aiogram.dispatcher import FSMContext
from btn import *
from states import BotStates
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN,parse_mode='HTML')
dp = Dispatcher(bot,storage=MemoryStorage())
kurs_rub = 140
kurs_usd = 12650
# Start command handler
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    check = await check_user(user_id)
    get_contact = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_button = types.KeyboardButton('📞 Raqamni yuborish', request_contact=True)
    get_contact.add(contact_button)
    if check is None:
        caption = "<b>Telefon raqamingizni pastdagi tugmani bosib yuboring</b>"
        await bot.send_message(chat_id=message.from_user.id, text=caption, parse_mode="HTML", reply_markup=get_contact)
    else:
        caption = "<b>TestPay</b> - telegram tarmog`idagi yirik\nvalyuta ayirboshlash sistemasi"
        await bot.send_message(chat_id=message.from_user.id, text=caption, parse_mode="HTML", reply_markup=menu)


# Help command handler
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply(
        "I can do the following:\n/start - Welcome message\n/help - List of commands\nAnd I can echo any message you send!")


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def get_user_phone(message: types.Message):
    phone = message.contact.phone_number
    user_id = str(message.from_user.id)
    await add_user(user_id, phone)
    caption = "<b>TestPay</b> - telegram tarmog`idagi yirik\nvalyuta ayirboshlash sistemasi"
    await bot.send_message(chat_id=message.from_user.id, text=caption, parse_mode="HTML", reply_markup=menu)


@dp.message_handler(text="📮 Hisob to'ldirish")
async def fill_in(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Hisobingizga pul solmoqchi bo'lgan Kontorani bosing:",
                           reply_markup=hisob_toldirish)

@dp.message_handler(text="🇺🇿 1XBET UZB")
async def fill_uzb(message: types.Message):
    data = await check_card_informations(user_id=str(message.from_user.id))
    if data[1] is not None:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>Summani kiriting (E'tibor bering kiritish valyutasi - UZS):</b>",
                               reply_markup=back_menu
                               )
        await BotStates.fill_uzb.set()
    else:
        await message.answer("Avval <b>Hisob raqamlar</b> bo'limida id raqam bilan karta raqamingizni kiriting")


@dp.message_handler(text="↪️ Bekor qilish", state='*')
async def cancel_func(message: types.Message, state:FSMContext):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id, text="Bosh menyu", reply_markup=menu)
    await state.finish()
@dp.message_handler(state=BotStates.fill_uzb)
async def fill_sum(message: types.Message, state:FSMContext):
    sum = message.text
    if sum.isdigit():
        caption = f"<b>Berish:</b> {sum} 🇺🇿 UZS\n<b>Olish:</b> {sum} 🇺🇿 UZS"
        await bot.send_message(chat_id=message.from_user.id,text=caption)
        await state.finish()
    else:
        await message.answer("Siz son kiritmadingiz!\nQaytadan kiriting:")

@dp.message_handler(text="🇷🇺 1XBET RUB")
async def fill_rub(message: types.Message):
    data = await check_card_informations(user_id=str(message.from_user.id))
    if data[3] is not None:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>Summani kiriting (E'tibor bering kiritish valyutasi - RUB):</b>",
                               reply_markup=back_menu
                               )
        await BotStates.fill_rub.set()
    else:
        await message.answer("Avval <b>Hisob raqamlar</b> bo'limida id raqam bilan karta raqamingizni kiriting")
@dp.message_handler(state=BotStates.fill_rub)
async def fill_sum(message: types.Message, state:FSMContext):
    rub = message.text
    if rub.isdigit():
        final_value = int(rub)*kurs_rub
        caption = f"<b>Berish:</b> {final_value} 🇺🇿 UZS\n<b>Olish:</b> {rub} 🇷🇺 RUB"
        await bot.send_message(chat_id=message.from_user.id,text=caption)
        await state.finish()
    else:
        await message.answer("Siz son kiritmadingiz\nQayta kiriting:")


@dp.message_handler(text="🇺🇸 1XBET USD")
async def fill_usd(message: types.Message):
    data = await check_card_informations(user_id=str(message.from_user.id))
    if data[2] is not None:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>Summani kiriting (E'tibor bering kiritish valyutasi - USD):</b>",
                               reply_markup=back_menu
                               )
        await BotStates.fill_usd.set()
    else:
        await message.answer("Avval <b>Hisob raqamlar</b> bo'limida id raqam bilan karta raqamingizni kiriting")

@dp.message_handler(state=BotStates.fill_usd)
async def fill_sum(message: types.Message, state:FSMContext):
    usd = message.text
    if usd.isdigit():
        final_value = int(usd)*kurs_usd
        caption = f"<b>Berish:</b> {final_value} 🇺🇿 UZS\n<b>Olish:</b> {usd} 🇺🇸 USD"
        await bot.send_message(chat_id=message.from_user.id,text=caption)
        await state.finish()
    else:
        await message.answer("Siz son kiritmadingiz\nQaytadan kiriting:")

@dp.message_handler(text="🔙 Bosh menyu",state='*')
async def back_menus(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id, text="Bosh menyu", reply_markup=menu)



###




from main import *


@dp.message_handler(text="💳 Hisob raqamlar")
async def payment(message: types.Message):
    data = await check_card_informations(message.from_user.id)
    card_id = data[0]
    uzb_id = data[1]
    usd_id = data[2]
    rub_id = data[3]
    if card_id is None:
        card_id = ''
    if uzb_id is None:
        uzb_id = ''
    if rub_id is None:
        rub_id = ''
    if usd_id is None:
        usd_id = ''

    information = f'''
🧰 UZCARD & HUMO: <code>{card_id}</code>

🇺🇿 1XBET UZB: <code>{uzb_id}</code>

🇷🇺 1XBET RUB: <code>{rub_id}</code>

🇺🇸 1XBET USD: <code>{usd_id}</code>
    '''
    await message.answer(information, reply_markup=cards_button)


@dp.callback_query_handler(text='add_card')
async def add_card_(call: types.CallbackQuery):
    await call.message.answer('Karta raqamini yozing\nmasalan: 8600123456789000')
    await BotStates.humo_uzcard.set()


@dp.message_handler(state=BotStates.humo_uzcard, content_types=types.ContentType.TEXT)
async def humo_adder(message: types.Message, state: FSMContext):
    card_number = message.text

    def luhn_check(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0

    # Example usage

    if luhn_check(card_number):

        await card_humo_update_add(card_id=card_number, user_id=str(message.from_user.id))
        await message.answer('UZCARD | HUMO hamyon raqamingiz kiritildi ✅')
        await state.finish()
    else:
        await message.answer('Bunday karta ma`lumotlari mavjud emas ❌')


@dp.callback_query_handler(text='xbet_rub')
async def rub_adder(call: types.CallbackQuery):
    await call.message.answer('1XBET RUB hisobingiz raqamini kiriting:')
    await BotStates.rub.set()


@dp.callback_query_handler(text='xbet_uzb')
async def rub_adder(call: types.CallbackQuery):
    await call.message.answer('1XBET UZB hisobingiz raqamini kiriting:')
    await BotStates.uzb.set()


@dp.callback_query_handler(text='xbet_usd')
async def rub_adder(call: types.CallbackQuery):
    await call.message.answer('1XBET USD hisobingiz raqamini kiriting:')
    await BotStates.usd.set()


@dp.message_handler(state=BotStates.rub, content_types=types.ContentType.TEXT)
async def state_rub_checker(message: types.Message, state: FSMContext):
    if len(message.text) <= 10 and message.text.isdigit():
        await rub_update(rub_id=int(message.text), user_id=message.from_user.id)
        await message.answer('Hisob raqamingiz saqlandi ✅')
        await state.finish()
    else:
        await message.answer('Bunday hisob raqam mavjud emas ❌')
        await state.finish()


@dp.message_handler(state=BotStates.uzb, content_types=types.ContentType.TEXT)
async def state_rub_checker(message: types.Message, state: FSMContext):
    if len(message.text) <= 10 and message.text.isdigit():
        await uzb_update(uzb_id=int(message.text), user_id=message.from_user.id)
        await message.answer('Hisob raqamingiz saqlandi ✅')
        await state.finish()
    else:
        await message.answer('Bunday hisob raqam mavjud emas ❌')
        await state.finish()


@dp.message_handler(state=BotStates.usd, content_types=types.ContentType.TEXT)
async def state_rub_checker(message: types.Message, state: FSMContext):
    if len(message.text) <= 10 and message.text.isdigit():
        await usd_update(usd_id=int(message.text), user_id=message.from_user.id)
        await message.answer('Hisob raqamingiz saqlandi ✅')
        await state.finish()
    else:
        await message.answer('Bunday hisob raqam mavjud emas ❌')
        await state.finish()







if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
