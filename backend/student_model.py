import json
from typing import Dict

class StudentModel:
    def __init__(self, db_manager):
        self.db = db_manager
        self.algebra_milestones = {
            'beginner': {
                'target_score': 50, 
                'required_lessons': 2,
                'description': 'Mastery of basic variables and simple equations'
            },
            'intermediate': {
                'target_score': 50, 
                'required_lessons': 4,
                'description': 'Proficiency with expressions and two-step equations'
            },
            'advanced': {
                'target_score': 50, 
                'required_lessons': 6,
                'description': 'Expertise in systems and quadratic equations'
            }
        }
    
    def _update_student_level(self, username: str, performance_score: float):
        """Update student level based on completed lessons only"""
        student = self.db.get_student(username)
        if not student:
            return False
        
        current_level = student['level']
        completed_lessons = len(student.get('completed_lessons', []))
        
        # Define progression rules based on completed lessons
        progression_rules = {
            'beginner': {
                'required_lessons': 2,  # Complete 2 beginner lessons
                'next_level': 'intermediate'
            },
            'intermediate': {
                'required_lessons': 4,  # Complete 4 total lessons
                'next_level': 'advanced'
            },
            'advanced': {
                'required_lessons': 6,  # Complete 6 total lessons
                'next_level': 'advanced'
            }
        }
        
        # Can't progress beyond advanced
        if current_level == 'advanced':
            return False
        
        rule = progression_rules.get(current_level)
        if not rule:
            return False
        
        # Print progression info
        print(f"🔍 Level Progression Check for {username}:")
        print(f"   Current Level: {current_level}")
        print(f"   Completed Lessons: {completed_lessons}/{rule['required_lessons']}")
        print(f"   Performance Score: {performance_score}% (Not used for progression)")
        
        # Check if student meets criteria for next level
        meets_lesson_criteria = completed_lessons >= rule['required_lessons']
        
        if meets_lesson_criteria:
            # Update student level in database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET level = ? WHERE username = ?",
                (rule['next_level'], username)
            )
            conn.commit()
            conn.close()
            
            # Log the level up
            print(f"🎉 {username} leveled up from {current_level} to {rule['next_level']}!")
            return True
        else:
            print(f"❌ {username} not ready for level up:")
            print(f"   Need {rule['required_lessons'] - completed_lessons} more lessons")
            return False

    def update_performance(self, username: str, exercise_id: str, correct: bool):
        """Update student performance based ONLY on quiz results"""
        student = self.db.get_student(username)
        if not student:
            return
        
        # Only update performance for quiz results (identified by 'quiz_' prefix)
        if not exercise_id.startswith('quiz_'):
            return 
        
        # Get current performance data
        current_score = student.get('performance_score', 0)
        
        # Calculate new score 
        if correct:
            new_score = min(100, current_score + 15) 
            print(f"📈 Quiz passed: {username} performance +15 ({current_score}% -> {new_score}%)")
        else:
            new_score = max(0, current_score - 8)  
            print(f"📉 Quiz failed: {username} performance -8 ({current_score}% -> {new_score}%)")
        
        # Update performance score in database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET performance_score = ? WHERE username = ?",
            (new_score, username)
        )
        conn.commit()
        conn.close()
        
        # Check for level progression with the UPDATED score
        self._update_student_level(username, new_score)
    
    def get_algebra_progress(self, username: str) -> Dict:
        """Get detailed algebra learning progress"""
        student = self.db.get_student(username)
        if not student:
            return {}
        
        current_level = student['level']
        milestone = self.algebra_milestones[current_level]
        
        completed_lessons = len(student.get('completed_lessons', []))
        performance_score = student.get('performance_score', 0)
        
        # Calculate progress towards next level
        level_order = ['beginner', 'intermediate', 'advanced']
        current_index = level_order.index(current_level)
        
        if current_index < len(level_order) - 1:
            next_level = level_order[current_index + 1]
            next_milestone = self.algebra_milestones[current_level]
            lessons_needed = max(0, next_milestone['required_lessons'] - completed_lessons)
            score_needed = 0
        else:
            next_level = current_level
            lessons_needed = 0
            score_needed = 0
        
        return {
            'current_level': current_level,
            'next_level': next_level,
            'performance_score': performance_score,
            'completed_lessons': completed_lessons,
            'completed_exercises': len(student.get('completed_exercises', [])),
            'target_score': milestone['target_score'],
            'required_lessons': milestone['required_lessons'],
            'level_description': milestone['description'],
            'questions_attempted': len(student.get('seen_questions', [])),
            'lessons_needed': lessons_needed,
            'score_needed': score_needed 
        }
    
    def update_level_progression(self, username: str, completed_lesson_id: str):
        """Update student level based on completed lessons only"""
        student = self.db.get_student(username)
        if not student:
            return
        
        current_level = student['level']
        completed_lessons = len(student.get('completed_lessons', []))
        
        progression_rules = {
            'beginner': {
                'required_lessons': 2, 
                'next_level': 'intermediate'
            },
            'intermediate': {
                'required_lessons': 4, 
                'next_level': 'advanced'
            },
            'advanced': {
                'required_lessons': 6, 
                'next_level': 'advanced' 
            }
        }
        
        # Can't progress beyond advanced
        if current_level == 'advanced':
            return False
        
        rule = progression_rules.get(current_level)
        if not rule:
            return False
        
        # Check if student meets criteria for next level 
        if completed_lessons >= rule['required_lessons']:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET level = ? WHERE username = ?",
                (rule['next_level'], username)
            )
            conn.commit()
            conn.close()
            
            print(f"🎉 {username} leveled up from {current_level} to {rule['next_level']}!")
            return True
        
        return False