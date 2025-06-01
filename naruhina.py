import os
import asyncio
import logging
import aiohttp
import json
from typing import Dict, Any

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

BOT1_TOKEN = os.getenv("BOT1_TOKEN")  # Naruto's token
BOT2_TOKEN = os.getenv("BOT2_TOKEN")  # Hinata's token

if not BOT1_TOKEN or not BOT2_TOKEN:
    logging.error("Both BOT1_TOKEN and BOT2_TOKEN must be set in the environment.")
    raise RuntimeError("Missing BOT token(s)")

if BOT1_TOKEN.strip() == BOT2_TOKEN.strip():
    logging.error("BOT1_TOKEN and BOT2_TOKEN are identical. Each bot needs its own token.")
    raise RuntimeError("BOT1_TOKEN == BOT2_TOKEN")

# ----------------------------------------
# Shared state for all group chats
# ----------------------------------------

group_chats = {}

Story = [
    "naruto: heyyyyy hinataaa 😁",
    "hinata: umm… naruto… hi ☺️",
    "naruto: what r u doin huh??",
    "hinata: i was just… reading something… 👉👈",
    "naruto: ohhh boring stuff huh 😝",
    "hinata: i-it's not boring… i like it…",
    "naruto: hehe just kiddin don't look so scared 🙃",
]

class TelegramBot:
    def __init__(self, token: str, name: str):
        self.token = token
        self.name = name
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        
    async def get_updates(self):
        """Get updates from Telegram API"""
        url = f"{self.api_url}/getUpdates"
        params = {"offset": self.offset, "timeout": 30}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["ok"]:
                            return data["result"]
                    return []
            except Exception as e:
                logging.error(f"Error getting updates for {self.name}: {e}")
                return []
    
    async def send_message(self, chat_id: int, text: str, reply_markup=None):
        """Send a message"""
        url = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["ok"]
                    return False
            except Exception as e:
                logging.error(f"Error sending message for {self.name}: {e}")
                return False
    
    async def send_chat_action(self, chat_id: int, action: str = "typing"):
        """Send chat action"""
        url = f"{self.api_url}/sendChatAction"
        data = {"chat_id": chat_id, "action": action}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    return response.status == 200
            except Exception as e:
                logging.error(f"Error sending chat action for {self.name}: {e}")
                return False
    
    async def get_chat_member(self, chat_id: int, user_id: int):
        """Get chat member info"""
        url = f"{self.api_url}/getChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result["ok"]:
                            return result["result"]
                    return None
            except Exception as e:
                logging.error(f"Error getting chat member for {self.name}: {e}")
                return None

    async def set_my_commands(self, commands):
        """Set bot commands"""
        url = f"{self.api_url}/setMyCommands"
        data = {"commands": json.dumps(commands)}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    return response.status == 200
            except Exception as e:
                logging.error(f"Error setting commands for {self.name}: {e}")
                return False

    async def get_me(self):
        """Get bot information"""
        url = f"{self.api_url}/getMe"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result["ok"]:
                            return result["result"]
                    return None
            except Exception as e:
                logging.error(f"Error getting bot info for {self.name}: {e}")
                return None

# ----------------------------------------
# Bot instances
# ----------------------------------------

naruto_bot = TelegramBot(BOT1_TOKEN, "Naruto")
hinata_bot = TelegramBot(BOT2_TOKEN, "Hinata")

# ----------------------------------------
# Utility functions
# ----------------------------------------

async def is_admin(chat_id: int, user_id: int, bot: TelegramBot) -> bool:
    """Check if user is admin"""
    member = await bot.get_chat_member(chat_id, user_id)
    if member:
        return member.get("status") in ["administrator", "creator"]
    return False

async def check_both_bots_present(chat_id: int) -> Dict[str, bool]:
    """Check if both bots are present in the group chat"""
    naruto_info = await naruto_bot.get_me()
    hinata_info = await hinata_bot.get_me()
    
    if not naruto_info or not hinata_info:
        logging.error("Failed to get bot information")
        return {"naruto_present": False, "hinata_present": False}
    
    naruto_user_id = naruto_info["id"]
    hinata_user_id = hinata_info["id"]
    
    # Check if Naruto bot is in the chat
    naruto_member = await naruto_bot.get_chat_member(chat_id, naruto_user_id)
    naruto_present = naruto_member and naruto_member.get("status") not in ["left", "kicked"]
    
    # Check if Hinata bot is in the chat
    hinata_member = await hinata_bot.get_chat_member(chat_id, hinata_user_id)
    hinata_present = hinata_member and hinata_member.get("status") not in ["left", "kicked"]
    
    return {
        "naruto_present": naruto_present,
        "hinata_present": hinata_present
    }

