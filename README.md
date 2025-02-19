Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

api docs: https://project-letsie.bounceme.net/api/docs/redoc.html

демо: https://project-letsie.bounceme.net
создание админа: python manage.py init_admin (food.management.commands.init_admin.Command)
