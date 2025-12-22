import csv
import random
from datetime import datetime, timedelta

# Animals available in the game
animals = ['cow', 'dog', 'cat', 'lion']

# Generate 200 new realistic entries
def generate_session_id():
    timestamp = int(datetime.now().timestamp() * 1000)
    random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=13))
    return f"session_{timestamp}_{random_suffix}"

def generate_response_time(is_correct, attempt_number, has_disability=False):
    """Generate realistic response times based on correctness, fatigue, and disability status"""
    if has_disability:
        # Children with hearing disabilities have slower response times
        if is_correct:
            # 6000-12000ms range for correct answers
            base_time = random.uniform(6000, 12000)
        else:
            # Even slower for incorrect (confusion)
            base_time = random.uniform(9000, 18000)
    else:
        # Normal hearing children
        if is_correct:
            # Normal response: 2500-5000ms
            base_time = random.uniform(2400, 5200)
            # Add slight fatigue factor for later attempts
            fatigue_factor = 1 + (attempt_number * 0.01)
            base_time *= fatigue_factor
        else:
            # Incorrect responses tend to be slower or hesitant
            # Mix of quick wrong answers and slow confused responses
            if random.random() < 0.6:
                base_time = random.uniform(3000, 7000)  # Hesitant
            else:
                base_time = random.uniform(8000, 16000)  # Very slow/confused
    
    return int(base_time)

def generate_game_data(num_entries=200):
    new_data = []
    
    # Generate 10-15 different sessions
    num_sessions = random.randint(10, 15)
    
    for session_idx in range(num_sessions):
        session_id = generate_session_id()
        session_start = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # 20-30% of sessions have children with hearing disabilities
        has_hearing_disability = random.random() < 0.25
        
        # Each session has 12-25 attempts
        num_attempts = random.randint(12, 25)
        total_score = 0
        cumulative_duration = random.uniform(5, 20)  # Start delay
        
        for attempt in range(num_attempts):
            animal_shown = random.choice(animals)
            
            # Children with disabilities have slightly lower accuracy
            if has_hearing_disability:
                accuracy_rate = random.uniform(0.60, 0.75)
            else:
                accuracy_rate = random.uniform(0.75, 0.85)
            
            is_correct = random.random() < accuracy_rate
            
            if is_correct:
                animal_selected = animal_shown
                total_score += 1
            else:
                # Select a different animal when wrong
                animal_selected = random.choice([a for a in animals if a != animal_shown])
            
            response_time = generate_response_time(is_correct, attempt, has_hearing_disability)
            
            # Add response time to cumulative duration (plus small delay between attempts)
            cumulative_duration += (response_time / 1000) + random.uniform(0.5, 2.0)
            
            # Occasionally add long pauses (child distraction)
            if random.random() < 0.1:  # 10% chance
                pause = random.uniform(30, 300)  # 30 sec to 5 min pause
                cumulative_duration += pause
            
            timestamp = session_start + timedelta(seconds=cumulative_duration)
            
            entry = {
                'session_id': session_id,
                'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                'animal_shown': animal_shown,
                'animal_selected': animal_selected,
                'is_correct': is_correct,
                'response_time_ms': response_time,
                'attempt_number': attempt,
                'total_score': total_score,
                'game_duration_sec': round(cumulative_duration, 3),
                'has_hearing_disability': has_hearing_disability
            }
            
            new_data.append(entry)
    
    return new_data

# Main execution
print("=" * 60)
print("Animal Sound Safari - Data Generation Script")
print("=" * 60)
print("\nGenerating 200+ entries of game analytics data...")

new_entries = generate_game_data(200)

# Check if CSV needs header update
csv_path = 'game_analytics/game_analytics.csv'
needs_header_update = False

try:
    with open(csv_path, 'r') as f:
        first_line = f.readline()
        needs_header_update = 'has_hearing_disability' not in first_line
except FileNotFoundError:
    needs_header_update = True
    print(f"⚠ Warning: {csv_path} not found!")

if needs_header_update:
    print("\n⚠ Adding 'has_hearing_disability' column to CSV...")
    # Read existing data
    existing_rows = []
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            # Add disability flag to existing rows based on response time > 6000ms
            for row in existing_rows:
                row['has_hearing_disability'] = int(row['response_time_ms']) > 6000
        print(f"✓ Read {len(existing_rows)} existing rows")
    except FileNotFoundError:
        print("✓ Creating new CSV file")
    
    # Rewrite CSV with new header
    with open(csv_path, 'w', newline='') as f:
        fieldnames = ['session_id', 'timestamp', 'animal_shown', 'animal_selected', 
                      'is_correct', 'response_time_ms', 'attempt_number', 'total_score', 
                      'game_duration_sec', 'has_hearing_disability']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)
    
    print("✓ Updated existing data with disability flags")

# Append new data
with open(csv_path, 'a', newline='') as f:
    fieldnames = ['session_id', 'timestamp', 'animal_shown', 'animal_selected', 
                  'is_correct', 'response_time_ms', 'attempt_number', 'total_score', 
                  'game_duration_sec', 'has_hearing_disability']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    for entry in new_entries:
        writer.writerow(entry)

print(f"\n✓ Successfully generated {len(new_entries)} entries!")
print(f"✓ Data appended to {csv_path}")

# Print statistics
correct_responses = sum(1 for e in new_entries if e['is_correct'])
with_disability = sum(1 for e in new_entries if e['has_hearing_disability'])
avg_response_time = sum(e['response_time_ms'] for e in new_entries) / len(new_entries)
unique_sessions = len(set(e['session_id'] for e in new_entries))

print("\n" + "=" * 60)
print("STATISTICS")
print("=" * 60)
print(f"  Total entries generated: {len(new_entries)}")
print(f"  Unique sessions: {unique_sessions}")
print(f"  Accuracy rate: {correct_responses/len(new_entries)*100:.1f}%")
print(f"  Average response time: {avg_response_time:.0f}ms")
print(f"  With hearing disability: {with_disability} entries ({with_disability/len(new_entries)*100:.1f}%)")
print(f"  Without disability: {len(new_entries) - with_disability} entries ({(len(new_entries) - with_disability)/len(new_entries)*100:.1f}%)")
print("=" * 60)
print("\n✓ Data generation complete!")
