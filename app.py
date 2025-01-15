import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Конфигурация подключения к PostgreSQL
db_config = {
    'dbname': 'railway',
    'user': 'postgres',
    'password': 'VfOorDfGdOXTaLnhKWjiUEBpFneqIeeI',
    'host': 'autorack.proxy.rlwy.net',
    'port': '12758'
}

def get_db_connection():
    return psycopg2.connect(**db_config)

# Преобразование кортежей в словари
def tuple_to_dict(cursor, data):
    columns = [desc[0] for desc in cursor.description]
    if isinstance(data, list):
        return [dict(zip(columns, row)) for row in data]
    if isinstance(data, tuple):
        return dict(zip(columns, data))
    return None

# Главная страница
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, author, genre, COALESCE(rating, 0) AS rating FROM books")
    books = tuple_to_dict(cursor, cursor.fetchall())
    cursor.close()
    connection.close()
    return render_template('index.html', books=books)

# Список жанров
GENRES = [
    "Автобиография", "Автомобили", "Архитектура", "Астрология", "Астрономия", "Аэрокосмос", "Бизнес", "Биография",
    "Биология", "Военная литература", "Гаджеты", "География", "Детектив", "Детская литература", "Дистопия",
    "Документальная литература", "Домоводство", "Драма", "Живопись", "Здоровье", "Инженерия", "Информатика", "Искусство",
    "История", "Йога", "Киберпанк", "Кино", "Классическая литература", "Краеведение", "Криминалистика", "Кулинария",
    "Ландшафтный дизайн", "Литература на иностранных языках", "Любовный роман", "Магия", "Маркетинг", "Математика",
    "Медитация", "Мемуары", "Менеджмент", "Методическая литература", "Механика", "Мистика", "Музыка", "Научная литература",
    "Научная фантастика", "Подростковая литература", "Политика", "Постапокалипсис", "Поэзия", "Приключения",
    "Программирование", "Психология", "Публицистика", "Путеводители", "Путешествия", "Пьеса", "Религия", "Роман",
    "Рукоделие", "Саморазвитие", "Сатира", "Сказки", "Словари", "Современная проза", "Спорт", "Стимпанк", "Сценарии",
    "Театр", "Телевидение", "Темное фэнтези", "Техническая литература", "Триллер", "Ужасы", "Утопия", "Учебная литература",
    "Фантастика", "Физика", "Философия", "Финансы", "Фольклор", "Фотоальбомы", "Фэнтези", "Фэнтези-эпос", "Химия",
    "Хобби", "Шпионский роман", "Эзотерика", "Экономика", "Энциклопедии", "Энциклопедии для детей", "Эпопея", "Эссе",
    "Юмор", "Юриспруденция", "Языки и перевод"
]

@app.route('/genres', methods=['GET'])
def get_genres():
    query = request.args.get('q', '').lower()
    suggestions = [genre for genre in GENRES if query in genre.lower()]
    return jsonify(suggestions)

@app.route('/add', methods=['POST'])
def add_book():
    data = request.json
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO books (title, author, genre, rating)
        VALUES (%s, %s, %s, %s)
        """,
        (data['title'], data['author'], data['genre'], 0.0)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Книга добавлена!"}), 201

@app.route('/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Книга удалена!"})

@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.json
    review = data.get('review')
    grade = data.get('grade')
    id_book = data.get('id_book')

    if not (review and grade and id_book):
        return "Все поля обязательны!", 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Добавление отзыва
    cursor.execute(
        """
        INSERT INTO book_reviews (review, grade, id_book)
        VALUES (%s, %s, %s)
        """,
        (review, grade, id_book)
    )

    # Пересчёт среднего рейтинга
    cursor.execute(
        "SELECT AVG(grade) FROM book_reviews WHERE id_book = %s", (id_book,)
    )
    new_rating = cursor.fetchone()[0]

    cursor.execute(
        "UPDATE books SET rating = %s WHERE id = %s", (new_rating, id_book)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Отзыв успешно добавлен!"}), 201



@app.route('/book/<int:book_id>', methods=['GET'])
def book_details(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Получаем данные о книге
    cursor.execute("SELECT id, title, author, genre, rating FROM books WHERE id = %s", (book_id,))
    book_data = cursor.fetchone()

    # Получаем отзывы для этой книги
    cursor.execute("SELECT review, grade FROM book_reviews WHERE id_book = %s", (book_id,))
    reviews_data = cursor.fetchall()

    cursor.close()
    connection.close()

    if book_data:
        book = {
            'id': book_data[0],
            'title': book_data[1],
            'author': book_data[2],
            'genre': book_data[3],
            'rating': book_data[4],
            'reviews': [{'review': r[0], 'grade': r[1]} for r in reviews_data]
        }
        return render_template('book_details.html', book=book)

    return jsonify({"error": "Книга не найдена"}), 404


@app.route('/recommendations_page', methods=['GET'])
def recommendations_page():
    genre = request.args.get('genre', None)
    connection = get_db_connection()
    cursor = connection.cursor()
    if genre:
        cursor.execute(
            "SELECT id, title, author, genre, rating FROM books WHERE genre = %s ORDER BY rating DESC",
            (genre,)
        )
    else:
        cursor.execute("SELECT id, title, author, genre, rating FROM books ORDER BY rating DESC")
    recommended_books = tuple_to_dict(cursor, cursor.fetchall())
    cursor.close()
    connection.close()
    return render_template('recommendations.html', genres=GENRES, recommended_books=recommended_books)

if __name__ == '__main__':
    app.run(debug=True)
