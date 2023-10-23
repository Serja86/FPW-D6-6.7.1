from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.validators import MinValueValidator


class Author(models.Model): # Модель, содержащая объекты всех авторов.
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)


    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum('rating'))
        pRat = 0
        print(postRat, pRat)
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = 0
        print(commentRat, cRat)
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return f'{self.authorUser.username}'


class Category(models.Model): # Категории новостей/статей — темы, которые они отражают (спорт, политика, образование и т. д.)
    name = models.CharField(max_length=255, unique = True)

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOISES = (
        (NEWS, 'Новость'),
        (ARTICLE, "Статья"),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOISES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True) # автоматически добавляемая дата и время создания
    postCategory = models.ManyToManyField(Category, through="PostCategory") # связь «многие ко многим» с моделью Category - добавить (с дополнительной моделью PostCategory)
    title = models.CharField(max_length=128) # доработать может не тот тип заголовок статьи/новости
    text = models.TextField()  # доработать текст статьи/новости
    rating = models.SmallIntegerField(default=0)  # доработать рейтинг статьи/новости

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'

    def __str__(self):
        return self.title.title()

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

class PostCategory (models.Model): # Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо организовать их способ хранения тоже.
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.postThrough.title}: {self.categoryThrough.name}'


class Comment (models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE) # связь «один ко многим» с моделью Post
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE) # добавить комментарии может оставить любой пользователь, необязательно автор
    text = models.TextField() # доработать
    dateCreations = models.DateTimeField(auto_now_add=True) # дата и время создания комментария
    rating = models.SmallIntegerField(default=0)  # рейтинг комментария

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.text}'

class Subscriber(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscrptions',
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name='subscrptions',
    )