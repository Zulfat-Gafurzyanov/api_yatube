from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import PermissionDenied

from posts.models import Comment, Group, Post
from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_post(self):
        # Функция для получения поста.
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_queryset(self):
        # Авторизованному пользователю показываем все комментарии поста.
        if self.request.user:
            post = self.get_post()
            return post.comments.all()

    def perform_create(self, serializer):
        # При создании нового комментария автор автоматически определяется
        # на основе текущего аутентифицированного пользователя.
        serializer.save(author=self.request.user, post=self.get_post())

    def perform_update(self, serializer):
        # Функция проверяет, что только автор может изменить свой комментарий.
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого комментария запрещено!')
        super(CommentViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        # Функция проверяет, что только автор может удалить свой комментарий.
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого комментария запрещено!')
        # Удаляем пост.
        instance.delete()


class GroupViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Group."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Post."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        # При создании нового поста автор автоматически определяется на основе
        # текущего аутентифицированного пользователя.
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Функция проверяет, что только автор может изменить свой пост.
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого поста запрещено!')
        super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        # Функция проверяет, что только автор может удалить свой пост.
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого поста запрещено!')
        # Удаляем все связанные с постом комментарии.
        for comment in instance.comments.all():
            comment.delete()
        # Удаляем пост.
        instance.delete()
