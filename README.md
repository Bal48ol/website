# Выполнил: Москвичев Яков Александрович и Майоршин Руслан Новрузович группа №26
# Описание 
Сайт является блогом, где гости не имеют возможности регистрации. Получать логин пароль могут только модераторы от главного админа.

На сайте можно добовлять рецепты еды, после чего в телеграме опубликуется добавленный рецепт c ссылкой на страницу рецепта. Код сайта находится в файле main.py, все html-оформление сайта находится в папке templates.

На сайте имеется регистрация, поле поиска рецептов, лента рецептов, админ панель для администраторов и модераторов.

В самом боте появляются новые рецепты, которые публикуют на сайте. Публикация сообщений происходит с помощью библиотеки telebot и метода bot.send_message. Файл lastkey используется для того чтобы бот не публиковал опубликованный рецепт заново при перезапуске бота. В нем содержится id следующего не созданного рецепта. 

# Домены
Доступ к сайту: http://localhost:5000/, http://127.0.0.1:5000/

Доступ к админке сайта: http://localhost:5000/admin, http://127.0.0.1:5000/admin или через кнопку "Админ-панель" в шапке сайта. 

Логин, пароль: admin@mail.ru, qwerty

Телеграм бот: https://t.me/VsyakoeVkusnoe

Имя бота: @VsyakoeVkusnoe

# Запуск 
Запустить docker-compose.yml