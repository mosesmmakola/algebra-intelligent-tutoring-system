import sqlite3
import json
import uuid
import random

class SQLiteManager:
    def __init__(self, db_path="math_its.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                level TEXT DEFAULT 'beginner',
                age INTEGER DEFAULT 15,
                performance_score REAL DEFAULT 0,
                completed_lessons TEXT DEFAULT '[]',
                completed_exercises TEXT DEFAULT '[]',
                seen_questions TEXT DEFAULT '[]',
                practice_sessions TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                lesson_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                level TEXT NOT NULL,
                prerequisites TEXT DEFAULT '[]',
                content TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 45,
                examples TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS practice_questions (
                question_id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                hint TEXT,
                explanation TEXT,
                difficulty TEXT DEFAULT 'medium',
                FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                question_id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                hint TEXT,
                explanation TEXT,
                difficulty TEXT DEFAULT 'medium',
                FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                passed BOOLEAN NOT NULL,
                quiz_data TEXT DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self._init_sample_data(cursor)
        conn.commit()
        conn.close()
    
    def _init_sample_data(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM lessons")
        if cursor.fetchone()[0] == 0:
            lessons = [
                ("ALG-BASIC-1", "Introduction to Variables", "beginner", '[]', 
                """# Introduction to Variables

## What are Variables?
Variables are symbols (like x, y, z) that represent unknown numbers in mathematical expressions and equations.

## Key Concepts:
- **Variables** stand for unknown values
- **Constants** are fixed numbers
- **Expressions** combine variables and constants with operations

## Examples:
- `x + 5` means "some number x plus 5"
- `3y` means "3 times some number y"
- `2x - 7` means "twice some number x minus 7"

## Real-world Applications:
- Calculating total costs: `total = price × quantity`
- Finding distances: `distance = speed × time`
- Solving for unknown quantities""", 
                45, 
                json.dumps([
                    {"problem": "If x = 3, what is x + 5?", "solution": "8", "explanation": "Substitute x with 3: 3 + 5 = 8"},
                    {"problem": "If y = 7, what is 2y?", "solution": "14", "explanation": "Multiply 2 times y: 2 × 7 = 14"},
                    {"problem": "If a = 10, what is a - 4?", "solution": "6", "explanation": "Subtract 4 from a: 10 - 4 = 6"}
                ]), 
                '["variables", "expressions"]'),
                
                ("ALG-BASIC-2", "Solving Basic Equations", "beginner", '["ALG-BASIC-1"]', 
                """# Solving Basic Equations

## What are Equations?
Equations are mathematical statements showing two expressions are equal, like `x + 3 = 8`.

## Solving Steps:
1. **Identify** the operation on the variable
2. **Apply inverse** operation to both sides
3. **Simplify** to find the solution
4. **Check** your answer

## Inverse Operations:
- Addition ↔ Subtraction
- Multiplication ↔ Division

## Examples:
- `x + 5 = 12` → Subtract 5 from both sides → `x = 7`
- `3y = 15` → Divide both sides by 3 → `y = 5`""", 
                50, 
                json.dumps([
                    {"problem": "Solve: x + 7 = 15", "solution": "x = 8", "explanation": "Subtract 7 from both sides: x = 15 - 7 = 8"},
                    {"problem": "Solve: 4y = 20", "solution": "y = 5", "explanation": "Divide both sides by 4: y = 20 ÷ 4 = 5"},
                    {"problem": "Solve: x - 3 = 12", "solution": "x = 15", "explanation": "Add 3 to both sides: x = 12 + 3 = 15"}
                ]), 
                '["equations", "solving"]'),
                
                ("ALG-INT-1", "Two-Step Equations", "intermediate", '["ALG-BASIC-1", "ALG-BASIC-2"]', 
                """# Two-Step Equations

## What are Two-Step Equations?
Equations that require two operations to solve, like `2x + 3 = 11`.

## Solving Strategy:
1. **Undo addition/subtraction** first
2. **Then undo multiplication/division**
3. Always work in reverse order of operations

## Examples:
- `2x + 5 = 13` → Subtract 5 → `2x = 8` → Divide by 2 → `x = 4`
- `3y - 7 = 14` → Add 7 → `3y = 21` → Divide by 3 → `y = 7`""", 
                60, 
                json.dumps([
                    {"problem": "Solve: 2x + 5 = 15", "solution": "x = 5", "explanation": "Subtract 5: 2x = 10, then divide by 2: x = 5"},
                    {"problem": "Solve: 3y - 4 = 11", "solution": "y = 5", "explanation": "Add 4: 3y = 15, then divide by 3: y = 5"},
                    {"problem": "Solve: 4z + 3 = 19", "solution": "z = 4", "explanation": "Subtract 3: 4z = 16, then divide by 4: z = 4"}
                ]), 
                '["equations", "two-step"]'),
                
                ("ALG-INT-2", "Algebraic Expressions", "intermediate", '["ALG-INT-1"]', 
                """# Algebraic Expressions

## What are Algebraic Expressions?
Mathematical phrases that can contain numbers, variables, and operations.

## Key Skills:
- **Simplifying** expressions by combining like terms
- **Evaluating** expressions by substituting values
- **Writing** expressions from word problems

## Like Terms:
Terms with the same variables raised to the same powers can be combined.

## Examples:
- `3x + 2x = 5x` (like terms)
- `2y + 3 + 4y = 6y + 3` (combine like terms)""", 
                55, 
                json.dumps([
                    {"problem": "Simplify: 3x + 2x + 5", "solution": "5x + 5", "explanation": "Combine like terms: 3x + 2x = 5x"},
                    {"problem": "Simplify: 4y - 2y + 7", "solution": "2y + 7", "explanation": "Combine like terms: 4y - 2y = 2y"},
                    {"problem": "If x=2, evaluate: 3x + 8", "solution": "14", "explanation": "Substitute: 3(2) + 8 = 6 + 8 = 14"}
                ]), 
                '["expressions", "simplifying"]'),
                
                ("ALG-ADV-1", "Systems of Equations", "advanced", '["ALG-INT-1", "ALG-INT-2"]', 
                """# Systems of Equations

## What are Systems of Equations?
Two or more equations with the same variables that are solved together.

## Solving Methods:
1. **Substitution**: Solve one equation for a variable, then substitute
2. **Elimination**: Add or subtract equations to eliminate a variable

## Examples:
- Substitution: `y = 2x` and `x + y = 12` → `x + 2x = 12` → `3x = 12` → `x = 4, y = 8`
- Elimination: Add equations to eliminate y""", 
                75, 
                json.dumps([
                    {"problem": "Solve: x + y = 10, x - y = 2", "solution": "x=6,y=4", "explanation": "Add equations: 2x=12, x=6, then y=4"},
                    {"problem": "Solve: 2x + y = 11, x - y = 1", "solution": "x=4,y=3", "explanation": "Add equations: 3x=12, x=4, then y=3"},
                    {"problem": "Solve: x + 2y = 8, 2x + y = 7", "solution": "x=2,y=3", "explanation": "Use elimination or substitution"}
                ]), 
                '["systems", "equations"]'),
                
                ("ALG-ADV-2", "Quadratic Equations", "advanced", '["ALG-ADV-1"]', 
                """# Quadratic Equations

## What are Quadratic Equations?
Equations of the form `ax² + bx + c = 0` where a ≠ 0.

## Solving Methods:
1. **Factoring**: Express as product of binomials
2. **Quadratic Formula**: `x = [-b ± √(b²-4ac)] / 2a`
3. **Completing the Square**

## Examples:
- `x² + 5x + 6 = 0` factors to `(x + 2)(x + 3) = 0` → `x = -2, -3`
- Use quadratic formula when factoring is difficult""", 
                80, 
                json.dumps([
                    {"problem": "Solve: x² + 5x + 6 = 0", "solution": "x=-2,-3", "explanation": "Factor: (x+2)(x+3)=0, so x=-2 or x=-3"},
                    {"problem": "Solve: x² - 4 = 0", "solution": "x=2,-2", "explanation": "Factor: (x-2)(x+2)=0, so x=2 or x=-2"},
                    {"problem": "Solve: x² - 3x + 2 = 0", "solution": "x=1,2", "explanation": "Factor: (x-1)(x-2)=0, so x=1 or x=2"}
                ]), 
                '["quadratic", "equations"]')
            ]
            cursor.executemany('INSERT INTO lessons VALUES (?,?,?,?,?,?,?,?)', lessons)
        
        # COMPREHENSIVE PRACTICE QUESTIONS POOL 
        cursor.execute("SELECT COUNT(*) FROM practice_questions")
        if cursor.fetchone()[0] == 0:
            practice_questions = []
            
            # ALG-BASIC-1: Introduction to Variables 
            practice_questions.extend([
                ("P-BASIC-1-1", "ALG-BASIC-1", "If x = 5, what is x + 3?", "8", "Substitute x with 5", "5 + 3 = 8"),
                ("P-BASIC-1-2", "ALG-BASIC-1", "If y = 8, what is 2y?", "16", "Multiply 2 times y", "2 × 8 = 16"),
                ("P-BASIC-1-3", "ALG-BASIC-1", "If a = 12, what is a - 4?", "8", "Subtract 4 from a", "12 - 4 = 8"),
                ("P-BASIC-1-4", "ALG-BASIC-1", "If b = 6, what is b + 7?", "13", "Add 7 to b", "6 + 7 = 13"),
                ("P-BASIC-1-5", "ALG-BASIC-1", "If x = 9, what is 3x?", "27", "Multiply 3 times x", "3 × 9 = 27"),
                ("P-BASIC-1-6", "ALG-BASIC-1", "If y = 15, what is y - 8?", "7", "Subtract 8 from y", "15 - 8 = 7"),
                ("P-BASIC-1-7", "ALG-BASIC-1", "If a = 4, what is a + a?", "8", "Add a to itself", "4 + 4 = 8"),
                ("P-BASIC-1-8", "ALG-BASIC-1", "If x = 10, what is 2x + 1?", "21", "Multiply then add", "2×10=20, 20+1=21"),
                ("P-BASIC-1-9", "ALG-BASIC-1", "If y = 7, what is y ÷ 1?", "7", "Divide by 1", "7 ÷ 1 = 7"),
                ("P-BASIC-1-10", "ALG-BASIC-1", "If a = 20, what is a - 12?", "8", "Subtract 12", "20 - 12 = 8"),
                ("P-BASIC-1-11", "ALG-BASIC-1", "If x = 3, what is 4x?", "12", "Multiply 4 times x", "4 × 3 = 12"),
                ("P-BASIC-1-12", "ALG-BASIC-1", "If y = 11, what is y + 9?", "20", "Add 9 to y", "11 + 9 = 20"),
                ("P-BASIC-1-13", "ALG-BASIC-1", "If a = 8, what is 5a?", "40", "Multiply 5 times a", "5 × 8 = 40"),
                ("P-BASIC-1-14", "ALG-BASIC-1", "If x = 6, what is x - 6?", "0", "Subtract 6 from x", "6 - 6 = 0"),
                ("P-BASIC-1-15", "ALG-BASIC-1", "If y = 14, what is 2y - 3?", "25", "Multiply then subtract", "2×14=28, 28-3=25"),
                ("P-BASIC-1-16", "ALG-BASIC-1", "If z = 10, what is z + 15?", "25", "Add 15 to z", "10 + 15 = 25"),
                ("P-BASIC-1-17", "ALG-BASIC-1", "If m = 7, what is 3m + 2?", "23", "Multiply then add", "3×7=21, 21+2=23"),
                ("P-BASIC-1-18", "ALG-BASIC-1", "If n = 12, what is n ÷ 3?", "4", "Divide by 3", "12 ÷ 3 = 4"),
                ("P-BASIC-1-19", "ALG-BASIC-1", "If p = 9, what is 4p - 5?", "31", "Multiply then subtract", "4×9=36, 36-5=31"),
                ("P-BASIC-1-20", "ALG-BASIC-1", "If q = 25, what is q ÷ 5?", "5", "Divide by 5", "25 ÷ 5 = 5")
            ])
            
            # ALG-BASIC-2: Solving Basic Equations 
            practice_questions.extend([
                ("P-BASIC-2-1", "ALG-BASIC-2", "Solve: x + 4 = 11", "7", "Subtract 4 from both sides", "x = 11 - 4 = 7"),
                ("P-BASIC-2-2", "ALG-BASIC-2", "Solve: 5x = 25", "5", "Divide both sides by 5", "x = 25 ÷ 5 = 5"),
                ("P-BASIC-2-3", "ALG-BASIC-2", "Solve: x - 2 = 9", "11", "Add 2 to both sides", "x = 9 + 2 = 11"),
                ("P-BASIC-2-4", "ALG-BASIC-2", "Solve: x + 8 = 15", "7", "Subtract 8 from both sides", "x = 15 - 8 = 7"),
                ("P-BASIC-2-5", "ALG-BASIC-2", "Solve: 3x = 18", "6", "Divide both sides by 3", "x = 18 ÷ 3 = 6"),
                ("P-BASIC-2-6", "ALG-BASIC-2", "Solve: x - 5 = 12", "17", "Add 5 to both sides", "x = 12 + 5 = 17"),
                ("P-BASIC-2-7", "ALG-BASIC-2", "Solve: x + 9 = 20", "11", "Subtract 9 from both sides", "x = 20 - 9 = 11"),
                ("P-BASIC-2-8", "ALG-BASIC-2", "Solve: 4x = 32", "8", "Divide both sides by 4", "x = 32 ÷ 4 = 8"),
                ("P-BASIC-2-9", "ALG-BASIC-2", "Solve: x - 7 = 3", "10", "Add 7 to both sides", "x = 3 + 7 = 10"),
                ("P-BASIC-2-10", "ALG-BASIC-2", "Solve: x + 12 = 25", "13", "Subtract 12 from both sides", "x = 25 - 12 = 13"),
                ("P-BASIC-2-11", "ALG-BASIC-2", "Solve: 6x = 42", "7", "Divide both sides by 6", "x = 42 ÷ 6 = 7"),
                ("P-BASIC-2-12", "ALG-BASIC-2", "Solve: x - 8 = 15", "23", "Add 8 to both sides", "x = 15 + 8 = 23"),
                ("P-BASIC-2-13", "ALG-BASIC-2", "Solve: x + 5 = 18", "13", "Subtract 5 from both sides", "x = 18 - 5 = 13"),
                ("P-BASIC-2-14", "ALG-BASIC-2", "Solve: 7x = 49", "7", "Divide both sides by 7", "x = 49 ÷ 7 = 7"),
                ("P-BASIC-2-15", "ALG-BASIC-2", "Solve: x - 10 = 5", "15", "Add 10 to both sides", "x = 5 + 10 = 15"),
                ("P-BASIC-2-16", "ALG-BASIC-2", "Solve: x + 6 = 14", "8", "Subtract 6 from both sides", "x = 14 - 6 = 8"),
                ("P-BASIC-2-17", "ALG-BASIC-2", "Solve: 8x = 64", "8", "Divide both sides by 8", "x = 64 ÷ 8 = 8"),
                ("P-BASIC-2-18", "ALG-BASIC-2", "Solve: x - 3 = 10", "13", "Add 3 to both sides", "x = 10 + 3 = 13"),
                ("P-BASIC-2-19", "ALG-BASIC-2", "Solve: x + 11 = 19", "8", "Subtract 11 from both sides", "x = 19 - 11 = 8"),
                ("P-BASIC-2-20", "ALG-BASIC-2", "Solve: 9x = 81", "9", "Divide both sides by 9", "x = 81 ÷ 9 = 9")
            ])
            
            # ALG-INT-1: Two-Step Equations 
            practice_questions.extend([
                ("P-INT-1-1", "ALG-INT-1", "Solve: 3x + 2 = 14", "4", "First subtract 2, then divide by 3", "3x = 12, x = 4"),
                ("P-INT-1-2", "ALG-INT-1", "Solve: 2y - 3 = 7", "5", "First add 3, then divide by 2", "2y = 10, y = 5"),
                ("P-INT-1-3", "ALG-INT-1", "Solve: 4z + 1 = 13", "3", "First subtract 1, then divide by 4", "4z = 12, z = 3"),
                ("P-INT-1-4", "ALG-INT-1", "Solve: 5x + 3 = 23", "4", "First subtract 3, then divide by 5", "5x = 20, x = 4"),
                ("P-INT-1-5", "ALG-INT-1", "Solve: 2a - 5 = 11", "8", "First add 5, then divide by 2", "2a = 16, a = 8"),
                ("P-INT-1-6", "ALG-INT-1", "Solve: 3b + 4 = 19", "5", "First subtract 4, then divide by 3", "3b = 15, b = 5"),
                ("P-INT-1-7", "ALG-INT-1", "Solve: 4c - 2 = 14", "4", "First add 2, then divide by 4", "4c = 16, c = 4"),
                ("P-INT-1-8", "ALG-INT-1", "Solve: 2x + 7 = 21", "7", "First subtract 7, then divide by 2", "2x = 14, x = 7"),
                ("P-INT-1-9", "ALG-INT-1", "Solve: 3y - 6 = 12", "6", "First add 6, then divide by 3", "3y = 18, y = 6"),
                ("P-INT-1-10", "ALG-INT-1", "Solve: 5z + 2 = 27", "5", "First subtract 2, then divide by 5", "5z = 25, z = 5"),
                ("P-INT-1-11", "ALG-INT-1", "Solve: 4x - 3 = 17", "5", "First add 3, then divide by 4", "4x = 20, x = 5"),
                ("P-INT-1-12", "ALG-INT-1", "Solve: 2a + 8 = 20", "6", "First subtract 8, then divide by 2", "2a = 12, a = 6"),
                ("P-INT-1-13", "ALG-INT-1", "Solve: 3b - 4 = 14", "6", "First add 4, then divide by 3", "3b = 18, b = 6"),
                ("P-INT-1-14", "ALG-INT-1", "Solve: 6c + 3 = 27", "4", "First subtract 3, then divide by 6", "6c = 24, c = 4"),
                ("P-INT-1-15", "ALG-INT-1", "Solve: 5x - 7 = 18", "5", "First add 7, then divide by 5", "5x = 25, x = 5"),
                ("P-INT-1-16", "ALG-INT-1", "Solve: 7y + 4 = 32", "4", "First subtract 4, then divide by 7", "7y = 28, y = 4"),
                ("P-INT-1-17", "ALG-INT-1", "Solve: 3z - 8 = 10", "6", "First add 8, then divide by 3", "3z = 18, z = 6"),
                ("P-INT-1-18", "ALG-INT-1", "Solve: 8x + 5 = 29", "3", "First subtract 5, then divide by 8", "8x = 24, x = 3"),
                ("P-INT-1-19", "ALG-INT-1", "Solve: 4y - 9 = 11", "5", "First add 9, then divide by 4", "4y = 20, y = 5"),
                ("P-INT-1-20", "ALG-INT-1", "Solve: 6z + 7 = 31", "4", "First subtract 7, then divide by 6", "6z = 24, z = 4")
            ])
            
            # ALG-INT-2: Algebraic Expressions 
            practice_questions.extend([
                ("P-INT-2-1", "ALG-INT-2", "Simplify: 5x + 3x + 2", "8x + 2", "Combine like terms", "5x + 3x = 8x"),
                ("P-INT-2-2", "ALG-INT-2", "Simplify: 7y - 2y + 5", "5y + 5", "Combine like terms", "7y - 2y = 5y"),
                ("P-INT-2-3", "ALG-INT-2", "If x=3, evaluate: 4x + 7", "19", "Substitute x with 3", "4(3) + 7 = 12 + 7 = 19"),
                ("P-INT-2-4", "ALG-INT-2", "Simplify: 8a + 2a - 3", "10a - 3", "Combine like terms", "8a + 2a = 10a"),
                ("P-INT-2-5", "ALG-INT-2", "If y=4, evaluate: 3y - 5", "7", "Substitute y with 4", "3(4) - 5 = 12 - 5 = 7"),
                ("P-INT-2-6", "ALG-INT-2", "Simplify: 6b + b + 9", "7b + 9", "Combine like terms", "6b + b = 7b"),
                ("P-INT-2-7", "ALG-INT-2", "If z=2, evaluate: 5z + 8", "18", "Substitute z with 2", "5(2) + 8 = 10 + 8 = 18"),
                ("P-INT-2-8", "ALG-INT-2", "Simplify: 9x - 4x + 1", "5x + 1", "Combine like terms", "9x - 4x = 5x"),
                ("P-INT-2-9", "ALG-INT-2", "If a=5, evaluate: 2a + 11", "21", "Substitute a with 5", "2(5) + 11 = 10 + 11 = 21"),
                ("P-INT-2-10", "ALG-INT-2", "Simplify: 4y + 3y - 7", "7y - 7", "Combine like terms", "4y + 3y = 7y"),
                ("P-INT-2-11", "ALG-INT-2", "If x=6, evaluate: 3x - 4", "14", "Substitute x with 6", "3(6) - 4 = 18 - 4 = 14"),
                ("P-INT-2-12", "ALG-INT-2", "Simplify: 7z - z + 6", "6z + 6", "Combine like terms", "7z - z = 6z"),
                ("P-INT-2-13", "ALG-INT-2", "If b=3, evaluate: 6b + 9", "27", "Substitute b with 3", "6(3) + 9 = 18 + 9 = 27"),
                ("P-INT-2-14", "ALG-INT-2", "Simplify: 8a + 2a + 5a", "15a", "Combine like terms", "8a + 2a + 5a = 15a"),
                ("P-INT-2-15", "ALG-INT-2", "If y=7, evaluate: 4y - 10", "18", "Substitute y with 7", "4(7) - 10 = 28 - 10 = 18"),
                ("P-INT-2-16", "ALG-INT-2", "Simplify: 5x + 2x - x + 4", "6x + 4", "Combine like terms", "5x + 2x - x = 6x"),
                ("P-INT-2-17", "ALG-INT-2", "If z=8, evaluate: 2z + 3z", "40", "Combine then substitute", "2(8) + 3(8) = 16 + 24 = 40"),
                ("P-INT-2-18", "ALG-INT-2", "Simplify: 10y - 3y + 2y", "9y", "Combine like terms", "10y - 3y + 2y = 9y"),
                ("P-INT-2-19", "ALG-INT-2", "If a=9, evaluate: 5a - 2a", "27", "Combine then substitute", "5(9) - 2(9) = 45 - 18 = 27"),
                ("P-INT-2-20", "ALG-INT-2", "Simplify: 6b + 4b - 3b + 7", "7b + 7", "Combine like terms", "6b + 4b - 3b = 7b")
            ])
            
            # ALG-ADV-1: Systems of Equations 
            practice_questions.extend([
                ("P-ADV-1-1", "ALG-ADV-1", "Solve: x + y = 7, x - y = 1", "x=4,y=3", "Add the two equations", "2x = 8, x = 4, then y = 3"),
                ("P-ADV-1-2", "ALG-ADV-1", "Solve: 2x + y = 9, x - y = 3", "x=4,y=1", "Add the equations to eliminate y", "3x = 12, x = 4, then y = 1"),
                ("P-ADV-1-3", "ALG-ADV-1", "Solve: x + 3y = 10, 2x + y = 5", "x=1,y=3", "Use elimination method", "Multiply first equation by 2: 2x+6y=20, subtract second: 5y=15, y=3, x=1"),
                ("P-ADV-1-4", "ALG-ADV-1", "Solve: 3x + y = 10, x + y = 6", "x=2,y=4", "Subtract the equations", "2x = 4, x = 2, then y = 4"),
                ("P-ADV-1-5", "ALG-ADV-1", "Solve: 2x + 3y = 16, x - y = 3", "x=5,y=2", "Use substitution", "From second: x=y+3, substitute: 2(y+3)+3y=16, 5y=10, y=2, x=5"),
                ("P-ADV-1-6", "ALG-ADV-1", "Solve: x + 2y = 8, 3x - y = 1", "x=2,y=3", "", "Multiply second by 2: 6x-2y=2, add to first: 7x=14, x=2, y=3"),
                ("P-ADV-1-7", "ALG-ADV-1", "Solve: 4x + y = 13, 2x - y = 5", "x=3,y=1", "Add equations", "6x = 18, x = 3, then y = 1"),
                ("P-ADV-1-8", "ALG-ADV-1", "Solve: x + 4y = 14, 2x + y = 8", "x=2,y=3", "", "Multiply first by 2: 2x+8y=28, subtract second: 7y=21, y=3, x=2"),
                ("P-ADV-1-9", "ALG-ADV-1", "Solve: 3x + 2y = 19, x - y = 2", "x=5,y=3", "", "From second: x=y+2, substitute: 3(y+2)+2y=19, 5y=13, y=3, x=5"),
                ("P-ADV-1-10", "ALG-ADV-1", "Solve: 5x + y = 16, 2x - y = 1", "x=3,y=1", "Add equations", "7x = 21, x = 3, then y = 1"),
                ("P-ADV-1-11", "ALG-ADV-1", "Solve: x + 5y = 17, 3x + y = 11", "x=3,y=2", "", "Multiply second by 5: 15x+5y=55, subtract first: 14x=42, x=3, y=2"),
                ("P-ADV-1-12", "ALG-ADV-1", "Solve: 2x + 4y = 20, x + y = 6", "x=2,y=4", "", "From second: x=6-y, substitute: 2(6-y)+4y=20, 12+2y=20, y=4, x=2"),
                ("P-ADV-1-13", "ALG-ADV-1", "Solve: 3x + y = 14, 2x - y = 6", "x=4,y=2", "Add equations", "5x = 20, x = 4, then y = 2"),
                ("P-ADV-1-14", "ALG-ADV-1", "Solve: x + 3y = 13, 2x + y = 11", "x=4,y=3", "", "Multiply first by 2: 2x+6y=26, subtract second: 5y=15, y=3, x=4"),
                ("P-ADV-1-15", "ALG-ADV-1", "Solve: 4x + 2y = 22, x - y = 1", "x=4,y=3", "", "From second: x=y+1, substitute: 4(y+1)+2y=22, 6y=18, y=3, x=4"),
                ("P-ADV-1-16", "ALG-ADV-1", "Solve: 2x + 5y = 23, x + y = 7", "x=4,y=3", "", "From second: x=7-y, substitute: 2(7-y)+5y=23, 14+3y=23, y=3, x=4"),
                ("P-ADV-1-17", "ALG-ADV-1", "Solve: 3x + 4y = 25, 2x - y = 3", "x=5,y=2", "", "Multiply second by 4: 8x-4y=12, add to first: 11x=37, x=5, y=2"),
                ("P-ADV-1-18", "ALG-ADV-1", "Solve: x + 2y = 9, 3x - 2y = 7", "x=4,y=2.5", "Add equations", "4x = 16, x = 4, then y = 2.5"),
                ("P-ADV-1-19", "ALG-ADV-1", "Solve: 5x + 3y = 26, x + y = 6", "x=4,y=2", "", "From second: x=6-y, substitute: 5(6-y)+3y=26, 30-2y=26, y=2, x=4"),
                ("P-ADV-1-20", "ALG-ADV-1", "Solve: 4x + 5y = 33, 2x + y = 11", "x=4,y=3", "", "Multiply second by 5: 10x+5y=55, subtract first: 6x=22, x=4, y=3")
            ])
            
            # ALG-ADV-2: Quadratic Equations 
            practice_questions.extend([
                ("P-ADV-2-1", "ALG-ADV-2", "Solve: x² + 6x + 8 = 0", "x=-2,-4", "Factor the equation", "(x+2)(x+4)=0, so x=-2 or x=-4"),
                ("P-ADV-2-2", "ALG-ADV-2", "Solve: x² - 9 = 0", "x=3,-3", "Factor as difference of squares", "(x-3)(x+3)=0, so x=3 or x=-3"),
                ("P-ADV-2-3", "ALG-ADV-2", "Solve: x² - 5x + 4 = 0", "x=1,4", "Factor the quadratic", "(x-1)(x-4)=0, so x=1 or x=4"),
                ("P-ADV-2-4", "ALG-ADV-2", "Solve: x² + 7x + 12 = 0", "x=-3,-4", "Factor the equation", "(x+3)(x+4)=0, so x=-3 or x=-4"),
                ("P-ADV-2-5", "ALG-ADV-2", "Solve: x² - 16 = 0", "x=4,-4", "Difference of squares", "(x-4)(x+4)=0, so x=4 or x=-4"),
                ("P-ADV-2-6", "ALG-ADV-2", "Solve: x² - 6x + 8 = 0", "x=2,4", "Factor the quadratic", "(x-2)(x-4)=0, so x=2 or x=4"),
                ("P-ADV-2-7", "ALG-ADV-2", "Solve: x² + 8x + 15 = 0", "x=-3,-5", "Factor the equation", "(x+3)(x+5)=0, so x=-3 or x=-5"),
                ("P-ADV-2-8", "ALG-ADV-2", "Solve: x² - 25 = 0", "x=5,-5", "Difference of squares", "(x-5)(x+5)=0, so x=5 or x=-5"),
                ("P-ADV-2-9", "ALG-ADV-2", "Solve: x² - 7x + 12 = 0", "x=3,4", "Factor the quadratic", "(x-3)(x-4)=0, so x=3 or x=4"),
                ("P-ADV-2-10", "ALG-ADV-2", "Solve: x² + 9x + 20 = 0", "x=-4,-5", "Factor the equation", "(x+4)(x+5)=0, so x=-4 or x=-5"),
                ("P-ADV-2-11", "ALG-ADV-2", "Solve: x² - 4x + 3 = 0", "x=1,3", "Factor the quadratic", "(x-1)(x-3)=0, so x=1 or x=3"),
                ("P-ADV-2-12", "ALG-ADV-2", "Solve: x² + 5x + 6 = 0", "x=-2,-3", "Factor the equation", "(x+2)(x+3)=0, so x=-2 or x=-3"),
                ("P-ADV-2-13", "ALG-ADV-2", "Solve: x² - 8x + 15 = 0", "x=3,5", "Factor the quadratic", "(x-3)(x-5)=0, so x=3 or x=5"),
                ("P-ADV-2-14", "ALG-ADV-2", "Solve: x² + 10x + 21 = 0", "x=-3,-7", "Factor the equation", "(x+3)(x+7)=0, so x=-3 or x=-7"),
                ("P-ADV-2-15", "ALG-ADV-2", "Solve: x² - 9x + 18 = 0", "x=3,6", "Factor the quadratic", "(x-3)(x-6)=0, so x=3 or x=6"),
                ("P-ADV-2-16", "ALG-ADV-2", "Solve: x² + 11x + 24 = 0", "x=-3,-8", "Factor the equation", "(x+3)(x+8)=0, so x=-3 or x=-8"),
                ("P-ADV-2-17", "ALG-ADV-2", "Solve: x² - 10x + 21 = 0", "x=3,7", "Factor the quadratic", "(x-3)(x-7)=0, so x=3 or x=7"),
                ("P-ADV-2-18", "ALG-ADV-2", "Solve: x² + 12x + 32 = 0", "x=-4,-8", "Factor the equation", "(x+4)(x+8)=0, so x=-4 or x=-8"),
                ("P-ADV-2-19", "ALG-ADV-2", "Solve: x² - 11x + 24 = 0", "x=3,8", "Factor the quadratic", "(x-3)(x-8)=0, so x=3 or x=8"),
                ("P-ADV-2-20", "ALG-ADV-2", "Solve: x² + 13x + 36 = 0", "x=-4,-9", "Factor the equation", "(x+4)(x+9)=0, so x=-4 or x=-9")
            ])
            
            cursor.executemany(
                'INSERT INTO practice_questions (question_id, lesson_id, question, answer, hint, explanation) VALUES (?,?,?,?,?,?)', 
                practice_questions
            )

        # COMPREHENSIVE QUIZ QUESTIONS BANK 
        cursor.execute("SELECT COUNT(*) FROM quiz_questions")
        if cursor.fetchone()[0] == 0:
            quiz_questions = []
            
            # ALG-BASIC-1: Introduction to Variables 
            quiz_questions.extend([
                ("Q-BASIC-1-1", "ALG-BASIC-1", "If m = 6, what is m + 4?", "10", "Substitute m with 6", "6 + 4 = 10"),
                ("Q-BASIC-1-2", "ALG-BASIC-1", "If n = 9, what is 3n?", "27", "Multiply 3 times n", "3 × 9 = 27"),
                ("Q-BASIC-1-3", "ALG-BASIC-1", "If p = 15, what is p - 7?", "8", "Subtract 7 from p", "15 - 7 = 8"),
                ("Q-BASIC-1-4", "ALG-BASIC-1", "If r = 12, what is r ÷ 4?", "3", "Divide r by 4", "12 ÷ 4 = 3"),
                ("Q-BASIC-1-5", "ALG-BASIC-1", "If s = 8, what is s + s?", "16", "Add s to itself", "8 + 8 = 16"),
                ("Q-BASIC-1-6", "ALG-BASIC-1", "If t = 11, what is 2t - 3?", "19", "Multiply then subtract", "2×11=22, 22-3=19"),
                ("Q-BASIC-1-7", "ALG-BASIC-1", "If u = 20, what is u ÷ 5?", "4", "Divide by 5", "20 ÷ 5 = 4"),
                ("Q-BASIC-1-8", "ALG-BASIC-1", "If v = 7, what is 4v + 2?", "30", "Multiply then add", "4×7=28, 28+2=30"),
                ("Q-BASIC-1-9", "ALG-BASIC-1", "If w = 14, what is w - 9?", "5", "Subtract 9 from w", "14 - 9 = 5"),
                ("Q-BASIC-1-10", "ALG-BASIC-1", "If x = 25, what is x ÷ 5?", "5", "Divide by 5", "25 ÷ 5 = 5"),
                ("Q-BASIC-1-11", "ALG-BASIC-1", "If y = 18, what is y + 12?", "30", "Add 12 to y", "18 + 12 = 30"),
                ("Q-BASIC-1-12", "ALG-BASIC-1", "If z = 5, what is 6z?", "30", "Multiply 6 times z", "6 × 5 = 30"),
                ("Q-BASIC-1-13", "ALG-BASIC-1", "If a = 16, what is a - 11?", "5", "Subtract 11 from a", "16 - 11 = 5"),
                ("Q-BASIC-1-14", "ALG-BASIC-1", "If b = 9, what is 7b?", "63", "Multiply 7 times b", "7 × 9 = 63"),
                ("Q-BASIC-1-15", "ALG-BASIC-1", "If c = 30, what is c ÷ 6?", "5", "Divide by 6", "30 ÷ 6 = 5"),
                ("Q-BASIC-1-16", "ALG-BASIC-1", "If d = 13, what is d + 8?", "21", "Add 8 to d", "13 + 8 = 21"),
                ("Q-BASIC-1-17", "ALG-BASIC-1", "If e = 22, what is e - 15?", "7", "Subtract 15 from e", "22 - 15 = 7"),
                ("Q-BASIC-1-18", "ALG-BASIC-1", "If f = 4, what is 9f?", "36", "Multiply 9 times f", "9 × 4 = 36"),
                ("Q-BASIC-1-19", "ALG-BASIC-1", "If g = 17, what is g ÷ 1?", "17", "Divide by 1", "17 ÷ 1 = 17"),
                ("Q-BASIC-1-20", "ALG-BASIC-1", "If h = 24, what is h + h?", "48", "Add h to itself", "24 + 24 = 48")
            ])
            
            # ALG-BASIC-2: Solving Basic Equations 
            quiz_questions.extend([
                ("Q-BASIC-2-1", "ALG-BASIC-2", "Solve: m + 6 = 14", "8", "Subtract 6 from both sides", "m = 14 - 6 = 8"),
                ("Q-BASIC-2-2", "ALG-BASIC-2", "Solve: 4n = 28", "7", "Divide both sides by 4", "n = 28 ÷ 4 = 7"),
                ("Q-BASIC-2-3", "ALG-BASIC-2", "Solve: p - 4 = 11", "15", "Add 4 to both sides", "p = 11 + 4 = 15"),
                ("Q-BASIC-2-4", "ALG-BASIC-2", "Solve: q + 9 = 17", "8", "Subtract 9 from both sides", "q = 17 - 9 = 8"),
                ("Q-BASIC-2-5", "ALG-BASIC-2", "Solve: 5r = 45", "9", "Divide both sides by 5", "r = 45 ÷ 5 = 9"),
                ("Q-BASIC-2-6", "ALG-BASIC-2", "Solve: s - 6 = 13", "19", "Add 6 to both sides", "s = 13 + 6 = 19"),
                ("Q-BASIC-2-7", "ALG-BASIC-2", "Solve: t + 11 = 25", "14", "Subtract 11 from both sides", "t = 25 - 11 = 14"),
                ("Q-BASIC-2-8", "ALG-BASIC-2", "Solve: 6u = 54", "9", "Divide both sides by 6", "u = 54 ÷ 6 = 9"),
                ("Q-BASIC-2-9", "ALG-BASIC-2", "Solve: v - 8 = 7", "15", "Add 8 to both sides", "v = 7 + 8 = 15"),
                ("Q-BASIC-2-10", "ALG-BASIC-2", "Solve: w + 13 = 29", "16", "Subtract 13 from both sides", "w = 29 - 13 = 16"),
                ("Q-BASIC-2-11", "ALG-BASIC-2", "Solve: 7x = 63", "9", "Divide both sides by 7", "x = 63 ÷ 7 = 9"),
                ("Q-BASIC-2-12", "ALG-BASIC-2", "Solve: y - 9 = 18", "27", "Add 9 to both sides", "y = 18 + 9 = 27"),
                ("Q-BASIC-2-13", "ALG-BASIC-2", "Solve: z + 7 = 22", "15", "Subtract 7 from both sides", "z = 22 - 7 = 15"),
                ("Q-BASIC-2-14", "ALG-BASIC-2", "Solve: 8a = 72", "9", "Divide both sides by 8", "a = 72 ÷ 8 = 9"),
                ("Q-BASIC-2-15", "ALG-BASIC-2", "Solve: b - 12 = 8", "20", "Add 12 to both sides", "b = 8 + 12 = 20"),
                ("Q-BASIC-2-16", "ALG-BASIC-2", "Solve: c + 15 = 31", "16", "Subtract 15 from both sides", "c = 31 - 15 = 16"),
                ("Q-BASIC-2-17", "ALG-BASIC-2", "Solve: 9d = 81", "9", "Divide both sides by 9", "d = 81 ÷ 9 = 9"),
                ("Q-BASIC-2-18", "ALG-BASIC-2", "Solve: e - 5 = 14", "19", "Add 5 to both sides", "e = 14 + 5 = 19"),
                ("Q-BASIC-2-19", "ALG-BASIC-2", "Solve: f + 18 = 35", "17", "Subtract 18 from both sides", "f = 35 - 18 = 17"),
                ("Q-BASIC-2-20", "ALG-BASIC-2", "Solve: 10g = 100", "10", "Divide both sides by 10", "g = 100 ÷ 10 = 10")
            ])
            
            # ALG-INT-1: Two-Step Equations 
            quiz_questions.extend([
                ("Q-INT-1-1", "ALG-INT-1", "Solve: 3m + 4 = 19", "5", "First subtract 4, then divide by 3", "3m = 15, m = 5"),
                ("Q-INT-1-2", "ALG-INT-1", "Solve: 2n - 5 = 13", "9", "First add 5, then divide by 2", "2n = 18, n = 9"),
                ("Q-INT-1-3", "ALG-INT-1", "Solve: 4p + 3 = 23", "5", "First subtract 3, then divide by 4", "4p = 20, p = 5"),
                ("Q-INT-1-4", "ALG-INT-1", "Solve: 5q - 6 = 19", "5", "First add 6, then divide by 5", "5q = 25, q = 5"),
                ("Q-INT-1-5", "ALG-INT-1", "Solve: 6r + 2 = 32", "5", "First subtract 2, then divide by 6", "6r = 30, r = 5"),
                ("Q-INT-1-6", "ALG-INT-1", "Solve: 3s - 7 = 14", "7", "First add 7, then divide by 3", "3s = 21, s = 7"),
                ("Q-INT-1-7", "ALG-INT-1", "Solve: 7t + 4 = 39", "5", "First subtract 4, then divide by 7", "7t = 35, t = 5"),
                ("Q-INT-1-8", "ALG-INT-1", "Solve: 2u - 8 = 12", "10", "First add 8, then divide by 2", "2u = 20, u = 10"),
                ("Q-INT-1-9", "ALG-INT-1", "Solve: 8v + 5 = 45", "5", "First subtract 5, then divide by 8", "8v = 40, v = 5"),
                ("Q-INT-1-10", "ALG-INT-1", "Solve: 4w - 9 = 15", "6", "First add 9, then divide by 4", "4w = 24, w = 6"),
                ("Q-INT-1-11", "ALG-INT-1", "Solve: 9x + 6 = 51", "5", "First subtract 6, then divide by 9", "9x = 45, x = 5"),
                ("Q-INT-1-12", "ALG-INT-1", "Solve: 5y - 11 = 19", "6", "First add 11, then divide by 5", "5y = 30, y = 6"),
                ("Q-INT-1-13", "ALG-INT-1", "Solve: 6z + 7 = 43", "6", "First subtract 7, then divide by 6", "6z = 36, z = 6"),
                ("Q-INT-1-14", "ALG-INT-1", "Solve: 3a - 12 = 9", "7", "First add 12, then divide by 3", "3a = 21, a = 7"),
                ("Q-INT-1-15", "ALG-INT-1", "Solve: 7b + 8 = 50", "6", "First subtract 8, then divide by 7", "7b = 42, b = 6"),
                ("Q-INT-1-16", "ALG-INT-1", "Solve: 2c - 13 = 7", "10", "First add 13, then divide by 2", "2c = 20, c = 10"),
                ("Q-INT-1-17", "ALG-INT-1", "Solve: 8d + 9 = 57", "6", "First subtract 9, then divide by 8", "8d = 48, d = 6"),
                ("Q-INT-1-18", "ALG-INT-1", "Solve: 4e - 14 = 10", "6", "First add 14, then divide by 4", "4e = 24, e = 6"),
                ("Q-INT-1-19", "ALG-INT-1", "Solve: 9f + 10 = 64", "6", "First subtract 10, then divide by 9", "9f = 54, f = 6"),
                ("Q-INT-1-20", "ALG-INT-1", "Solve: 5g - 15 = 20", "7", "First add 15, then divide by 5", "5g = 35, g = 7")
            ])
            
            # ALG-INT-2: Algebraic Expressions 
            quiz_questions.extend([
                ("Q-INT-2-1", "ALG-INT-2", "Simplify: 6m + 4m + 3", "10m + 3", "Combine like terms", "6m + 4m = 10m"),
                ("Q-INT-2-2", "ALG-INT-2", "Simplify: 8n - 3n + 6", "5n + 6", "Combine like terms", "8n - 3n = 5n"),
                ("Q-INT-2-3", "ALG-INT-2", "If p=4, evaluate: 5p + 9", "29", "Substitute p with 4", "5(4) + 9 = 20 + 9 = 29"),
                ("Q-INT-2-4", "ALG-INT-2", "Simplify: 9q + 2q - 5", "11q - 5", "Combine like terms", "9q + 2q = 11q"),
                ("Q-INT-2-5", "ALG-INT-2", "If r=7, evaluate: 4r - 8", "20", "Substitute r with 7", "4(7) - 8 = 28 - 8 = 20"),
                ("Q-INT-2-6", "ALG-INT-2", "Simplify: 7s + s + 8", "8s + 8", "Combine like terms", "7s + s = 8s"),
                ("Q-INT-2-7", "ALG-INT-2", "If t=5, evaluate: 6t + 12", "42", "Substitute t with 5", "6(5) + 12 = 30 + 12 = 42"),
                ("Q-INT-2-8", "ALG-INT-2", "Simplify: 10u - 5u + 2", "5u + 2", "Combine like terms", "10u - 5u = 5u"),
                ("Q-INT-2-9", "ALG-INT-2", "If v=8, evaluate: 3v + 15", "39", "Substitute v with 8", "3(8) + 15 = 24 + 15 = 39"),
                ("Q-INT-2-10", "ALG-INT-2", "Simplify: 12w + 3w - 9", "15w - 9", "Combine like terms", "12w + 3w = 15w"),
                ("Q-INT-2-11", "ALG-INT-2", "If x=9, evaluate: 7x - 6", "57", "Substitute x with 9", "7(9) - 6 = 63 - 6 = 57"),
                ("Q-INT-2-12", "ALG-INT-2", "Simplify: 11y - y + 4", "10y + 4", "Combine like terms", "11y - y = 10y"),
                ("Q-INT-2-13", "ALG-INT-2", "If z=6, evaluate: 8z + 18", "66", "Substitute z with 6", "8(6) + 18 = 48 + 18 = 66"),
                ("Q-INT-2-14", "ALG-INT-2", "Simplify: 14a + 3a + 7a", "24a", "Combine like terms", "14a + 3a + 7a = 24a"),
                ("Q-INT-2-15", "ALG-INT-2", "If b=10, evaluate: 9b - 12", "78", "Substitute b with 10", "9(10) - 12 = 90 - 12 = 78"),
                ("Q-INT-2-16", "ALG-INT-2", "Simplify: 6c + 3c - c + 5", "8c + 5", "Combine like terms", "6c + 3c - c = 8c"),
                ("Q-INT-2-17", "ALG-INT-2", "If d=11, evaluate: 5d + 4d", "99", "Combine then substitute", "5(11) + 4(11) = 55 + 44 = 99"),
                ("Q-INT-2-18", "ALG-INT-2", "Simplify: 15e - 4e + 3e", "14e", "Combine like terms", "15e - 4e + 3e = 14e"),
                ("Q-INT-2-19", "ALG-INT-2", "If f=12, evaluate: 6f - 3f", "36", "Combine then substitute", "6(12) - 3(12) = 72 - 36 = 36"),
                ("Q-INT-2-20", "ALG-INT-2", "Simplify: 8g + 5g - 2g + 9", "11g + 9", "Combine like terms", "8g + 5g - 2g = 11g")
            ])
            
            # ALG-ADV-1: Systems of Equations 
            quiz_questions.extend([
                ("Q-ADV-1-1", "ALG-ADV-1", "Solve: m + n = 9, m - n = 1", "m=5,n=4", "Add the two equations", "2m = 10, m = 5, then n = 4"),
                ("Q-ADV-1-2", "ALG-ADV-1", "Solve: 3p + q = 13, p - q = 3", "p=4,q=1", "Add the equations to eliminate q", "4p = 16, p = 4, then q = 1"),
                ("Q-ADV-1-3", "ALG-ADV-1", "Solve: r + 4s = 18, 2r + s = 12", "r=2,s=4", "Use elimination method", "Multiply first by 2: 2r+8s=36, subtract second: 7s=28, s=4, r=2"),
                ("Q-ADV-1-4", "ALG-ADV-1", "Solve: 4t + u = 17, t + u = 8", "t=3,u=5", "Subtract the equations", "3t = 9, t = 3, then u = 5"),
                ("Q-ADV-1-5", "ALG-ADV-1", "Solve: 2v + 3w = 19, v - w = 2", "v=5,w=3", "Use substitution", "From second: v=w+2, substitute: 2(w+2)+3w=19, 5w=15, w=3, v=5"),
                ("Q-ADV-1-6", "ALG-ADV-1", "Solve: x + 3y = 14, 3x - y = 4", "x=2,y=4", "", "Multiply second by 3: 9x-3y=12, add to first: 10x=26, x=2, y=4"),
                ("Q-ADV-1-7", "ALG-ADV-1", "Solve: 5z + a = 21, 2z - a = 3", "z=3,a=6", "Add equations", "7z = 21, z = 3, then a = 6"),
                ("Q-ADV-1-8", "ALG-ADV-1", "Solve: b + 5c = 23, 2b + c = 13", "b=4,c=3", "", "Multiply first by 2: 2b+10c=46, subtract second: 9c=27, c=3, b=4"),
                ("Q-ADV-1-9", "ALG-ADV-1", "Solve: 3d + 2e = 20, d - e = 1", "d=4,e=3", "", "From second: d=e+1, substitute: 3(e+1)+2e=20, 5e=17, e=3, d=4"),
                ("Q-ADV-1-10", "ALG-ADV-1", "Solve: 6f + g = 25, 2f - g = 3", "f=3,g=7", "Add equations", "8f = 28, f = 3, then g = 7"),
                ("Q-ADV-1-11", "ALG-ADV-1", "Solve: h + 6i = 26, 3h + i = 17", "h=4,i=3", "", "Multiply second by 6: 18h+6i=102, subtract first: 17h=76, h=4, i=3"),
                ("Q-ADV-1-12", "ALG-ADV-1", "Solve: 2j + 5k = 24, j + k = 7", "j=3,k=4", "", "From second: j=7-k, substitute: 2(7-k)+5k=24, 14+3k=24, k=4, j=3"),
                ("Q-ADV-1-13", "ALG-ADV-1", "Solve: 4m + n = 22, 2m - n = 6", "m=4,n=6", "Add equations", "6m = 28, m = 4, then n = 6"),
                ("Q-ADV-1-14", "ALG-ADV-1", "Solve: p + 4q = 21, 2p + q = 16", "p=5,q=4", "", "Multiply first by 2: 2p+8q=42, subtract second: 7q=26, q=4, p=5"),
                ("Q-ADV-1-15", "ALG-ADV-1", "Solve: 5r + 3s = 29, r - s = 1", "r=4,s=3", "", "From second: r=s+1, substitute: 5(s+1)+3s=29, 8s=24, s=3, r=4"),
                ("Q-ADV-1-16", "ALG-ADV-1", "Solve: 2t + 6u = 28, t + u = 8", "t=5,u=3", "", "From second: t=8-u, substitute: 2(8-u)+6u=28, 16+4u=28, u=3, t=5"),
                ("Q-ADV-1-17", "ALG-ADV-1", "Solve: 3v + 5w = 31, 2v - w = 5", "v=4,w=3", "", "Multiply second by 5: 10v-5w=25, add to first: 13v=56, v=4, w=3"),
                ("Q-ADV-1-18", "ALG-ADV-1", "Solve: x + 3y = 16, 3x - 2y = 11", "x=5,y=3", "", "Multiply first by 3: 3x+9y=48, subtract second: 11y=37, y=3, x=5"),
                ("Q-ADV-1-19", "ALG-ADV-1", "Solve: 4z + 2a = 30, z + a = 9", "z=6,a=3", "", "From second: z=9-a, substitute: 4(9-a)+2a=30, 36-2a=30, a=3, z=6"),
                ("Q-ADV-1-20", "ALG-ADV-1", "Solve: 5b + 4c = 37, 2b + c = 14", "b=5,c=4", "", "Multiply second by 4: 8b+4c=56, subtract first: 3b=19, b=5, c=4")
            ])
            
            # ALG-ADV-2: Quadratic Equations 
            quiz_questions.extend([
                ("Q-ADV-2-1", "ALG-ADV-2", "Solve: x² + 8x + 12 = 0", "x=-2,-6", "Factor the equation", "(x+2)(x+6)=0, so x=-2 or x=-6"),
                ("Q-ADV-2-2", "ALG-ADV-2", "Solve: x² - 16 = 0", "x=4,-4", "Factor as difference of squares", "(x-4)(x+4)=0, so x=4 or x=-4"),
                ("Q-ADV-2-3", "ALG-ADV-2", "Solve: x² - 7x + 10 = 0", "x=2,5", "Factor the quadratic", "(x-2)(x-5)=0, so x=2 or x=5"),
                ("Q-ADV-2-4", "ALG-ADV-2", "Solve: x² + 9x + 18 = 0", "x=-3,-6", "Factor the equation", "(x+3)(x+6)=0, so x=-3 or x=-6"),
                ("Q-ADV-2-5", "ALG-ADV-2", "Solve: x² - 25 = 0", "x=5,-5", "Difference of squares", "(x-5)(x+5)=0, so x=5 or x=-5"),
                ("Q-ADV-2-6", "ALG-ADV-2", "Solve: x² - 8x + 12 = 0", "x=2,6", "Factor the quadratic", "(x-2)(x-6)=0, so x=2 or x=6"),
                ("Q-ADV-2-7", "ALG-ADV-2", "Solve: x² + 10x + 21 = 0", "x=-3,-7", "Factor the equation", "(x+3)(x+7)=0, so x=-3 or x=-7"),
                ("Q-ADV-2-8", "ALG-ADV-2", "Solve: x² - 36 = 0", "x=6,-6", "Difference of squares", "(x-6)(x+6)=0, so x=6 or x=-6"),
                ("Q-ADV-2-9", "ALG-ADV-2", "Solve: x² - 9x + 14 = 0", "x=2,7", "Factor the quadratic", "(x-2)(x-7)=0, so x=2 or x=7"),
                ("Q-ADV-2-10", "ALG-ADV-2", "Solve: x² + 11x + 24 = 0", "x=-3,-8", "Factor the equation", "(x+3)(x+8)=0, so x=-3 or x=-8"),
                ("Q-ADV-2-11", "ALG-ADV-2", "Solve: x² - 6x + 8 = 0", "x=2,4", "Factor the quadratic", "(x-2)(x-4)=0, so x=2 or x=4"),
                ("Q-ADV-2-12", "ALG-ADV-2", "Solve: x² + 12x + 27 = 0", "x=-3,-9", "Factor the equation", "(x+3)(x+9)=0, so x=-3 or x=-9"),
                ("Q-ADV-2-13", "ALG-ADV-2", "Solve: x² - 10x + 21 = 0", "x=3,7", "Factor the quadratic", "(x-3)(x-7)=0, so x=3 or x=7"),
                ("Q-ADV-2-14", "ALG-ADV-2", "Solve: x² + 13x + 30 = 0", "x=-3,-10", "Factor the equation", "(x+3)(x+10)=0, so x=-3 or x=-10"),
                ("Q-ADV-2-15", "ALG-ADV-2", "Solve: x² - 11x + 24 = 0", "x=3,8", "Factor the quadratic", "(x-3)(x-8)=0, so x=3 or x=8"),
                ("Q-ADV-2-16", "ALG-ADV-2", "Solve: x² + 14x + 33 = 0", "x=-3,-11", "Factor the equation", "(x+3)(x+11)=0, so x=-3 or x=-11"),
                ("Q-ADV-2-17", "ALG-ADV-2", "Solve: x² - 12x + 27 = 0", "x=3,9", "Factor the quadratic", "(x-3)(x-9)=0, so x=3 or x=9"),
                ("Q-ADV-2-18", "ALG-ADV-2", "Solve: x² + 15x + 36 = 0", "x=-3,-12", "Factor the equation", "(x+3)(x+12)=0, so x=-3 or x=-12"),
                ("Q-ADV-2-19", "ALG-ADV-2", "Solve: x² - 13x + 30 = 0", "x=3,10", "Factor the quadratic", "(x-3)(x-10)=0, so x=3 or x=10"),
                ("Q-ADV-2-20", "ALG-ADV-2", "Solve: x² + 16x + 39 = 0", "x=-3,-13", "Factor the equation", "(x+3)(x+13)=0, so x=-3 or x=-13")
            ])
            
            cursor.executemany(
                'INSERT INTO quiz_questions (question_id, lesson_id, question, answer, hint, explanation) VALUES (?,?,?,?,?,?)', 
                quiz_questions
            )
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def add_student(self, name, level, username, age=15, password=""):
        """Add a new student with password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        student_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO students (student_id, name, username, password, level, age, performance_score, completed_lessons, completed_exercises, seen_questions, practice_sessions) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (student_id, name, username, password, level, age, 0, '[]', '[]', '[]', '{}'))
        
        conn.commit()
        conn.close()
        return student_id

    def get_student(self, username):
        """Get student by username with password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        if not row: 
            return None
        
        # Parse practice_sessions if it exists, otherwise use empty dict
        practice_sessions = {}
        if len(row) > 10:  
            try:
                practice_sessions = json.loads(row[10]) if row[10] else {}
            except:
                practice_sessions = {}
        
        return {
            'student_id': row[0], 
            'name': row[1], 
            'username': row[2], 
            'password': row[3],
            'level': row[4], 
            'age': row[5], 
            'performance_score': row[6], 
            'completed_lessons': json.loads(row[7]) if row[7] else [],
            'completed_exercises': json.loads(row[8]) if row[8] else [],
            'seen_questions': json.loads(row[9]) if row[9] else [],
            'practice_sessions': practice_sessions
        }

    def verify_student_password(self, username, password):
        """Verify student username and password"""
        student = self.get_student(username)
        if not student:
            return False
        return student['password'] == password

    def update_student_progress(self, username, completed_lesson=None, completed_exercise=None, correct=None):
        """Update student progress - automatically mark lessons as complete"""
        conn = self.get_connection()
        cursor = conn.cursor()
        student = self.get_student(username)
        if not student: 
            conn.close()
            return
        
        updates, params = [], []
        
        if completed_lesson:
            lessons = set(student.get('completed_lessons', []))
            lessons.add(completed_lesson)
            updates.append("completed_lessons = ?")
            params.append(json.dumps(list(lessons)))
            print(f"✅ Lesson automatically completed: {completed_lesson} for {username}")
        
        if completed_exercise:
            exercises = set(student.get('completed_exercises', []))
            exercises.add(completed_exercise)
            updates.append("completed_exercises = ?")
            params.append(json.dumps(list(exercises)))
            print(f"✅ Exercise completed: {completed_exercise} for {username}")
        
        if correct is not None:
            current = student.get('performance_score', 0)
            if correct:
                new_score = min(100, current + 6) 
            else:
                new_score = max(0, current - 3) 
            updates.append("performance_score = ?")
            params.append(new_score)
            print(f"📈 Performance update: {current}% -> {new_score}% for {username}")
        
        if updates:
            query = f"UPDATE students SET {', '.join(updates)} WHERE username = ?"
            params.append(username)
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    def get_lesson(self, lesson_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE lesson_id = ?', (lesson_id,))
        row = cursor.fetchone()
        conn.close()
        if not row: 
            return None
        return {
            'lesson_id': row[0], 'title': row[1], 'level': row[2], 'prerequisites': json.loads(row[3]),
            'content': row[4], 'duration_minutes': row[5], 'examples': json.loads(row[6]), 'tags': json.loads(row[7])
        }
    
    def get_lessons_by_level(self, level):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE level = ?', (level,))
        lessons = []
        for row in cursor.fetchall():
            lessons.append({
                'lesson_id': row[0], 'title': row[1], 'level': row[2], 'prerequisites': json.loads(row[3]),
                'content': row[4], 'duration_minutes': row[5], 'examples': json.loads(row[6]), 'tags': json.loads(row[7])
            })
        conn.close()
        return lessons
    
    def get_all_lessons(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons')
        lessons = []
        for row in cursor.fetchall():
            lessons.append({
                'lesson_id': row[0], 'title': row[1], 'level': row[2], 'prerequisites': json.loads(row[3]),
                'content': row[4], 'duration_minutes': row[5], 'examples': json.loads(row[6]), 'tags': json.loads(row[7])
            })
        conn.close()
        return lessons
    
    def get_quiz_questions(self, lesson_id, count=5, exclude_previous=None):
        """Get quiz questions for a lesson with optional exclusion of previous attempts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        exclude_previous = exclude_previous or []
        placeholders = ','.join(['?'] * len(exclude_previous)) if exclude_previous else 'NULL'
        
        if exclude_previous:
            query = f'''
                SELECT question_id, question, answer, hint, explanation, difficulty 
                FROM quiz_questions 
                WHERE lesson_id = ? AND question_id NOT IN ({placeholders})
                ORDER BY RANDOM() 
                LIMIT ?
            '''
            params = [lesson_id] + exclude_previous + [count]
        else:
            query = '''
                SELECT question_id, question, answer, hint, explanation, difficulty 
                FROM quiz_questions 
                WHERE lesson_id = ? 
                ORDER BY RANDOM() 
                LIMIT ?
            '''
            params = [lesson_id, count]
        
        cursor.execute(query, params)
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'ex_id': row[0],  # Using ex_id for compatibility
                'question': row[1],
                'answer': row[2],
                'hint': row[3],
                'explanation': row[4],
                'difficulty': row[5]
            })
        
        conn.close()
        return questions

    def save_quiz_results(self, username, lesson_id, score, total_questions, passed):
        """Save quiz results - FIXED to be student-specific"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create quiz results table with proper structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                passed BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, lesson_id, timestamp)  -- Prevent duplicates
            )
        ''')

    def save_quiz_results(self, username, lesson_id, score, total_questions, passed, question_ids=None):
        """Save quiz results with question IDs for exclusion in future"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        quiz_data = json.dumps({'question_ids': question_ids or []})
        
        cursor.execute('''
            INSERT INTO quiz_results (username, lesson_id, score, total_questions, passed, quiz_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, lesson_id, score, total_questions, passed, quiz_data))
        
        conn.commit()
        conn.close()

    def has_passed_quiz(self, username, lesson_id):
        """Check if specific student has passed quiz for a lesson"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT passed FROM quiz_results 
            WHERE username = ? AND lesson_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (username, lesson_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0]

    def get_student_quiz_history(self, username, limit=10):
        """Get quiz history for a specific student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lesson_id, score, total_questions, passed, timestamp 
            FROM quiz_results 
            WHERE username = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (username, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'lesson_id': row[0],
                'score': row[1],
                'total_questions': row[2],
                'passed': bool(row[3]),
                'timestamp': row[4]
            })
        
        conn.close()
        return history

    def get_lesson_progress(self, username):
        """Get detailed lesson progress"""
        student = self.get_student(username)
        if not student:
            return {}
        
        all_lessons = self.get_all_lessons()
        progress = {}
        
        for lesson in all_lessons:
            lesson_id = lesson['lesson_id']
            completed = lesson_id in student.get('completed_lessons', [])
            quiz_passed = self.has_passed_quiz(username, lesson_id)
            
            progress[lesson_id] = {
                'completed': completed,
                'quiz_passed': quiz_passed,
                'title': lesson['title'],
                'level': lesson['level']
            }
        
        return progress
    
    def get_practice_questions(self, lesson_id, count=3, exclude_used=None):
        """Get practice questions for a lesson"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        exclude_used = exclude_used or []
        placeholders = ','.join(['?'] * len(exclude_used)) if exclude_used else 'NULL'
        
        if exclude_used:
            query = f'''
                SELECT question_id, question, answer, hint, explanation, difficulty 
                FROM practice_questions 
                WHERE lesson_id = ? AND question_id NOT IN ({placeholders})
                ORDER BY RANDOM() 
                LIMIT ?
            '''
            params = [lesson_id] + exclude_used + [count]
        else:
            query = '''
                SELECT question_id, question, answer, hint, explanation, difficulty 
                FROM practice_questions 
                WHERE lesson_id = ? 
                ORDER BY RANDOM() 
                LIMIT ?
            '''
            params = [lesson_id, count]
        
        cursor.execute(query, params)
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'question_id': row[0],
                'question': row[1],
                'answer': row[2],
                'hint': row[3],
                'explanation': row[4],
                'difficulty': row[5]
            })
        
        conn.close()
        return questions

    def get_all_practice_questions(self, lesson_id):
        """Get ALL practice questions for a lesson (for verification)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question_id, question, answer, hint, explanation, difficulty 
            FROM practice_questions 
            WHERE lesson_id = ?
        ''', (lesson_id,))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'question_id': row[0],
                'question': row[1],
                'answer': row[2],
                'hint': row[3],
                'explanation': row[4],
                'difficulty': row[5]
            })
        
        conn.close()
        return questions

    def get_all_quiz_questions(self, lesson_id):
        """Get ALL quiz questions for a lesson (for verification)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question_id, question, answer, hint, explanation, difficulty 
            FROM quiz_questions 
            WHERE lesson_id = ?
        ''', (lesson_id,))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'question_id': row[0],
                'question': row[1],
                'answer': row[2],
                'hint': row[3],
                'explanation': row[4],
                'difficulty': row[5]
            })
        
        conn.close()
        return questions

    def get_student_practice_session(self, username, lesson_id):
        """Get student's practice session data for a lesson"""
        student = self.get_student(username)
        if not student:
            return {'used_questions': [], 'session_count': 0}
        
        practice_sessions = student.get('practice_sessions', {})
        
        # If practice_sessions is a string, parse it as JSON
        if isinstance(practice_sessions, str):
            try:
                practice_sessions = json.loads(practice_sessions)
            except:
                practice_sessions = {}
        
        # If practice_sessions is already a dict, use it directly
        lesson_data = practice_sessions.get(lesson_id, {'used_questions': [], 'session_count': 0})
        return lesson_data

    def update_student_practice_session(self, username, lesson_id, used_questions):
        """Update student's practice session data"""
        student = self.get_student(username)
        if not student:
            return
        
        practice_sessions = student.get('practice_sessions', {})
        
        # If practice_sessions is a string, parse it as JSON
        if isinstance(practice_sessions, str):
            try:
                practice_sessions = json.loads(practice_sessions)
            except:
                practice_sessions = {}
        
        lesson_data = practice_sessions.get(lesson_id, {'used_questions': [], 'session_count': 0})
        
        # Add new used questions and increment session count
        lesson_data['used_questions'].extend(used_questions)
        lesson_data['session_count'] += 1
        
        # Keep only unique questions
        lesson_data['used_questions'] = list(set(lesson_data['used_questions']))
        
        practice_sessions[lesson_id] = lesson_data
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET practice_sessions = ? WHERE username = ?",
            (json.dumps(practice_sessions), username)  # Always store as JSON string
        )
        conn.commit()
        conn.close()

    def mark_practice_completed(self, username, question_id, correct):
        """Mark a practice question as completed - NO performance impact"""
        student = self.get_student(username)
        if not student:
            return
        
        print(f"📝 Practice question completed: {username} - Q{question_id} - {'Correct' if correct else 'Incorrect'}")
        
        return student.get('performance_score', 0) 

    def get_student_quiz_history(self, username, lesson_id):
        """Get questions used in previous quiz attempts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT quiz_data FROM quiz_results 
            WHERE username = ? AND lesson_id = ?
            ORDER BY timestamp DESC
        ''', (username, lesson_id))
        
        used_questions = []
        for row in cursor.fetchall():
            try:
                quiz_data = json.loads(row[0]) if row[0] else {}
                used_questions.extend(quiz_data.get('question_ids', []))
            except:
                pass
        
        conn.close()
        return list(set(used_questions))
    
    def change_password(self, username, old_password, new_password):
        """Change student password"""
        if not self.verify_student_password(username, old_password):
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE students SET password = ? WHERE username = ?",
            (new_password, username)
        )
        conn.commit()
        conn.close()
        return True
    