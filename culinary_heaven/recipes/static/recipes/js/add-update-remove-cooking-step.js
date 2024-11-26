document.addEventListener('DOMContentLoaded', function() {
  const addMoreBtnCookingStep = document.getElementById('add-cooking-step');
  const totalNewFormsCookingStep = document.getElementById('id_recipe_cooking_step-TOTAL_FORMS');

  let currentFormCountCookingStep = document.querySelectorAll('.cooking-step-form').length;

  addMoreBtnCookingStep.addEventListener('click', add_new_form_cooking_step);

  function add_new_form_cooking_step(event) {
    if (event) {
      event.preventDefault();
    }
    let hiddenFormCountCookingStep = document.querySelectorAll('.cooking-step-form[hidden]').length;
    currentFormCountCookingStep = document.querySelectorAll('.cooking-step-form').length;
    if (currentFormCountCookingStep - hiddenFormCountCookingStep >= 5) {
      alert("Вы можете добавить максимум 5 шагов");
      return;
    }
    const formCopyTargetCookingStep = document.getElementById('cooking-step');
    const copyEmptyFormElCookingStep = document.getElementById('empty-form-cooking-step').cloneNode(true);
    copyEmptyFormElCookingStep.setAttribute('class', 'cooking-step-form');
    copyEmptyFormElCookingStep.setAttribute('id', 'recipe_cooking_step-' + currentFormCountCookingStep);
    const regex = new RegExp('__prefix__', 'g');
    copyEmptyFormElCookingStep.innerHTML = copyEmptyFormElCookingStep.innerHTML.replace(regex, currentFormCountCookingStep);
    totalNewFormsCookingStep.setAttribute('value', currentFormCountCookingStep + 1);
    formCopyTargetCookingStep.append(copyEmptyFormElCookingStep);
    currentFormCountCookingStep += 1;
  }

  // Добавляем обработчик событий для удаления форм
  const cookingStepContainer = document.getElementById('cooking-step');
  cookingStepContainer.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-cooking-step')) {
      delete_cooking_step_form(event);
    }
  });

  function delete_cooking_step_form(event) {
    if (event) { event.preventDefault(); }
    const cookingStepForm = event.target.closest('.cooking-step-form');
    if (!cookingStepForm) { return; }
    cookingStepForm.querySelector("input[name$='-DELETE']").checked = true;
    cookingStepForm.setAttribute('hidden', true);
  }

  // Скрыть чекбоксы удаления и их метки
  const deleteCheckboxes = document.querySelectorAll('input[name$="-DELETE"]');
  deleteCheckboxes.forEach(checkbox => {
    checkbox.style.display = 'none';
    checkbox.parentElement.style.display = 'none';
  });
});