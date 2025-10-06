import discord
from dotenv import load_dotenv
import os
from utils import NotificationManager
from events import BotEvents
from queries import DatabaseQueries
from supabase import create_client, Client

# Setup Discord client
intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.members = True
intents.voice_states = True
intents.guilds = True
bugs = discord.Client(intents=intents)


# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN') 
dbUrl = os.getenv('DATABASE_URL')
dbKey = os.getenv('DATABASE_KEY')

# Initialize database connection (global)
supabase: Client = create_client(dbUrl, dbKey)
db = DatabaseQueries(supabase)

# Initialize managers
notification_manager = NotificationManager(db)

# Register events
bot_events = BotEvents(bugs, notification_manager, db)

# Start the bot
if __name__ == "__main__":
    bugs.run(token)