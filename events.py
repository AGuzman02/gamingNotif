import discord
from utils import NotificationManager, is_user_joining_voice, is_second_person_in_channel, get_arrival_time, is_user_leaving_voice, log_game_time
from queries import DatabaseQueries

class BotEvents:
    def __init__(self, bot, notification_manager, log_file, gameplay_time_file, db: DatabaseQueries):
        self.bot = bot
        self.notification_manager = notification_manager
        self.log_file = log_file
        self.gameplay_time_file = gameplay_time_file
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
        if is_user_joining_voice(before, after):
            if not await self.db.existsMember(member):
              await self.db.newMember(member)
            get_arrival_time(member, self.log_file)
            if is_second_person_in_channel(after.channel):
                # Check cooldown
                if self.notification_manager.is_on_cooldown():
                    print("Global cooldown active")
                    return
                # Update cooldown and send notifications
                self.notification_manager.update_cooldown()
                await self.notification_manager.send_notifications(member, after.channel.name)
        
        if is_user_leaving_voice(before, after):
            log_game_time(member, self.log_file, self.gameplay_time_file)