async def send_emotional_response(chat_id: int, requesting_bot: TelegramBot, missing_bot_name: str):
    """Send emotional response when companion bot is missing"""
    if requesting_bot.name == "Naruto":
        # Naruto's emotional response when Hinata is missing
        emotional_message = (
            "😭😭😭 NOOOOO! I'm completely useless without my precious Hinata-chan! 💔\n\n"
            "I can't do the duet chat without her! She's my everything, my light, my reason to exist! 🥺💔\n"
            "Please... PLEASE add my beloved Hinata to this group! I'm nothing without her! 😢\n\n"
            "I need my Hinata-chan here with me or I'll go crazy! dattebayo! 😭🍥💕"
        )
    else:
        # Hinata's emotional response when Naruto is missing
        emotional_message = (
            "😢😢😢 I... I'm so useless without Naruto-kun... 💔\n\n"
            "I c-can't do anything without him... He gives me strength and courage... 🥺💗\n"
            "Please... please add my beloved Naruto-kun to this group... I'm so lonely without him... 😭\n\n"
            "Without Naruto-kun, I... I can't even speak properly... He completes me... 🌸💔"
        )
    
    await requesting_bot.send_message(chat_id, emotional_message)

async def handle_start_command(message: Dict[Any, Any], bot: TelegramBot):
    """Handle /start command"""
    chat_id = message["chat"]["id"]
    chat_type = message["chat"]["type"]
    
    if chat_type == "private":
        if bot.name == "Naruto":
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "Updates", "url": "https://t.me/WorkGlows"},
                        {"text": "Support", "url": "https://t.me/TheCryptoElders"}
                    ],
                    [
                        {"text": "Add Me to Your Group", "url": f"https://t.me/PervyNarutoBot?startgroup=true"}
                    ]
                ]
            }
            text = ("Hey! It's me, Naruto Uzumaki! 😁\n\n"
                   "I can't stop thinking about Hinata... like, ever! She's everything to me—my light, my heart, my everything! 💓💫\n"
                   "Please add me and my precious Hinata-chan to your group so we can have our sweet moments together! 🥺💖🍥")
        else:
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "Updates", "url": "https://t.me/WorkGlows"},
                        {"text": "Support", "url": "https://t.me/TheCryptoElders"}
                    ],
                    [
                        {"text": "Add Me to Your Group", "url": f"https://t.me/HornyHinataBot?startgroup=true"}
                    ]
                ]
            }
            text = ("H-Hello... I'm Hinata Hyuga... ☺️\n\n"
                   "I c-can't stop thinking about Naruto-kun... He means everything to me. 🥺💗\n"
                   "Please add me and my beloved Naruto-kun to your group, so we can be together again and share our love openly… 🌸🍥")
        
        await bot.send_message(chat_id, text, keyboard)

async def handle_private_text(message: Dict[Any, Any], bot: TelegramBot):
    """Handle private text messages"""
    chat_id = message["chat"]["id"]
    chat_type = message["chat"]["type"]
    
    if chat_type == "private":
        if bot.name == "Naruto":
            text = ("I miss Hinata-chan so much… every second without her feels like forever! 🥺💔\n"
                   "Please… can you add me and my precious Hinata to your group?")
        else:
            text = ("I miss Naruto-kun so much… my heart races just imagining him near me... 🥺💗\n"
                   "Please... add me and Naruto-kun to your group?")
        
        await bot.send_message(chat_id, text)

async def start_duet_chat(message: Dict[Any, Any], bot: TelegramBot):
    """Start duet chat - now with emotional response if companion bot is missing"""
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    
    if not await is_admin(chat_id, user_id, bot):
        return
    
    # Check if both bots are present in the group
    bot_presence = await check_both_bots_present(chat_id)
    
    if not bot_presence["naruto_present"] and not bot_presence["hinata_present"]:
        # Neither bot is present - this shouldn't happen as one of them received the command
        await bot.send_message(chat_id, "❌ Error: Unable to verify bot presence in this group.")
        return
    
    if not bot_presence["naruto_present"]:
        # Naruto is missing, send emotional response from whichever bot received the command
        await send_emotional_response(chat_id, bot, "Naruto")
        return
    
    if not bot_presence["hinata_present"]:
        # Hinata is missing, send emotional response from whichever bot received the command
        await send_emotional_response(chat_id, bot, "Hinata")
        return
    
    # Both bots are present, proceed with normal duet chat
    if chat_id not in group_chats or not group_chats[chat_id].get("chat_started", False):
        group_chats[chat_id] = {"story_index": 0, "chat_started": True, "paused": False, "task": None}
        task = asyncio.create_task(chat_loop(chat_id))
        group_chats[chat_id]["task"] = task
        logging.info(f"[start_duet_chat] duet started in chat {chat_id}")

