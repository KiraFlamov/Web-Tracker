# 🟢 Web-Tracker

Web-Tracker — это full-stack веб-приложение для управления задачами с авторизацией пользователей и REST API на FastAPI.

🌐 **Демо:** [web-tracker-7q0i.onrender.com](https://web-tracker-7q0i.onrender.com/)

> Приложение размещено на бесплатном тарифе Render: после простоя сервер «засыпает», поэтому первая загрузка может занять до минуты.

---

## Скриншоты

### Авторизация
<img src="screenshots/login.png" width="700"/>

### Заметки
<img src="screenshots/main.png" width="700"/>

### Изменение заметки
<img src="screenshots/edit.png" width="700"/>

## 🚀 Возможности

- Регистрация и авторизация пользователей (JWT + cookies)
- Создание, редактирование и удаление задач
- Сортировка задач по дате и статусу
- Разделение задач по пользователям
- AJAX-обновление данных без перезагрузки страницы
- Защита маршрутов (доступ только авторизованным пользователям)

---

## 🛠 Технологии

- Python
- FastAPI
- SQLAlchemy
- Jinja2
- PostgreSQL
- JWT
- HTML / CSS / JavaScript
- Render (хостинг) + Neon (PostgreSQL)

---

## ⚙️ Запуск проекта

```bash
git clone https://github.com/KiraFlamov/Web-Tracker.git
cd Web-Tracker

pip install -r requirements.txt
uvicorn main:app --reload
```

Перед запуском создайте файл `.env` в корне проекта:

```env
SECRET_KEY=любая-случайная-строка
DATABASE_URL=postgresql://user:password@localhost/task_tracker
```

Таблицы в базе создаются автоматически при первом запуске.

---

## Лицензия

Проект распространяется под лицензией MIT. Подробнее — в файле [LICENSE](LICENSE).
