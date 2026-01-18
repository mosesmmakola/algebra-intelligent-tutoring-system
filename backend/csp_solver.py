import random
from typing import List, Dict, Tuple
import re

class CSPSolver:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def can_access_lesson(self, username: str, lesson_id: str) -> bool:
        """Check if student can access a lesson based on CSP constraints"""
        student = self.db.get_student(username)
        if not student:
            return False
        
        lesson = self.db.get_lesson(lesson_id)
        if not lesson:
            return False
        
        # Check level appropriateness
        level_weights = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
        student_level_num = level_weights.get(student['level'], 0)
        lesson_level_num = level_weights.get(lesson['level'], 0)
        
        if lesson_level_num > student_level_num + 1:
            return False
        
        # All prerequisites must be completed
        prerequisites = lesson.get('prerequisites', [])
        completed_lessons = set(student.get('completed_lessons', []))
        
        for prereq in prerequisites:
            if prereq not in completed_lessons:
                return False
        
        return True
    
    def can_take_quiz(self, username: str, lesson_id: str) -> bool:
        """Check if student can take quiz for a lesson"""
        # Must be able to access the lesson first
        if not self.can_access_lesson(username, lesson_id):
            return False
        
        return True
    
    def get_accessible_lessons(self, username: str) -> List[Dict]:
        """Get all lessons that student can access based on CSP constraints"""
        student = self.db.get_student(username)
        if not student:
            return []
        
        all_lessons = self.db.get_all_lessons()
        accessible_lessons = []
        
        for lesson in all_lessons:
            if self.can_access_lesson(username, lesson['lesson_id']):
                accessible_lessons.append(lesson)
        
        return accessible_lessons

    def generate_learning_path(self, username: str, max_lessons: int = 5) -> List[str]:
        """Generate personalized algebra learning path with CSP enforcement"""
        student = self.db.get_student(username)
        if not student:
            return []
        
        # Get only accessible lessons
        accessible_lessons = self.get_accessible_lessons(username)
        completed_lessons = set(student.get('completed_lessons', []))
        
        # Filter out completed lessons
        available_lessons = [lesson for lesson in accessible_lessons 
                           if lesson['lesson_id'] not in completed_lessons]
        
        if not available_lessons:
            return []
        
        # Prioritize lessons based on algebra learning sequence
        learning_path = self._prioritize_algebra_lessons(available_lessons, student['level'], max_lessons)
        
        return learning_path
    
    def _filter_algebra_lessons(self, all_lessons: List[Dict], completed_lessons: set, student_level: str) -> List[Dict]:
        """Filter algebra lessons based on level and prerequisites - ENHANCED with CSP"""
        level_weights = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
        student_level_num = level_weights.get(student_level, 0)
        
        accessible_lessons = []
        
        for lesson in all_lessons:
            # Skip completed lessons
            if lesson['lesson_id'] in completed_lessons:
                continue
            
            # Check level appropriateness 
            lesson_level_num = level_weights.get(lesson['level'], 0)
            if lesson_level_num > student_level_num: 
                continue
            
            # Check prerequisites - ALL must be completed
            prerequisites_met = all(prereq in completed_lessons for prereq in lesson.get('prerequisites', []))
            if not prerequisites_met:
                continue
            
            accessible_lessons.append(lesson)
        
        return accessible_lessons
    
    def _prioritize_algebra_lessons(self, available_lessons: List[Dict], student_level: str, max_lessons: int) -> List[str]:
        """Prioritize algebra lessons for optimal learning sequence with CSP"""
        if not available_lessons:
            return []
        
        scored_lessons = []
        
        for lesson in available_lessons:
            score = 0
            
            # Priority for current level
            if lesson['level'] == student_level:
                score += 10
            
            # Priority based on algebra topic sequence
            topic_priority = self._get_topic_priority(lesson)
            score += topic_priority
            
            # Priority for lessons with fewer prerequisites 
            prereq_count = len(lesson.get('prerequisites', []))
            score += max(0, 5 - prereq_count) 
            
            # Small random factor for variety
            score += random.uniform(0, 1)
            
            scored_lessons.append((score, lesson))
        
        # Sort by score and get top lessons
        scored_lessons.sort(key=lambda x: x[0], reverse=True)
        learning_path = [lesson['lesson_id'] for _, lesson in scored_lessons[:max_lessons]]
        
        return learning_path
    
    def _get_topic_priority(self, lesson: Dict) -> int:
        """Get priority score based on algebra topic importance"""
        topic_priorities = {
            'variables': 8,
            'basic equations': 7,
            'expressions': 6,
            'two-step equations': 5,
            'word problems': 4,
            'systems': 3,
            'quadratic': 2,
            'advanced': 1
        }
        
        # Check lesson tags for topic matches
        for tag in lesson.get('tags', []):
            for topic, priority in topic_priorities.items():
                if topic in tag.lower():
                    return priority
        
        return 1  # Default priority
    
    def get_recommended_lessons(self, username: str, count: int = 3) -> List[Dict]:
        """Get recommended lessons for quick start with CSP enforcement"""
        accessible_lessons = self.get_accessible_lessons(username)
        
        # Return lessons that have no prerequisites or met prerequisites
        recommended = []
        for lesson in accessible_lessons:
            if len(recommended) >= count:
                break
            recommended.append(lesson)
        
        return recommended

    def check_exercise_answer(self, exercise: Dict, student_answer: str) -> Tuple[bool, str]:
        """Enhanced answer checking with intelligent feedback"""
        correct_answer = str(exercise.get('answer', '')).strip().lower()
        student_answer_clean = str(student_answer).strip().lower()
        
        is_correct = self._flexible_answer_match(student_answer_clean, correct_answer)
        
        if is_correct:
            feedback = self._generate_correct_feedback(exercise, student_answer)
        else:
            feedback = self._generate_incorrect_feedback(exercise, student_answer, correct_answer)
        
        return is_correct, feedback
    
    def _flexible_answer_match(self, student_answer: str, correct_answer: str) -> bool:
        """Enhanced flexible answer matching to handle different formats"""
        
        # Clean both answers
        student_clean = student_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()
        
        # 1. Exact match
        if student_clean == correct_clean:
            return True
        
        # 2. Extract numeric values from "variable=value" format
        def extract_numeric_value(answer):
            # Handle formats like "x=5", "y = 7"
            if '=' in answer:
                parts = answer.split('=')
                if len(parts) == 2:
                    return parts[1].strip()
            return answer
        
        student_numeric = extract_numeric_value(student_clean)
        correct_numeric = extract_numeric_value(correct_clean)
        
        # 3. Try numeric comparison
        try:
            student_num = float(student_numeric)
            correct_num = float(correct_numeric)
            return abs(student_num - correct_num) < 0.001
        except (ValueError, TypeError):
            pass
        
        # 4. Handle different answer formats for systems and quadratics
        if "x=" in correct_clean and "y=" in correct_clean:
            return self._match_system_answer(student_clean, correct_clean)
        elif "," in correct_clean:
            return self._match_multiple_answers(student_clean, correct_clean)
        
        # 5. Case insensitive match
        if student_clean.lower() == correct_clean.lower():
            return True
        
        # 6. Remove spaces and compare
        if student_clean.replace(" ", "") == correct_clean.replace(" ", ""):
            return True
        
        return False
    
    def _match_system_answer(self, student_answer: str, correct_answer: str) -> bool:
        """Match system of equations answers"""
        try:
            # Extract x and y values from both answers
            student_parts = student_answer.replace("x=", "").replace("y=", "").split(",")
            correct_parts = correct_answer.replace("x=", "").replace("y=", "").split(",")
            
            if len(student_parts) != 2 or len(correct_parts) != 2:
                return False
            
            student_x = float(student_parts[0].strip())
            student_y = float(student_parts[1].strip())
            correct_x = float(correct_parts[0].strip())
            correct_y = float(correct_parts[1].strip())
            
            return (abs(student_x - correct_x) < 0.001 and 
                    abs(student_y - correct_y) < 0.001)
        except:
            return False
    
    def _match_multiple_answers(self, student_answer: str, correct_answer: str) -> bool:
        """Match multiple solution answers (like quadratics)"""
        try:
            student_solutions = [s.strip() for s in student_answer.split(",")]
            correct_solutions = [s.strip() for s in correct_answer.split(",")]
            
            if len(student_solutions) != len(correct_solutions):
                return False
            
            # Convert to floats and sort for comparison
            student_nums = sorted([float(s) for s in student_solutions])
            correct_nums = sorted([float(s) for s in correct_solutions])
            
            return all(abs(s - c) < 0.001 for s, c in zip(student_nums, correct_nums))
        except:
            return False
    
    def _generate_correct_feedback(self, exercise: Dict, student_answer: str) -> str:
        """Generate encouraging feedback for correct answers"""
        
        explanations = [
            f"🎉 **Excellent work!** Your answer '{student_answer}' is correct!\n\n{exercise.get('explanation', '')}",
            f"🌟 **Perfect!** '{student_answer}' is the right answer!\n\n{exercise.get('explanation', '')}",
            f"✅ **Correct!** Great job solving this algebra problem!\n\n{exercise.get('explanation', '')}",
            f"💡 **Brilliant thinking!** You got it right with '{student_answer}'!\n\n{exercise.get('explanation', '')}"
        ]
        
        return random.choice(explanations)
    
    def _generate_incorrect_feedback(self, exercise: Dict, student_answer: str, correct_answer: str) -> str:
        """Generate helpful feedback for incorrect answers"""
        
        hint = exercise.get('hint', '')
        explanation = exercise.get('explanation', '')
        
        feedback_templates = [
            f"🤔 Not quite. You answered '{student_answer}', but let's think this through.\n\n**Hint:** {hint}\n\n**Correct Answer:** {correct_answer}\n\n**Explanation:** {explanation}",
            f"📚 Good attempt! The answer was '{student_answer}', but we need '{correct_answer}'.\n\n**Hint:** {hint}\n\n**Explanation:** {explanation}",
            f"💭 Let's review this together. You said '{student_answer}', but here's the approach:\n\n**Hint:** {hint}\n\n**Correct Answer:** {correct_answer}\n\n**Explanation:** {explanation}"
        ]
        
        return random.choice(feedback_templates)