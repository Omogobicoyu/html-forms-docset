<?php
// ПАНЕЛЬ АДМИНИСТРАТОРА: все заявки, данные их авторов и изменение статуса.
require 'db.php';
// Сначала проверяем вход, затем отдельно проверяем право администратора.
require_login();
// !== означает строгое «не равно». Роль берётся из сессии, созданной при входе.
if ($_SESSION['role'] !== 'admin') {
    // Код HTTP 403 означает отказ в доступе. exit выводит текст и завершает PHP.
    http_response_code(403);
    exit('Доступ только для администратора.');
}
// Сообщение об ошибке и полный список допустимых статусов.
$error = '';
$statuses = ['Новая', 'Мероприятие назначено', 'Завершено'];
// POST приходит при нажатии «Изменить статус» в одной из карточек.
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // ?? '' подставляет пустую строку, если status не был передан.
    $status = $_POST['status'] ?? '';
    // Принимаем только значение из списка; true включает строгое сравнение.
    if (!in_array($status, $statuses, true)) {
        $error = 'Недопустимый статус.';
    } else {
        // UPDATE меняет status, а WHERE id = ? выбирает конкретную заявку.
        // Подготовленный запрос получает значения отдельно от текста SQL.
        $query = $db->prepare('UPDATE requests SET status = ? WHERE id = ?');
        // Порядок значений совпадает с ?: новый статус, затем целочисленный ID заявки.
        $query->execute([$status, (int)($_POST['id'] ?? 0)]);
        // Перенаправление после POST открывает обновлённый список без повторной отправки.
        header('Location: admin.php');
        exit;
    }
}
// SELECT requests.* берёт все столбцы заявки и дополнительно данные её автора из users.
// JOIN соединяет таблицы: requests.user_id указывает на users.id.
// ORDER BY requests.id DESC выводит новые заявки первыми.
// Здесь нет подставляемых данных формы, поэтому выполняем постоянный SQL через query.
// ->fetchAll() сразу превращает результат запроса в массив заявок.
$requests = $db->query('SELECT requests.*, users.login, users.full_name, users.phone, users.email FROM requests JOIN users ON users.id = requests.user_id ORDER BY requests.id DESC')->fetchAll();
// Заголовок и возможную ошибку выводит общий файл шапки.
$title = 'Панель администратора';
require 'header.php';
?>
<!-- Сообщение показывается, когда массив результатов пуст. -->
<?php if (!$requests): ?><p>Заявок пока нет.</p><?php endif; ?>
<!-- Для каждого элемента массива создаём карточку. $request — одна текущая заявка. -->
<?php foreach ($requests as $request): ?>
    <!-- Bootstrap-классы добавляют рамку, скругление и отступы. -->
    <section class="border rounded p-3 mb-3">
        <!-- Короткие вставки PHP выводят поля строки. e() обрабатывает текст для HTML. -->
        <h3>Заявка №<?= $request['id'] ?>: <?= e($request['room']) ?></h3>
        <!-- strtotime читает дату из БД, date переводит её в формат день.месяц.год часы:минуты. -->
        <p class="help-text">Создана: <?= date('d.m.Y H:i', strtotime($request['created_at'])) ?></p>
        <!-- Данные автора доступны благодаря JOIN в запросе выше. -->
        <p>Пользователь: <?= e($request['full_name']) ?> (<?= e($request['login']) ?>)</p>
        <p>Телефон: <?= e($request['phone']) ?>. Почта: <?= e($request['email']) ?></p>
        <p>Начало: <?= date('d.m.Y H:i', strtotime($request['starts_at'])) ?></p>
        <p>Оплата: <?= e($request['payment']) ?></p>
        <!-- Отзыв выводим, только если он непустой. -->
        <?php if ($request['review']): ?><p>Отзыв: <?= e($request['review']) ?></p><?php endif; ?>
        <!-- У каждой заявки своя POST-форма, отправляемая на эту же страницу. -->
        <form method="post" class="col-md-6">
            <!-- Скрытое поле сообщает обработчику, какую именно заявку изменять. -->
            <input type="hidden" name="id" value="<?= $request['id'] ?>">
            <!-- Число в id делает идентификатор списка уникальным для каждой карточки. -->
            <label class="form-label" for="status-<?= $request['id'] ?>">Статус</label>
            <select class="form-select mb-3" id="status-<?= $request['id'] ?>" name="status">
                <!-- Перебираем разрешённые статусы. selected отмечает текущий статус.
                     У option без value отправляемым значением будет его текст.
                     Условие ? 'selected' : '' выводит атрибут или пустую строку. -->
                <?php foreach ($statuses as $status): ?>
                    <option <?= $request['status'] === $status ? 'selected' : '' ?>><?= e($status) ?></option>
                <?php endforeach; ?>
            </select>
            <!-- Кнопка отправляет поля id и status в $_POST. -->
            <button class="btn btn-primary">Изменить статус</button>
        </form>
    </section>
<?php endforeach; ?>
<!-- Завершаем общую разметку страницы. -->
<?php require 'footer.php'; ?>
