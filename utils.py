from typing import Dict
import discord
import time
import os
import json
from queries import DatabaseQueries

class NotificationManager:
    def __init__(self, db):
        self.last_notification_time = 0
        self.COOLDOWN_SECONDS = 3600 * 4
        self.dmGroup = []
        self.db = db
    
    async def is_on_cooldown(self, guild):
        """Check if notifications are on cooldown"""
        current_time = time.time()
        cooldown = await self.db.getCoolDown(guild)
        print(cooldown)
        if cooldown:
            return current_time - cooldown.data[0] < self.COOLDOWN_SECONDS
    
    async def update_cooldown(self, guild):
        """Update the last notification time"""
        await self.db.updateCoolDown(guild)
    
    async def send_notifications(self, channel):
        """Send notifications to all DM group members"""
        membersStr = " and ".join([member.name for member in channel.members])
        for group_member in self.dmGroup:
            if group_member in channel.members:
                continue
            try:
                await group_member.send(f'Gaming time in "{channel.name}" with {membersStr}!')
            except discord.Forbidden:
                print(f"Cannot send DM to {group_member.name}")
    
    def setup_dm_group(self, guild, role_name='DM'):
        """Setup the DM group from guild role"""
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            self.dmGroup = role.members
            return True
        else:
            print(f"{role_name} role not found")
            return False

def is_user_joining_voice(before, after):
    """Check if user is joining a voice channel"""
    return before.channel is None and after.channel is not None

def is_second_person_in_channel(channel):
    """Check if this makes the channel have exactly 2 people"""
    return len(channel.members) == 2

def is_user_leaving_voice(before, after):
    """Check if user is leaving a voice channel"""
    return before.channel is not None and after.channel is None

async def handleVoiceJoin(member, db: DatabaseQueries):
    """Handle new user by checking and inserting into DB"""
    await db.newMember(member)
    await db.newMemberToGuild(member, member.guild)
    await db.logArrivalTime(member)
        

async def handleVoiceLeave(member, db: DatabaseQueries):
    """Handle complete voice leave process: log leave time and calculate duration"""
    try:
        # Step 1: Log leave time
        leave_success = await db.logLeaveTime(member)
        if not leave_success:
            return None
        
        # Step 2: Calculate and update game time
        await db.logGameTime(member)

        return None
    except Exception as e:
        print(f"Error handling voice leave for {member.name}: {e}")
        return None

def _format_duration(seconds: float) -> str:
    """Format seconds into MM:SS or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

async def handleNewGuild(guild, db): 
    return await db.registerGuild(guild)