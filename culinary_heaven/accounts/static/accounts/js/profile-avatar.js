document.addEventListener('DOMContentLoaded', function() {
    var formGroup = document.querySelector('.profile-avatar');
    var uploadedFile = formGroup.querySelector('.uploaded-file');
    var clearButton = formGroup.querySelector('.btn-clear');
    var fileInput = formGroup.querySelector('.custom-file-input');
    var label = formGroup.querySelector('.custom-file-label');
    var previewImage = formGroup.querySelector('#profile-avatar');
    var deleteInput = formGroup.querySelector("input[name='image_profile-clear']"); // Скрытое поле DELETE

    if (uploadedFile && uploadedFile.querySelector('img').src !== '') {
        clearButton.style.display = 'block'; // Показываем кнопку очистки, если загружен файл
    }

    formGroup.addEventListener('change', function(event) {
        if (event.target === fileInput) {
            var fileName = fileInput.files[0] ? fileInput.files[0].name : '';
            label.textContent = fileName || 'Выберите файл'; // Обновляем текст label

            if (uploadedFile) {
                uploadedFile.style.display = 'none'; // Скрываем старое загруженное изображение
            }

            // Если файл выбран, показать изображение
            if (fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result; // загружаем изображение в preview
                    previewImage.style.display = 'block'; // Показываем изображение
                    clearButton.style.display = 'block'; // Показываем кнопку очистки
                };
                reader.readAsDataURL(fileInput.files[0]);
            } else {
                previewImage.src = ''; // Очищаем путь к превью изображения
                previewImage.style.display = 'none'; // Скрываем изображение
                clearButton.style.display = 'none'; // Скрываем кнопку очистки
            }

            // Отключаем флаг удаления при выборе нового файла
            if (deleteInput) {
                deleteInput.checked = false;
            }
        }
    });

    formGroup.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-clear')) {
            // Очищаем поле ввода файла
            fileInput.value = ''; // Очищаем значение input
            label.textContent = 'Выберите файл'; // Сбрасываем текст label
            previewImage.src = ''; // Очищаем путь к превью изображения
            previewImage.style.display = 'none'; // Скрываем изображение
            clearButton.style.display = 'none'; // Скрываем кнопку очистки

            // Скрываем контейнер с загруженным файлом
            if (uploadedFile) {
                uploadedFile.style.display = 'none'; // Скрываем загруженное изображение при очистке
            }

            // Устанавливаем флаг DELETE в true
            if (deleteInput) {
                deleteInput.checked = true;
            }
        }
    });
});