$(document).ready(function() {
  $('.favorite-toggle').click(function(e) {
    e.preventDefault();
    var btn = $(this);
    var recipeId = btn.data('recipe-id');
    var addToFavoritesUrl = btn.data('url');
    var recipeElement = btn.closest('.recipes');
    var noFavoritesText = 'Нет избранных рецептов'; // Текст сообщения

    $.ajax({
      url: addToFavoritesUrl,
      type: 'POST',
      data: {
        'recipe_id': recipeId,
        'csrfmiddlewaretoken': getCookie('csrftoken')
      },
      success: function(response) {
        if (!response.is_favorite) {
          recipeElement.remove(); // Удаляем элемент рецепта из DOM

          // Проверяем, остались ли ещё элементы рецептов
          if ($('.recipes').length === 0) {
            // Если рецептов больше нет, показываем сообщение "Нет избранных рецептов"
            $('#no-favorites-message').html('<h1 class="h1">' + noFavoritesText + '</h1>').show();
          }
        } else {
          alert('Произошла ошибка');
        }
      }
    });
  });
});
