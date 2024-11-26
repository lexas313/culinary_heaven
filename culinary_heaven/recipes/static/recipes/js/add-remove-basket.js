document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-basket-action]') || event.target.parentNode.matches('[data-basket-action]')) {
            var basketButton = event.target.matches('[data-basket-action]') ? event.target : event.target.parentNode;
            var recipeId = basketButton.getAttribute('data-recipe-id');
            var action = basketButton.getAttribute('data-basket-action');

            // Проверяем, аутентифицирован ли пользователь
            if (!userIsAuthenticated) {
                // Получаем текущий URL, который будет использоваться для возврата
                var currentUrl = window.location.href;
                // Добавляем параметр 'next' с текущим URL в адрес страницы авторизации
                window.location.href = '/accounts/login/?next=' + encodeURIComponent(currentUrl);
                return; // Прекращаем выполнение функции
            }

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/recipes/add_basket/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

            xhr.onload = function() {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    var icon = basketButton.querySelector('i');
                    // Переключение действия и стилей кнопки и иконки
                    if(action === 'add') {
                        basketButton.className = 'remove-from-basket-button';
                        basketButton.setAttribute('data-basket-action', 'remove');
                        basketButton.setAttribute('title', 'Удалить из корзины');
                        icon.classList.add('ion-md-cart');
                        icon.style.color = '#1f8f0e';
                    } else {
                        basketButton.className = 'add-to-basket-button';
                        basketButton.setAttribute('data-basket-action', 'add');
                        basketButton.setAttribute('title', 'Добавить в корзину');
                        icon.classList.add('ion-md-cart');
                        icon.style.color = '#8f8f8f';
                    }
                } else {
                    alert('Произошла ошибка при обработке вашего запроса');
                }
            };

            xhr.send('recipe_id=' + recipeId);
        }
    });
});