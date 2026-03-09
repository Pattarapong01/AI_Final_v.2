import sqlite3
import json
import os

# --- Configuration ---
DB_PATH = 'clothing_store.db'

def calculate_targeted_kpi():
    """
    Calculate KPI = (In-Scope Sessions handled by AI / Total In-Scope Sessions) * 100
    using real data from the database.
    """
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch all tickets
        cursor.execute("SELECT id, ai_category, chat_history, created_at FROM tickets")
        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            print("No conversation data found in the system.")
            return

        # Define keywords for In-Scope (Expanded to include greetings and initial engagement)
        in_scope_keywords = [
            "ราคา", "บาท", "เสื้อ", "กางเกง", "ชุด", "ไซส์", 
            "แนะนำ", "เหมาะ", "มีของไหม", "สต็อก", "สไตล์", "ผ้า", "สี",
            "สวัสดี", "hi", "hello", "hey", "สอบถาม" # Added greetings for better tracking
        ]

        total_sessions = len(tickets)
        total_in_scope = 0
        ai_handled_success = 0
        human_escalated = 0

        print("-" * 60)
        print(f"Analyzing KPI for {total_sessions} total sessions...")
        print("-" * 60)

        for t in tickets:
            history_json = t['chat_history'] or "[]"
            try:
                history_list = json.loads(history_json)
            except json.JSONDecodeError:
                continue

            # Combine all user messages in this session
            user_messages = [m['content'] for m in history_list if m['role'] == 'user']
            combined_user_text = " ".join(user_messages).lower()
            
            # Check if this session is "In-Scope"
            is_in_scope = any(key in combined_user_text for key in in_scope_keywords)

            if is_in_scope:
                total_in_scope += 1
                # Check if it stayed with AI or moved to Human
                if t['ai_category'] == 'STYLIST_SESSION':
                    ai_handled_success += 1
                else:
                    human_escalated += 1

        # Calculate percentage
        kpi_percent = (ai_handled_success / total_in_scope * 100) if total_in_scope > 0 else 0

        # Display results
        print(f"1. Total Sessions Recorded: {total_sessions} cases")
        print(f"2. In-Scope Engagement: {total_in_scope} cases")
        print(f"   - AI Managed Successfully: {ai_handled_success} cases")
        print(f"   - Handover to Human Staff: {human_escalated} cases")
        print("-" * 60)
        print(f">>> TARGETED AI KPI: {kpi_percent:.2f}% <<<")
        print("-" * 60)
        print("Note: This KPI tracks AI efficiency in styling and product inquiries.")
        print("Initial greetings and 'hi' are now counted as start of engagement.")

    except Exception as e:
        print(f"Calculation Error: {e}")

if __name__ == "__main__":
    calculate_targeted_kpi()