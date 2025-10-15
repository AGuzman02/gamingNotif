# botCommands.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import time
from utils import _format_duration
from queries import DatabaseQueries

class BotCommands:
    def __init__(self, bot: commands.Bot, notification_manager, db: DatabaseQueries, discord_logger=None):
        self.bot = bot
        self.notification_manager = notification_manager
        self.db = db
        self.discord_logger = discord_logger
        
        # Register all commands
        self.register_commands()
    
    def register_commands(self):
        """Register all bot commands"""
        
        # Create wrapper functions that call your methods
        @self.bot.command(name='stats', help='Get voice stats for a member')
        async def stats(ctx, member: Optional[discord.Member] = None):
            await self.stats_command(ctx, member)
        
        @self.bot.command(name='leaderboard', aliases=['lb'], help='Show voice time leaderboard')
        async def leaderboard(ctx):
            await self.leaderboard_command(ctx)
        
        @self.bot.command(name='dm', help='Toggle DM notifications for yourself')
        async def dm_toggle(ctx):
            await self.dm_toggle_command(ctx)
        
        @self.bot.command(name='cooldown', help='Check notification cooldown status')
        @commands.has_permissions(manage_guild=True)
        async def cooldown_status(ctx):
            await self.cooldown_status_command(ctx)
        
        @self.bot.command(name='setup', help='Setup the bot for this guild')
        @commands.has_permissions(administrator=True)
        async def setup_guild(ctx):
            await self.setup_guild_command(ctx)
        
        # @self.bot.command(name='help', help='Show all available commands')
        # async def help_command(ctx):
        #     await self.help_command_impl(ctx)
        
        # Setup error handling
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ You don't have permission to use this command!")
            elif isinstance(error, commands.CommandNotFound):
                return  # Ignore unknown commands
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Missing required argument. Use `!help` for command usage.")
            else:
                await ctx.send(f"❌ An error occurred: {error}")
                print(f"Command error: {error}")
    
    # ================================
    # COMMAND IMPLEMENTATIONS
    # ================================
    
    async def stats_command(self, ctx, member: Optional[discord.Member] = None):
        """Get voice stats for a member (defaults to yourself)"""
        target = member or ctx.author
        
        try:
            # For now, just show a placeholder
            embed = discord.Embed(
                title=f"📊 Voice Stats for {target.display_name}",
                color=0x00ff00
            )
            embed.add_field(name="Total Voice Time", value="Feature coming soon!", inline=False)
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting stats: {e}")
            print(f"Error in stats command: {e}")
    
    async def leaderboard_command(self, ctx):
        """Show voice time leaderboard for the server"""
        try:
            embed = discord.Embed(
                title=f"🏆 Voice Leaderboard - {ctx.guild.name}",
                color=0xffd700
            )
            embed.add_field(name="Status", value="Leaderboard feature coming soon!", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting leaderboard: {e}")
            print(f"Error in leaderboard command: {e}")
    
    async def dm_toggle_command(self, ctx):
        """Toggle DM notifications for yourself"""
        try:
            if await self.db.existsMembersGuild(ctx.author, ctx.guild):
                status = await self.db.getDmStatus(ctx.guild, ctx.author)
            
                if status:
                    await self.db.remove_from_dm_group(ctx.guild, ctx.author)
                else:
                    await self.db.add_to_dm_group(ctx.guild, ctx.author)

            await ctx.send(f"Your status went from DM: {status} to DM:{not status}  ")
                
        except Exception as e:
            await ctx.send(f"❌ Error toggling DM: {e}")
            print(f"Error in dm_toggle command: {e}")
            
            # Debug information
            print(f"Debug info:")
            print(f"  User: {ctx.author.name} ({ctx.author.id})")
            print(f"  Guild: {ctx.guild.name} ({ctx.guild.id})") 
    
    async def cooldown_status_command(self, ctx):
        """Check notification cooldown status (Manage Server permission)"""
        try:
            await ctx.send("⏰ Cooldown status feature coming soon!")
                
        except Exception as e:
            await ctx.send(f"❌ Error checking cooldown: {e}")
            print(f"Error in cooldown_status command: {e}")
    
    async def setup_guild_command(self, ctx):
        """Setup the bot for this guild (Admin only)"""
        try:
            embed = discord.Embed(
                title="🛠️ Bot Setup",
                description="Setup feature coming soon!",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Setup error: {e}")
            print(f"Error in setup_guild command: {e}")
    
    async def help_command_impl(self, ctx):
        """Show all available commands"""
        embed = discord.Embed(
            title="🤖 Gaming Notification Bot Commands",
            description="Track voice channel activity and get gaming notifications!",
            color=0x0099ff
        )
        
        embed.add_field(
            name="📊 User Commands",
            value="`!stats [@user]` - View voice time stats\n"
                  "`!leaderboard` - Server voice leaderboard\n"
                  "`!dm` - Toggle DM notifications",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Admin Commands",
            value="`!setup` - Setup bot for this server\n"
                  "`!cooldown` - Check notification cooldown",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Info",
            value="Prefix: `!`\nBot is currently in development",
            inline=False
        )
        
        await ctx.send(embed=embed)