document.addEventListener('DOMContentLoaded', function() {
    // Найти все элементы ингредиентов
    var ingredientElements = document.querySelectorAll('.recipe-detail-ingredients li[data-ingredient-id]');

    ingredientElements.forEach(function(element) {
        var ingredientId = element.getAttribute('data-ingredient-id');
        var unitElement = element.querySelector('select[name="unit-selector"]');
        var currentUnit = unitElement.value;

        // Отправка AJAX запроса для получения возможных единиц измерения
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/recipes/convert_unit/', true);
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                if (data.status === 'success') {
                    unitElement.innerHTML = ''; // Очистить предыдущие опции
                    var option = document.createElement('option');
                    option.value = currentUnit;
                    option.textContent = currentUnit;
                    unitElement.appendChild(option);
                    data.possible_units.forEach(function(unit) {
                        var option = document.createElement('option');
                        option.value = unit;
                        option.textContent = unit;
                        unitElement.appendChild(option);
                    });
                }
            }
        };

        var data = new FormData();
        data.append('old_unit', currentUnit);
        data.append('amount', 1); // Пример: заменить на фактическое количество, если необходимо
        data.append('possible_units', true); // Указать, что запрашиваются возможные единицы

        xhr.send(data);
    });

    // Добавление обработчиков событий изменения единицы измерения
    var unitSelectors = document.querySelectorAll('select[name="unit-selector"]');

    unitSelectors.forEach(function(selectElement) {
      var originalUnit = selectElement.getAttribute('data-old-unit');
      var originalAmount = document.getElementById('amount-' + selectElement.getAttribute('data-ingredient-id')).textContent.trim();

      selectElement.addEventListener('change', function() {
        var ingredientId = this.getAttribute('data-ingredient-id');
        var oldUnit = this.getAttribute('data-old-unit');
        var newUnit = this.value;

        // Получение актуального значения количества из элемента <span>
        var amount = document.getElementById('amount-' + ingredientId).textContent.trim();

        function sendConversionRequest(oldUnit, amount, newUnit) {
          var xhr = new XMLHttpRequest();
          xhr.open('POST', '/recipes/convert_unit/', true);
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
          xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

          xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
              if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.status === 'success') {
                  document.getElementById('amount-' + ingredientId).textContent = response.result;
                  selectElement.setAttribute('data-old-unit', newUnit);
                } else {
                  // Повторная отправка только при конкретной ошибке конвертации
                  if (response.message === 'Недоступная конвертация') {
                    sendConversionRequest(originalUnit, originalAmount, newUnit);
                  }
                }
              } else {
                // Обработка других ошибок
                console.error('Error:', xhr.status, xhr.statusText);
              }
            }
          };

          var data = 'old_unit=' + encodeURIComponent(oldUnit) +
                     '&new_unit=' + encodeURIComponent(newUnit) +
                     '&amount=' + encodeURIComponent(amount);

          xhr.send(data);
        }

        sendConversionRequest(oldUnit, amount, newUnit);
      });
    });
});