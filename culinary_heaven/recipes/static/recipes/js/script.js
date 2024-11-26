// Получение доступа к основным элементам меню
const menu = document.querySelector('.menu');
const menuSection = menu.querySelector('.menu-section');
const menuArrow = menu.querySelector('.menu-mobile-arrow');
const menuClosed = menu.querySelector('.menu-mobile-close');
const menuTrigger = document.querySelector('.menu-mobile-trigger');
const menuOverlay = document.querySelector('.overlay');
let subMenu; // Переменная для подменю

// Обработчик клика по секции меню
menuSection.addEventListener('click', (e) => {
   // Если меню не активно, выходим из функции
   if (!menu.classList.contains('active')) {
      return;
   }

   // Если кликнули по элементу с дочерними пунктами меню
   if (e.target.closest('.menu-item-has-children')) {
      const hasChildren = e.target.closest('.menu-item-has-children');
      showSubMenu(hasChildren); // Показываем подменю
   }
});

// Обработчик клика по стрелке в мобильной версии меню
menuArrow.addEventListener('click', () => {
   hideSubMenu(); // Скрываем подменю
});

// Обработчики клика по триггерам меню и оверлею
menuTrigger.addEventListener('click', () => {
   toggleMenu(); // Переключаем видимость меню
});
menuClosed.addEventListener('click', () => {
   toggleMenu(); // Переключаем видимость меню
});
menuOverlay.addEventListener('click', () => {
   toggleMenu(); // Переключаем видимость меню
});

// Функция переключения меню
function toggleMenu() {
   menu.classList.toggle('active'); // Переключаем класс 'active'
   menuOverlay.classList.toggle('active'); // Переключаем класс 'active' для оверлея
}

// Функция показа подменю
function showSubMenu(hasChildren) {
   subMenu = hasChildren.querySelector('.menu-subs'); // Находим подменю
   subMenu.classList.add('active'); // Добавляем класс 'active'
   subMenu.style.animation = 'slideLeft 0.5s ease forwards'; // Анимация появления слева
   const menuTitle = hasChildren.querySelector('i').parentNode.childNodes[0].textContent;
   menu.querySelector('.menu-mobile-title').innerHTML = menuTitle; // Устанавливаем заголовок меню
   menu.querySelector('.menu-mobile-header').classList.add('active'); // Активируем заголовок меню
}

// Функция скрытия подменю
function hideSubMenu() {
   subMenu.style.animation = 'slideRight 0.5s ease forwards'; // Анимация исчезновения вправо
   setTimeout(() => {
      subMenu.classList.remove('active'); // Удаляем класс 'active' после анимации
   }, 300);

   menu.querySelector('.menu-mobile-title').innerHTML = ''; // Очищаем заголовок меню
   menu.querySelector('.menu-mobile-header').classList.remove('active'); // Деактивируем заголовок меню
}

// Обработчик изменения размера окна
window.onresize = function () {
   // Если ширина окна больше 991px и меню активно
   if (this.innerWidth > 991) {
      if (menu.classList.contains('active')) {
         toggleMenu(); // Переключаем меню
      }
   }
};



document.addEventListener('DOMContentLoaded', function () {
    var popup = document.getElementById("searchPopup");
    var overlay = document.getElementById("overlay");
    var btn = document.getElementById("searchButton");

    // Проверяем наличие кнопки для открытия попапа
    if (btn) {
        btn.onclick = function () {
            if (popup && overlay) { // Также проверяем наличие popup и overlay
                popup.classList.toggle('active');
                overlay.classList.toggle('active');
            }
        }
    }

    var closeBtn = document.querySelector('.popup .close');
    // Проверяем наличие закрывающей кнопки
    if (closeBtn) {
        closeBtn.onclick = function () {
            if (popup && overlay) { // Проверяем наличие перед удалением классов
                popup.classList.remove('active');
                overlay.classList.remove('active');
            }
        }
    }

    // Проверяем наличие overlay для обработки кликов
    if (overlay) {
        overlay.onclick = function () {
            if (popup) { // Проверяем наличие popup
                popup.classList.remove('active');
                overlay.classList.remove('active');
            }
        }
    }
});