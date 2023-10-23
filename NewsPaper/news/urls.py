from django.urls import path
from .views import (NewsList, NewsDetail, PostCreateAR, PostCreateNW, PostSearchView,
                    PostEditNW, PostDeleteNW, PostEditAR, PostDeleteAR)

urlpatterns = [
    path('', NewsList.as_view(), name='post_list'),
    path('<int:pk>', NewsDetail.as_view(), name='post_detail'),
    path('search/', PostSearchView.as_view()),
    path('create/', PostCreateNW.as_view(), name='post_createNW'),
    path('create2/', PostCreateAR.as_view(), name='post_createAR'),
    path('<int:pk>/edit/', PostEditNW.as_view(), name='post_editNW'),
    path('<int:pk>/edit2/', PostEditAR.as_view(), name='post_editAR'),
    path('<int:pk>/delete/', PostDeleteNW.as_view(), name='post_deleteNW'),
    path('<int:pk>/delete2/', PostDeleteAR.as_view(), name='post_deleteAR'),
]