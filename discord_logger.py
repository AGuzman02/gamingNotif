# discord_logger.py
import asyncio
import discord
from typing import Optional
from datetime import datetime

class DiscordLogger:
    def __init__(self, bot: discord.Client, guild_id: int, channel_name: str):
        self.bot = bot
        self.guild_id = guild_id
        self.channel_name = channel_name
        self.channel: Optional[discord.TextChannel] = None
        self.original_print = print  # Store original print function
        
    async def setup(self):
        """Setup the Discord channel for logging"""
        try:
            guild = self.bot.get_guild(self.guild_id)
            if guild:
                self.channel = discord.utils.get(guild.channels, name=self.channel_name)
                if self.channel:
                    await self.log(f"🔧 Discord Logger initialized in {guild.name} -> #{self.channel_name}")
                    return True
                else:
                    self.original_print(f"❌ Channel '{self.channel_name}' not found in guild {guild.name}")
            else:
                self.original_print(f"❌ Guild {self.guild_id} not found")
        except Exception as e:
            self.original_print(f"❌ Error setting up Discord logger: {e}")
        return False
    
    async def log(self, message: str, level: str = "INFO"):
        """Send a log message to Discord channel"""
        if not self.channel:
            self.original_print(message)  # Fallback to console
            return
        
        try:
            # Format the message with timestamp and level
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"`[{timestamp}] [{level}]` {message}"
            
            # Split long messages to avoid Discord's 2000 character limit
            if len(formatted_message) > 1990:
                chunks = [formatted_message[i:i+1990] for i in range(0, len(formatted_message), 1990)]
                for chunk in chunks:
                    await self.channel.send(chunk)
            else:
                await self.channel.send(formatted_message)
                
        except Exception as e:
            # Fallback to console if Discord fails
            self.original_print(f"Discord log failed: {e}")
            self.original_print(message)
    
    def override_print(self):
        """Override the global print function"""
        def async_print(*args, **kwargs):
            # Convert print arguments to string
            message = " ".join(str(arg) for arg in args)
            
            # Try to get the current event loop and send to Discord
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule the coroutine if loop is already running
                    asyncio.create_task(self.log(message))
                else:
                    # Fallback to original print if no loop
                    self.original_print(message)
            except Exception as e:
                # Fallback to original print if async fails
                self.original_print(message)
        
        # Replace the global print function
        import builtins
        builtins.print = async_print
    
    def restore_print(self):
        """Restore the original print function"""
        import builtins
        builtins.print = self.original_print

# Global logger instance
discord_logger: Optional[DiscordLogger] = None

def setup_discord_logging(bot: discord.Client, guild_id: int, channel_name: str = "testingchannel"):
    """Setup Discord logging globally"""
    global discord_logger
    discord_logger = DiscordLogger(bot, guild_id, channel_name)
    return discord_logger

async def log_info(message: str):
    """Log an info message"""
    if discord_logger:
        await discord_logger.log(message, "INFO")
    else:
        print(message)

async def log_error(message: str):
    """Log an error message"""
    if discord_logger:
        await discord_logger.log(f"❌ {message}", "ERROR")
    else:
        print(f"ERROR: {message}")

async def log_success(message: str):
    """Log a success message"""
    if discord_logger:
        await discord_logger.log(f"✅ {message}", "SUCCESS")
    else:
        print(f"SUCCESS: {message}")

async def log_warning(message: str):
    """Log a warning message"""
    if discord_logger:
        await discord_logger.log(f"⚠️ {message}", "WARNING")
    else:
        print(f"WARNING: {message}")