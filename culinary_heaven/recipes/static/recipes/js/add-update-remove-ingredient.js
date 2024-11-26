document.addEventListener('DOMContentLoaded', function() {
  const addMoreBtn = document.getElementById('add-ingredient');
  const totalNewForms = document.getElementById('id_recipe_ingredient-TOTAL_FORMS');

  let currentFormCount = document.querySelectorAll('.ingredient-form').length;

  addMoreBtn.addEventListener('click', add_new_form);

  function add_new_form(event) {
    if (event) {
      event.preventDefault();
    }
    let hiddenFormCount = document.querySelectorAll('.ingredient-form[hidden]').length;
    currentFormCount = document.querySelectorAll('.ingredient-form').length;
    if (currentFormCount - hiddenFormCount >= 5) {
      alert("Вы можете добавить максимум 5 ингредиентов");
      return;
    }
    const formCopyTarget = document.getElementById('ingredients');
    const copyEmptyFormEl = document.getElementById('empty-form').cloneNode(true);
    copyEmptyFormEl.setAttribute('class', 'ingredient-form');
    copyEmptyFormEl.setAttribute('id', 'recipe_ingredient-' + currentFormCount);
    const regex = new RegExp('__prefix__', 'g');
    copyEmptyFormEl.innerHTML = copyEmptyFormEl.innerHTML.replace(regex, currentFormCount);
    totalNewForms.setAttribute('value', currentFormCount + 1);
    formCopyTarget.append(copyEmptyFormEl);
    currentFormCount += 1;
  }

  // Добавляем обработчик событий для удаления форм
  const ingredientsContainer = document.getElementById('ingredients');
  ingredientsContainer.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-ingredient')) {
      delete_form(event);
    }
  });

  function delete_form(event) {
    if (event) { event.preventDefault(); }
    const form = event.target.closest('.ingredient-form');
    if (!form) { return; }
    form.querySelector("input[name$='-DELETE']").checked = true;
    form.setAttribute('hidden', true);
  }

  // Скрыть чекбоксы удаления и их метки
  const deleteCheckboxes = document.querySelectorAll('input[name$="-DELETE"]');
  deleteCheckboxes.forEach(checkbox => {
    checkbox.style.display = 'none';
    checkbox.parentElement.style.display = 'none';
  });
});