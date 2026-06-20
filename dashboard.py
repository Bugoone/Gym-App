import flet as ft
from flet import (
    Page,
    Text,
    Column,
    Row,
    TextButton,
    ButtonStyle,
    MainAxisAlignment,
    CrossAxisAlignment,
    FontWeight,
    Colors,
    Container,
    padding,
    Button,
    ScrollMode
)

def create_dashboard(page: Page, username: str):
    # set window size first before cleaning
    page.window.width = 1700
    page.window.height = 1000
    page.window.min_width = 1700
    page.window.min_height = 1000
    page.window.max_width = 1700
    page.window.max_height = 1000
    page.window.resizable = False
    
    page.clean()
    page.update()
    
    welcome_msg = Text(value=f"Welcome back, {username}!", size=28, weight=FontWeight.BOLD)
    
    def make_section(title, subtitle, msg):
        return Column(
            controls=[Text(title, size=24, weight=FontWeight.BOLD), Text(subtitle, size=14), Text(msg, size=16, color=Colors.GREY_600)],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=15,
            visible=False
        )
    
    planner = make_section("Create Workout Plan", "Build a custom workout based on your goals", "Click below to start")
    planner.visible = True  #  starts visible
    
    # check if user has completed questionnaire
    from database import get_user_data
    user_data = get_user_data(username)
    
    if user_data and user_data[2]:  # if fitness_goal is set
        # user already did questionnaire - go straight to planner
        plan_btn = Button(content=Text("Generate Workout Plan"), on_click=lambda e: open_planner(page, username))
        planner.controls.append(plan_btn)
    else:
        # need questionnaire first
        start_quest_btn = Button(content=Text("Start Questionnaire"), on_click=lambda e: open_questionnaire(page, username))
        planner.controls.append(start_quest_btn)
    
    workouts_page = Column(
        controls=[Text("My Workouts", size=24, weight=FontWeight.BOLD), Text("View your saved workouts", size=14)],
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=12,
        visible=False
    )
    
    # container for workout list
    workout_list = Column(spacing=10, scroll=ScrollMode.AUTO, height=500)
    workouts_page.controls.append(workout_list)
    
    # load workouts from db
    def load_workouts():
        workout_list.controls.clear()
        
        from database import get_workouts, get_workout_exercises, delete_workout
        user_workouts = get_workouts(username)
        
        if not user_workouts:
            # no workouts yet
            workout_list.controls.append(Text("No workouts saved yet!", size=15, color=Colors.GREY_500))
        else:
            # show each workout
            for w in user_workouts:
                w_id = w[0]
                w_name = w[2]
                
                # get exercises for this workout
                exs = get_workout_exercises(w_id)
                
                # group by day manually
                days_dict = {}
                for ex in exs:
                    name, muscle, sets, reps, day = ex
                    if day not in days_dict:
                        days_dict[day] = []
                    days_dict[day].append((name, muscle, sets, reps))
                
                # build day sections
                day_sections = Column(spacing=10)
                
                # sort days and build each one
                day_nums = list(days_dict.keys())
                day_nums.sort()
                
                for d in day_nums:
                    day_title = Text(f"Day {d}", size=14, weight=FontWeight.BOLD, color=Colors.BLUE_700)
                    
                    ex_items = Column(spacing=3)
                    for ex_info in days_dict[d]:
                        name, muscle, sets, reps = ex_info
                        ex_txt = Text(f"• {name} - {sets}x{reps} ({muscle})", size=13)
                        ex_items.controls.append(ex_txt)
                    
                    day_sections.controls.append(day_title)
                    day_sections.controls.append(ex_items)
                
                # delete button for this workout
                def make_delete(workout_id):
                    def do_delete(e):
                        delete_workout(workout_id)
                        load_workouts()  # refresh list
                        page.update()
                    return do_delete
                
                del_btn = Button(
                    content=Text("Delete", size=12),
                    on_click=make_delete(w_id),
                    color=Colors.RED_400
                )
                
                # workout card
                card = Container(
                    content=Column([
                        Row([
                            Text(w_name, size=18, weight=FontWeight.BOLD),
                            del_btn
                        ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                        day_sections
                    ], spacing=8),
                    padding=padding.all(15),
                    border=ft.border.all(1, Colors.GREY_400),
                    border_radius=8,
                    bgcolor=Colors.WHITE
                )
                
                workout_list.controls.append(card)
        
        page.update()
    
    # load workouts when switching to this tab
    def switch_to_workouts():
        load_workouts()
        for s in sections:
            s.visible = False
        workouts_page.visible = True
        
        # reset tabs
        exercises_tab.style = ButtonStyle(color=Colors.GREY)
        planner_tab.style = ButtonStyle(color=Colors.GREY)
        workouts_tab.style = ButtonStyle(color="#08B9FF")
        page.update()
    
    exercises_tab = TextButton(content=Text("Exercise Library"), on_click=lambda e: open_ex_lib(page, username))
    planner_tab = TextButton(content=Text("Create Workout"), on_click=lambda e: switch_to("planner"))
    workouts_tab = TextButton(content=Text("My Workouts"), on_click=lambda e: switch_to_workouts())
    
    logout = Button(content=Text("Logout"), color=Colors.RED_400, on_click=lambda e: logout_user(page))
    
    sections = [planner, workouts_page, ]
    
    def switch_to(section_name):
        # hide everything
        for s in sections:
            s.visible = False
        
        # reset tab colors manually
        exercises_tab.style = ButtonStyle(color=Colors.GREY)
        planner_tab.style = ButtonStyle(color=Colors.GREY)
        workouts_tab.style = ButtonStyle(color=Colors.GREY)
        
        if section_name == "planner":
            planner.visible = True
            planner_tab.style = ButtonStyle(color="#08B9FF")
        
        page.update()
    
    planner_tab.style = ButtonStyle(color="#08B9FF")
    
    page.add(
        Column(
            controls=[
                Container(content=welcome_msg, padding=padding.only(top=20, bottom=10)),
                Row(controls=[exercises_tab, planner_tab, workouts_tab ], 
                    alignment=MainAxisAlignment.CENTER, spacing=10),
                Container(
                    content=Column(
                        controls=[planner, workouts_page],
                        horizontal_alignment=CrossAxisAlignment.CENTER
                    ),
                    padding=padding.only(top=30)
                ),
                Container(content=logout, padding=padding.only(top=40))
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=15
        )
    )
    
    # make sure window size is set
    page.window.width = 1700
    page.window.height = 1000
    page.update()

def open_ex_lib(page, username):
    from exercise_library import show_exercise_library
    show_exercise_library(page, username)

def open_questionnaire(page, username):
    from questionnaire import show_questionnaire
    show_questionnaire(page, username)

def open_planner(page, username):
    from workout_planner import show_planner
    show_planner(page, username)

def logout_user(page):
    page.window.width = 400
    page.window.height = 500
    page.window.min_width = 400
    page.window.min_height = 500
    page.window.max_width = 400
    page.window.max_height = 500
    page.window.resizable = False
    page.update()  # apply window changes
    
    from Login_signup import main
    main(page)
