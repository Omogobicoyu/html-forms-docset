<?php
// РЕГИСТРАЦИЯ: получаем данные, проверяем их и добавляем пользователя в users.
// Сначала подключаем базу, сессию и функцию e() для вывода текста.
require 'db.php';
// Общая шапка покажет сообщение, если эта строка станет непустой.
$error = '';
// Проверки выполняются после отправки формы, а не при первом открытии страницы.
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Ключи $_POST совпадают с name полей формы внизу файла.
    // ?? '' — значение по умолчанию; trim удаляет пробелы по краям.
    // Пароль не обрезаем: пробел может быть частью пароля.
    $login = trim($_POST['login'] ?? '');
    $password = $_POST['password'] ?? '';
    $full_name = trim($_POST['full_name'] ?? '');
    $phone = trim($_POST['phone'] ?? '');
    $email = trim($_POST['email'] ?? '');

    // preg_match проверяет строку по шаблону (регулярному выражению).
    // ^ и $ — границы строки; [A-Za-z0-9] — латиница и цифры;
    // {6,100} — от 6 до 100 символов; D требует конец строки без лишнего переноса.
    // ! означает «проверка не прошла». elseif проверяется, только если предыдущая прошла.
    if (!preg_match('/^[A-Za-z0-9]{6,100}$/D', $login)) {
        $error = 'Логин: латинские буквы и цифры, от 6 до 100 символов.';
    // mb_strlen с UTF-8 считает символы, а не байты: это важно для русского текста.
    } elseif (mb_strlen($password, 'UTF-8') < 8) {
        $error = 'Пароль должен содержать минимум 8 символов.';
    // Разрешены кириллические буквы, Ё/ё и пробелы; + требует хотя бы один символ.
    // u включает обработку Unicode; || означает «или»: неверный состав ИЛИ длина.
    } elseif (!preg_match('/^[А-Яа-яЁё ]+$/uD', $full_name) || mb_strlen($full_name, 'UTF-8') > 200) {
        $error = 'ФИО: только кириллица и пробелы, до 200 символов.';
    // Скобки экранированы обратной косой чертой: ожидаются именно символы ( и ).
    // [0-9]{3} — три цифры, {2} — две. Получается формат 8(999)123-45-67.
    } elseif (!preg_match('/^8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}$/D', $phone)) {
        $error = 'Телефон должен быть в формате 8(XXX)XXX-XX-XX.';
    // filter_var проверяет формат email; strlen ограничивает длину строки в байтах.
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 254) {
        $error = 'Введите правильный адрес электронной почты.';
    } else {
        // Все проверки прошли. Ищем совпадение логина ИЛИ электронной почты.
        // Значения для двух знаков ? передаются в том же порядке: логин, затем email.
        $query = $db->prepare('SELECT id FROM users WHERE login = ? OR email = ?');
        $query->execute([$login, $email]);
        // Если fetch вернул строку, такой пользователь уже есть.
        if ($query->fetch()) {
            $error = 'Этот логин или почта уже заняты.';
        } else {
            // INSERT INTO добавляет новую строку. Пять ? соответствуют пяти столбцам.
            $query = $db->prepare('INSERT INTO users (login, password, full_name, phone, email) VALUES (?, ?, ?, ?, ?)');
            // password_hash создаёт хеш пароля: в базу записывается он, а не сам пароль.
            // PASSWORD_DEFAULT выбирает стандартный алгоритм PHP.
            // На странице входа этот хеш проверяется функцией password_verify.
            $query->execute([$login, password_hash($password, PASSWORD_DEFAULT), $full_name, $phone, $email]);
            // После сохранения переходим ко входу. Параметр registered включает сообщение.
            // Переход также не даёт повторить INSERT простым обновлением страницы.
            header('Location: index.php?registered=1');
            exit;
        }
    }
}
// Шапка берёт заголовок и ошибку из переменных $title и $error.
$title = 'Регистрация';
// Общая шапка добавит класс страницы, который расположит форму по центру.
$auth_page = true;
require 'header.php';
?>
<!-- Форма отправляет POST на эту же страницу. name определяет ключ в $_POST.
     required, pattern и maxlength проверяют ввод в браузере; PHP проверяет его ещё раз.
     value с e($_POST[...]) возвращает введённый текст в поля после ошибки.
     Классы form-label, form-control, mb-3, btn задают оформление Bootstrap. -->
<form method="post">
    <p class="help-text">Все поля обязательны для заполнения.</p>
    <!-- Логин: шаблон разрешает латиницу и цифры, maxlength ограничивает длину.
         for="login" связывает подпись с id="login", name="login" отправляет значение. -->
    <label class="form-label" for="login">Логин (латиница и цифры, минимум 6 символов)</label>
    <input class="form-control mb-3" id="login" name="login" pattern="[A-Za-z0-9]{6,100}" maxlength="100" value="<?= e($_POST['login'] ?? '') ?>" required autocomplete="username">
    <!-- Пароль: ввод скрыт, minlength требует минимум 8 символов.
         autocomplete="new-password" сообщает браузеру, что создаётся новый пароль. -->
    <label class="form-label" for="password">Пароль (минимум 8 символов)</label>
    <input class="form-control mb-3" id="password" name="password" type="password" minlength="8" required autocomplete="new-password">
    <!-- ФИО: только русские буквы и пробелы, максимум 200 символов. -->
    <label class="form-label" for="full_name">ФИО (кириллица и пробелы)</label>
    <input class="form-control mb-3" id="full_name" name="full_name" pattern="[А-Яа-яЁё ]+" maxlength="200" value="<?= e($_POST['full_name'] ?? '') ?>" required>
    <!-- Телефон: inputmode="numeric" предлагает цифровую клавиатуру на телефоне.
         phone.js удаляет буквы и автоматически добавляет скобки и дефисы.
         maxlength ограничивает длину готового номера, pattern требует полный формат.
         placeholder показывает образец; PHP повторно проверяет номер перед сохранением. -->
    <label class="form-label" for="phone">Телефон: 8(XXX)XXX-XX-XX</label>
    <input class="form-control mb-3" id="phone" name="phone" type="tel" inputmode="numeric" autocomplete="tel-national" maxlength="15" placeholder="8(___)___-__-__" title="Введите полный номер: 8(999)123-45-67" pattern="8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}" value="<?= e($_POST['phone'] ?? '') ?>" required>
    <!-- type="email" включает проверку формата почты в браузере. -->
    <label class="form-label" for="email">Электронная почта</label>
    <input class="form-control mb-3" id="email" name="email" type="email" maxlength="254" value="<?= e($_POST['email'] ?? '') ?>" required>
    <!-- Отправка формы запускает PHP-блок POST в начале этого файла. -->
    <button class="btn btn-primary">Создать пользователя</button>
</form>
<!-- Ссылка для тех, у кого уже есть учётная запись. text-center выравнивает текст. -->
<p class="mt-3 text-center"><a href="index.php">Уже зарегистрированы? Авторизация</a></p>
<!-- Локальная маска телефона. defer запускает код после разбора HTML, без интернета. -->
<script src="phone.js" defer></script>
<!-- Закрываем общую разметку страницы. -->
<?php require 'footer.php'; ?>
