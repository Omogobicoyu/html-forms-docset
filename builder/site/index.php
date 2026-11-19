<?php
// АВТОРИЗАЦИЯ: проверяем логин и пароль, затем запоминаем пользователя в сессии.
// require выполняет db.php: получаем $db, сессию и функции e(), require_login().
require 'db.php';
// Уже вошедшего пользователя сразу отправляем в его раздел.
if (isset($_SESSION['user_id'])) {
    // Условие ? значение_если_да : значение_если_нет — короткая запись выбора.
    // === сравнивает и значение, и тип; точка соединяет строки.
    header('Location: ' . ($_SESSION['role'] === 'admin' ? 'admin.php' : 'requests.php'));
    exit;
}
// Пока ошибки нет — пустая строка. Позже header.php выведет непустую ошибку.
$error = '';
// При обычном открытии страницы запрос GET: только показываем форму.
// После отправки формы запрос POST: выполняем следующий блок проверки.
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // $_POST содержит значения полей с соответствующим атрибутом name.
    // ?? '' подставляет пустую строку, если поле не передано.
    // trim убирает пробелы по краям логина. Пароль читаем без trim.
    $login = trim($_POST['login'] ?? '');
    $password = $_POST['password'] ?? '';
    // SELECT * выбирает все столбцы пользователя с таким логином.
    // prepare готовит запрос; ? — место для значения, переданного через execute.
    $query = $db->prepare('SELECT * FROM users WHERE login = ?');
    // Значение логина передаётся отдельно от SQL и не становится SQL-командой.
    $query->execute([$login]);
    // fetch возвращает одну строку-массив или false, если пользователь не найден.
    $user = $query->fetch();
    // && означает «и»: нужны и найденный пользователь, и правильный пароль.
    // password_verify сравнивает введённый пароль с хешем из базы.
    if ($user && password_verify($password, $user['password'])) {
        // После входа меняем идентификатор сессии; true удаляет старую сессию.
        session_regenerate_id(true);
        // Сохраняем ID и роль для последующих страниц; пароль в сессию не пишем.
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['role'] = $user['role'];
        // Администратору открываем панель, обычному пользователю — его заявки.
        header('Location: ' . ($user['role'] === 'admin' ? 'admin.php' : 'requests.php'));
        exit;
    }
    // Сюда попадаем, если пользователь не найден или пароль не подошёл.
    $error = 'Неверный логин или пароль.';
}
// Название страницы используется в общей шапке: во вкладке браузера и в h2.
$title = 'Авторизация';
// Включаем расположение по центру только для страниц входа и регистрации.
$auth_page = true;
require 'header.php';
?>
<!-- После регистрации адрес содержит ?registered=1. $_GET читает этот параметр.
     if (...): и endif; — запись условия, удобная для HTML внутри PHP. -->
<?php if (isset($_GET['registered'])): ?><p class="alert alert-success">Пользователь создан. Войдите в систему.</p><?php endif; ?>
<!-- method="post" отправляет поля в $_POST этой же страницы: action не указан.
     Ширину и расположение по центру задают стили .auth-page в style.css. -->
<form method="post">
    <!-- for у label совпадает с id поля: щелчок по подписи переводит фокус в поле.
         name="login" задаёт ключ $_POST['login']; required требует заполнения.
         value сохраняет введённый логин после ошибки; e() обрабатывает его для HTML.
         Вставка PHP со знаком = после открывающего тега выводит значение (как echo).
         form-control оформляет поле, mb-3 добавляет отступ снизу. -->
    <label class="form-label" for="login">Логин</label>
    <input class="form-control mb-3" id="login" name="login" value="<?= e($_POST['login'] ?? '') ?>" required autocomplete="username">
    <!-- type="password" скрывает ввод символами; autocomplete подсказывает браузеру
         назначение поля. Пароль после ошибки заново в value не подставляется. -->
    <label class="form-label" for="password">Пароль</label>
    <input class="form-control mb-3" id="password" name="password" type="password" required autocomplete="current-password">
    <!-- Кнопка внутри формы без type по умолчанию отправляет её. btn — оформление. -->
    <button class="btn btn-primary">Войти</button>
</form>
<!-- Ссылка открывает регистрацию; mt-3 — отступ сверху, text-center — текст по центру. -->
<p class="mt-3 text-center"><a href="register.php">Еще не зарегистрированы? Регистрация</a></p>
<!-- Общий файл завершает HTML-документ, начатый в header.php. -->
<?php require 'footer.php'; ?>
