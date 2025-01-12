from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

# Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, default=0.0)

# Главная страница
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

# Список жанров
GENRES = [
    "Фантастика",
    "Роман",
    "Детектив",
    "Научная литература",
    "Поэзия",
    "Фэнтези",
    "История",
    "Биография",
    "Автобиография",
    "Приключения",
    "Ужасы",
    "Триллер",
    "Мистика",
    "Любовный роман",
    "Юмор",
    "Сатира",
    "Пьеса",
    "Драма",
    "Эпопея",
    "Эссе",
    "Публицистика",
    "Детская литература",
    "Подростковая литература",
    "Сказки",
    "Фольклор",
    "Научная фантастика",
    "Киберпанк",
    "Стимпанк",
    "Фэнтези-эпос",
    "Темное фэнтези",
    "Современная проза",
    "Классическая литература",
    "Дистопия",
    "Утопия",
    "Постапокалипсис",
    "Психология",
    "Саморазвитие",
    "Философия",
    "Религия",
    "Мемуары",
    "Документальная литература",
    "Кулинария",
    "Здоровье",
    "Спорт",
    "Путешествия",
    "Фотоальбомы",
    "Искусство",
    "Музыка",
    "Архитектура",
    "Живопись",
    "Техническая литература",
    "Информатика",
    "Программирование",
    "Гаджеты",
    "Бизнес",
    "Финансы",
    "Маркетинг",
    "Менеджмент",
    "Экономика",
    "Политика",
    "Юриспруденция",
    "Криминалистика",
    "Военная литература",
    "Шпионский роман",
    "География",
    "Краеведение",
    "Энциклопедии",
    "Словари",
    "Учебная литература",
    "Методическая литература",
    "Языки и перевод",
    "Энциклопедии для детей",
    "Физика",
    "Химия",
    "Биология",
    "Астрономия",
    "Математика",
    "Инженерия",
    "Механика",
    "Автомобили",
    "Аэрокосмос",
    "Ландшафтный дизайн",
    "Домоводство",
    "Рукоделие",
    "Хобби",
    "Кино",
    "Театр",
    "Телевидение",
    "Сценарии",
    "Путеводители",
    "Эзотерика",
    "Магия",
    "Астрология",
    "Медитация",
    "Йога",
    "Литература на иностранных языках"
]


# Маршрут для получения жанров
@app.route('/genres', methods=['GET'])
def get_genres():
    query = request.args.get('q', '').lower()  # Получение параметра запроса
    suggestions = [genre for genre in GENRES if query in genre.lower()]
    return jsonify(suggestions)


# Добавление книги
@app.route('/add', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(title=data['title'], author=data['author'], genre=data['genre'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Книга добавлена!"}), 201

# Удаление книги
@app.route('/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Книга удалена!"})
    return jsonify({"error": "Книга не найдена"}), 404

if __name__ == '__main__':
    with app.app_context():  # Создание контекста приложения
        db.create_all()      # Создание всех таблиц
    app.run(debug=True)


