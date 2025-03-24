import os
import time
import asyncio
import sys
import humanize
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from helper.utils import Compress_Stats, skip, CompressVideo
from helper.database import db
from script import Txt

# Dictionary to store queues for different users
QUEUE = {}

@Client.on_callback_query()
async def Cb_Handle(bot: Client, query: CallbackQuery):
    data = query.data

    if data == 'help':
        btn = [
            [InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='home')]
        ]
        await query.message.edit(text=Txt.HELP_MSG, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

    elif data == 'home':
        btn = [
            [InlineKeyboardButton(text='❗ Hᴇʟᴘ', callback_data='help'), 
             InlineKeyboardButton(text='🌨️ Aʙᴏᴜᴛ', callback_data='about')],
            [InlineKeyboardButton(text='📢 Uᴘᴅᴀᴛᴇs', url='https://t.me/AIORFT'), 
             InlineKeyboardButton(text='💻 Dᴇᴠᴇʟᴏᴘᴇʀ', url='https://t.me/Snowball_Official')]
        ]
        await query.message.edit(text=Txt.PRIVATE_START_MSG.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(btn))

    elif data == 'about':
        BUTN = [
            [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='home')]
        ]
        botuser = await bot.get_me()
        await query.message.edit(Txt.ABOUT_TXT.format(botuser.username), reply_markup=InlineKeyboardMarkup(BUTN), disable_web_page_preview=True)

    elif data.startswith('stats'):
        user_id = data.split('-')[1]
        try:
            await Compress_Stats(e=query, userid=user_id)
        except Exception as e:
            print(e)

    elif data.startswith('skip'):
        user_id = data.split('-')[1]
        try:
            await skip(e=query, userid=user_id)
            if user_id in QUEUE:
                QUEUE[user_id] = []  # Clear queue on skip
        except Exception as e:
            print(e)

    elif data == 'option':
        file = getattr(query.message.reply_to_message, query.message.reply_to_message.media.value)
        text = f"""**__What do you want me to do with this file?__**\n\n**File Name** :- `{file.file_name}`\n\n**File Size** :- `{humanize.naturalsize(file.file_size)}`"""
        buttons = [
            [InlineKeyboardButton("Rᴇɴᴀᴍᴇ 📝", callback_data=f"rename-{query.from_user.id}")],
            [InlineKeyboardButton("Cᴏᴍᴘʀᴇss 🗜️", callback_data=f"compress-{query.from_user.id}")]
        ]
        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == 'setffmpeg':
        try:
            ffmpeg_code = await bot.ask(text=Txt.SEND_FFMPEG_CODE, chat_id=query.from_user.id, filters=filters.text, timeout=60, disable_web_page_preview=True)
            SnowDev = await query.message.reply_text(text="**Setting Your FFMPEG CODE**\n\nPlease Wait...")
            await db.set_ffmpegcode(query.from_user.id, ffmpeg_code.text)
            await SnowDev.edit("✅️ __**Fғᴍᴘᴇɢ Cᴏᴅᴇ Sᴇᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ**__")
        except:
            await query.message.reply_text("**Eʀʀᴏʀ!!**\n\nRᴇǫᴜᴇsᴛ ᴛɪᴍᴇᴅ ᴏᴜᴛ.\nSᴇ� secondeᴛ ʙʏ ᴜsɪɴɢ /set_ffmpeg")

    elif data.startswith('compress'):
        user_id = data.split('-')[1]
        if int(user_id) not in [query.from_user.id, 0]:
            return await query.answer(f"⚠️ Hᴇʏ {query.from_user.first_name}\nTʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴀɴʏ ᴏᴘᴇʀᴀᴛɪᴏɴ", show_alert=True)
        
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg = "-preset veryfast -c:v libx264 -s 1280x720 -x265-params 'bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1' -pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k -c:s copy -map 0 -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
            
            # Add to queue
            if user_id not in QUEUE:
                QUEUE[user_id] = []
            
            QUEUE[user_id].append({
                'query': query,
                'ffmpegcode': ffmpeg,
                'c_thumb': c_thumb
            })
            
            queue_position = len(QUEUE[user_id])
            await query.message.edit(f'Added to compression queue at 720p!\nPosition: {queue_position}')
            
            # Process queue if this is the first item
            if queue_position == 1:
                await process_queue(bot, user_id)
                
        except Exception as e:
            print(e)

    elif data.startswith("close"):
        user_id = data.split('-')[1]
        if int(user_id) not in [query.from_user.id, 0]:
            return await query.answer(f"⚠️ Hᴇʏ {query.from_user.first_name}\nTʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴀɴʏ ᴏᴘᴇʀᴀᴛɪᴏɴ", show_alert=True)
        
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()

async def process_queue(bot, user_id):
    while user_id in QUEUE and QUEUE[user_id]:
        task = QUEUE[user_id].pop(0)
        await CompressVideo(bot=bot, query=task['query'], ffmpegcode=task['ffmpegcode'], c_thumb=task['c_thumb'])
        await asyncio.sleep(2)  # Small delay between processing videos

# Handler for automatic queue addition when video is sent
@Client.on_message(filters.video & filters.private)
async def auto_compress(bot: Client, message: Message):
    user_id = str(message.from_user.id)
    
    # Create a dummy query object to mimic callback behavior
    class DummyQuery:
        def __init__(self, message):
            self.message = message
            self.from_user = message.from_user
    
    dummy_query = DummyQuery(message)
    
    # Add to queue automatically
    if user_id not in QUEUE:
        QUEUE[user_id] = []
    
    c_thumb = await db.get_thumbnail(message.from_user.id)
    ffmpeg = "-preset veryfast -c:v libx264 -s 1280x720 -x265-params 'bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1' -pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k -c:s copy -map 0 -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
    
    QUEUE[user_id].append({
        'query': dummy_query,
        'ffmpegcode': ffmpeg,
        'c_thumb': c_thumb
    })
    
    queue_position = len(QUEUE[user_id])
    await message.reply(f'Video added to compression queue at 720p!\nPosition: {queue_position}')
    
    # Start processing if this is the first item
    if queue_position == 1:
        await process_queue(bot, user_id)
