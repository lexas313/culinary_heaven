// Функция для увеличение и уменьшение количества
function updateQuantity(basketId, url) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/recipes/' + url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.status === 'deleted') {
                // Удаление всего блока корзины, если товар удален
                // document.getElementById('basket-' + basketId).remove();
                // Перезагрузка страницы
                location.reload();
                // alert('Элемент удален из корзины');
            } else {
                // Обновление количества на странице без перезагрузки
                // document.getElementById('quantity-' + basketId).textContent = response.quantity;
                location.reload();
                // alert('Количество обновлено: ' + response.quantity);
            }
        } else {
            alert('Ошибка при обновлении количества');
        }
    };

    xhr.send('basket_id=' + basketId);
}



// Удаление из корзины
function deleteBasketItem(basketId) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/recipes/delete_basket_item/', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    xhr.onload = function() {
        if (xhr.status === 200) {
            // Удаление всего блока корзины, если сервер подтвердил удаление
            // document.getElementById('basket-' + basketId).remove();
            // alert('Рецепт удален из корзины');
            location.reload();
        } else {
            alert('Ошибка при удалении рецепта из корзины');
        }
    };

    xhr.send('basket_id=' + basketId);
}

// Удаление из корзины всех рецептов
function deleteBasket() {
    // Отправляем запрос на серверный маршрут 'delete_basket/'
    fetch('/recipes/delete_basket/', {
        method: 'POST',
        headers: {
            // Необходимо добавить CSRF токен для защиты от CSRF атак
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'delete': 'all' }) // Отправляем данные, если нужно
    })
    .then(response => response.json())
    .then(data => {
        console.log(data); // Обработка данных, полученных от сервера
        if(data.success) {
            // Если сервер вернул успех, очищаем корзину на клиенте
            // document.getElementById('basket-container').innerHTML = '';
            location.reload();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Удаление ингредиентов из корзины
function deleteBasketIngredient(ingredientId, basketId) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/recipes/delete_ingredient/', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.success) {
                // Удаление элемента ингредиента
                var ingredientElement = document.getElementById('ingredient-' + ingredientId);
                ingredientElement.remove();

                // Проверяем, остались ли ингредиенты
                if (!response.ingredients_left) {
                    // Если ингредиентов не осталось, удаляем блок ингредиентов для конкретной корзины
                    var basketIngredientsElement = document.getElementById('basket-' + basketId + '-ingredients');
                    basketIngredientsElement.remove();
                }
            } else {
                alert('Ошибка при удалении ингредиента из корзины');
            }
        }
    };

    xhr.send('basket_ingredient_id=' + ingredientId);
}

// Обновить ингредиенты в корзине
function updateBasket() {
    fetch('/recipes/update_basket_ingredient/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // Получение CSRF токена
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}) // Отправка пустого тела запроса
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            location.reload();
        } else {
            console.error('Ошибка при обновлении корзины:', data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}