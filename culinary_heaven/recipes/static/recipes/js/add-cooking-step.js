const addMoreBtnCookingStep = document.getElementById('add-cooking-step')
const totalNewFormsCookingStep = document.getElementById('id_recipe_cooking_step-TOTAL_FORMS')

let currentFormCountCookingStep = 0;

addMoreBtnCookingStep.addEventListener('click', add_new_form_cooking_step)
function add_new_form_cooking_step(event) {
    if (event) {
        event.preventDefault()
    }
    if (currentFormCountCookingStep >= 19) {
        alert("Вы можете добавить максимум 20 шагов");
        return;
    }
    const currentIngredientFormsCookingStep = document.querySelectorAll('.cooking-step-form')
    currentFormCountCookingStep = currentIngredientFormsCookingStep.length
    const formCopyTargetCookingStep = document.getElementById('cooking-step')
    const copyEmptyFormElCookingStep = document.getElementById('empty-form-cooking-step').cloneNode(true)
    copyEmptyFormElCookingStep.setAttribute('class', 'cooking-step-form')
    copyEmptyFormElCookingStep.setAttribute('id', `recipe_cooking_step-${currentFormCountCookingStep}`)
    const regex = new RegExp('__prefix__', 'g')
    copyEmptyFormElCookingStep.innerHTML = copyEmptyFormElCookingStep.innerHTML.replace(regex, currentFormCountCookingStep)
    totalNewFormsCookingStep.setAttribute('value', currentFormCountCookingStep + 1)
    // now add new empty form element to our html form
    formCopyTargetCookingStep.append(copyEmptyFormElCookingStep)
    // Обновление номеров шагов после добавления новой формы
    updateStepNumbers();
}

// Функция для обновления всех номеров шагов
function updateStepNumbers() {
    const cookingStepForms = document.querySelectorAll('.cooking-step-form');
    cookingStepForms.forEach((form, index) => {
        const stepNumberSpan = form.querySelector('.step-number');
        if (stepNumberSpan) {
            stepNumberSpan.textContent = `${index + 1}. `; // Обновляем номер шага
        }
    });
}

// add delete buttons to each ingredient form
const CookingStepForms = document.querySelectorAll('.cooking-step-form')
CookingStepForms.forEach(form => {
    const deleteBtnCookingStep = form.querySelector('.remove-cooking-step')
    deleteBtnCookingStep.addEventListener('click', delete_cooking_step_form)
})

function delete_cooking_step_form(event) {
    if (event) { event.preventDefault(); }
    const CookingStepForm = event.target.closest('.cooking-step-form');
    if (!CookingStepForm) { return; } // Проверка на существование формы
    CookingStepForm.remove();

    // Обновить идентификаторы оставшихся форм
    const remainingForms = document.querySelectorAll('.cooking-step-form');
    remainingForms.forEach((form, index) => {
        const formId = form.getAttribute('id');
        if (!formId) { return; } // Проверка на существование идентификатора формы

        // Устанавливаем новый идентификатор для формы
        const newFormId = formId.replace(/\d+/, index);
        form.setAttribute('id', newFormId);

        // Обновляем все инпуты, текстовые области, выборы и лэйблы внутри формы
        const inputs = form.querySelectorAll('textarea, select, input');
        inputs.forEach(input => {
            const inputId = input.getAttribute('id');
            if (!inputId) { return; } // Проверка на существование идентификатора поля ввода

            // Обновляем ID и имя инпута
            const newInputId = inputId.replace(/\d+/, index);
            input.setAttribute('id', newInputId);
            input.setAttribute('name', input.getAttribute('name').replace(/\d+/, index));

            // Обновляем связанные лэйблы
            const label = form.querySelector(`label[for="${inputId}"]`);
            if (label) {
                label.setAttribute('for', newInputId);
            }
        });

        // Обновляем все label в текущей форме, если они ссылаются на другие элементы
        const labels = form.querySelectorAll('label');
        labels.forEach(label => {
            const labelFor = label.getAttribute('for');
            if (labelFor) {
                const newLabelFor = labelFor.replace(/\d+/, index);
                label.setAttribute('for', newLabelFor);
            }
        });
    });

    currentFormCountCookingStep -= 1; // Уменьшаем количество форм
    updateStepNumbers(); // Обновляем номера шагов при удалении формы
}

const CookingStepContainer = document.getElementById('cooking-step')

CookingStepContainer.addEventListener('click', function(event) {
  if (event.target.classList.contains('remove-cooking-step')) {
    delete_cooking_step_form(event)
  }
})