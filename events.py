import discord
from utils import *
from queries import DatabaseQueries

class BotEvents:
    def __init__(self, bot, notification_manager, db: DatabaseQueries, discord_logger=None):
        self.bot = bot
        self.notification_manager = notification_manager
        self.db = db
        self.discord_logger = discord_logger
        
        # Register all event handlers
        self.register_events()
    
    def register_events(self):
        """Register all event handlers with the bot"""
        self.bot.event(self.on_ready)
        self.bot.event(self.on_voice_state_update)
        self.bot.event(self.on_guild_join)
        self.bot.event(self.on_member_update) 
    
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}')
        
        # Setup Discord logging
        if self.discord_logger:
            setup_success = await self.discord_logger.setup()
            if setup_success:
                self.discord_logger.override_print()  # Override print function
        
        # Get the guild (server)
        guild = self.bot.guilds[0]  # Assuming first guild
        
        # Setup DM group
        self.notification_manager.setup_dm_group(guild, 'DM')
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates"""

        if is_user_joining_voice(before, after):
            await handleVoiceJoin(member, self.db)
            if is_second_person_in_channel(after.channel):
                # Check cooldown
                if await self.notification_manager.is_on_cooldown(member.guild):
                    print("Global cooldown active")
                    return
                # Update cooldown and send notifications
                await self.notification_manager.update_cooldown(member.guild)
                await self.notification_manager.send_notifications(after.channel)
        
        if is_user_leaving_voice(before, after):
            await handleVoiceLeave(member, self.db)

    async def on_guild_join(self, guild):
        """Register a new guild in the db"""
        if await handleNewGuild(guild):
            print(f"Guild {guild.name} was succesfully added into the db")

    async def on_member_update(self, before, after):
        """Auto-update DM group when DM role changes"""
        before_roles = {role.name for role in before.roles}
        after_roles = {role.name for role in after.roles}
        
        # Check if DM role was added or removed
        if "DM" in after_roles and "DM" not in before_roles:
            # DM role added
            self.notification_manager.setup_dm_group(after.guild, 'DM')
            print(f"✅ {after.name} added to DM notifications")
            
        elif "DM" in before_roles and "DM" not in after_roles:
            # DM role removed
            self.notification_manager.setup_dm_group(after.guild, 'DM')
            print(f"❌ {after.name} removed from DM notifications")