import os
import asyncio
import logging
from telegram import (
    Update, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand,
)
from telegram.constants import ChatAction, ChatType
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters,
)

# ----------------------------------------
# Logging setup
# ----------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ----------------------------------------
# Bot tokens (set these in your environment)
# ----------------------------------------

BOT1_TOKEN = os.getenv("BOT1_TOKEN")  # Naruto’s token
BOT2_TOKEN = os.getenv("BOT2_TOKEN")  # Hinata’s token

if not BOT1_TOKEN or not BOT2_TOKEN:
    logging.error("Both BOT1_TOKEN and BOT2_TOKEN must be set in the environment.")
    raise RuntimeError("Missing BOT token(s)")

if BOT1_TOKEN.strip() == BOT2_TOKEN.strip():
    logging.error("BOT1_TOKEN and BOT2_TOKEN are identical. Each bot needs its own token.")
    raise RuntimeError("BOT1_TOKEN == BOT2_TOKEN")

# ----------------------------------------
# Shared state for all group chats
# ----------------------------------------

group_chats: dict[int, dict[str, any]] = {}

Story = [
    "naruto: heyyyyy hinataaa 😁",
    "hinata: umm… naruto… hi ☺️",
    "naruto: what r u doin huh??",
    "hinata: i was just… reading something… 👉👈",
    "naruto: ohhh boring stuff huh 😝",
    "hinata: i-it’s not boring… i like it…",
    "naruto: hehe just kiddin don’t look so scared 🙃",
]

# ----------------------------------------
# Utility: Check if the command‐sender is an admin
# ----------------------------------------

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        member: ChatMember = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

# ----------------------------------------
# Emotional response if only one bot is added
# ----------------------------------------

async def check_partner_presence(update: Update, context: ContextTypes.DEFAULT_TYPE, partner_bot_username: str, is_naruto: bool) -> bool:
    chat = update.effective_chat
    try:
        member = await context.bot.get_chat_member(chat.id, partner_bot_username)
        if member.status not in ["administrator", "member"]:
            raise Exception()
        return True
    except:
        message = (
            "I’m useless without her... Without Hinata, I have no reason to speak. Please... bring her to me. 🥺💔"
            if is_naruto else
            "I... I can't talk without Naruto-kun. Please... I need him beside me... I feel so lost... 🥺💔"
        )
        await update.message.reply_text(message)
        return False

# ----------------------------------------
# Handlers for private chats (Naruto & Hinata)
# ----------------------------------------

