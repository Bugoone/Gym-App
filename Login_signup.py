import flet as ft
from flet import (
    Page,
    TextField,
    TextAlign,
    Text,
    Checkbox,
    Button,
    Column,
    Row,
    TextButton,
    ButtonStyle,
    MainAxisAlignment,
    CrossAxisAlignment,
    ThemeMode,
    FontWeight,
    Colors,
    ControlEvent
)
from database import add_user, check_user, username_exists

#authentication page

def main(page: Page) -> None:
    page.title = "PeakForm"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.theme_mode = ThemeMode.LIGHT
    page.window.width = 400
    page.window.height = 500
    page.window.resizable = False
    
    # signup and login fields kept separate so showing and hiding them doesn't affect each other
    signup_user = TextField(label="username", text_align=TextAlign.LEFT, width=200)
    signup_user_err = Text(value="", color=Colors.RED, size=12)
    signup_pass = TextField(label="password", text_align=TextAlign.LEFT, width=200, password=True)
    signup_pass_err = Text(value="", color=Colors.RED, size=12)
    terms_checkbox = Checkbox(label="Accept terms", value=False)
    signup_btn = Button(content=Text("Sign Up"), width=200, disabled=True)
    
    # login fields
    login_user = TextField(label="username", text_align=TextAlign.LEFT, width=200)
    login_user_err = Text(value="", color=Colors.RED, size=12)
    login_pass = TextField(label="password", text_align=TextAlign.LEFT, width=200, password=True)
    login_pass_err = Text(value="", color=Colors.RED, size=12)
    login_btn = Button(content=Text("Log In"), width=200, disabled=True)
    
    # check if password has special chars
    def has_special_char(text):
        special = "!@#$%^&*()_+-=[]{}|;:',.<>?/`~"
        return any(c in special for c in text)
    
    # validate username input
    def check_username(username: str) -> str:
        if len(username) < 3:
            return "Username must be at least 3 characters"
        if len(username) > 20:
            return "Username must be no more than 20 characters"
        if " " in username:
            return "Username cannot contain spaces"
        return ""
    
    # validate password - needs to be secure
    def check_password(password: str) -> str:
        length = len(password)
        if length < 8:
            return "Password must be at least 8 characters"
        if length > 20:
            return "Password must be no more than 20 characters"
        
        # check for spaces
        has_space = False
        for c in password:
            if c == " ":
                has_space = True
                break
        
        if has_space:
            return "Password cannot contain spaces"
        
        if not has_special_char(password):
            return "Password must contain at least one special character"
        
        return ""
    
    # made this to avoid repeating blur validation code
    def make_blur_handler(field, err_text, validator, form_check):
        def blur_handler(e):
            error = validator(field.value)
            err_text.value = error
            form_check(e)
        return blur_handler
    
    # blur handlers for signup
    signup_user_blur = make_blur_handler(
        signup_user, signup_user_err, check_username, lambda e: check_signup(e)
    )
    signup_pass_blur = make_blur_handler(
        signup_pass, signup_pass_err, check_password, lambda e: check_signup(e)
    )
    
    # blur handlers for login
    login_user_blur = make_blur_handler(
        login_user, login_user_err, check_username, lambda e: check_login(e)
    )
    login_pass_blur = make_blur_handler(
        login_pass, login_pass_err, check_password, lambda e: check_login(e)
    )
    
    # check if signup form is valid
    def check_signup(e):
        user_err = check_username(signup_user.value) # type: ignore
        pass_err = check_password(signup_pass.value) # type: ignore
        
        user_ok = user_err == ""
        pass_ok = pass_err == ""
        terms_ok = terms_checkbox.value
        
        # only enable if everything is good
        if user_ok and pass_ok and terms_ok:
            signup_btn.disabled = False
        else:
            signup_btn.disabled = True
        page.update()
    
    # check if login form is valid
    def check_login(e: ControlEvent) -> None:
        user_valid = check_username(login_user.value) == "" # type: ignore
        pass_valid = check_password(login_pass.value) == "" # type: ignore
        
        if all([user_valid, pass_valid]):
            login_btn.disabled = False
        else:
            login_btn.disabled = True
        page.update()
    
    # signup form
    signup_form = Column(
        controls=[
            signup_user,
            signup_user_err,
            signup_pass,
            signup_pass_err,
            terms_checkbox,
            signup_btn
        ],
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=5,
        visible=True
    )
    
    # login form - starts hidden
    login_form = Column(
        controls=[login_user, login_user_err, login_pass, 
                  login_pass_err, login_btn],
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=5,
        visible=False
    )
    
    # tabs to switch between signup and login
    tab_signup = TextButton(content=Text("Sign Up"), on_click=lambda e: switch_tab("signup"))
    tab_login = TextButton(content=Text("Log In"), on_click=lambda e: switch_tab("login"))
    
    def switch_tab(tab: str) -> None:
        if tab == "signup":
            signup_form.visible = True
            login_form.visible = False
            tab_signup.style = ButtonStyle(color="#08B9FF")
            tab_login.style = ButtonStyle(color=Colors.GREY)
        else:
            signup_form.visible = False
            login_form.visible = True
            tab_signup.style = ButtonStyle(color=Colors.GREY)
            tab_login.style = ButtonStyle(color="#08B9FF")
        page.update()
    
    # set signup as default
    tab_signup.style = ButtonStyle(color="#08B9FF")
    tab_login.style = ButtonStyle(color=Colors.GREY)
    
    def do_signup(e):
        # check if username is already taken
        user = signup_user.value
        if username_exists(user):
            signup_user_err.value = "Username already taken"
            page.update()
            return
        
        # create the account
        pwd = signup_pass.value
        add_user(user, pwd)
        
        # go to dashboard
        from dashboard import create_dashboard
        create_dashboard(page, user) # type: ignore
    
    def do_login(e: ControlEvent) -> None:
        user = login_user.value
        pwd = login_pass.value
        
        # check credentials
        valid = check_user(user, pwd)
        
        if not valid:
            login_pass_err.value = "Wrong username or password"
            page.update()
            return
        
        # logged in successfully
        from dashboard import create_dashboard
        create_dashboard(page, user) # type: ignore
    
    # connect event handlers signup
    signup_user.on_change = check_signup
    signup_user.on_blur = signup_user_blur
    signup_pass.on_change = check_signup
    signup_pass.on_blur = signup_pass_blur
    terms_checkbox.on_change = check_signup
    signup_btn.on_click = do_signup
    
    # connect event handlers for login
    login_user.on_change = check_login # type: ignore
    login_user.on_blur = login_user_blur
    login_pass.on_change = check_login # type: ignore
    login_pass.on_blur = login_pass_blur
    login_btn.on_click = do_login # type: ignore
    
    # build the page
    page.add(
        Row(
            controls=[
                Column(
                    controls=[
                        Text(value="PeakForm", size=28, weight=FontWeight.BOLD),
                        Row(
                            controls=[tab_signup, tab_login],
                            alignment=MainAxisAlignment.CENTER
                        ),
                        signup_form,
                        login_form
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    spacing=20
                )
            ],
            alignment=MainAxisAlignment.CENTER
        )
    )

if __name__ == '__main__':
    ft.app(target=main)
