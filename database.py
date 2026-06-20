import sqlite3

#create the database and cursor
def create_database():
    con = sqlite3.connect("peakform.db")
    c = con.cursor()

    # users table - username is primary key - if changing to email login in future, this column would need updating
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            fitness_goal TEXT,
            experience_level TEXT,
            days_per_week INTEGER
        )
    """)

    # exercises table
    c.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            benefits TEXT,
            drawbacks TEXT,
            target_muscle TEXT,
            difficulty TEXT
        )
    """)

    # workouts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            workout_name TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # workout_exercises table
    c.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            workout_id INTEGER,
            exercise_id INTEGER,
            sets INTEGER,
            reps INTEGER,
            day_number INTEGER,
            PRIMARY KEY (workout_id, exercise_id, day_number),
            FOREIGN KEY (workout_id) REFERENCES workouts(workout_id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
        )
    """)

    # progress table
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            exercise_id INTEGER NOT NULL,
            weight REAL,
            reps INTEGER,
            sets INTEGER,
            date_logged DATE,
            FOREIGN KEY (username) REFERENCES users(username),
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
        )
    """)

    con.commit()
    con.close()

def add_user(username, password):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    con.commit()
    con.close()
    return True

def username_exists(username):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    con.close()
    if result:
        return True
    else:
        return False

def check_user(username, password):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    con.close()
    if result:
        return True
    else:
        return False

# exercise functions kept separate - add new exercise features here without touching user authentication 

def add_exercise(name, desc, benefits, drawbacks, muscle, diff):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("""
        INSERT INTO exercises (name, description, benefits, drawbacks, target_muscle, difficulty)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, desc, benefits, drawbacks, muscle, diff))
    con.commit()
    con.close()

def get_exercises():
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("SELECT * FROM exercises")
    ex = c.fetchall()
    con.close()
    return ex

# search exercises by filters
def find_exercises(muscle=None, difficulty=None):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    
    # build query - starts with getting everything
    query = "SELECT * FROM exercises WHERE 1=1"
    params = []
    
    if muscle:
        query += " AND target_muscle = ?"
        params.append(muscle)
    
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
    
    c.execute(query, params)
    results = c.fetchall()
    con.close()
    return results

# add some starter exercises so database isnt empty
def add_sample_exercises():
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    
    # check if we already have exercises
    c.execute("SELECT COUNT(*) FROM exercises")
    count = c.fetchone()[0]
    
    if count > 0:
        con.close()
        return
    
    # sample exercises - these are common ones beginners should know
    exercises = [
        ("Bench Press", "Lie on bench, lower bar to chest, press up", 
         "Builds chest strength, good for upper body power", 
         "Requires spotter for safety, can strain shoulders if done incorrectly",
         "chest", "intermediate"),
        
        ("Squats", "Stand with bar on shoulders, lower down keeping back straight",
         "Great for leg strength, works entire lower body",
         "Can be hard on knees if form is bad, requires flexibility",
         "legs", "beginner"),
        
        ("Deadlift", "Lift bar from ground to standing position",
         "Full body exercise, builds overall strength",
         "Easy to injure back with poor form, quite technical",
         "back", "advanced"),
        
        ("Pull-ups", "Hang from bar, pull yourself up until chin over bar",
         "Excellent for back and arm strength, no equipment needed besides bar",
         "requires significant upper body strength",
         "back", "intermediate"),
        
        ("Push-ups", "Hands on ground, lower body down and push back up",
         "No equipment needed, works chest and triceps",
         "Can be boring, limited progressive overload",
         "chest", "beginner"),
        
        ("Bicep Curls", "Hold dumbbells, curl up to shoulders",
         "Isolates biceps, easy to learn",
         "Only works biceps, not very functional",
         "arms", "beginner"),
        
        ("Shoulder Press", "Press dumbbells or bar overhead from shoulders",
         "Builds shoulder strength and size",
         "Can cause shoulder pain if mobility is poor",
         "shoulders", "intermediate"),
        
        ("Lunges", "Step forward and lower back knee toward ground",
         "Works legs and improves balance",
         "Requires balance, can be hard on knees",
         "legs", "beginner"),
        
        ("Plank", "Hold push-up position on forearms",
         "Strengthens core, improves posture",
         "Can be boring, not much progression",
         "core", "beginner"),
        
        ("Barbell Row", "Bend over and pull bar to chest",
         "Great for back thickness",
         "Can be hard on lower back if form is bad",
         "back", "intermediate")
    ]
    
    # TODO: maybe add more exercises later, these are just the basics
    for e in exercises:
        c.execute("""
            INSERT INTO exercises (name, description, benefits, drawbacks, target_muscle, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        """, e)
    
    con.commit()
    con.close()
    print("Sample exercises added!")

# update user fitness preferences
def update_user_preferences(username, goal, exp_level, days):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("""
        UPDATE users 
        SET fitness_goal = ?, experience_level = ?, days_per_week = ?
        WHERE username = ?
    """, (goal, exp_level, days, username))
    con.commit()
    rows = c.rowcount
    con.close()
    return rows > 0

# get user data for workout generation
def get_user_data(username):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    con.close()
    return data

# save workout to database
def save_workout(username, workout_name, exercises):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    
    # create workout first
    c.execute("INSERT INTO workouts (username, workout_name) VALUES (?, ?)", (username, workout_name))
    workout_id = c.lastrowid
    
    # now add exercises - doing individually instead of executemany
    for ex_data in exercises:
        ex_id, sets, reps, day = ex_data
        c.execute("""
            INSERT INTO workout_exercises (workout_id, exercise_id, sets, reps, day_number)
            VALUES (?, ?, ?, ?, ?)
        """, (workout_id, ex_id, sets, reps, day))
    
    con.commit()
    con.close()
    return True

# get user's saved workouts
def get_workouts(username):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    c.execute("SELECT * FROM workouts WHERE username = ?", (username,))
    workouts = c.fetchall()
    con.close()
    return workouts

# get exercises for a specific workout
def get_workout_exercises(workout_id):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    # join to get exercise details
    c.execute("""
        SELECT e.name, e.target_muscle, we.sets, we.reps, we.day_number
        FROM workout_exercises we
        JOIN exercises e ON we.exercise_id = e.exercise_id
        WHERE we.workout_id = ?
        ORDER BY we.day_number
    """, (workout_id,))
    exs = c.fetchall()
    con.close()
    return exs

# exercises have to be deleted from workout_exercises first before deleting the workout, otherwise the foreign key will cause an error
def delete_workout(workout_id):
    con = sqlite3.connect("peakform.db")
    c = con.cursor()
    # delete exercises first because of foreign key
    c.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    c.execute("DELETE FROM workouts WHERE workout_id = ?", (workout_id,))
    con.commit()
    con.close()
    return True

create_database()
add_sample_exercises()