async def naruto_start_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    keyboard = [
        [
            InlineKeyboardButton("Updates", url="https://t.me/WorkGlows"),
            InlineKeyboardButton("Support", url="https://t.me/TheCryptoElders")
        ],
        [
            InlineKeyboardButton(
                "Add Me to Your Group",
                url=f"https://t.me/{(await context.bot.get_me()).username}?startgroup=true"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hey! It's me, Naruto Uzumaki! 😁\n\n"
        "I can't stop thinking about Hinata... like, ever! She's everything to me—my light, my heart, my everything! 💓💫\n"
        "Please add me and my precious Hinata-chan to your group so we can have our sweet moments together! 🥺💖🍥",
        reply_markup=reply_markup,
    )

async def naruto_private_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            "I miss Hinata-chan so much… every second without her feels like forever! 🥺💔\n"
            "Please… can you add me and my precious Hinata (@HornyHinataBot) to your group?"
        )

async def hinata_start_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    keyboard = [
        [
            InlineKeyboardButton("Updates", url="https://t.me/WorkGlows"),
            InlineKeyboardButton("Support", url="https://t.me/TheCryptoElders")
        ],
        [
            InlineKeyboardButton(
                "Add Me to Your Group",
                url=f"https://t.me/{(await context.bot.get_me()).username}?startgroup=true"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "H-Hello... I'm Hinata Hyuga... ☺️\n\n"
        "I c-can’t stop thinking about Naruto-kun... He means everything to me. 🥺💗\n"
        "Please add me and my beloved Naruto-kun to your group, so we can be together again and share our love openly… 🌸🍥",
        reply_markup=reply_markup,
    )

async def hinata_private_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            "I miss Naruto-kun so much… my heart races just imagining him near me... 🥺💗\n"
            "Please... add me and Naruto-kun (@PervyNarutoBot) to your group?"
        )

# ----------------------------------------
# /fuck — start the duet chat in this group
# ----------------------------------------

async def start_duet_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not await is_admin(update, context):
        return
    if chat_id not in group_chats or not group_chats[chat_id]["chat_started"]:
        group_chats[chat_id] = {"story_index": 0, "chat_started": True, "paused": False, "task": None}
        bot1 = context.application.bot
        bot2 = context.application._other_bot
        task = asyncio.create_task(chat_loop(chat_id, bot1, bot2))
        group_chats[chat_id]["task"] = task
        await check_missing_partner(update, context, "Naruto" if bot1.token == BOT1_TOKEN else "Hinata", "Hinata" if bot1.token == BOT1_TOKEN else "Naruto")
        logging.info(f"[start_duet_chat] duet started in chat {chat_id}")

# ----------------------------------------
# /kiss — pause the duet chat
# ----------------------------------------

async def pause_duet_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not await is_admin(update, context):
        return
    if chat_id in group_chats and group_chats[chat_id]["chat_started"]:
        group_chats[chat_id]["paused"] = True
        await context.bot.send_message(chat_id=chat_id, text="😐")

# ----------------------------------------
# /rub — resume the duet chat
# ----------------------------------------

async def resume_duet_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not await is_admin(update, context):
        return
    if chat_id in group_chats and group_chats[chat_id]["chat_started"]:
        group_chats[chat_id]["paused"] = False
        await context.bot.send_message(chat_id=chat_id, text="😊")

# ----------------------------------------
# /cum — stop the duet chat in this group
# ----------------------------------------

async def stop_duet_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not await is_admin(update, context):
        return
    if chat_id in group_chats and group_chats[chat_id]["chat_started"]:
        group_chats[chat_id]["chat_started"] = False
        task = group_chats[chat_id]["task"]
        if task:
            task.cancel()
        del group_chats[chat_id]
        logging.info(f"[stop_duet_chat] duet stopped in chat {chat_id}")

# ----------------------------------------
# The shared chat loop: sends Story lines sequentially
# ----------------------------------------

async def chat_loop(chat_id: int, bot1, bot2):
    await asyncio.sleep(2)
    while True:
        # stop if the chat’s been marked as ended
        if not (chat_id in group_chats and group_chats[chat_id]["chat_started"]):
            break
        if group_chats[chat_id].get("paused", False):
            await asyncio.sleep(3)
            continue

        idx = group_chats[chat_id]["story_index"]
        # **new**: end after the last line instead of looping
        if idx >= len(Story):
            group_chats[chat_id]["chat_started"] = False
            break

        line = Story[idx]
        speaker, text = line.split(":", 1)
        text = text.strip()
        sender = bot1 if speaker.lower() == 'naruto' else bot2

        await sender.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(4)
        await sender.send_message(chat_id=chat_id, text=text)

        group_chats[chat_id]["story_index"] = idx + 1
        await asyncio.sleep(8)

# ----------------------------------------
# Register bot menu commands
# ----------------------------------------

async def set_commands(app, bot_label: str):
    commands = [
        BotCommand("start", "Show bot intro and links"),
        BotCommand("fuck", "Start duet chat in this group"),
        BotCommand("kiss", "Pause the duet chat"),
        BotCommand("rub", "Resume the duet chat"),
        BotCommand("cum", "Stop duet chat in this group"),
    ]
    await app.bot.set_my_commands(commands)
    logging.info(f"[{bot_label}] menu commands registered")

# ----------------------------------------
# Boilerplate to launch each Application
# ----------------------------------------

async def run_app(app):
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

# ----------------------------------------
# Main entrypoint: build two Application instances
# ----------------------------------------

async def main():
    app1 = ApplicationBuilder().token(BOT1_TOKEN).build()
    app2 = ApplicationBuilder().token(BOT2_TOKEN).build()
    app1._other_bot = app2.bot
    app2._other_bot = app1.bot

    for app in (app1, app2):
        app.add_handler(CommandHandler("fuck", start_duet_chat, filters=filters.ChatType.GROUPS))
        app.add_handler(CommandHandler("kiss", pause_duet_chat, filters=filters.ChatType.GROUPS))
        app.add_handler(CommandHandler("rub", resume_duet_chat, filters=filters.ChatType.GROUPS))
        app.add_handler(CommandHandler("cum", stop_duet_chat, filters=filters.ChatType.GROUPS))

    app1.add_handler(CommandHandler("start", naruto_start_private))
    app1.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, naruto_private_text))
    app2.add_handler(CommandHandler("start", hinata_start_private))
    app2.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, hinata_private_text))

    await asyncio.gather(
        set_commands(app1, "naruto"),
        set_commands(app2, "hinata"),
        run_app(app1),
        run_app(app2),
    )

if __name__ == "__main__":
    asyncio.run(main())
