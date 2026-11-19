// МАСКА ТЕЛЕФОНА: пользователь вводит цифры, код добавляет 8, скобки и дефисы.
// Скрипт подключён только на странице регистрации после разбора HTML (defer).
const phone = document.getElementById('phone');

// Получаем до десяти цифр после начальной 8 и собираем номер по шаблону.
// Разделитель появляется, только когда за ним есть цифра: Backspace работает в конце.
function formatPhone(digits) {
    let result = '8(' + digits.slice(0, 3);
    if (digits.length > 3) result += ')' + digits.slice(3, 6);
    if (digits.length > 6) result += '-' + digits.slice(6, 8);
    if (digits.length > 8) result += '-' + digits.slice(8, 10);
    return result;
}

// input срабатывает при вводе, удалении и автозаполнении поля.
phone.addEventListener('input', function () {
    // Запоминаем, сколько цифр было слева от курсора, чтобы он не прыгал в конец.
    const cursor = phone.selectionStart;
    let beforeCursor = phone.value.slice(0, cursor).replace(/\D/g, '').length;
    // \D означает «не цифра», g — найти все такие символы. Буквы сразу удаляются.
    let digits = phone.value.replace(/\D/g, '');
    const hasDigits = digits.length > 0;

    // Начальная 8 — фиксированная часть номера, отдельно от десяти остальных цифр.
    if (digits.startsWith('8')) {
        digits = digits.slice(1);
        beforeCursor--;
    }
    // Лишние цифры отбрасываем. Полностью очищенное поле оставляем пустым.
    phone.value = hasDigits ? formatPhone(digits.slice(0, 10)) : '';

    // Восстанавливаем курсор после того же количества цифр, пропуская скобки и дефисы.
    let position = Math.min(2, phone.value.length);
    while (beforeCursor > 0 && position < phone.value.length) {
        if (/[0-9]/.test(phone.value[position])) beforeCursor--;
        position++;
    }
    phone.setSelectionRange(position, position);
});

// При вставке обрабатываем весь номер отдельно: перед ним уже может стоять «8(».
phone.addEventListener('paste', function (event) {
    event.preventDefault(); // Отменяем обычную вставку текста в позицию курсора.
    let digits = event.clipboardData.getData('text').replace(/\D/g, '');
    // Принимаем 11 цифр с начальной 8 или 10 цифр без неё.
    if (digits.length > 10 && digits.startsWith('8')) digits = digits.slice(1);
    phone.value = digits ? formatPhone(digits.slice(0, 10)) : '';
    // После вставки курсор находится в конце готового номера.
    phone.setSelectionRange(phone.value.length, phone.value.length);
});
