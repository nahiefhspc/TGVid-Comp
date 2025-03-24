import os
import time
import asyncio
import sys
import humanize
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.utils import Compress_Stats, skip, CompressVideo, QUEUE
from helper.database import db
from script import Txt

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
            print(f"Stats error: {e}")
            await query.answer("Error getting stats", show_alert=True)

    elif data.startswith('skip'):
        user_id = data.split('-')[1]
        try:
            await skip(e=query, userid=user_id)
            if user_id in QUEUE and QUEUE[user_id]:
                await query.message.edit(f"Process cancelled. Next item in queue starting...\nQueue remaining: {len(QUEUE[user_id])} items")
        except Exception as e:
            print(f"Skip error: {e}")
            await query.answer("Error cancelling process", show_alert=True)

    elif data == 'option':
        file = getattr(query.message.reply_to_message, query.message.reply_to_message.media.value)
        text = f"""**__What do you want me to do with this file?__**\n\n**File Name** :- `{file.file_name}`\n\n**File Size** :- `{humanize.naturalsize(file.file_size)}`"""
        buttons = [
            [InlineKeyboardButton("Rᴇɴᴀᴍᴇ 📝", callback_data=f"rename-{query.from_user.id}")],
            [InlineKeyboardButton("Cᴏᴍᴘʀᴇss 🗜️", callback_data=f"auto_compress-{query.from_user.id}")]
        ]
        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == 'setffmpeg':
        try:
            ffmpeg_code = await bot.ask(text=Txt.SEND_FFMPEG_CODE, chat_id=query.from_user.id, filters=filters.text, timeout=60, disable_web_page_preview=True)
            SnowDev = await query.message.reply_text(text="**Setting Your FFMPEG CODE**\n\nPlease Wait...")
            await db.set_ffmpegcode(query.from_user.id, ffmpeg_code.text)
            await SnowDev.edit("✅️ __**Fғᴍᴘᴇɢ Cᴏᴅᴇ Sᴇᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ**__")
        except Exception as e:
            print(f"Set ffmpeg error: {e}")
            await query.message.reply_text("**Eʀʀᴏʀ!!**\n\nRequest timed out.\nSet by using /set_ffmpeg")

    elif data.startswith('auto_compress'):
        user_id = data.split('-')[1]
        
        if int(user_id) not in [query.from_user.id, 0]:
            return await query.answer(f"⚠️ Hᴇʏ {query.from_user.first_name}\nTʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴀɴʏ ᴏᴘᴇʀᴀᴛɪᴏɴ", show_alert=True)
        
        try:
            custom_ffmpeg = await db.get_ffmpegcode(query.from_user.id)
            if not custom_ffmpeg:
                custom_ffmpeg = "-preset veryfast -c:v libx264 -s 1280x720 -x265-params 'bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1' -pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k -c:s copy -map 0 -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
            
            c_thumb = await db.get_thumbnail(query.from_user.id)
            await CompressVideo(bot=bot, query=query, ffmpegcode=custom_ffmpeg, c_thumb=c_thumb)
            
        except Exception as e:
            print(f"Error in auto_compress: {e}")
            await query.message.edit(f"Error occurred: {str(e)}")

    elif data.startswith("close"):
        user_id = data.split('-')[1]
        
        if int(user_id) not in [query.from_user.id, 0]:
            return await query.answer(f"⚠️ Hᴇʏ {query.from_user.first_name}\nTʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴀɴʏ ᴏᴘᴇʀᴀᴛɪᴏɴ", show_alert=True)
        
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except Exception as e:
            print(f"Close error: {e}")
            await query.message.delete()

@Client.on_message(filters.video & filters.private)
async def auto_queue_video(bot: Client, message):
    try:
        text = f"""**__Video received! What do you want to do?__**\n\n**File Name** :- `{message.video.file_name}`\n\n**File Size** :- `{humanize.naturalsize(message.video.file_size)}`"""
        buttons = [
            [InlineKeyboardButton("Rᴇɴᴀᴍᴇ 📝", callback_data=f"rename-{message.from_user.id}")],
            [InlineKeyboardButton("Cᴏᴍᴘʀᴇss 🗜️", callback_data=f"auto_compress-{message.from_user.id}")]
        ]
        
        user_id = str(message.from_user.id)
        queue_length = len(QUEUE.get(user_id, []))
        if queue_length > 0:
            text += f"\n\nCurrent queue position: {queue_length + 1}"
        
        await message.reply_text(text=test, reply_markup=InlineKeyboardMarkup(buttons), quote=True)
    except Exception as e:
        print(f"Error in auto_queue_video: {e}")
