document.addEventListener('DOMContentLoaded', (event) => {
  const commentForm = document.forms.commentForm;
  const commentFormContent = commentForm.content;
  const commentFormParentInput = commentForm.parent;
  const commentFormSubmit = document.getElementById('commentSubmit');
  const commentArticleId = commentForm.getAttribute('data-recipe-id');
  const replyButtons = document.querySelectorAll('a[href="#commentForm"]');

  commentForm.addEventListener('submit', createComment);
  replyButtons.forEach(button => button.addEventListener('click', replyComment));

  async function createComment(event) {
    event.preventDefault();

    commentFormSubmit.disabled = true;
    commentFormSubmit.innerText = "Ожидаем ответа сервера";
    try {
      const response = await fetch(`/recipes/comment_create_view/${commentArticleId}/comments/create/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(commentForm),
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert(`Ошибка: ${errorData.errors}`);
        commentFormSubmit.disabled = false;  // Делаем кнопку доступной
        commentFormSubmit.innerText = "Добавить комментарий";  // Возвращаем текст кнопки
        return;  // Выход из функции
      }

      const comment = await response.json();

      let deleteButton = '';
      if (userIsAuthenticated) {
          deleteButton = `<a class="delete-comment-button"
              href="#"
              data-comment-id="${comment.id}"
              data-comment-username="${comment.author}">Удалить</a>`;
      }

      let commentTemplate = `<ul id="comment-thread-${comment.id}" class="list-none">
                              <li class="card">
                                <div class="comment-container">
                                  <img src="${comment.avatar}" class="comment-image-profile" alt="${comment.author}" />
                                    <div class="card-body">

                                    <div class="comment-author-time">
                                      <h6 class="card-title">
                                        <b>
                                            <a class="comment-author" href="${comment.get_absolute_url}">${comment.author}</a>
                                        </b>
                                      </h6>
                                      <time class="comment-time-create">${comment.time_create}</time>
                                    </div>

                                      <p class="card-text">
                                        ${comment.content}
                                      </p>
                                      <div class="comment-btn">
                                        <a class="comment-btn-answer" href="#commentForm" data-comment-id="${comment.id}" data-comment-username="${comment.author}">Ответить</a>
                                        ${deleteButton}
                                      </div>
                                    </div>
                                  </div>
                                <hr />
                              </li>
                            </ul>`;
    if (comment.is_child) {
      const parentCommentThread = document.querySelector(`#comment-thread-${comment.parent_id}`);
      let nestedUl = parentCommentThread.querySelector('ul');
      if (!nestedUl) {
        nestedUl = document.createElement('ul');
        nestedUl.className = 'nested-comm';
        parentCommentThread.appendChild(nestedUl);
      }
      nestedUl.insertAdjacentHTML("beforeend", commentTemplate);
    } else {
      document.querySelector('.nested-comments').insertAdjacentHTML("beforeend", commentTemplate);
    }
      commentForm.reset();
      commentFormSubmit.disabled = false;
      commentFormSubmit.innerText = "Добавить комментарий";
      commentFormParentInput.value = '';
      updateReplyButtons();
              // Обновляем количество комментариев
        const commentCountElement = document.getElementById('comment_count');
        commentCountElement.textContent = `Комментарии (${comment.comment_count}):`;
    } catch (error) {
      console.error(error);
    }
  }

  function replyComment(event) {
    event.preventDefault();
    const commentUsername = this.getAttribute('data-comment-username');
    const commentMessageId = this.getAttribute('data-comment-id');
    commentFormContent.value = `${commentUsername}, `;
    commentFormParentInput.value = commentMessageId;
    commentFormContent.focus();
  }

  function updateReplyButtons() {
    document.querySelectorAll('a[href="#commentForm"]').forEach(button => {
      button.removeEventListener('click', replyComment);
      button.addEventListener('click', replyComment);
    });
  }
});


// Скрипт для удаления комментария
document.addEventListener('DOMContentLoaded', (event) => {
//  const deleteButtons = document.querySelectorAll('.delete-comment-button');
//  deleteButtons.forEach(button => button.addEventListener('click', deleteComment));

  const commentsContainer = document.querySelector('.nested-comments');
  commentsContainer.addEventListener('click', function(event) {
    if (event.target.classList.contains('delete-comment-button')) {
      deleteComment.call(event.target, event);
    }
  });

  async function deleteComment(event) {
    event.preventDefault();
    const commentId = this.getAttribute('data-comment-id');
    const formData = new FormData();
    formData.append('comment_id', commentId);

    try {
      const response = await fetch(`/recipes/comment/${commentId}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
      });

    if (response.ok) {
      const result = await response.json();
      if (result.status === 'success') {
        // Удалите элемент комментария из DOM
        const commentElement = document.querySelector(`#comment-thread-${commentId}`);
        commentElement.remove();

        // Обновите счетчик комментариев
        const commentCountElement = document.getElementById('comment_count');
        commentCountElement.textContent = `Комментарии (${result.comment_count}):`;
      } else {
        console.error('Ошибка при удалении комментария');
      }
    } else {
      console.error('Ошибка сервера');
    }
    } catch (error) {
      console.error(error);
    }
  }
});
