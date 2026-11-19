<?php
// МОИ ЗАЯВКИ: показываем заявки текущего пользователя и принимаем отзывы.
require 'db.php';
// До чтения и изменения заявок убеждаемся, что пользователь вошёл.
require_login();
$error = '';
// POST на этой странице приходит из формы сохранения отзыва.
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Читаем текст, убираем пробелы по краям; отсутствующее поле заменяем пустой строкой.
    $review = trim($_POST['review'] ?? '');
    // Пустой отзыв и отзыв длиннее 5000 символов не сохраняем.
    if ($review === '' || mb_strlen($review, 'UTF-8') > 5000) {
        $error = 'Введите отзыв (до 5000 символов).';
    } else {
        // UPDATE меняет существующую строку. SET задаёт новое значение review.
        // WHERE ограничивает изменение: нужный ID, свой user_id и статус «Завершено».
        // AND требует выполнения всех трёх условий одновременно.
        $query = $db->prepare("UPDATE requests SET review = ? WHERE id = ? AND user_id = ? AND status = 'Завершено'");
        // Значения соответствуют трём ?: отзыв, ID заявки, ID владельца из сессии.
        // (int) приводит ID к целому числу; если поле не передано, получится 0.
        // Проверка владельца в SQL не позволяет изменить чужую заявку подменой ID.
        $query->execute([$review, (int)($_POST['id'] ?? 0), $_SESSION['user_id']]);
        // После обработки переходим на GET этой страницы: обновление не повторит POST.
        header('Location: requests.php');
        exit;
    }
}
// Выбираем все столбцы только своих заявок. DESC — сначала больший, то есть более новый ID.
$query = $db->prepare('SELECT * FROM requests WHERE user_id = ? ORDER BY id DESC');
$query->execute([$_SESSION['user_id']]);
// fetchAll возвращает массив строк; каждая строка — массив с именами столбцов.
$requests = $query->fetchAll();
// Передаём название и возможную ошибку в общую шапку.
$title = 'Мои заявки';
require 'header.php';
?>
<!-- Пустой массив считается ложным, поэтому !$requests означает «заявок нет». -->
<?php if (!$requests): ?><p>У вас пока нет заявок.</p><?php endif; ?>
<!-- foreach создаёт отдельную карточку для каждой строки из $requests.
     $request — текущая заявка. endforeach внизу завершает повторение. -->
<?php foreach ($requests as $request): ?>
    <!-- Классы Bootstrap: border — рамка, rounded — скругление,
         p-3 — внутренний отступ, mb-3 — отступ снизу. -->
    <section class="border rounded p-3 mb-3">
        <!-- Ключи id и room совпадают с именами столбцов таблицы requests.
             Текстовые значения выводим через e(), чтобы они не стали HTML-разметкой. -->
        <h3>Заявка №<?= $request['id'] ?>: <?= e($request['room']) ?></h3>
        <!-- strtotime переводит дату MySQL в метку времени, date оформляет её для человека.
             d.m.Y H:i — день.месяц.год часы:минуты. -->
        <p class="help-text">Создана: <?= date('d.m.Y H:i', strtotime($request['created_at'])) ?></p>
        <p>Начало: <?= date('d.m.Y H:i', strtotime($request['starts_at'])) ?></p>
        <p>Оплата: <?= e($request['payment']) ?></p>
        <p>Статус: <?= e($request['status']) ?></p>
        <!-- Форму отзыва показываем только для завершённой заявки.
             Это же условие повторено в SQL выше: одной проверки интерфейса недостаточно. -->
        <?php if ($request['status'] === 'Завершено'): ?>
            <form method="post">
                <!-- Скрытое поле не видно, но оно отправляет ID вместе с отзывом. -->
                <input type="hidden" name="id" value="<?= $request['id'] ?>">
                <!-- ID с номером заявки уникален: у каждой карточки своя подпись и поле. -->
                <label class="form-label" for="review-<?= $request['id'] ?>">Отзыв о качестве проведенного мероприятия</label>
                <!-- textarea — многострочный ввод. Его значение пишут между тегами,
                     а не в value. Уже сохранённый отзыв можно отредактировать.
                     rows задаёт видимую высоту, maxlength — предел длины. -->
                <textarea class="form-control mb-3" id="review-<?= $request['id'] ?>" name="review" rows="2" maxlength="5000" required><?= e($request['review']) ?></textarea>
                <button class="btn btn-primary">Сохранить отзыв</button>
            </form>
        <!-- Если статус другой, но отзыв уже есть, показываем его обычным текстом. -->
        <?php elseif ($request['review']): ?>
            <p>Отзыв: <?= e($request['review']) ?></p>
        <?php endif; ?>
    </section>
<?php endforeach; ?>
<!-- Общий файл закрывает main, body и html. -->
<?php require 'footer.php'; ?>
