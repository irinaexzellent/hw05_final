from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    """Модель для хранения сообществ(групп)."""
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(
        max_length=255, unique=True,
        db_index=True, verbose_name="URL")
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    """Модель для хранения постов."""
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')

    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу')

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    def __str__(self):
        count_symbol = 15
        return self.text[:count_symbol]

    class Meta:
        ordering = ['-pub_date']


class Comment(CreatedModel):
    """Модель для хранения комментриев постов."""
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    post = models.ForeignKey(
        Post,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Комментарий',
        help_text='Комментарии')


class Follow(models.Model):
    """Модель для хранения связей между авторами и
    подписчиками

    Ключевые аргументы:
    user -- ссылка на объект пользователя, который подписывается,
    author -- ссылка на объект пользователя, на которого подписываются
    """
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE)

    def __str__(self):
        return f"Подписчик: '{self.user}', автор: '{self.author}'"

