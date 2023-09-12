from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import resolve
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings

from .filters import NewsFilter
from .forms import PostForm, RegisterForm, LoginForm
from .models import Post, Author, Category

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


# Create your views here.
class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'det_news.html'
    context_object_name = 'det_news'


class SearchList(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    # paginate_by = 10
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())

        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

        return super().get(request, *args, **kwargs)


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'add_post.html'
    form_class = PostForm
    permission_required = ('news.add_post',)


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'post_update.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    def get_object(self, **kwargs):
        id_id = self.kwargs.get('pk')
        return Post.objects.get(pk=id_id)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'
    permission_required = ('news.delete_post',)


class PostCategoryView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'
    queryset = Category.objects.order_by('name')


class CategoryDetail(ListView):
    model = Post
    template_name = 'det_cat.html'
    context_object_name = 'cat_posts'
    paginate_by = 3

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        c = Category.objects.get(id=self.id)
        queryset = Post.objects.filter(postCategory=c).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        c = Category.objects.get(id=self.id)
        context['category'] = c
        return context


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'sign/signup.html'
    success_url = '/'

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get_or_create(name='common')[0]
        user.groups.add(group)
        user.save()
        return super().form_valid(form)


class LoginView(FormView):
    model = User
    form_class = LoginForm
    template_name = 'sign/login.html'
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'sign/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


@login_required
def get_author(request):
    user = request.user
    Author.objects.create(authorUser=user)
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/')


@login_required
def subscribe_to_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)
        email = user.email
        html = render_to_string(
            'mail/subscribe.html',
            {
                'category': category,
                'user': user
            },
        )
        msg = EmailMultiAlternatives(
            subject=f'Вы подписались на категорию {category}',
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[email, ],
        )

        msg.attach_alternative(html, 'text/html')

        try:
            msg.send()
        except Exception as e:
            print(e)
        return redirect(request.META.get('HTTP_REFERER'))

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_from_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)

    return redirect(request.META.get('HTTP_REFERER'))
