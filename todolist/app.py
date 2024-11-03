import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect, url_for,
    flash,
    request
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from db_interaction import get_session
from forms import TaskForm, RegistrationForm, LoginForm
from models import User, Task

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    with get_session() as session:
        user = session.query(User).get(int(user_id))
        return user  # Этот объект будет отслеживаться в рамках сессии


@app.route("/")
def index():
    # Получаем параметр категории из запроса
    category_filter = request.args.get("category")

    with get_session() as session:
        # Если фильтр по категории задан, фильтруем задачи по этой категории
        if category_filter:
            tasks = session.query(Task).filter(
                Task.category == category_filter).all()
        else:
            tasks = session.query(Task).all()

        # Получаем уникальные категории задач
        categories = session.query(Task.category).distinct().all()

        # Преобразуем список кортежей категорий в простой список
        categories = [category[0] for category in categories]

        # Проверяем, аутентифицирован ли текущий пользователь
        user = current_user if current_user.is_authenticated else None

        if user:
            user = session.merge(user)  # user будет связан с текущей сессией

        return render_template("index.html", tasks=tasks,
                               categories=categories, current_user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        with get_session() as session:
            session.add(user)
            session.commit()

        flash("Your account has been created! You can now log in.",
              "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with get_session() as session:
            user = session.query(User).filter_by(
                username=form.username.data).first()
            if user:
                if user.check_password(form.password.data):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash("Login unsuccessful. Please check your "
                          "username and password", "danger")
            else:
                flash("Login unsuccessful. User not found.",
                      "danger")

    return render_template("login.html", form=form)


@app.route("/task/<int:task_id>")
@login_required
def task_detail(task_id):
    with get_session() as session:
        task = session.query(Task).get(task_id)
        if task is None:
            # Переход на главную страницу, если задача не найдена
            return redirect(url_for("index"))
        return render_template("task_detail.html", task=task)


@app.route("/create_task", methods=["GET", "POST"])
@login_required
def create_task():
    with get_session() as session:
        form = TaskForm()

        # Получаем список пользователей из базы данных
        users = session.query(User).all()
        form.user_id.choices = [(user.id, user.username) for user in users]

        if form.validate_on_submit():
            new_task = Task(
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                status=form.status.data if form.status.data else None,
                attachment=form.attachment.data if form.attachment.data else None,
                user_id=form.user_id.data,
                due_date=form.due_date.data if form.due_date.data else None
            )
            session.add(new_task)
            session.commit()
            # После создания задачи перенаправляем на главную страницу
            return redirect(url_for("index"))
        # Если метод GET или форма не прошла валидацию, показываем ту же форму
        return render_template("create_task.html", form=form)


@app.route("/<int:task_id>/edit_task", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    with get_session() as session:
        task = session.query(Task).get(task_id)

        form = TaskForm(obj=task)
        users = session.query(User).all()
        form.user_id.choices = [(user.id, user.username) for user in users]

        if form.validate_on_submit():
            task.title = form.title.data
            task.description = form.description.data
            task.category = form.category.data
            task.status = form.status.data if form.status.data else None
            task.attachment = form.attachment.data if form.attachment.data else None
            task.user_id = form.user_id.data
            task.due_date = form.due_date.data if form.due_date.data else None

            session.commit()

            # Перенаправляем на страницу с описанием задачи
            return redirect(url_for("task_detail", task_id=task.id))

        # Если метод GET или форма не прошла валидацию
        # возвращаем шаблон с формой для редактирования задачи
        return render_template("edit_task.html",
                               form=form, task=task)


@app.route("/<int:task_id>/delete_task", methods=["POST"])
@login_required
def delete_task(task_id):
    with get_session() as session:
        task = session.query(Task).get(task_id)
        if not task:
            return redirect(url_for("index"))
    session.delete(task)
    session.commit()
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
