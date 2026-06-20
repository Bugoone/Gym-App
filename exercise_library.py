import flet as ft
from flet import (
    Page,
    Text,
    Column,
    Row,
    ListView,
    Container,
    padding,
    Dropdown,
    dropdown,
    MainAxisAlignment,
    CrossAxisAlignment,
    FontWeight,
    Colors,
    Button,
    ScrollMode
)
from database import get_exercises, find_exercises

def show_exercise_library(page: Page, username: str):
    page.clean()
    
    title = Text("Exercise Library", size=32, weight=FontWeight.BOLD)
    
    # filters
    muscle_dropdown = Dropdown(
        label="Muscle Group",
        width=200,
        options=[
            dropdown.Option("all"),
            dropdown.Option("chest"),
            dropdown.Option("back"),
            dropdown.Option("legs"),
            dropdown.Option("shoulders"),
            dropdown.Option("arms"),
            dropdown.Option("core")
        ],
        value="all"
    )
    
    diff_dropdown = Dropdown(
        label="Difficulty",
        width=200,
        options=[
            dropdown.Option("all"),
            dropdown.Option("beginner"),
            dropdown.Option("intermediate"),
            dropdown.Option("advanced")
        ],
        value="all"
    )
    
    exercise_list = Column(spacing=10, scroll=ScrollMode.AUTO, height=600)
    
    def load_ex():
        exercise_list.controls.clear()
        
        muscle = muscle_dropdown.value
        diff = diff_dropdown.value
        
        # get exercises
        if muscle != "all" or diff != "all":
            m = muscle if muscle != "all" else None
            d = diff if diff != "all" else None
            exercises = find_exercises(m, d)
        else:
            exercises = get_exercises()
        
        # build list
        for ex in exercises:
            id, name, desc, benefits, drawbacks, target, difficulty = ex
            
            card = Container(
                content=Column([
                    Text(name, size=20, weight=FontWeight.BOLD),
                    Text(f"Target: {target} | Difficulty: {difficulty}", size=12, color=Colors.GREY_700),
                    Text(f"How to: {desc}", size=14),
                    Text(f"✓ {benefits}", size=13, color=Colors.GREEN_700),
                    Text(f"✗ {drawbacks}", size=13, color=Colors.RED_700),
                ], spacing=5),
                padding=padding.all(15),
                border=ft.border.all(1, Colors.GREY_400),
                border_radius=8,
                bgcolor=Colors.WHITE
            )
            
            exercise_list.controls.append(card)
        
        page.update()
    
    filter_button = Button(
        content=Text("Apply Filters"),
        on_click=lambda e: load_ex()
    )
    
    back_button = Button(
        content=Text("Back"),
        on_click=lambda e: go_back(page, username)
    )
    
    # load exercises
    load_ex()
    
    page.add(
        Column([
            Container(content=title, padding=padding.only(top=20, bottom=10)),
            
            Row([
                muscle_dropdown,
                diff_dropdown,
                filter_button
            ], spacing=15),
            
            exercise_list,
            
            Container(content=back_button, padding=padding.only(top=20))
        ],
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=20)
    )

def go_back(page, username):
    from dashboard import create_dashboard
    create_dashboard(page, username)
