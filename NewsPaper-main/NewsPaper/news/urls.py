from django.urls import path, include
from django.views.decorators.cache import cache_page
from .views import *

urlpatterns = [
    path('', cache_page(10)(NewsList.as_view()), name='news'),
    path('<int:pk>', cache_page(10)(NewsDetail.as_view()), name='news_detail'),
    path('search', SearchList.as_view(), name='search'),
    path('add', PostCreateView.as_view(), name='add_post'),
    path('update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('login/', LoginView.as_view(template_name='login_page.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout_page.html'), name='logout'),
    path('login/signup/', RegisterView.as_view(), name='signup'),
    path('accounts/', include('allauth.urls')),
    path('getauthor/', get_author, name='getauthor'),
    path('categories', PostCategoryView.as_view(), name='categories'),
    path('categories/<int:pk>', CategoryDetail.as_view(), name='cat_detail'),
    path('subscribe/<int:pk>', subscribe_to_category, name='subscribe'),
    path('unsubscribe/<int:pk>', unsubscribe_from_category, name='unsubscribe'),
]
