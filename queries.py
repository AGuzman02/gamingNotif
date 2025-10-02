from supabase import Client
from typing import Optional, List, Dict
import time
from datetime import datetime
from discord import Member

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
          self.supabase.table("Members").insert([
              {"memberId": member.id, "name" : member.name, "guildId" : member.guild.id}
          ]).execute()
          return True
        except Exception as e:
            print(f"Error inserting member {member.name}: {e}")
            return False
        
    async def logArrivalTime(self, member) -> None:
        # Insert member into arrival time
        
        pass
    
    async def logLeaveTime(self, member) -> None:
        #Insert member into leaving time
        
        
        pass
    

    async def getLastArrivaAndLeave(self, member) -> Dict:
        # getArrivalTime left join leaveTime
        # Return row with biggest leftAt
        # Return row with biggest arrivalTime
        pass