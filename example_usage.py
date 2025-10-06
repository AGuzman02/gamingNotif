# example_usage.py - Example of how to use the Discord logger

"""
After setting up the Discord logger in main.py, all print() statements 
will automatically be sent to your Discord channel!

Examples:
"""

# Regular print statements (these will go to Discord after setup)
print("✅ Bot started successfully!")
print("🔍 Checking database connection...")
print("⚠️ Warning: High memory usage detected")
print("❌ Failed to connect to external API")

# You can also use the specific logging functions for better formatting:
"""
from discord_logger import log_info, log_error, log_success, log_warning

# These need to be called with await in async functions:
await log_info("Database connection established")
await log_success("Member successfully added to database")
await log_warning("API rate limit approaching")
await log_error("Failed to send notification to user")
"""

# The system will:
# 1. Send all output to Discord channel "testingchannel" in guild 1422756400584724622
# 2. Format messages with timestamps and levels
# 3. Handle long messages by splitting them
# 4. Fallback to console if Discord fails