document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-like-action]') || event.target.parentNode.matches('[data-like-action]')) {
            var likeButton = event.target.matches('[data-like-action]') ? event.target : event.target.parentNode;
            var recipeId = likeButton.getAttribute('data-recipe-id');
            var action = likeButton.getAttribute('data-like-action');
            var likeCountSpan = likeButton.parentNode.querySelector('.like-count');

            // Проверяем, аутентифицирован ли пользователь
            if (!userIsAuthenticated) {
                // Получаем текущий URL, который будет использоваться для возврата
                var currentUrl = window.location.href;
                // Добавляем параметр 'next' с текущим URL в адрес страницы авторизации
                window.location.href = '/accounts/login/?next=' + encodeURIComponent(currentUrl);
                return; // Прекращаем выполнение функции
            }

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/recipes/like_recipe/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

            xhr.onload = function() {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    var icon = likeButton.querySelector('i');
                    // Переключение действия и стилей кнопки и иконки
                    if(action === 'add') {
                        likeButton.className = 'remove-like-button';
                        likeButton.setAttribute('data-like-action', 'remove');
                        likeButton.setAttribute('title', 'Убрать лайк');
                        icon.classList.add('ion-md-thumbs-up');
                        icon.style.color = '#263ded';
                    } else {
                        likeButton.className = 'add-like-button';
                        likeButton.setAttribute('data-like-action', 'add');
                        likeButton.setAttribute('title', 'Поставить лайк');
                        icon.classList.add('ion-md-thumbs-up');
                        icon.style.color = '#8f8f8f';
                    }
                    likeCountSpan.textContent = response.like_count;
                } else {
                    alert('Произошла ошибка при обработке вашего запроса');
                }
            };

            xhr.send('recipe_id=' + recipeId);
        }
    });
});