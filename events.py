import discord
from utils import NotificationManager, is_user_joining_voice, is_second_person_in_channel, is_user_leaving_voice, handleVoiceJoin, handleVoiceLeave
from queries import DatabaseQueries

class BotEvents:
    def __init__(self, bot, notification_manager, db: DatabaseQueries):
        self.bot = bot
        self.notification_manager = notification_manager
        self.db = db
        
        # Register all event handlers
        self.register_events()
    
    def register_events(self):
        """Register all event handlers with the bot"""
        self.bot.event(self.on_ready)
        self.bot.event(self.on_voice_state_update)
    
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}')
        
        # Get the guild (server)
        guild = self.bot.guilds[0]  # Assuming first guild
        
        # Setup DM group
        self.notification_manager.setup_dm_group(guild, 'DM')
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates"""
        # Only log arrival time when joining
        # await self.db.logArrivalTime(member)

        if is_user_joining_voice(before, after):
            await handleVoiceJoin(member, self.db)
            if is_second_person_in_channel(after.channel):
                # Check cooldown
                if self.notification_manager.is_on_cooldown():
                    print("Global cooldown active")
                    return
                # Update cooldown and send notifications
                self.notification_manager.update_cooldown()
                await self.notification_manager.send_notifications(member, after.channel.name)
        
        if is_user_leaving_voice(before, after):
            await handleVoiceLeave(member, self.db)
            