async def pause_duet_chat(message: Dict[Any, Any], bot: TelegramBot):
    """Pause duet chat"""
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    
    if not await is_admin(chat_id, user_id, bot):
        return
    
    if chat_id in group_chats and group_chats[chat_id].get("chat_started", False):
        group_chats[chat_id]["paused"] = True
        await bot.send_message(chat_id, "😐")

async def resume_duet_chat(message: Dict[Any, Any], bot: TelegramBot):
    """Resume duet chat"""
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    
    if not await is_admin(chat_id, user_id, bot):
        return
    
    if chat_id in group_chats and group_chats[chat_id].get("chat_started", False):
        group_chats[chat_id]["paused"] = False
        await bot.send_message(chat_id, "😊")

async def stop_duet_chat(message: Dict[Any, Any], bot: TelegramBot):
    """Stop duet chat"""
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    
    if not await is_admin(chat_id, user_id, bot):
        return
    
    if chat_id in group_chats and group_chats[chat_id].get("chat_started", False):
        group_chats[chat_id]["chat_started"] = False
        task = group_chats[chat_id].get("task")
        if task:
            task.cancel()
        del group_chats[chat_id]
        logging.info(f"[stop_duet_chat] duet stopped in chat {chat_id}")

async def chat_loop(chat_id: int):
    """Main chat loop for duet conversation"""
    await asyncio.sleep(2)
    
    while True:
        if not (chat_id in group_chats and group_chats[chat_id].get("chat_started", False)):
            break
            
        if group_chats[chat_id].get("paused", False):
            await asyncio.sleep(3)
            continue

        idx = group_chats[chat_id]["story_index"]
        
        if idx >= len(Story):
            group_chats[chat_id]["chat_started"] = False
            break

        line = Story[idx]
        speaker, text = line.split(":", 1)
        text = text.strip()
        
        sender = naruto_bot if speaker.lower() == 'naruto' else hinata_bot

        try:
            await sender.send_chat_action(chat_id, "typing")
            await asyncio.sleep(4)
            await sender.send_message(chat_id, text)
            group_chats[chat_id]["story_index"] = idx + 1
            await asyncio.sleep(8)
        except Exception as e:
            logging.error(f"Error in chat_loop: {e}")
            break

async def handle_message(message: Dict[Any, Any], bot: TelegramBot):
    """Handle incoming messages"""
    text = message.get("text", "")
    chat_type = message["chat"]["type"]
    
    if text.startswith("/start"):
        await handle_start_command(message, bot)
    elif text.startswith("/fuck") and chat_type in ["group", "supergroup"]:
        await start_duet_chat(message, bot)
    elif text.startswith("/kiss") and chat_type in ["group", "supergroup"]:
        await pause_duet_chat(message, bot)
    elif text.startswith("/rub") and chat_type in ["group", "supergroup"]:
        await resume_duet_chat(message, bot)
    elif text.startswith("/cum") and chat_type in ["group", "supergroup"]:
        await stop_duet_chat(message, bot)
    elif chat_type == "private" and not text.startswith("/"):
        await handle_private_text(message, bot)

async def bot_polling(bot: TelegramBot):
    """Main polling loop for a bot"""
    logging.info(f"Starting {bot.name} bot...")
    
    # Set bot commands
    commands = [
        {"command": "start", "description": "Show bot intro and links"},
        {"command": "fuck", "description": "Start duet chat in this group"},
        {"command": "kiss", "description": "Pause the duet chat"},
        {"command": "rub", "description": "Resume the duet chat"},
        {"command": "cum", "description": "Stop duet chat in this group"},
    ]
    await bot.set_my_commands(commands)
    
    while True:
        try:
            updates = await bot.get_updates()
            
            for update in updates:
                bot.offset = update["update_id"] + 1
                
                if "message" in update:
                    await handle_message(update["message"], bot)
                    
        except Exception as e:
            logging.error(f"Error in {bot.name} polling: {e}")
            await asyncio.sleep(5)

async def main():
    """Main function to run both bots concurrently"""
    await asyncio.gather(
        bot_polling(naruto_bot),
        bot_polling(hinata_bot)
    )

if __name__ == "__main__":
    asyncio.run(main())