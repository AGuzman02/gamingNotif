# Gaming Notification Discord Bot

A Discord bot that tracks voice channel activity, sends notifications when users join voice channels, and logs gaming session statistics to a Supabase database.

## 🏗️ Project Architecture

### Overview
This project follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────┐
│     main.py     │  ← Entry point & dependency injection
├─────────────────┤
│    events.py    │  ← Discord event handlers
├─────────────────┤
│    utils.py     │  ← Business logic & utilities
├─────────────────┤
│   queries.py    │  ← Database operations (Supabase)
└─────────────────┘
```

### Core Components

#### 1. **main.py** - Application Bootstrap
- **Purpose**: Entry point, configuration, and dependency wiring
- **Responsibilities**:
  - Load environment variables
  - Initialize Discord client with proper intents
  - Set up Supabase database connection
  - Wire up all components and start the bot

```python
# Key components initialized:
- Discord Client (bugs)
- DatabaseQueries (db)
- NotificationManager
- BotEvents (event handlers)
```

#### 2. **events.py** - Event Handling Layer
- **Purpose**: Handle Discord events and coordinate responses
- **Key Events**:
  - `on_ready()`: Bot initialization and DM group setup
  - `on_voice_state_update()`: Voice channel join/leave detection

```python
# Event flow:
User joins voice → handleVoiceJoin() → Database logging
User leaves voice → handleVoiceLeave() → Session calculation
```

#### 3. **utils.py** - Business Logic Layer
- **Purpose**: Business logic, notifications, and voice state utilities
- **Key Components**:
  - `NotificationManager`: Handles DM notifications and cooldowns
  - `handleVoiceJoin()`: Process user joining voice channels
  - `handleVoiceLeave()`: Process user leaving and calculate session time
  - Voice state checking utilities

#### 4. **queries.py** - Data Access Layer
- **Purpose**: All database operations and queries
- **Key Methods**:
  - User management (`existsMember`, `newMember`)
  - Session tracking (`logArrivalTime`, `logLeaveTime`)
  - Game time calculation (`logGameTime`)
  - Data retrieval (`getLastArrivalAndLeave`)

## 🗄️ Database Schema

### Tables

#### **Members**
```sql
- id: SERIAL PRIMARY KEY
- memberId: BIGINT (Discord user ID)
- name: VARCHAR(255) (Discord username)
- guildId: BIGINT (Discord server ID)
- gameTime: NUMERIC (Total gaming time in seconds)
```

#### **timeLog**
```sql
- id: SERIAL PRIMARY KEY
- memberId: BIGINT (Foreign key to Members)
- arrivalTime: TIMESTAMPTZ (When user joined voice)
- leavingTime: TIMESTAMPTZ (When user left voice)
```

### Stored Procedures

#### **get_session_duration_seconds(BIGINT)**
```sql
-- Calculates session duration in seconds for the most recent session
-- Returns: NUMERIC (duration in seconds)
```

## 🔄 Data Flow

### Voice Channel Join Flow
```
1. Discord Event: User joins voice channel
2. events.py: Detect join via on_voice_state_update()
3. utils.py: handleVoiceJoin() processes the event
4. queries.py: Check if user exists, create if needed
5. queries.py: Log arrival time to timeLog table
6. utils.py: Send notifications if second person in channel
```

### Voice Channel Leave Flow
```
1. Discord Event: User leaves voice channel
2. events.py: Detect leave via on_voice_state_update()
3. utils.py: handleVoiceLeave() processes the event
4. queries.py: Update leaving time for active session
5. queries.py: Calculate session duration using stored procedure
6. queries.py: Update user's total game time
7. Console: Display formatted session duration
```

## 🚀 Features

### Core Functionality
- **Voice Channel Monitoring**: Tracks when users join/leave voice channels
- **Smart Notifications**: Sends DMs to users with "DM" role when someone joins a voice channel
- **Session Tracking**: Logs detailed gaming sessions with arrival/departure times
- **Game Time Statistics**: Calculates and tracks total gaming time per user
- **Cooldown System**: Prevents notification spam with configurable cooldowns

### Notification System
- **Target Audience**: Users with "DM" role in Discord server
- **Trigger**: When a user joins a voice channel and makes it have exactly 2 people
- **Cooldown**: 30-second global cooldown to prevent spam
- **Message Format**: `{username} joined {channel_name}`

### Database Features
- **PostgreSQL/Supabase Integration**: Modern cloud database with real-time capabilities
- **Stored Procedures**: Efficient server-side calculations for session durations
- **BIGINT Support**: Proper handling of Discord's 64-bit user IDs
- **Automatic Timestamps**: Server-side timestamp generation for consistency

## 🛠️ Configuration

### Environment Variables (.env)
```env
DISCORD_TOKEN=your_discord_bot_token
DATABASE_URL=your_supabase_database_url
DATABASE_KEY=your_supabase_anon_key
SERVICE_ROLE_KEY=your_supabase_service_role_key  # For bypassing RLS
```

### Discord Bot Permissions
Required intents:
- `guilds`: Access to server information
- `members`: Access to member data
- `voice_states`: Track voice channel activity
- `typing`: Enhanced presence detection
- `presences`: User status monitoring

### Required Discord Permissions
- Send Messages (for DMs)
- Read Message History
- View Channels
- Connect (to voice channels for monitoring)

## 📁 File Structure

```
gamingNotif/
├── main.py              # Application entry point
├── events.py            # Discord event handlers
├── utils.py             # Business logic & utilities
├── queries.py           # Database operations
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in repo)
├── bot-env/            # Virtual environment
└── README.md           # This file
```

## 🔧 Installation & Setup

### 1. Prerequisites
- Python 3.8+
- Discord Bot Token
- Supabase Account & Project

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/AGuzman02/gamingNotif.git
cd gamingNotif

# Create virtual environment
python -m venv bot-env
bot-env\Scripts\activate  # Windows
# or
source bot-env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
1. Create Supabase project
2. Run SQL schema creation scripts
3. Create stored procedures
4. Set up Row Level Security policies if needed

### 4. Configuration
1. Copy `.env.example` to `.env`
2. Fill in your Discord bot token and Supabase credentials
3. Create "DM" role in your Discord server
4. Assign the role to users who want notifications

### 5. Run the Bot
```bash
python main.py
```

## 🏛️ Design Principles

### Separation of Concerns
- **events.py**: Only handles Discord events, delegates to business logic
- **utils.py**: Contains business rules and utility functions
- **queries.py**: Strictly database operations, no business logic
- **main.py**: Configuration and wiring, minimal logic

### Error Handling
- Comprehensive try-catch blocks in all async operations
- Graceful degradation when database operations fail
- Detailed logging for debugging and monitoring

### Scalability Considerations
- Database operations use efficient queries with proper indexing
- Cooldown system prevents API rate limiting
- Modular design allows easy feature additions

### Security
- Environment variables for sensitive data
- Supabase RLS policies for data protection
- Service role key for trusted bot operations

## 📊 Monitoring

The bot provides console logging for:
- User join/leave events
- Database operation results
- Session duration calculations
- Error messages with stack traces
- Notification delivery status

Monitor the console output to ensure proper operation and troubleshoot issues.