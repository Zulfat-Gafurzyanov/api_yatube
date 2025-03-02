from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import PermissionDenied

from posts.models import Comment, Group, Post
from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class UpdateDeleteViewSet(mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """Миксин для проверки прав при запросе на изменение или удаление."""

    def perform_update(self, serializer):
        # Функция проверяет, что только автор может вносить изменения.
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(UpdateDeleteViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        # Функция проверяет, что только автор может удалить созданный объект.
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        # Удаляем пост.
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet, UpdateDeleteViewSet):
    """Вьюсет для модели Comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_post(self):
        # Функция для получения поста.
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def perform_create(self, serializer):
        # При создании нового комментария автор автоматически определяется
        # на основе текущего аутентифицированного пользователя.
        serializer.save(author=self.request.user, post=self.get_post())


class GroupViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Group."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet, UpdateDeleteViewSet):
    """Вьюсет для модели Post."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        # При создании нового поста автор автоматически определяется на основе
        # текущего аутентифицированного пользователя.
        serializer.save(author=self.request.user)
