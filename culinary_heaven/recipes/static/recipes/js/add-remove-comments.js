// JavaScript для добавления комментария
$(document).on('submit', '#comment-form', function(e) {
    e.preventDefault();
    var form = $(this);

    // Проверяем, аутентифицирован ли пользователь
    if (!userIsAuthenticated) {
        // Получаем текущий URL, который будет использоваться для возврата
        var currentUrl = window.location.href;
        // Добавляем параметр 'next' с текущим URL в адрес страницы авторизации
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(currentUrl);
        return; // Прекращаем выполнение функции
    }

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function(response) {
            // Добавьте новый комментарий и кнопку удаления в контейнер комментариев
            $('#comments').append(
                '<div id="comment-' + response.comment_id + '" class="comment">' +
                '<strong>' + response.author + '</strong>' +
                '<p>' + response.text + '</p>' +
                '<a href="#" class="delete-comment" data-comment-id="' + response.comment_id +
                '" data-url="/recipes/comment_remove/' + response.comment_id + '/' + '">Удалить комментарий</a>' +
                '</div>'
            );
            // Очистите форму после успешного добавления комментария
            form.trigger('reset');
        },
        error: function(xhr, errmsg, err) {
            console.log(xhr.status + ': ' + xhr.responseText);
        }
    });
});

// JavaScript для удаления комментария
$(document).on('click', '.delete-comment', function(e) {
    e.preventDefault();
    var commentId = $(this).data('comment-id');
    var deleteUrl = $(this).data('url'); // Получаем URL из data-url атрибута

    // Проверяем, аутентифицирован ли пользователь
    if (!userIsAuthenticated) {
        // Получаем текущий URL, который будет использоваться для возврата
        var currentUrl = window.location.href;
        // Добавляем параметр 'next' с текущим URL в адрес страницы авторизации
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(currentUrl);
        return; // Прекращаем выполнение функции
    }

    $.ajax({
        type: 'POST',
        url: deleteUrl,
        data: {
            'id': commentId, // Убедитесь, что 'id' соответствует ключу, который вы используете в Django view
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            $('#comment-' + commentId).remove();
        },
        error: function(xhr, errmsg, err) {
            console.log(xhr.status + ': ' + xhr.responseText);
        }
    });
});