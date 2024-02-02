from django.shortcuts import render, get_object_or_404
from .models import Book, BookInstance, Author, Genre
from django.views import generic
import datetime
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required  ## for function based views
from django.contrib.auth.mixins import LoginRequiredMixin  ## for class based views
from django.contrib.auth.decorators import permission_required  ## for function based views
from django.contrib.auth.mixins import PermissionRequiredMixin  ## for class based views
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



from myapp.forms import RenewBookForm, BookForm






# Create your views here.
class IndexView(LoginRequiredMixin, generic.TemplateView):
    def get(self, request):
        num_books = Book.objects.all().count()
        num_instances = BookInstance.objects.all().count()
        num_instances_available = BookInstance.objects.filter(
            status__exact='a').count()
        num_authors = Author.objects.count()
        num_genres = Genre.objects.count()

        # Number of visits to this view, as counted in the session variable.
        num_visits = request.session.get('num_visits', 0)
        request.session['num_visits'] = num_visits + 1

        context = {
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_genres': num_genres,
            'num_visits': num_visits,
        }

        return render(request, 'myapp/index.html', context=context)


# class BookListView(generic.ListView):
#     model = Book
#     context_object_name = 'book_list' # own name for the list as a template variable
#     queryset = Book.objects.filter(title__icontains='war')[:5]   # get 5 books containing the title war

#     template_name = 'myapp/book_list'

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404('Book does not exist')

        return render(request, 'myapp/book_detail.html', context={'book': book})




class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk = primary_key)
        except:
            raise Http404('Author does not exist')
        return render(request, 'mayapp/author_detail.html', context={"autor": author})
    

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'myapp/bookinstance_list_borrowed_user.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(borrowerdue_back=self.request.user, status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'myapp.can_mark_returned'
    template_name = 'myapp/bookinstance_list_borrowed_all.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    



def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'myapp/book_renew_librarian.html', context)



@login_required
@permission_required('myapp.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'myapp/book_renew_librarian.html', context)





class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '31/01/2023'}
    permission_required = 'myapp.add_author'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'myapp.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )
        

class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'myapp/book_form.html'
    success_url = reverse_lazy('book_list')

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'myapp/book_form.html'
    success_url = reverse_lazy('book_list')

class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'myapp/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')