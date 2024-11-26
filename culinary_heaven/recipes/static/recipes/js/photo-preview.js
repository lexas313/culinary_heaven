// Обработчик предварительного просмотра изображений для cooking-step-photo-formset
$('#cooking-step').on('change', 'input[type="file"]', function (event) {
    var input = event.currentTarget;
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $(input).closest('.cooking-step-form').find('.image-preview img').attr('src', e.target.result).show();
            $(input).closest('.cooking-step-form').find('a').hide();
        };
        reader.readAsDataURL(input.files[0]);
    }
});

// Обработчик предварительного просмотра изображений для image-ready-dish
$('#form-container').on('change', '#id_image_ready_dish', function(event) {
    var input = event.currentTarget;
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#image-preview-dish').attr('src', e.target.result).show();

        };
        reader.readAsDataURL(input.files[0]);
    }
});


// Кнопка загрузки файла для "Шагов приготовления"
// Добавляем название файла в кнопку
document.addEventListener('DOMContentLoaded', function() {
    // Находим все формы в формсете
    var forms = document.querySelectorAll('.cooking-step-form');

    forms.forEach(function(formGroup, index) {
        var fileInput = formGroup.querySelector('.custom-file-input');
        var label = formGroup.querySelector('.custom-file-label');
        var previewImage = formGroup.querySelector('.image-preview img');
        var clearButton = formGroup.querySelector('.btn-clear');
        var deleteInput = formGroup.querySelector("input[name='recipe_cooking_step-" + index + "-image_step-clear']");
        var uploadedFile = formGroup.querySelector('.uploaded-file');

        if (uploadedFile && uploadedFile.querySelector('a') && uploadedFile.querySelector('a').href !== '') {
            clearButton.style.display = 'block'; // Показываем кнопку очистки, если загружен файл
        }

        formGroup.addEventListener('change', function(event) {
            if (event.target === fileInput) {
                var fileName = fileInput.files[0] ? fileInput.files[0].name : '';
                label.textContent = fileName || 'Выберите фото'; // Обновляем текст label

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
                label.textContent = 'Выберите фото'; // Сбрасываем текст label
                previewImage.src = ''; // Очищаем путь к превью изображения
                previewImage.style.display = 'none'; // Скрываем изображение
                clearButton.style.display = 'none'; // Скрываем кнопку очистки

                // Скрываем ссылку на загруженный файл
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
});






// Кнопка загрузки файла для "Готового блюда"
// Добавляем название файла в кнопку
document.addEventListener('DOMContentLoaded', function() {
    var formGroup = document.querySelector('.load-file-ready-dish');
    var uploadedFile = formGroup.querySelector('.uploaded-file');
    var clearButton = formGroup.querySelector('.btn-clear');
    var fileInput = formGroup.querySelector('.custom-file-input');
    var label = formGroup.querySelector('.custom-file-label');
    var previewImage = formGroup.querySelector('#image-preview-dish');
    var deleteInput = formGroup.querySelector("input[name='image_ready_dish-clear']"); // Скрытое поле DELETE

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