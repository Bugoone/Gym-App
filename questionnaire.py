import flet as ft
from flet import (
    Page,
    Text,
    Column,
    Dropdown,
    dropdown,
    Button,
    Container,
    padding,
    CrossAxisAlignment,
    FontWeight,
    Colors
)
from database import update_user_preferences

def show_questionnaire(page: Page, username: str):
    page.clean()

    header = Text("Fitness Questionnaire", size=28, weight=FontWeight.BOLD)
    subtext = Text("Tell us about your fitness goals", size=14, color=Colors.GREY_700)
    err = Text("", color=Colors.RED, size=12)
    continue_btn = Button(content=Text("Continue"), width=200, disabled=True)

    def validate_form(_e):
        continue_btn.disabled = not all([goal_dd.value, exp_dd.value, days_dd.value])
        page.update()

    def submit(_e):
        g = goal_dd.value
        exp = exp_dd.value
        days_val = days_dd.value

        if not g or not exp or not days_val:
            err.value = "Please fill all fields"
            page.update()
            return

        success = update_user_preferences(username, g, exp, int(days_val))

        if success:
            from workout_planner import show_planner
            show_planner(page, username)
        else:
            err.value = "Save failed"
            page.update()

    goal_dd = Dropdown(
        label="What's your main goal?",
        width=350,
        hint_text="Select your goal",
        options=[
            dropdown.Option("build_muscle", "Build Muscle"),
            dropdown.Option("lose_weight", "Lose Weight"),
            dropdown.Option("get_stronger", "Get Stronger"),
            dropdown.Option("general_fitness", "General Fitness")
        ]
    )

    exp_dd = Dropdown(
        label="What's your experience level?",
        width=350,
        hint_text="Select your level",
        options=[
            dropdown.Option("beginner", "Beginner (Never worked out before)"),
            dropdown.Option("intermediate", "Intermediate (Been training for a while)"),
            dropdown.Option("advanced", "Advanced (Training for years)")
        ]
    )

    days_dd = Dropdown(
        label="Days per week",
        width=200,
        hint_text="How many days?",
        options=[
            dropdown.Option("3"),
            dropdown.Option("4"),
            dropdown.Option("5"),
            dropdown.Option("6")
        ]
    )

    goal_dd.on_select = validate_form
    exp_dd.on_select = validate_form
    days_dd.on_select = validate_form
    continue_btn.on_click = submit

    back_btn = Button(
        content=Text("Back"),
        on_click=lambda e: go_back(page, username)
    )

    page.add(
        Column(
            controls=[
                Container(content=header, padding=padding.only(top=30)),
                subtext,
                Container(height=20),
                goal_dd,
                Container(height=15),
                exp_dd,
                Container(height=15),
                days_dd,
                err,
                Container(height=20),
                continue_btn,
                Container(height=10),
                back_btn
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=5
        )
    )

def go_back(page, username):
    from dashboard import create_dashboard
    create_dashboard(page, username)
