import asyncio
import math, time
from . import *
from datetime import datetime as dt
import sys
import shutil
import signal
import os
import logging
from pathlib import Path
from datetime import datetime
import psutil
from pytz import timezone
from config import Config
from script import Txt
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUEUE = {}

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:        
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["⬢" for i in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for i in range(20 - math.floor(percentage / 5))])
        )            
        tmp = progress + Txt.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),            
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",               
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data=f"close-{message.from_user.id}")]])                                               
            )
        except:
            pass

def humanbytes(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def ts(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]

async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        botusername = await b.get_me()
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        await b.send_message(
            Config.LOG_CHANNEL,
            f"**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\nUꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: @{u.username}\n\nDᴀᴛᴇ: {date}\nTɪᴍᴇ: {time}\n\nBy: @{botusername.username}"
        )

def Filename(filename, mime_type):
    if filename.split('.')[-1] in ['mkv', 'mp4', 'mp3', 'mov']:
        return filename
    else:
        if mime_type.split('/')[1] in ['pdf', 'mkv', 'mp4', 'mp3']:
            return f"{filename}.{mime_type.split('/')[1]}"
        elif mime_type.split('/')[0] == "audio":
            return f"{filename}.mp3"
        else:
            return f"{filename}.mkv"

async def CANT_CONFIG_GROUP_MSG(client, message):
    botusername = await client.get_me()
    btn = [
        [InlineKeyboardButton(text='Bᴏᴛ Pᴍ', url=f'https://t.me/{botusername.username}')]
    ]
    ms = await message.reply_text(text="Sᴏʀʀʏ Yᴏᴜ Cᴀɴ'ᴛ Cᴏɴғɪɢ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs\n\nFɪʀsᴛ sᴛᴀʀᴛ ᴍᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍʏ ғᴇᴀᴛᴜᴇʀs ɪɴ ɢʀᴏᴜᴘ", reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(btn))
    await asyncio.sleep(10)
    await ms.delete()

async def Compress_Stats(e, userid):
    if int(userid) not in [e.from_user.id, 0]:
        return await e.answer(f"⚠️ Hᴇʏ {e.from_user.first_name}\nYᴏᴜ ᴄᴀɴ'ᴛ sᴇᴇ sᴛᴀᴛᴜs ᴀs ᴛʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ", show_alert=True)
    
    try:
        inp = f"ffmpeg/{e.from_user.id}/{os.listdir(f'ffmpeg/{e.from_user.id}')[0]}"
        outp = f"encode/{e.from_user.id}/{os.listdir(f'encode/{e.from_user.id}')[0]}"
        ot = humanbytes(int((Path(outp).stat().st_size)))
        ov = humanbytes(int(Path(inp).stat().st_size))
        processing_file_name = inp.replace(f"ffmpeg/{userid}/", "").replace(f"_", " ")
        ans = f"Processing Media: {processing_file_name}\n\nDownloaded: {ov}\n\nCompressed: {ot}"
        await e.answer(ans, cache_time=0, show_alert=True)
    except Exception as er:
        logger.error(f"Compress_Stats error: {str(er)}")
        await e.answer("Something Went Wrong.\nSend Media Again.", cache_time=0, alert=True)

async def skip(e, userid):
    if int(userid) not in [e.from_user.id, 0]:
        return await e.answer(f"⚠️ Hᴇʏ {e.from_user.first_name}\nYᴏᴜ ᴄᴀɴ'ᴛ ᴄᴀɴᴄᴇʟ ᴛʜᴇ ᴘʀᴏᴄᴇss ᴀs ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛ ɪᴛ", show_alert=True)
    try:
        await e.message.delete()
        os.system(f"rm -rf ffmpeg/{userid}*")
        os.system(f"rm -rf encode/{userid}*")
        for proc in psutil.process_iter():
            processName = proc.name()
            processID = proc.pid
            if processName == "ffmpeg":
                os.kill(processID, signal.SIGKILL)
        shutil.rmtree(f'ffmpeg/{userid}', ignore_errors=True)
        shutil.rmtree(f'encode/{userid}', ignore_errors=True)
        if userid in QUEUE:
            QUEUE[userid] = []
        logger.info(f"Process skipped for user {userid}")
    except Exception as e:
        logger.error(f"Skip error for user {userid}: {str(e)}")
    return

async def process_queue(bot, UID, ffmpegcode, c_thumb):
    while UID in QUEUE and QUEUE[UID]:
        query = QUEUE[UID].pop(0)
        logger.info(f"Processing queue item for user {UID}. Queue remaining: {len(QUEUE[UID])}")
        try:
            await process_single_video(bot, query, ffmpegcode, c_thumb)
        except Exception as e:
            logger.error(f"Queue processing error for user {UID}: {str(e)}")
            QUEUE[UID] = []  # Clear queue on error
            
async def process_single_video(bot, query, ffmpegcode, c_thumb):
    UID = query.from_user.id
    ms = await query.message.edit('Pʟᴇᴀsᴇ Wᴀɪᴛ...\n\n**Fᴇᴛᴄʜɪɴɢ Qᴜᴇᴜᴇ 👥**')
    
    try:
        media = query.message.reply_to_message
        if not media:
            await ms.edit("No media found in reply")
            return
            
        file = getattr(media, media.media.value)
        filename = Filename(filename=str(file.file_name), mime_type=str(file.mime_type))
        Download_DIR = f"ffmpeg/{UID}"
        Output_DIR = f"encode/{UID}"
        File_Path = f"ffmpeg/{UID}/{filename}"
        Output_Path = f"encode/{UID}/{filename}"
        
        await ms.edit(f'⚠️__**Please wait...**__\n**Tʀyɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅɪɴɢ....**\nQueue remaining: {len(QUEUE.get(UID, []))} items')
        s = dt.now()
        
        if not os.path.isdir(Download_DIR):
            os.makedirs(Download_DIR)
        if not os.path.isdir(Output_DIR):
            os.makedirs(Output_DIR)

        dl = await bot.download_media(
            message=file,
            file_name=File_Path,
            progress=progress_for_pyrogram,
            progress_args=(f"\n⚠️__**Please wait...**__\n\n☃️ **Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....**\nQueue remaining: {len(QUEUE.get(UID, []))} items", ms, time.time())
        )
        logger.info(f"Download completed for {filename}")
        
        es = dt.now()
        dtime = ts(int((es - s).seconds) * 1000)

        await ms.edit(
            "**🗜 Compressing...**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Sᴛᴀᴛs', callback_data=f'stats-{UID}')],
                [InlineKeyboardButton(text='Cᴀɴᴄᴇʟ', callback_data=f'skip-{UID}')]
            ])
        )
        
        cmd = f"""ffmpeg -i "{dl}" {ffmpegcode} "{Output_Path}" -y"""
        logger.info(f"Starting compression with command: {cmd}")

        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        er = stderr.decode()
        if er:
            logger.error(f"FFmpeg error: {er}")
            await ms.edit(f"Compression failed: {er}\n\n**Error**")
            shutil.rmtree(f"ffmpeg/{UID}", ignore_errors=True)
            shutil.rmtree(f"encode/{UID}", ignore_errors=True)
            QUEUE[UID] = []
            return
            
        logger.info(f"Compression completed for {filename}")
        ees = dt.now()
        
        ph_path = None
        if file.thumbs or c_thumb:
            ph_path = await bot.download_media(c_thumb if c_thumb else file.thumbs[0].file_id)

        org = int(Path(File_Path).stat().st_size)
        com = int(Path(Output_Path).stat().st_size)
        pe = 100 - ((com / org) * 100)
        per = str(f"{pe:.2f}") + "%"
        eees = dt.now()
        x = dtime
        xx = ts(int((ees - es).seconds) * 1000)
        xxx = ts(int((eees - ees).seconds) * 1000)
        
        await ms.edit("⚠️__**Please wait...**__\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
        await bot.send_document(
            UID,
            document=Output_Path,
            thumb=ph_path,
            caption=Config.caption.format(filename, humanbytes(org), humanbytes(com), per, x, xx, xxx),
            progress=progress_for_pyrogram,
            progress_args=("⚠️__**Please wait...**__\n🌨️ **Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
        logger.info(f"Upload completed for {filename}")
        
        if query.message.chat.type == enums.ChatType.SUPERGROUP:
            botusername = await bot.get_me()
            await ms.edit(f"Hey {query.from_user.mention},\n\nI Have Send Compressed File To Your Pm", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Bᴏᴛ Pᴍ", url=f'https://t.me/{botusername.username}')]]))
        else:
            await ms.delete()

        shutil.rmtree(f"ffmpeg/{UID}", ignore_errors=True)
        shutil.rmtree(f"encode/{UID}", ignore_errors=True)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
            
        await process_queue(bot, UID, ffmpegcode, c_thumb)

    except Exception as e:
        logger.error(f"Process single video error for user {UID}: {str(e)}")
        await ms.edit(f"An error occurred: {str(e)}")
        shutil.rmtree(f"ffmpeg/{UID}", ignore_errors=True)
        shutil.rmtree(f"encode/{UID}", ignore_errors=True)
        QUEUE[UID] = []

async def CompressVideo(bot, query, ffmpegcode, c_thumb):
    UID = query.from_user.id
    ms = await query.message.edit('Pʟᴇᴀsᴇ Wᴀɪᴛ...\n\n**Fᴇᴛᴄʜɪɴɢ Qᴜᴇᴜᴇ 👥**')
    
    if UID not in QUEUE:
        QUEUE[UID] = []
    
    QUEUE[UID].append(query)
    queue_position = len(QUEUE[UID])
    await ms.edit(f'Added to queue!\nPosition: {queue_position}\n\nPlease wait for your turn...')
    logger.info(f"Video added to queue for user {UID}. Position: {queue_position}")
    
    if queue_position == 1:
        await process_queue(bot, UID, ffmpegcode, c_thumb)
