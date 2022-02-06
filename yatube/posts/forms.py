from django import forms

from .models import Post, Group, Comment

group_list = Group.objects.all().values_list('title')


class PostForm(forms.ModelForm):
    """Модель формы создания нового поста"""

    class Meta():
        model = Post

        fields = ('text', 'group', 'image')

        text = forms.CharField(
            label='Текст поста',
        )
        group = forms.ModelChoiceField(label='Группа',
                                       required=False,
                                       queryset=group_list,
                                       empty_label='---------',
                                       )
        image = forms.ImageField(
            label='Картинка поста',
        )


class CommentForm(forms.ModelForm):
    """Модель формы создания нового поста"""

    class Meta():
        model = Comment

        fields = ('text',)

        text = forms.CharField(
            label='Текст комментария',
        )
