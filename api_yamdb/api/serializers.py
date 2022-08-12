from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api_yamdb.settings import MAX_LEN_CODE, MAX_LEN_EMAIL, MAX_LEN_USERNAME
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username, validate_year

UNIQUE_REVIEW_MSG = 'Можно писать только 1 отзыв.'


class UsernameValidationMixin:
    """Миксин-валидатор для поля username."""

    def validate_username(self, value):
        return validate_username(value)


class UserSerializer(serializers.ModelSerializer, UsernameValidationMixin):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignUpSerializer(serializers.Serializer, UsernameValidationMixin):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(max_length=MAX_LEN_USERNAME)
    email = serializers.EmailField(max_length=MAX_LEN_EMAIL)


class TokenSerializer(serializers.Serializer, UsernameValidationMixin):
    """Сериализатор для получения токена пользователя."""

    username = serializers.CharField(max_length=MAX_LEN_USERNAME)
    confirmation_code = serializers.CharField(
        max_length=MAX_LEN_CODE,
        required=True
    )


class UserProfileSerializer(UserSerializer):
    """Сериализатор для страницы профиля пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасных запросов."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        read_only = '__all__'


class TitleSaveSerializer(serializers.ModelSerializer):
    """Сериализатор для SAVE запросов."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    def validate_year(self, value):
        return validate_year(value)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                title=get_object_or_404(
                    Title,
                    pk=self.context.get('view').kwargs.get('title_id')
                ),
                author=self.context['request'].user
            ).exists():
                raise serializers.ValidationError(UNIQUE_REVIEW_MSG)
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
