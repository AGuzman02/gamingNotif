from supabase import Client
from typing import Optional, List, Dict
import time
from datetime import datetime
from discord import Member, Guild

class DatabaseQueries:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def existsMember(self, member) -> bool:
        try:
            data = self.supabase.table("Members").select("memberId", count="exact").eq("memberId", member.id).execute()
            return data.count > 0
        except Exception as e:
            print(f"Error fetching member {member.name}: {e}")
            return False
            
    async def newMember(self, member: Member) -> bool:
        try:
          self.supabase.table("Members").upsert([
              {"memberId": member.id, "name" : member.name}
          ]).execute()
          return True
        except Exception as e:
            print(f"Error inserting member {member.name}: {e}")
            return False

    async def newMemberToGuild(self, member, guild):
        try:
            self.supabase.table("MembersGuild").upsert({"membersId": member.id, "guildId" : guild.id}).execute()
        except Exception as e:
            print(f"Error linking {member.name} to guild {guild.name}: {e}")
            return False
        
    async def logArrivalTime(self, member) -> bool:
        # Insert member into arrival time
        try:
            self.supabase.table("TimeLog").upsert([{"memberId" : member.id}]).execute()
            return True
        except Exception as e:
            print(f"Error time log {member.name}: {e}")
            return False
    
    async def logLeaveTime(self, member) -> bool:
        try:
            data = self.supabase.table("TimeLog").select("id").eq("memberId", member.id).order("arrivalTime", desc=True).limit(1).execute()
            timeId = data.data[0]["id"]
            self.supabase.table("TimeLog").update({"leavingTime": "now()"}).eq("id", timeId).execute()
            return True
        except Exception as e:
            print(f"Error leaving time log {member.name}: {e}")
            return False

    async def logGameTime(self, member) -> bool:
        try:
            # Call the stored procedure
            result = self.supabase.rpc('get_session_duration_seconds', {'recievedmemberid': member.id}).execute()
            data = self.supabase.table("Members").select("gameTime").eq("memberId", member.id).execute()

            data = data.data[0]["gameTime"] if data.data else 0.0
            duration = float(result.data) if result.data else 0.0

            if data is not None:
                duration += float(data)
            self.supabase.table("Members").update({"gameTime": duration}).eq("memberId", member.id).execute()

            if duration > 0:
                print(f"{member.name} played for {duration:.1f} seconds")
            return True
        except Exception as e:
            print(f"Error calculating game time for {member.name}: {e}")
            return False
        
    async def registerGuild(self, guild: Guild) -> bool:
        try:
            self.supabase.table("Guild").upsert({
                "guildId" : guild.id, "guildName": guild.name,
            }).execute()
            return True
        except Exception as e:
            print(f"There was an error on registering this guild {guild.name}: {e}")
            return False
        
    async def getCoolDown(self, guild: Guild):
        try:
            result = self.supabase.table("Guild").select("Cooldown").eq("guildId", guild.id).execute()
            return result
        except Exception as e:
            print(f"There was an error getting the cooldown for {guild.name}: {e}")
            return False
        
    async def updateCoolDown(self, guild: Guild):
        try:
            self.supabase.table("Guild").update({
                "Cooldown" : time.time()
            }).eq("guildId", guild.id).execute()
        except Exception as e:
            print(f"There was an error updating {guild.name}'s cooldown: {e}")
            return False



