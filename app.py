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

class BookReview(db.Model):
    __tablename__ = 'book_reviews'  # Имя таблицы
    id_review = db.Column(db.Integer, primary_key=True)  # Первичный ключ
    review = db.Column(db.Text, nullable=False)  # Отзыв о книге
    grade = db.Column(db.Float, nullable=False)  # Оценка книги
    id_book = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)  # Внешний ключ

    # Отношение между таблицами
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))


# Главная страница
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

# Список жанров
GENRES = [
    "Автобиография",
    "Автомобили",
    "Архитектура",
    "Астрология",
    "Астрономия",
    "Аэрокосмос",
    "Бизнес",
    "Биография",
    "Биология",
    "Военная литература",
    "Гаджеты",
    "География",
    "Детектив",
    "Детская литература",
    "Дистопия",
    "Документальная литература",
    "Домоводство",
    "Драма",
    "Живопись",
    "Здоровье",
    "Инженерия",
    "Информатика",
    "Искусство",
    "История",
    "Йога",
    "Киберпанк",
    "Кино",
    "Классическая литература",
    "Краеведение",
    "Криминалистика",
    "Кулинария",
    "Ландшафтный дизайн",
    "Литература на иностранных языках",
    "Любовный роман",
    "Магия",
    "Маркетинг",
    "Математика",
    "Медитация",
    "Мемуары",
    "Менеджмент",
    "Методическая литература",
    "Механика",
    "Мистика",
    "Музыка",
    "Научная литература",
    "Научная фантастика",
    "Подростковая литература",
    "Политика",
    "Постапокалипсис",
    "Поэзия",
    "Приключения",
    "Программирование",
    "Психология",
    "Публицистика",
    "Путеводители",
    "Путешествия",
    "Пьеса",
    "Религия",
    "Роман",
    "Рукоделие",
    "Саморазвитие",
    "Сатира",
    "Сказки",
    "Словари",
    "Современная проза",
    "Спорт",
    "Стимпанк",
    "Сценарии",
    "Театр",
    "Телевидение",
    "Темное фэнтези",
    "Техническая литература",
    "Триллер",
    "Ужасы",
    "Утопия",
    "Учебная литература",
    "Фантастика",
    "Физика",
    "Философия",
    "Финансы",
    "Фольклор",
    "Фотоальбомы",
    "Фэнтези",
    "Фэнтези-эпос",
    "Химия",
    "Хобби",
    "Шпионский роман",
    "Эзотерика",
    "Экономика",
    "Энциклопедии",
    "Энциклопедии для детей",
    "Эпопея",
    "Эссе",
    "Юмор",
    "Юриспруденция",
    "Языки и перевод"
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

# Переход в раздел информации о книге
@app.route('/book/<int:book_id>', methods=['GET'])
def book_details(book_id):
    book = Book.query.get_or_404(book_id)  # Получаем книгу по ID
    return render_template('book_details.html', book=book)

# Добавление отзыва
@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.json
    review = data.get('review')
    grade = data.get('grade')
    id_book = data.get('id_book')

    # Проверка данных
    if not review or not grade or not id_book:
        return jsonify({'error': 'Все поля обязательны'}), 400

    # Добавляем новый отзыв
    new_review = BookReview(review=review, grade=float(grade), id_book=id_book)
    db.session.add(new_review)

    # Пересчитываем средний рейтинг книги
    book = Book.query.get(id_book)
    reviews = BookReview.query.filter_by(id_book=id_book).all()
    book.rating = round(sum([r.grade for r in reviews]) / len(reviews), 2)

    db.session.commit()

    return jsonify({'message': 'Отзыв добавлен!'}), 201

#Получение рекомендаций
@app.route('/recommendations_page', methods=['GET'])
def recommendations_page():
    genre = request.args.get('genre', None)
    if genre:
        recommended_books = Book.query.filter(Book.genre == genre).order_by(Book.rating.desc()).all()
    else:
        recommended_books = Book.query.order_by(Book.rating.desc()).all()
    return render_template('recommendations.html', genres=GENRES, recommended_books=recommended_books)



if __name__ == '__main__':
    with app.app_context():  # Создание контекста приложения
        db.create_all()      # Создание всех таблиц
    app.run(debug=True)


