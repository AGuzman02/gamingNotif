def readLogFile(log_file):
    """Read the log file and return its content"""
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    else:
        return []

def get_arrival_time(member, log_file):
    """Log member arrival to JSON file"""
    arrival_data = {
        "member_id": member.id,
        "details" : 
        {
            "member_name": member.name,
            "arrival_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "timestamp": time.time()
        }
    }
    
    # Read existing data or create empty list
    data = readLogFile(log_file)
    
    # Append new entry
    data.append(arrival_data)
    
    # Write back to file
    with open(log_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return arrival_data

def log_game_time(member, log_file, gameplay_time_file):
    # Load existing log data
    joinFile = readLogFile(log_file)
    gameFile = readLogFile(gameplay_time_file)
    
    # Find the latest entry for this member
    for entry in reversed(joinFile):
        if entry['member_id'] == member.id:
            # Debug the timestamps
            current_timestamp = time.time()
            arrival_timestamp = entry['details']['timestamp']
            
            # Check if timestamps are in the wrong format/scale
            gameplay_time_seconds = current_timestamp - arrival_timestamp
            
            # Convert seconds to readable format
            hours = int(gameplay_time_seconds // 3600)
            minutes = int((gameplay_time_seconds % 3600) // 60)
            seconds = int(gameplay_time_seconds % 60)
            
            # Format as MM:SS or HH:MM:SS
            if hours > 0:
                gameplay_time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                gameplay_time_formatted = f"{minutes:02d}:{seconds:02d}"
            
            
            # Log gameplay time
            if member.id not in [g['member_id'] for g in gameFile]:
                gameFile.append({
                    "member_id": member.id,
                    "member_name": member.name,
                    "total_gameplay_time_seconds": gameplay_time_seconds,
                    "last_session": gameplay_time_formatted
                })
            else:
                for g in gameFile:
                    if g['member_id'] == member.id:
                        g['total_gameplay_time_seconds'] += gameplay_time_seconds
                        g['last_session'] = gameplay_time_formatted
                        
                        # Convert total time to readable format
                        total_seconds = g['total_gameplay_time_seconds']
                        total_hours = int(total_seconds // 3600)
                        total_minutes = int((total_seconds % 3600) // 60)
                        total_secs = int(total_seconds % 60)
                        total_formatted = f"{total_hours:02d}:{total_minutes:02d}:{total_secs:02d}"
                        g['total_gameplay_time_formatted'] = total_formatted
                        
                        break
            break
            
    with open(gameplay_time_file, 'w') as f:
        json.dump(gameFile, f, indent=2)