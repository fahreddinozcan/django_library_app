import datetime

from django.shortcuts import render, get_object_or_404
from .models import Book, BookInstance, Author, Genre, Language
from django.contrib.auth.decorators import permission_required, login_required
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import RenewBookForm


def index(request):
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.all().count()
    num_genres_fiction=Genre.objects.filter(name__icontains='fiction').count()
    num_genres=Genre.objects.all().count()
    num_books_harrypotter = Book.objects.filter(title__icontains='harry').count()

    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits']=num_visits+1
    context={
        'num_books':num_books,
        'num_instances':num_instances,
        'num_instances_available':num_instances_available,
        'num_authors':num_authors,
        'num_genres':num_genres,
        'num_genres_fiction':num_genres_fiction,
        'num_books_harrypotter':num_books_harrypotter,
        'num_visits':num_visits,
    }

    return render(request, 'index.html', context=context)

class AuthorListView(generic.ListView):
    model=Author
    paginate_by = 1
    context_object_name = 'author_list'
    queryset = Author.objects.all()[:5]
    template_name = 'authors/my_arbitrary_template_name_list.html'

    def get_queryset(self):
        return Author.objects.all()[:5]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class AuthorDetailView(generic.DetailView):
    model=Author

def author_detail_view(request, primary_key):
    author=get_object_or_404(Author, pk=primary_key)

    return render(request, 'catalog/author_detail.html', context={'author':author})


class BookListView(generic.ListView):
    model=Book
    paginate_by = 1
    context_object_name = 'book_list'
    queryset = Book.objects.all()[:5]
    template_name = 'books/my_arbitrary_template_name_list.html'

    def get_queryset(self):
        return Book.objects.all()[:5]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model=Book

def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)

    return render(request, 'catalog/book_detail.html', context={'book': book})

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class LoanedBooksToLibrarianListView(LoginRequiredMixin, generic.ListView):
    model=BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_to_librarian.html'
    paginate_by = 5
    permission_required='catalog.can_see_all_onloans'

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact='o').order_by('due_back')
        )

@login_required
@permission_required('catalog.can_mark_required')
def renew_book_librarian(request, pk):
    book_instance=get_object_or_404(BookInstance, pk=pk)

    if request.method=='POST':
        form=RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back=form.cleaned_data['renewal_date']

            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model=Book
    fields=['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(UpdateView):
    model=Book
    fields='__all__'
class BookDelete(DeleteView):
    model=Book
    success_url = reverse_lazy('books')