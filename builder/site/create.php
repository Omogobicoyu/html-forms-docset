<?php
// СОЗДАНИЕ ЗАЯВКИ: принимаем помещение, дату и способ оплаты, затем пишем в requests.
require 'db.php';
// Если входа нет, функция перенаправит на index.php и остановит страницу.
require_login();
// Переменная для сообщения об ошибке и список разрешённых вариантов оплаты.
$error = '';
$payments = ['При очном посещении', 'Переводом по системе СБП'];
// При первом открытии показываем форму; при POST обрабатываем отправленные поля.
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // name полей формы определяет ключи в $_POST.
    // ?? '' защищает от отсутствующего поля; trim убирает пробелы по краям.
    $room = trim($_POST['room'] ?? '');
    $starts_at = trim($_POST['starts_at'] ?? '');
    $payment = $_POST['payment'] ?? '';
    // Превращаем строку даты в объект DateTime.
    // d.m.Y — день.месяц.год, H:i — часы:минуты; ! сбрасывает неуказанные части,
    // в частности секунды, чтобы они не брались из текущего времени.
    $date = DateTime::createFromFormat('!d.m.Y H:i', $starts_at);
    // Название не должно быть пустым или длиннее 200 символов.
    if ($room === '' || mb_strlen($room, 'UTF-8') > 200) {
        $error = 'Введите название помещения (до 200 символов).';
    // DateTime может исправить несуществующую дату, например 31 февраля.
    // Сравниваем дату после обратного форматирования с исходной строкой.
    // !$date — разбор вообще не удался; год от 1000 соответствует диапазону DATETIME.
    } elseif (!$date || $date->format('d.m.Y H:i') !== $starts_at || $date->format('Y') < 1000) {
        $error = 'Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ.';
    // in_array проверяет наличие значения в списке; true включает строгое сравнение.
    } elseif (!in_array($payment, $payments, true)) {
        $error = 'Выберите способ оплаты.';
    } else {
        // INSERT добавляет строку в requests. Четырём столбцам соответствуют четыре ?.
        $query = $db->prepare('INSERT INTO requests (user_id, room, starts_at, payment) VALUES (?, ?, ?, ?)');
        // user_id берём из сессии, чтобы заявка принадлежала вошедшему пользователю.
        // Дату переводим в формат MySQL: год-месяц-день часы:минуты:секунды.
        // execute подставляет значения по порядку, отдельно от текста SQL.
        $query->execute([$_SESSION['user_id'], $room, $date->format('Y-m-d H:i:s'), $payment]);
        // После сохранения открываем список заявок и прекращаем выполнение.
        // При обновлении списка форма создания повторно не отправится.
        header('Location: requests.php');
        exit;
    }
}
// Общая шапка выводит название страницы, меню и сообщение $error, если оно есть.
$title = 'Формирование заявки';
require 'header.php';
?>
<!-- POST отправляет данные на эту же страницу. Bootstrap-класс col-md-6 задаёт ширину.
     required требует заполнения; value возвращает введённые данные после ошибки.
     e() обрабатывает текст для вставки в HTML. -->
<form method="post" class="col-md-6">
    <!-- label связан с полем через for/id. name="room" создаёт $_POST['room']. -->
    <label class="form-label" for="room">Название помещения</label>
    <input class="form-control mb-3" id="room" name="room" maxlength="200" value="<?= e($_POST['room'] ?? '') ?>" required>
    <!-- placeholder — пример ввода, который сам по себе не отправляется.
         Это текстовое поле; точный формат даты проверяет PHP в начале файла. -->
    <label class="form-label" for="starts_at">Дата и время начала (ДД.ММ.ГГГГ ЧЧ:ММ)</label>
    <input class="form-control mb-3" id="starts_at" name="starts_at" placeholder="20.12.2026 10:00" value="<?= e($_POST['starts_at'] ?? '') ?>" required>
    <!-- select — выпадающий список. Его выбранное значение придёт в $_POST['payment']. -->
    <label class="form-label" for="payment">Способ оплаты</label>
    <select class="form-select mb-3" id="payment" name="payment" required>
        <!-- Пустое значение не проходит required: нужно выбрать настоящий вариант. -->
        <option value="">Выберите способ оплаты</option>
        <!-- foreach перебирает массив $payments: на каждом шаге $payment — один вариант.
             selected сохраняет выбор после ошибки. У option без value отправляется текст.
             endforeach завершает цикл, а короткая вставка PHP выводит значение. -->
        <?php foreach ($payments as $payment): ?>
            <option <?= ($_POST['payment'] ?? '') === $payment ? 'selected' : '' ?>><?= e($payment) ?></option>
        <?php endforeach; ?>
    </select>
    <!-- Кнопка без type внутри формы отправляет данные на сервер. -->
    <button class="btn btn-primary">Отправить</button>
</form>
<!-- Закрывающие теги общей страницы вынесены в footer.php. -->
<?php require 'footer.php'; ?>
