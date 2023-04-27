from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Dog, Toy
from .forms import FeedingForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

def home(request):
    return HttpResponse("<h1>Hello World</h1>")

def about(request):
    return render(request, "about.html")

@login_required
def dogs_index(request):
    dogs = Dog.objects.filter(user=request.user)
    return render(request, "dogs/index.html", {"dogs": dogs})

def dogs_detail(request, dog_id):
  dog = Dog.objects.get(id=dog_id)
  # instantiate FeedingForm to be rendered in the template

  toys_dog_doesnt_have = Toy.objects.exclude(id__in = dog.toys.all().values_list('id'))

  feeding_form = FeedingForm()
  return render(request, 'dogs/detail.html', {
    # include the dog and feeding_form in the context
    'dog': dog,'feeding_form': feeding_form,
    'toys': toys_dog_doesnt_have
  })

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      signup(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

@login_required
def add_feeding(request, dog_id):
  # create the ModelForm using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the dog_id assigned
    new_feeding = form.save(commit=False)
    new_feeding.dog_id = dog_id
    new_feeding.save()
  return redirect('detail', dog_id=dog_id)


def assoc_toy(request, dog_id, toy_id):
  # Note that you can pass a toy's id instead of the whole object
  Dog.objects.get(id=dog_id).toys.add(toy_id)
  return redirect('detail', dog_id=dog_id)


class DogCreate(LoginRequiredMixin, CreateView):
  model = Dog
  fields = ('name','breed', 'description', 'age')
  # success_url = '/dogs/'

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the dog
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class DogUpdate(LoginRequiredMixin, UpdateView):
  model = Dog
  # Let's disallow the renaming of a dog by excluding the name field!
  fields = ['breed', 'description', 'age']

class DogDelete(LoginRequiredMixin, DeleteView):
  model = Dog
  success_url = '/dogs/'

class ToysIndex(ListView):
  model = Toy

class ToysDetail(LoginRequiredMixin, DetailView):
  model = Toy

class ToyCreate(LoginRequiredMixin, CreateView):
  model = Toy
  fields = '__all__'

class ToyUpdate(LoginRequiredMixin, UpdateView):
  model = Toy
  fields = '__all__'

class ToyDelete(LoginRequiredMixin, DeleteView):
  model = Toy
  success_url = '/toys/'