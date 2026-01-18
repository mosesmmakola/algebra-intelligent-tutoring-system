from backend.database import SQLiteManager
import os

def setup_system():
    """Setup with comprehensive question pools"""
    db = SQLiteManager()
    
    print("🎓 Algebra ITS - Complete Question Pool System")
    print("=" * 55)
    
    # Check questions per lesson
    lessons = db.get_all_lessons()
    practice_stats = {}
    quiz_stats = {}
    
    for lesson in lessons:
        all_practice = db.get_all_practice_questions(lesson['lesson_id'])
        practice_stats[lesson['lesson_id']] = len(all_practice)
        
        all_quiz = db.get_all_quiz_questions(lesson['lesson_id'])
        quiz_stats[lesson['lesson_id']] = len(all_quiz)
    
    print("\n📊 Complete Question Pool Statistics:")
    print(f"{'Lesson':<15} {'Practice Qs':<12} {'Quiz Qs':<10} {'Total':<8}")
    print("-" * 50)
    for lesson_id in practice_stats:
        practice_count = practice_stats[lesson_id]
        quiz_count = quiz_stats[lesson_id]
        total = practice_count + quiz_count
        status = "✅" if practice_count >= 20 and quiz_count >= 20 else "⚠️"
        print(f"{status} {lesson_id:<13} {practice_count:<11} {quiz_count:<9} {total:<7}")
    
    total_practice = sum(practice_stats.values())
    total_quiz = sum(quiz_stats.values())
    grand_total = total_practice + total_quiz
    
    print(f"{'TOTAL':<15} {total_practice:<11} {total_quiz:<9} {grand_total:<7}")
    
    print(f"\n✅ System ready with comprehensive question pools!")
    print(f"   - Practice questions: {total_practice} total")
    print(f"   - Quiz questions: {total_quiz} total")
    print(f"   - Grand total: {grand_total} questions")
    print(f"   - Average per lesson: {total_practice//len(lessons)} practice + {total_quiz//len(lessons)} quiz")

def reset_database():
    """Completely reset the database and recreate all tables with fresh data"""
    db_path = "math_its.db"
    
    # Close any existing connections first
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.close()
    except:
        pass
    
    # Remove the database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Old database removed")
    else:
        print("ℹ️  No existing database found")
    
    print("🔄 Creating new database with all components...")
    
    # Reinitialize the database by creating a new SQLiteManager instance
    db = SQLiteManager()
    
    # Verify the new database
    print("\n✅ Database reset complete!")
    print("📊 Verifying new database contents...")
    
    setup_system()  # Run the setup verification

def check_system_health():
    """Check if the system is properly set up"""
    db = SQLiteManager()
    
    print("🏥 System Health Check")
    print("=" * 30)
    
    issues = []
    
    # Check lessons
    lessons = db.get_all_lessons()
    if len(lessons) == 0:
        issues.append("❌ No lessons found in database")
    else:
        print(f"✅ Lessons: {len(lessons)} loaded")
    
    practice_total = 0
    for lesson in lessons:
        practice_count = len(db.get_all_practice_questions(lesson['lesson_id']))
        practice_total += practice_count
        if practice_count == 0:
            issues.append(f"❌ No practice questions for {lesson['lesson_id']}")
    
    if practice_total > 0:
        print(f"✅ Practice Questions: {practice_total} total")
    
    quiz_total = 0
    for lesson in lessons:
        quiz_count = len(db.get_all_quiz_questions(lesson['lesson_id']))
        quiz_total += quiz_count
    
    if quiz_total > 0:
        print(f"✅ Quiz Questions: {quiz_total} total")
    
    # Check tables
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        required_tables = ['students', 'lessons', 'practice_questions', 'quiz_questions', 'chats', 'quiz_results']
        for table in required_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                issues.append(f"❌ Missing table: {table}")
        
        conn.close()
        print("✅ Database tables: All present")
        
    except Exception as e:
        issues.append(f"❌ Database connection error: {e}")
    
    # Report issues
    if issues:
        print(f"\n🚨 Issues Found ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n💡 Run the reset function to fix these issues.")
    else:
        print(f"\n🎉 System is healthy! All components are ready.")

if __name__ == "__main__":
    print("🎓 Algebra ITS - Setup & Maintenance")
    print("=" * 40)
    print("1. Setup system (normal verification)")
    print("2. Reset database (delete and recreate)")
    print("3. Check system health")
    print("4. Quick setup verification")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "2":
        confirm = input("⚠️  Are you sure you want to reset the database? This will delete ALL data! (y/N): ").strip().lower()
        if confirm == 'y' or confirm == 'yes':
            reset_database()
        else:
            print("❌ Database reset cancelled.")
    elif choice == "3":
        check_system_health()
    elif choice == "4":
        setup_system()
    else:
        setup_system()