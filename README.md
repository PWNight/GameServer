## О проекте
Игровой API сервер на Flask с системой авторизации/регистрации,
управления персонажем, его инвентарём, предметами и сделками
## Методы
### `GET /`
Получение HTML-страницы с содержимым README.md.

    curl http://localhost:5005/

---

### `POST /reg`
Регистрация аккаунта.

    curl -X POST http://localhost:5005/reg -H "Content-Type: application/json" -d 
    '{"login": "user1", "password": "pass123"}'

---

### `POST /login`
Авторизация пользователя.

    curl -X POST http://localhost:5005/login -H "Content-Type: application/json" -d 
    '{"login": "user1", "password": "pass123"}'

---

### `POST /out`
Выход из аккаунта.

    curl -X POST http://localhost:5005/out -H "Content-Type: application/json" -d 
    '{"login": "user1"}'

---

### `POST /password`
Изменение пароля.

    curl -X POST http://localhost:5005/password -H "Content-Type: application/json" -d 
    '{"login": "user1", "password": "newpass456"}'

---

### `POST /character`
Создание персонажа.

    curl -X POST http://localhost:5005/character -H "Content-Type: application/json" -d 
    '{"login": "user1", "name": "Hero1"}'

---

### `POST /level_up`
Повышение уровня персонажа.

    curl -X POST http://localhost:5005/level_up -H "Content-Type: application/json" -d 
    '{"name": "Hero1"}'

---

### `POST /level_down`
Понижение уровня персонажа.

    curl -X POST http://localhost:5005/level_down -H "Content-Type: application/json" -d 
    '{"name": "Hero1"}'

---

### `POST /inventory/add`
Добавление предмета в инвентарь.

    curl -X POST http://localhost:5005/inventory/add -H "Content-Type: application/json" -d 
    '{"character_name": "Hero1", "item": {"name": "Sword", "type": "weapon", "value": 100, "weight": 5, "bonus": "strength"}}'

---

### `POST /inventory/remove`
Удаление предмета из инвентаря.

    curl -X POST http://localhost:5005/inventory/remove -H "Content-Type: application/json" -d 
    '{"character_name": "Hero1", "item_name": "Sword"}'

---

### `POST /trade/offer`
Создание предложения сделки.

    curl -X POST http://localhost:5005/trade/offer -H "Content-Type: application/json" -d 
    '{"initiator_name": "Hero1", "target_name": "Hero2", "items_offered": ["Sword"], "items_requested": ["Shield"]}'

---

### `POST /trade/accept`
Принятие сделки.

    curl -X POST http://localhost:5005/trade/accept -H "Content-Type: application/json" -d '{"target_name": "Hero2", "initiator_name": "Hero1"}'

---

### `POST /trade/decline`
Отклонение сделки.

    curl -X POST http://localhost:5005/trade/decline -H "Content-Type: application/json" -d '{"target_name": "Hero2", "initiator_name": "Hero1"}'

---

### `POST /trade/cancel`
Отмена сделки.

    curl -X POST http://localhost:5005/trade/cancel -H "Content-Type: application/json" -d '{"initiator_name": "Hero1"}'
## Планы на версии:
### v1.1
* Обновление readme
* Улучшение названий текущих методов
* Улучшение названий входящих параметров
* Метод получения инвентаря игрока
* Метод получения уровня игрока
* Метод изменения названия персонажа игрока
* Метод изменения логина
* Метод удаления персонажа игрока
* Метод удаления аккаунта