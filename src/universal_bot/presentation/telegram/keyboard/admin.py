ADMIN_KEYBOARD = {
    "keyboard": [
        [{"text": text} for text in row]
        for row in [
            ("Пользователи", "Добавить пользователя"),
            ("Получить уведомления", "Запросы на доступ"),
            ("Состояние сервера",),
        ]
    ],
    "resize_keyboard": True,
}
