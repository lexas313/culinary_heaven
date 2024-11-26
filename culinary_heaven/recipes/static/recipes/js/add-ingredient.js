const addMoreBtn = document.getElementById('add-ingredient')
const totalNewForms = document.getElementById('id_recipe_ingredient-TOTAL_FORMS')

let currentFormCount = 0;

addMoreBtn.addEventListener('click', add_new_form)
function add_new_form(event) {
    if (event) {
        event.preventDefault()
    }
    if (currentFormCount >= 19) {
        alert("Вы можете добавить максимум 20 ингредиентов");
        return;
    }
    const currentIngredientForms = document.querySelectorAll('.ingredient-form')
    currentFormCount = currentIngredientForms.length
    const formCopyTarget = document.getElementById('ingredients')
    const copyEmptyFormEl = document.getElementById('empty-form').cloneNode(true)
    copyEmptyFormEl.setAttribute('class', 'ingredient-form')
    copyEmptyFormEl.setAttribute('id', `recipe_ingredient-${currentFormCount}`)
    const regex = new RegExp('__prefix__', 'g')
    copyEmptyFormEl.innerHTML = copyEmptyFormEl.innerHTML.replace(regex, currentFormCount)
    totalNewForms.setAttribute('value', currentFormCount + 1)
    // now add new empty form element to our html form
    formCopyTarget.append(copyEmptyFormEl)
    // Обновление номеров ингредиентов после добавления новой формы
    updateIngredientNumbers();
}

// Функция для обновления всех номеров ингредиентов
function updateIngredientNumbers() {
    const cookingStepForms = document.querySelectorAll('.ingredient-form');
    cookingStepForms.forEach((form, index) => {
        const stepNumberSpan = form.querySelector('.ingredient-number');
        if (stepNumberSpan) {
            stepNumberSpan.textContent = `${index + 1}. `; // Обновляем номер ингредиента
        }
    });
}

// add delete buttons to each ingredient form
const ingredientForms = document.querySelectorAll('.ingredient-form')
ingredientForms.forEach(form => {
    const deleteBtn = form.querySelector('.remove-ingredient')
    deleteBtn.addEventListener('click', delete_ingredient_form)
})

function delete_ingredient_form(event) {
  if (event) { event.preventDefault() }
  const ingredientForm = event.target.closest('.ingredient-form')
  if (!ingredientForm) { return } // Проверка на существование формы
  ingredientForm.remove()
  // Обновить идентификаторы оставшихся форм
  const remainingForms = document.querySelectorAll('.ingredient-form')
  remainingForms.forEach((form, index) => {
    const formId = form.getAttribute('id')
    if (!formId) { return } // Проверка на существование идентификатора формы
    const newFormId = formId.replace(/\d+/, index)
    form.setAttribute('id', newFormId)
    const inputs = form.querySelectorAll('input, select')
    inputs.forEach(input => {
      const inputId = input.getAttribute('id')
      if (!inputId) { return } // Проверка на существование идентификатора поля ввода
      const newInputId = inputId.replace(/\d+/, index)
      input.setAttribute('id', newInputId)
      input.setAttribute('name', input.getAttribute('name').replace(/\d+/, index))
    })
  })
  currentFormCount -= 1; // Отнимаем 1 от currentFormCount
  updateIngredientNumbers() // Обновляем номера ингредиентов при удалении формы
}

const ingredientsContainer = document.getElementById('ingredients')

ingredientsContainer.addEventListener('click', function(event) {
  if (event.target.classList.contains('remove-ingredient')) {
    delete_ingredient_form(event)
  }
})