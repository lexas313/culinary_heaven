document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-favorite-action]') || event.target.parentNode.matches('[data-favorite-action]')) {
            var favoriteButton = event.target.matches('[data-favorite-action]') ? event.target : event.target.parentNode;
            var recipeId = favoriteButton.getAttribute('data-recipe-id');
            var action = favoriteButton.getAttribute('data-favorite-action');
            var favoriteCountSpan = favoriteButton.parentNode.querySelector('.favorite_count');

            // Проверяем, аутентифицирован ли пользователь
            if (!userIsAuthenticated) {
                // Получаем текущий URL, который будет использоваться для возврата
                var currentUrl = window.location.href;
                // Добавляем параметр 'next' с текущим URL в адрес страницы авторизации
                window.location.href = '/accounts/login/?next=' + encodeURIComponent(currentUrl);
                return; // Прекращаем выполнение функции
            }

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/recipes/add_to_favorites/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

            xhr.onload = function() {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    var icon = favoriteButton.querySelector('i');
                    // Переключение действия и стилей кнопки и иконки
                    if(action === 'add') {
                        favoriteButton.className = 'remove-from-favorites-button';
                        favoriteButton.setAttribute('data-favorite-action', 'remove');
                        favoriteButton.setAttribute('title', 'Удалить из избранного');
                        icon.classList.add('ion-md-heart');
                        icon.style.color = '#ea1a1a';
                    } else {
                        favoriteButton.className = 'add-to-favorites-button';
                        favoriteButton.setAttribute('data-favorite-action', 'add');
                        favoriteButton.setAttribute('title', 'Добавить в избранное');
                        icon.classList.add('ion-md-heart');
                        icon.style.color = '#8f8f8f';
                    }
                    favoriteCountSpan.textContent = response.favorite_count;
                } else {
                    alert('Произошла ошибка при обработке вашего запроса');
                }
            };

            xhr.send('recipe_id=' + recipeId);
        }
    });
});