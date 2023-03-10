# Django marketplace
Это backend-основа для создания онлайн-магазина. Реализовано следующее:
- отображение списка товаров (кэшировано) на главной странице с пагинацией и добавлением в корзину;
- регистрация и авторизация пользователя;
- страница корзины с редактированием состава;
- сохранение корзины анонимного пользователя и объединение корзин при авторизации;
- личный кабинет с данными пользователя и историей оформленных заказов (кэшировано);
- смена статуса пользователя в зависимости от суммы покупок;
- сервис оформления заказа;
- сервис пополнения баланса;
- сервис формирования отчёта по наиболее продаваемым товарам;
- i18n и L10n для русского и английского языков;
- настройка логирования (консоль, файл) и профилирования (django-debug-toolbar);
- тестирование представлений.

*Примечания:*
1) В сервисном слое бизнес-логика изолирована от инфраструктуры с использованием Data Access Objects.
2) Сброс кэша и удаление устаревших корзин реализовано через сигналы.

## Установка и запуск
Клонируйте проект:
```
git clone https://github.com/AlexEmelianov/Django-marketplace.git
```
Установите зависимости:
```
pip install -r requirements.txt
```
Создайте и примените миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Примените файл переводов на русский язык:
```
python manage.py compilemessages -l ru
```
- Создайте учетную запись суперпользователя:
```
python manage.py createsuperuser
```
- Для тестирования установите фикстуры товаров (10) и магазинов (4):
```
python manage.py loaddata app_shops_fixture.json
```
- Для создания большого количества товаров (1000) используете команду:
```
python manage.py create_products
``` 
- Запустите сервер с указанием порта:
```
python manage.py runserver <порт>
```

## Автор проекта
Алексей Емельянов — Python developer
- [Telegram](https://web.telegram.org/k/): @emelianov_alex
- e-mail: emelyanov000@gmail.com