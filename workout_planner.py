import flet as ft
import random
from flet import (
    Page,
    Text,
    Column,
    Row,
    Container,
    Button,
    ScrollMode,
    padding,
    MainAxisAlignment,
    CrossAxisAlignment,
    FontWeight,
    Colors
)
from database import get_user_data, find_exercises, save_workout

def show_planner(page: Page, username: str):
    page.clean()
    
    title = Text("Generate Workout Plan", size=28, weight=FontWeight.BOLD)
    
    # get user prefs
    user_data = get_user_data(username)
    
    if not user_data:
        # stops the app crashing if the user somehow reaches this page without completing the questionnaire
        error_txt = Text("Error: No questionnaire data found. Please complete the questionnaire first.", 
                        color=Colors.RED)
        back = Button(content=Text("Back"), on_click=lambda e: go_back(page, username))
        page.add(Column([error_txt, back], horizontal_alignment=CrossAxisAlignment.CENTER))
        return
    
    goal = user_data[2]
    exp = user_data[3]
    days = user_data[4]
    
    status = Text(f"Generating plan for: {goal.replace('_', ' ').title()}, {exp.title()}, {days} days/week", 
                 size=14, color=Colors.GREY_700)
    
    workout_display = Column(spacing=15, scroll=ScrollMode.AUTO, height=600)
    
    def generate():
        workout_display.controls.clear()
        
        # figure out muscle split based on days
        if days <= 3:
            # full body each session
            splits = ["full_body"] * days
        elif days == 4:
            # upper/lower split
            splits = ["upper", "lower", "upper", "lower"]
        else:
            # 5-6 days - push/pull/legs
            splits = ["push", "pull", "legs", "push", "pull", "legs"][:days]
        
        # get exercises for each day
        workout_data = []
        
        for i, split_type in enumerate(splits):
            day_num = i + 1
            
            # pick muscles for this split
            if split_type == "full_body":
                muscles = ["chest", "back", "legs", "shoulders"]
            elif split_type == "upper":
                muscles = ["chest", "back", "shoulders", "arms"]
            elif split_type == "lower":
                muscles = ["legs"]
            elif split_type == "push":
                muscles = ["chest", "shoulders"]
            elif split_type == "pull":
                muscles = ["back"]
            else:  # legs
                muscles = ["legs"]
            
            day_exercises = []
            
            # get exercises for each muscle 
            for muscle in muscles:
                exs = find_exercises(muscle=muscle, difficulty=exp)
                
                # if no exercises at user level, get any from that muscle
                if not exs:
                    exs = find_exercises(muscle=muscle)
                
                if exs:
                    day_exercises.append(random.choice(exs))  # choose random exercise for muscle
            
            # sets and reps based on goal
            if goal == "build_muscle":
                sets = 4
                reps = "10-12"
            elif goal == "get_stronger":
                sets = 5
                reps = "4-6"
            elif goal == "lose_weight":
                sets = 3
                reps = "12-15"
            else:  # general fitness
                sets = 3
                reps = "10-12"
            
            workout_data.append({
                "day": day_num,
                "type": split_type,
                "exercises": day_exercises,
                "sets": sets,
                "reps": reps
            })
        
        # display workouts
        for workout in workout_data:
            day_title = Text(f"Day {workout['day']}: {workout['type'].replace('_', ' ').title()}", 
                           size=20, weight=FontWeight.BOLD)
            
            ex_list = Column(spacing=8)
            
            for ex in workout['exercises']:
                ex_id, name, desc, benefits, drawbacks, muscle, difficulty = ex
                
                ex_card = Container(
                    content=Column([
                        Text(name, size=16, weight=FontWeight.BOLD),
                        Text(f"{workout['sets']} sets x {workout['reps']} reps", size=13, color=Colors.BLUE_700),
                        Text(f"Target: {muscle}", size=12, color=Colors.GREY_600)
                    ], spacing=3),
                    padding=padding.all(10),
                    border=ft.border.all(1, Colors.GREY_300),
                    border_radius=5
                )
                
                ex_list.controls.append(ex_card)
            
            day_container = Container(
                content=Column([day_title, ex_list], spacing=10),
                padding=padding.all(15),
                bgcolor=Colors.GREY_100,
                border_radius=8
            )
            
            workout_display.controls.append(day_container)
        
        page.update()
    
    def save_plan(e):
        # save to database
        user_data = get_user_data(username)
        goal = user_data[2]
        exp = user_data[3]
        days = user_data[4]
    
        # regenerate workout data - format for DB
        if days <= 3:
            splits = ["full_body"] * days
        elif days == 4:
            splits = ["upper", "lower", "upper", "lower"]
        else:
            splits = ["push", "pull", "legs", "push", "pull", "legs"][:days]
    
        #  database stores whole numbers not strings like "10-12" so reps are stored differently here than how they display
        if goal == "build_muscle":
            sets = 4
            reps = 12
        elif goal == "get_stronger":
            sets = 5
            reps = 5
        elif goal == "lose_weight":
            sets = 3
            reps = 15
        else:
            sets = 3
            reps = 12
    
        workout_name = f"{goal.replace('_', ' ').title()} Plan"
    
        exercises_to_save = []
        day_num = 1
    
        for split_type in splits:
            if split_type == "full_body":
                muscles = ["chest", "back", "legs", "shoulders"]
            elif split_type == "upper":
                muscles = ["chest", "back", "shoulders", "arms"]
            elif split_type == "lower":
                muscles = ["legs"]
            elif split_type == "push":
                muscles = ["chest", "shoulders"]
            elif split_type == "pull":
                muscles = ["back"]
            else:
                muscles = ["legs"]
        
            for muscle in muscles:
                exs = find_exercises(muscle=muscle, difficulty=exp)
                if not exs:
                    exs = find_exercises(muscle=muscle)
                if exs:
                    ex_id = exs[0][0]
                    exercises_to_save.append((ex_id, sets, reps, day_num))
        
            day_num += 1  # increment after all muscles added for day
    
        success = save_workout(username, workout_name, exercises_to_save)
    
        if success:
            saved_msg = Text("Workout saved!", color=Colors.GREEN, size=14, weight=FontWeight.BOLD)
            workout_display.controls.insert(0, saved_msg)
            page.update()
        else:
            err = Text("Failed to save", color=Colors.RED, size=14)
            workout_display.controls.insert(0, err)
            page.update()
    
    gen_btn = Button(content=Text("Generate Plan"), on_click=lambda e: generate())
    save_btn = Button(content=Text("Save Workout"), on_click=save_plan)
    back_btn = Button(content=Text("Back to Dashboard"), on_click=lambda e: go_back(page, username))
    
    # auto-generate on load
    generate()
    
    page.add(
        Column([
            Container(content=title, padding=padding.only(top=20)),
            status,
            Container(height=10),
            Row([gen_btn, save_btn], spacing=10, alignment=MainAxisAlignment.CENTER),
            Container(height=15),
            workout_display,
            Container(height=10),
            back_btn
        ],
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=10)
    )

def go_back(page, username):
    from dashboard import create_dashboard
    create_dashboard(page, username)
