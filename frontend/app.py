import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import SQLiteManager
from backend.csp_solver import CSPSolver
from backend.student_model import StudentModel
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# Initialize components
db = SQLiteManager()
csp_solver = CSPSolver(db)
student_model = StudentModel(db)

def init_session_state():
    """Initialize session state"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    if 'current_lesson' not in st.session_state:
        st.session_state.current_lesson = None
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

def clear_quiz_state(lesson_id):
    """Clear quiz state for a specific lesson"""
    quiz_key = f'quiz_{lesson_id}'
    if quiz_key in st.session_state.quiz_data:
        del st.session_state.quiz_data[quiz_key]

def login_page():
    st.title("🎓 Algebra Intelligent Tutoring System")
    st.markdown("### Master Algebra with Personalized AI Tutoring")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        # Use a unique key for login form
        with st.form("login_form_" + str(hash("login"))):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("Login", type="primary")
            
            if login_btn:
                if username.strip() and password.strip():
                    student = db.get_student(username)
                    if student and db.verify_student_password(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = student['student_id']
                        st.session_state.current_page = "dashboard"
                        st.success(f"Welcome back, {student['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        # Use a unique key for register form
        with st.form("register_form_" + str(hash("register"))):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Choose Username", placeholder="Choose a unique username")
            password = st.text_input("Choose Password", type="password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            age = st.number_input("Age", min_value=4, max_value=99, value=15)
            # level = st.selectbox("Starting Level", ["beginner", "intermediate", "advanced"])
            register_btn = st.form_submit_button("Register", type="primary")
            
            if register_btn:
                if name.strip() and username.strip() and password.strip():
                    if password != confirm_password:
                        st.error("Passwords do not match!")
                    elif len(password) < 5:
                        st.error("Password must be at least 5 characters long")
                    else:
                        if db.get_student(username):
                            st.error("Username already exists. Please choose another.")
                        else:
                            student_id = db.add_student(name, "beginner", username, age, password)
                            st.success("Registration successful! Please login with your new account.")
                else:
                    st.error("Please fill all required fields")

def display_quiz_interface(lesson_id):
    """Display quiz for a lesson with new questions on each attempt and 50% passing threshold"""
    # Check if student can take this quiz
    if not csp_solver.can_take_quiz(st.session_state.username, lesson_id):
        st.error("🚫 Quiz Locked! You cannot take this quiz yet.")
        st.info("""
        **Requirements to unlock this quiz:**
        - Complete all prerequisite lessons
        - Reach the appropriate skill level
        - Complete previous lessons in sequence
        """)
        
        # Show what's needed
        student = db.get_student(st.session_state.username)
        lesson = db.get_lesson(lesson_id)
        
        if lesson:
            st.warning(f"**This quiz requires:** {lesson['level'].title()} level")
            st.write(f"**Your current level:** {student['level'].title()}")
            
            if lesson.get('prerequisites'):
                st.write("**Prerequisite lessons:**")
                for prereq_id in lesson['prerequisites']:
                    prereq_lesson = db.get_lesson(prereq_id)
                    if prereq_lesson:
                        completed = prereq_id in student.get('completed_lessons', [])
                        status = "✅ Completed" if completed else "❌ Not Completed"
                        st.write(f"- {prereq_lesson['title']} - {status}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 View Learning Path", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        with col2:
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        return
    
    lesson = db.get_lesson(lesson_id)
    if not lesson:
        st.error("Lesson not found!")
        return
    
    st.title(f"📝 Quiz: {lesson['title']}")
    
    # Initialize quiz state
    quiz_key = f'quiz_{lesson_id}'
    if quiz_key not in st.session_state.quiz_data:
        st.session_state.quiz_data[quiz_key] = {
            'questions': [],
            'answers': {},
            'submitted': False,
            'score': 0,
            'started': False,
            'question_ids': [], 
            'total_questions': 0
        }
    
    quiz_state = st.session_state.quiz_data[quiz_key]
    
    # Load NEW questions each time quiz is started or restarted
    if not quiz_state['started'] or not quiz_state['questions']:
        # Get previous quiz attempts to exclude those questions
        previous_attempts = db.get_student_quiz_history(st.session_state.username, lesson_id)
        
        # Get new quiz questions excluding previous ones
        quiz_questions = db.get_quiz_questions(
            lesson_id, 
            count=5,  # 5 questions per quiz
            exclude_previous=previous_attempts
        )

        if not quiz_questions:
            st.warning("⚠️ You've attempted most available quiz questions!")
            # Fallback: allow repeating questions if all have been used
            quiz_questions = db.get_quiz_questions(lesson_id, count=5)
        
        if quiz_questions:
            quiz_state['questions'] = quiz_questions
            quiz_state['question_ids'] = [q['ex_id'] for q in quiz_questions]
            quiz_state['started'] = True
            quiz_state['submitted'] = False
            quiz_state['answers'] = {}
            quiz_state['score'] = 0
            quiz_state['total_questions'] = len(quiz_questions)
        else:
            st.error("No quiz questions available for this lesson.")
            if st.button("← Back to Lesson"):
                st.session_state.current_page = "lesson"
                st.rerun()
            return
    
    if not quiz_state['submitted']:
        # Display quiz instructions
        st.info(f"📋 This quiz has {quiz_state['total_questions']} questions. You need 50% to pass.")
        st.warning("🎯 **Performance scoring is based only on quiz results.**")
        st.warning("⚠️ Please complete the quiz in one session.")
        
        # Display quiz questions
        st.write("### Questions:")
        
        for i, question in enumerate(quiz_state['questions'], 1):
            st.markdown(f"**{i}. {question['question']}**")
            
            answer_key = f"q{i}"
            
            # Initialize answer if not exists
            if answer_key not in quiz_state['answers']:
                quiz_state['answers'][answer_key] = ""
            
            user_answer = st.text_input(
                f"Your answer for question {i}:",
                value=quiz_state['answers'][answer_key],
                key=f"{quiz_key}_{answer_key}",
                placeholder="Enter your answer here..."
            )
            
            quiz_state['answers'][answer_key] = user_answer
            
            st.divider()
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Submit Quiz", type="primary", use_container_width=True):
                # Validate that all questions are answered
                unanswered_questions = []
                for i in range(1, len(quiz_state['questions']) + 1):
                    if not quiz_state['answers'].get(f"q{i}", "").strip():
                        unanswered_questions.append(i)
                
                if unanswered_questions:
                    st.error(f"❌ Please answer questions: {', '.join(map(str, unanswered_questions))}")
                else:
                    score = 0
                    total = len(quiz_state['questions'])

                    for i, question in enumerate(quiz_state['questions'], 1):
                        answer_key = f"q{i}"
                        user_answer = quiz_state['answers'][answer_key].strip()
                        correct_answer = question['answer']
                        
                        # Check if answer is correct
                        if csp_solver._flexible_answer_match(user_answer, correct_answer):
                            score += 1

                    quiz_state['score'] = score
                    quiz_state['submitted'] = True
                    quiz_state['total_questions'] = total

                    # Save quiz results with 50% passing threshold
                    passed = score >= (total * 0.5) 
                    db.save_quiz_results(
                        st.session_state.username,
                        lesson_id,
                        score,
                        total,
                        passed,
                        quiz_state['question_ids']
                    )

                    if passed:
                        student_model.update_performance(
                            st.session_state.username, 
                            f"quiz_{lesson_id}", 
                            True 
                        )
                        
                        # Mark lesson as completed automatically
                        db.update_student_progress(
                            st.session_state.username, 
                            completed_lesson=lesson_id
                        )
                        
                        student_model.update_level_progression(st.session_state.username, lesson_id)
                        st.balloons()
                    else:
                        student_model.update_performance(
                            st.session_state.username, 
                            f"quiz_{lesson_id}", 
                            False 
                        )
                    st.rerun()
        
        # Restart quiz button
        with col1:
            if st.button("🔄 Restart Quiz", use_container_width=True):
                clear_quiz_state(lesson_id)
                st.rerun()
        
        # Back to lesson button
        with col3:
            if st.button("← Back to Lesson", use_container_width=True):
                st.session_state.current_page = "lesson"
                st.rerun()
    
    else:
        # Show quiz results
        score = quiz_state['score']
        total = quiz_state['total_questions']
        percentage = (score / total) * 100 if total > 0 else 0
        
        st.subheader("📊 Quiz Results")
        
        # Display score with emoji
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{score}/{total}")
        with col2:
            st.metric("Percentage", f"{percentage:.1f}%")
        with col3:
            status = "✅ Passed" if percentage >= 50 else "❌ Failed"
            st.metric("Status", status)
        
        if percentage >= 50:
            st.success("🎉 Congratulations! You passed the quiz!")
            st.info("📈 Your performance score has been updated based on this quiz.")
            st.balloons()
            
            # Check if this unlocks new levels
            student = db.get_student(st.session_state.username)
            current_level = student['level']
            
            if current_level == 'beginner' and lesson_id in ['ALG-BASIC-1', 'ALG-BASIC-2']:
                st.info("🌟 Great progress! You're mastering beginner algebra concepts.")
            elif current_level == 'intermediate' and lesson_id in ['ALG-INT-1', 'ALG-INT-2']:
                st.info("🌟 Excellent work! You're ready for more advanced algebra topics.")
            elif current_level == 'advanced':
                st.info("🌟 Impressive! You're tackling advanced algebra concepts.")
                
        else:
            st.warning("📚 Keep practicing! You need 50% to pass. Review the lesson and try again.")
            st.info("📉 Your performance score has been adjusted based on this quiz attempt.")
        
        # Show detailed results
        with st.expander("📝 Review Your Answers", expanded=True):
            for i, question in enumerate(quiz_state['questions'], 1):
                answer_key = f"q{i}"
                user_answer = quiz_state['answers'][answer_key]
                correct_answer = question['answer']
                is_correct = csp_solver._flexible_answer_match(user_answer.strip(), correct_answer)
                
                st.markdown(f"**Question {i}: {question['question']}**")
                st.markdown(f"**Your answer:** {user_answer} {'✅' if is_correct else '❌'}")
                st.markdown(f"**Correct answer:** {correct_answer}")
                
                if question.get('explanation'):
                    st.markdown(f"**Explanation:** {question['explanation']}")
                
                st.divider()
        
        # Navigation buttons after quiz
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Take New Quiz", use_container_width=True):
                clear_quiz_state(lesson_id)
                st.rerun()
        
        with col2:
            if st.button("📚 Back to Lesson", use_container_width=True):
                st.session_state.current_page = "lesson"
                st.rerun()
        
        with col3:
            if st.button("🏠 Dashboard", type="primary", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()

def clear_quiz_state(lesson_id):
    """Clear quiz state for a specific lesson"""
    quiz_key = f'quiz_{lesson_id}'
    if quiz_key in st.session_state.quiz_data:
        del st.session_state.quiz_data[quiz_key]

def display_lesson_interface(lesson_id):
    """Display interactive lesson content with enhanced practice system and quiz integration"""
    student = db.get_student(st.session_state.username)
    lesson = db.get_lesson(lesson_id)
    
    if not lesson:
        st.error("Lesson not found!")
        return
    
    completed_lessons = set(student.get('completed_lessons', []))
    lesson_prerequisites = lesson.get('prerequisites', [])
    prerequisites_met = all(prereq in completed_lessons for prereq in lesson_prerequisites)
    
    # Check level appropriateness
    level_weights = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
    student_level_num = level_weights.get(student['level'], 0)
    lesson_level_num = level_weights.get(lesson['level'], 0)
    level_appropriate = lesson_level_num <= student_level_num + 1
    
    if not prerequisites_met or not level_appropriate:
        st.error("🚫 Access Denied! You don't meet the requirements for this lesson.")
        
        if not prerequisites_met and lesson_prerequisites:
            st.warning("**Complete these prerequisite lessons first:**")
            for prereq_id in lesson_prerequisites:
                prereq_lesson = db.get_lesson(prereq_id)
                if prereq_lesson:
                    completed = prereq_id in completed_lessons
                    status = "✅ Completed" if completed else "❌ Missing"
                    st.write(f"- **{prereq_lesson['title']}** - {status}")
        
        if not level_appropriate:
            st.warning(f"**Level restriction:** This lesson requires {lesson['level']} level. Your current level is {student['level']}.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 View Learning Path", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        with col2:
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        return
    
    # If access granted, show the lesson content
    st.title(f"📚 {lesson['title']}")
    
    # Progress tracking
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Level", lesson['level'].title())
    with col2:
        st.metric("Duration", f"{lesson['duration_minutes']} min")
    with col3:
        completion_status = "🔴 Not Started"
        if lesson_id in student.get('completed_lessons', []):
            completion_status = "✅ Completed"
        st.metric("Status", completion_status)
    
    # Display lesson content
    st.markdown("### 📖 Lesson Content")
    
    # Display the actual lesson content
    lesson_content = lesson.get('content', '')
    if lesson_content and lesson_content.strip():
        st.markdown(lesson_content)
    else:
        st.info("No content available for this lesson.")
    
    # Interactive examples
    examples = lesson.get('examples', [])
    if examples and len(examples) > 0:
        st.markdown("### 🎯 Interactive Examples")
        
        # Initialize session state for examples if not exists
        examples_key = f"examples_{lesson_id}"
        if examples_key not in st.session_state:
            st.session_state[examples_key] = {}
        
        for i, example in enumerate(examples, 1):
            example_key = f"example_{i}"
            example_problem = example.get('problem', 'Algebra Problem')
            
            with st.expander(f"Example {i}: {example_problem}", expanded=False):
                st.write(f"**Problem:** {example_problem}")
                
                # Check if solution is revealed
                if st.session_state[examples_key].get(example_key, False):
                    st.success(f"**Solution:** {example.get('solution', 'No solution available')}")
                    st.info(f"**Explanation:** {example.get('explanation', 'No explanation available')}")
                else:
                    if st.button(f"Reveal Solution", key=f"sol_{lesson_id}_{i}"):
                        st.session_state[examples_key][example_key] = True
                        st.rerun()
    else:
        st.info("No interactive examples available for this lesson.")
    
    st.markdown("### 💪 Practice Questions")
    st.write("Complete all 5 questions in your current session before requesting new ones.")
    st.info("💡 **Practice questions don't affect your performance score.**")
    
    # Initialize practice session state with completion tracking
    practice_key = f'practice_{lesson_id}'
    if practice_key not in st.session_state:
        st.session_state[practice_key] = {
            'current_questions': [],
            'used_question_ids': [],
            'session_count': 0,
            'current_answers': {},
            'checked_questions': set(),
            'completed_questions': set() 
        }
    
    practice_state = st.session_state[practice_key]
    
    # Load or reload practice questions (5 per session)
    if not practice_state['current_questions']:
        # Get student's previously used questions
        session_data = db.get_student_practice_session(st.session_state.username, lesson_id)
        used_questions = session_data['used_questions']
        
        # Get new practice questions excluding used ones
        new_questions = db.get_practice_questions(
            lesson_id, 
            count=5,  # 5 questions per session
            exclude_used=used_questions
        )
        
        if new_questions:
            practice_state['current_questions'] = new_questions
            practice_state['used_question_ids'].extend([q['question_id'] for q in new_questions])
            practice_state['session_count'] += 1
            practice_state['current_answers'] = {}
            practice_state['checked_questions'] = set()
            practice_state['completed_questions'] = set()  # Reset completion tracking
            
            # Update student's practice session
            db.update_student_practice_session(
                st.session_state.username, 
                lesson_id, 
                [q['question_id'] for q in new_questions]
            )
        else:
            st.info("🎉 Amazing! You've completed all available practice questions for this lesson!")
    
    # Display current practice questions
    if practice_state['current_questions']:
        st.write(f"**Practice Session {practice_state['session_count']}** (5 questions)")
        
        # Show completion progress
        completed_count = len(practice_state['completed_questions'])
        total_questions = len(practice_state['current_questions'])
        progress = completed_count / total_questions
        
        st.progress(progress)
        st.write(f"**Progress:** {completed_count}/{total_questions} questions completed")
        
        for i, question in enumerate(practice_state['current_questions'], 1):
            st.markdown(f"**Question {i}:** {question['question']}")
            
            # Practice question interface
            answer_key = f"practice_ans_{lesson_id}_{question['question_id']}"
            
            # Initialize answer if not exists
            if answer_key not in practice_state['current_answers']:
                practice_state['current_answers'][answer_key] = ''
            
            user_answer = st.text_input(
                "Your answer:",
                value=practice_state['current_answers'][answer_key],
                key=answer_key,
                placeholder="Enter your solution..."
            )
            
            # Update stored answer
            practice_state['current_answers'][answer_key] = user_answer
            
            col1, col2 = st.columns(2)
            
            with col1:
                check_key = f"check_{answer_key}"
                if st.button(f"Check Answer", key=check_key):
                    if user_answer.strip():
                        is_correct = csp_solver._flexible_answer_match(user_answer.strip(), question['answer'])
                        practice_state['checked_questions'].add(question['question_id'])
                        
                        # Mark as completed when checked 
                        practice_state['completed_questions'].add(question['question_id'])
                        
                        db.mark_practice_completed(st.session_state.username, question['question_id'], is_correct)
                        
                        if is_correct:
                            st.success("✅ Correct! Well done!")
                        else:
                            st.error(f"❌ Not quite right. The correct answer is: {question['answer']}")
                        
                        if question.get('explanation'):
                            st.info(f"**Explanation:** {question['explanation']}")
                    else:
                        st.warning("Please enter an answer before checking.")
            
            with col2:
                hint_key = f"hint_{answer_key}"
                if st.button(f"💡 Hint", key=hint_key):
                    st.info(f"**Hint:** {question.get('hint', 'Think step by step!')}")
            
            # Show previous result if already checked
            if question['question_id'] in practice_state['checked_questions']:
                # Re-check to show persistent result
                user_answer = practice_state['current_answers'][answer_key]
                if user_answer.strip():
                    is_correct = csp_solver._flexible_answer_match(user_answer.strip(), question['answer'])
                    if is_correct:
                        st.success("✅ Your answer was correct!")
                    else:
                        st.error("❌ Your previous answer was incorrect.")
            
            st.divider()
        
        # "More Practice" button - ONLY available when all questions are completed
        col1, col2, col3 = st.columns([1, 2, 1])
        
        all_questions_completed = len(practice_state['completed_questions']) == len(practice_state['current_questions'])
        
        with col2:
            if all_questions_completed:
                if st.button("🔄 Get New Practice Session (5 Questions)", type="primary", use_container_width=True):
                    # Clear current questions to get new ones
                    practice_state['current_questions'] = []
                    st.rerun()
            else:
                remaining = len(practice_state['current_questions']) - len(practice_state['completed_questions'])
                st.button(
                    f"Complete {remaining} more question(s) to continue", 
                    use_container_width=True, 
                    disabled=True,
                    help="You must complete all questions in your current session before starting a new one"
                )
        
        # Show session statistics
        checked_count = len(practice_state['checked_questions'])
        completed_count = len(practice_state['completed_questions'])
        st.info(f"**Session Progress:** {completed_count}/5 questions completed")
        
    else:
        st.info("Click the button below to start a new practice session with 5 questions!")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Start Practice Session (5 Questions)", type="primary", use_container_width=True):
                practice_state['current_questions'] = []
                st.rerun()
    
    # Quiz Section - Updated with 50% passing threshold
    st.markdown("### 🎯 Lesson Quiz")
    st.write("Take the quiz to test your understanding and update your performance score.")
    st.warning("📊 **Performance scoring is based only on quiz results. Need 50% to pass.**")
    
    # Check quiz status
    quiz_key = f'quiz_{lesson_id}'
    has_quiz_data = quiz_key in st.session_state.quiz_data
    quiz_passed = db.has_passed_quiz(st.session_state.username, lesson_id)
    current_quiz_submitted = has_quiz_data and st.session_state.quiz_data[quiz_key].get('submitted', False)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        quiz_button_text = "📝 Take Quiz (5 Questions)"
        if has_quiz_data and not current_quiz_submitted:
            quiz_button_text = "📝 Continue Quiz"
        
        if st.button(quiz_button_text, type="primary", use_container_width=True):
            st.session_state.current_page = "quiz"
            st.session_state.current_lesson = lesson_id
            st.rerun()
    
    with col2:
        if quiz_passed:
            st.success("✅ Quiz Passed - Lesson automatically marked as complete!")
            if lesson_id not in student.get('completed_lessons', []):
                st.info("🔄 System is updating your progress...")
            else:
                st.success("✅ Lesson Completed")
    
    with col3:
        if st.button("← Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.session_state.current_lesson = None
            st.rerun()
    
    # Progress encouragement
    st.markdown("---")
    st.write(f"**📈 Your current performance: {student.get('performance_score', 0)}%**")

    # Show what's needed for next level
    progress = student_model.get_algebra_progress(st.session_state.username)

    if progress and progress.get('lessons_needed', 0) > 0:
        st.info(f"**🎯 To reach {progress.get('next_level', 'next level').title()}: "
                f"Need {progress.get('lessons_needed', 0)} more lessons**")

def main_dashboard():
    """Enhanced main dashboard with personalized content"""
    student = db.get_student(st.session_state.username)
    
    # Sidebar with comprehensive student info
    st.sidebar.title(f"👤 {student['name']}")
    st.sidebar.markdown(f"**Username:** {st.session_state.username}")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("📊 Your Progress")
    
    # Progress metrics
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Level", student['level'].title())
        st.metric("Lessons", len(student.get('completed_lessons', [])))
    with col2:
        st.metric("Performance", f"{student.get('performance_score', 0)}%")
        st.metric("Exercises", len(student.get('completed_exercises', [])))
    
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Quick Actions")
    
    if st.sidebar.button("🔄 Generate New Learning Path", use_container_width=True):
        with st.spinner("Creating your personalized learning path..."):
            learning_path = csp_solver.generate_learning_path(st.session_state.username)
            if learning_path:
                st.sidebar.success("New path generated!")
            else:
                st.sidebar.warning("Complete more lessons for better recommendations")
    
    # FIXED LOGOUT BUTTON
    st.sidebar.markdown("---")
    st.sidebar.subheader("Account")
    
    # Simple logout button without confirmation checkbox
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        # Clear all session state
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_id = None
        st.session_state.current_page = "dashboard"
        st.session_state.current_lesson = None
        st.session_state.quiz_data = {}
        st.session_state.quiz_submitted = False
        
        st.success("Logged out successfully!")
        st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 Learning Path",  
        "📚 Curriculum", 
        "🏆 Achievements"
    ])
    
    with tab1:
        display_learning_path(student)
    
    with tab2:
        display_curriculum_browser(student)
    
    with tab3:
        display_achievements(student)

def display_learning_path(student):
    """Display personalized learning path with intelligent recommendations"""
    st.header("🎯 Your Personalized Learning Path")
    st.write("This path is optimized based on your current level and performance")
    
    # Generate or get current learning path
    learning_path = csp_solver.generate_learning_path(st.session_state.username, max_lessons=5)
    
    if not learning_path:
        st.info("📝 Let me recommend some great starter lessons for you!")
        st.markdown("### 🚀 Get Started")
        
        # Get recommended beginner lessons
        recommended_lessons = csp_solver.get_recommended_lessons(st.session_state.username, count=3)
        
        if not recommended_lessons:
            # Fallback: show any beginner lessons
            recommended_lessons = db.get_lessons_by_level("beginner")[:3]
        
        for lesson in recommended_lessons:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(lesson['title'])
                st.write(f"⏱️ {lesson['duration_minutes']} min | 🎯 {lesson['level'].title()}")
                # st.write(lesson['content'][:100] + "...")
            with col2:
                if st.button("Start", key=f"start_{lesson['lesson_id']}"):
                    st.session_state.current_page = "lesson"
                    st.session_state.current_lesson = lesson['lesson_id']
                    st.rerun()
            st.divider()
        return
    
    # Display learning path
    st.success(f"🌟 Personalized path with {len(learning_path)} recommended lessons")
    
    for i, lesson_id in enumerate(learning_path, 1):
        lesson = db.get_lesson(lesson_id)
        if not lesson:
            continue
            
        completed = lesson_id in student.get('completed_lessons', [])
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Status indicator
            status_icon = "✅" if completed else "🔄"
            st.subheader(f"{status_icon} {i}. {lesson['title']}")
            
            # Progress and info
            level_indicator = f"🎯 {lesson['level'].title()}"
            duration_info = f"⏱️ {lesson['duration_minutes']} min"
            prereq_info = f"📋 Prereqs: {', '.join(lesson['prerequisites']) or 'None'}"
            
            st.write(f"{level_indicator} | {duration_info} | {prereq_info}")
            # st.write(lesson['content'][:120] + "...")
        
        with col2:
            # Access status
            if completed:
                st.success("Completed")
            else:
                st.info("Ready to Start")
        
        with col3:
            # Action buttons
            if not completed:
                if st.button("Start Lesson", key=f"path_{lesson_id}"):
                    st.session_state.current_page = "lesson"
                    st.session_state.current_lesson = lesson_id
                    st.rerun()
            else:
                if st.button("Review", key=f"review_{lesson_id}"):
                    st.session_state.current_page = "lesson"
                    st.session_state.current_lesson = lesson_id
                    st.rerun()
        
        st.divider()
    
    # Path completion analytics
    completed_in_path = sum(1 for lesson_id in learning_path if lesson_id in student.get('completed_lessons', []))
    completion_rate = (completed_in_path / len(learning_path)) * 100 if learning_path else 0
    
    st.metric("Path Completion", f"{completion_rate:.1f}%")
    st.progress(completion_rate / 100)

def display_curriculum_browser(student):
    """Enhanced curriculum browser with CSP filtering"""
    st.header("📚 Algebra Curriculum")
    st.write("Browse lessons available to you based on your progress")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        level_filter = st.selectbox(
            "Filter by Level",
            ["all", "beginner", "intermediate", "advanced"]
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["all", "completed", "accessible", "locked"]
        )
    
    # Get accessible lessons based on CSP
    accessible_lessons = csp_solver.get_accessible_lessons(st.session_state.username)
    all_lessons = db.get_all_lessons()
    
    filtered_lessons = []
    for lesson in all_lessons:
        # Check accessibility
        is_accessible = any(acc_lesson['lesson_id'] == lesson['lesson_id'] for acc_lesson in accessible_lessons)
        is_completed = lesson['lesson_id'] in student.get('completed_lessons', [])
        
        # Level filter
        if level_filter != "all" and lesson['level'] != level_filter:
            continue
        
        # Status filter
        if status_filter == "completed" and not is_completed:
            continue
        elif status_filter == "accessible" and (not is_accessible or is_completed):
            continue
        elif status_filter == "locked" and is_accessible:
            continue
        
        # Add accessibility info
        lesson['accessible'] = is_accessible
        filtered_lessons.append(lesson)
    
    # Display lessons with accessibility status
    if not filtered_lessons:
        st.info("No lessons match your filters. Try adjusting your search criteria.")
        return
    
    st.write(f"**Found {len(filtered_lessons)} lessons**")
    
    for lesson in filtered_lessons:
        completed = lesson['lesson_id'] in student.get('completed_lessons', [])
        accessible = lesson['accessible']
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Status indicator
            if completed:
                status_icon = "✅"
                status_text = "Completed"
            elif accessible:
                status_icon = "📖"
                status_text = "Available"
            else:
                status_icon = "🔒"
                status_text = "Locked"
            
            st.subheader(f"{status_icon} {lesson['title']}")
            
            # Lesson info
            level_badge = f"**Level:** {lesson['level'].title()}"
            duration_badge = f"**Duration:** {lesson['duration_minutes']} min"
            
            st.write(f"{level_badge} | {duration_badge} | **Status:** {status_text}")
            
            if not accessible and lesson.get('prerequisites'):
                st.write("**Requires:** " + ", ".join(lesson['prerequisites']))
        
        with col2:
            # Access information
            if completed:
                st.success("✅ Completed")
            elif accessible:
                st.info("📖 Available")
            else:
                st.warning("🔒 Locked")
        
        with col3:
            # Action buttons
            if accessible and not completed:
                if st.button("Start", key=f"browse_{lesson['lesson_id']}"):
                    st.session_state.current_page = "lesson"
                    st.session_state.current_lesson = lesson['lesson_id']
                    st.rerun()
            elif completed:
                if st.button("Review", key=f"review_browse_{lesson['lesson_id']}"):
                    st.session_state.current_page = "lesson"
                    st.session_state.current_lesson = lesson['lesson_id']
                    st.rerun()
            else:
                st.button("Locked", key=f"locked_{lesson['lesson_id']}", disabled=True)
        
        st.divider()

def display_achievements(student):
    """Display student achievements and progress analytics"""
    st.header("🏆 Your Learning Achievements")
    
    # Overall progress
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_lessons = len(db.get_all_lessons())
        completed_lessons = len(student.get('completed_lessons', []))
        completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        st.metric("Course Completion", f"{completion_rate:.1f}%")
    
    with col2:
        st.metric("Current Level", student['level'].title())
    
    with col3:
        performance = student.get('performance_score', 0)
        st.metric("Performance Score", f"{performance}%")
    
    # Practice Questions Progress (Simplified - no JSON parsing)
    practice_count = 0
    practice_sessions = student.get('practice_sessions', {})
    
    # Handle both string and dict formats safely
    if isinstance(practice_sessions, str):
        # If it's a string, try to count questions from all lessons
        # This is a fallback - ideally practice_sessions should be a dict
        practice_count = len(student.get('completed_exercises', []))  # Fallback count
    else:
        # If it's already a dict, count questions normally
        for lesson_id, session_data in practice_sessions.items():
            if isinstance(session_data, dict):
                practice_count += len(session_data.get('used_questions', []))
    
    # Show practice progress
    st.subheader("📊 Practice Progress")
    st.metric("Practice Questions Completed", practice_count)
    
    # Practice progress bar
    if practice_count > 0:
        practice_progress = min(practice_count / 70, 1.0)
        st.progress(practice_progress)
        st.caption(f"Progress towards Practice Master badge: {practice_count}/70 questions")
    
    # Level Progression Information
    st.subheader("🎯 Level Progression")
    
    from backend.student_model import StudentModel
    temp_model = StudentModel(db)
    progress = temp_model.get_algebra_progress(st.session_state.username)
    
    if progress:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Current Level:** {progress['current_level'].title()}")
            st.write(f"**Completed Lessons:** {progress['completed_lessons']}/{progress['required_lessons']}")
        
        with col2:
            st.write(f"**Performance Score:** {progress['performance_score']}%")
            st.write(f"**Next Level:** {progress.get('next_level', 'Max Level').title()}")
    
    # Achievement badges
    st.subheader("🎖️ Your Badges")
    
    badges = []
    completed_lessons = len(student.get('completed_lessons', []))
    performance = student.get('performance_score', 0)
    
    # Lesson-based badges
    if completed_lessons >= 1:
        badges.append(("🚀 First Steps", "Completed your first algebra lesson"))
    if completed_lessons >= 3:
        badges.append(("📚 Dedicated Learner", "Completed 3 algebra lessons"))
    
    # Performance-based badges
    if performance >= 80:
        badges.append(("⭐ Algebra Whiz", "Maintained 80%+ performance"))
    
    # Level-based badges
    if student['level'] == 'intermediate':
        badges.append(("🎯 Level Up", "Reached intermediate algebra"))
    if student['level'] == 'advanced':
        badges.append(("🏆 Algebra Master", "Reached advanced algebra"))
    
    # Practice-based badges
    if practice_count >= 70:
        badges.append(("💪 Practice Master", f"Completed {practice_count}+ practice questions!"))
    elif practice_count >= 50:
        badges.append(("📝 Practice Enthusiast", f"Completed {practice_count} practice questions"))
    elif practice_count >= 25:
        badges.append(("✏️ Practice Learner", f"Completed {practice_count} practice questions"))
    
    # Display badges
    if badges:
        cols = st.columns(3)
        for i, (badge, description) in enumerate(badges):
            with cols[i % 3]:
                if "Master" in badge:
                    st.success(f"**{badge}**\n\n{description}")
                else:
                    st.info(f"**{badge}**\n\n{description}")
    else:
        st.info("Complete algebra lessons and practice questions to earn badges!")

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Algebra ITS - Intelligent Tutoring System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .achievement-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Application routing
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.current_page == "quiz" and st.session_state.current_lesson:
            display_quiz_interface(st.session_state.current_lesson)
        elif st.session_state.current_page == "lesson" and st.session_state.current_lesson:
            display_lesson_interface(st.session_state.current_lesson)
        else:
            main_dashboard()

if __name__ == "__main__":
    main()


