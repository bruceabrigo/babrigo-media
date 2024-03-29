from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Review, AllCollections, UploadPhoto, ContactForm
import os
import uuid
import boto3
from django.conf import settings
# ------------------------------ for contact ------------------------------
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
# ------------------------------ user forms ------------------------------
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django import forms
from django.contrib.auth.models import User


# ------------------------------ aws auth ------------------------------


AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
S3_BUCKET = settings.S3_BUCKET
S3_BASE_URL = settings.S3_BASE_URL

# ------------------------------ user auth ------------------------------
def signup(request):
    error_messsage = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_messsage = 'Error on signup, please try again...'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_messsage}
    return render(request, 'registration/signup.html', context)
            
# ------------------------------ end user auth ------------------------------

def photos(request):
    secret_key = os.environ['SECRET_KEY']
# views.py

# Create your views here.
def home(request): # home page view
    # user_id = request.user.id  # or however you want to get the user_id
    # context = {'user_id': user_id}
    return render(request, 'home.html')


from django.conf import settings
from django.core.mail import send_mail, BadHeaderError

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry" 
            body = {
            'first_name': form.cleaned_data['first_name'], 
            'last_name': form.cleaned_data['last_name'], 
            'email': form.cleaned_data['email'],  
            'message':form.cleaned_data['message'], 
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, ['bruceabrigo@outlook.com']) 
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('home')
      
    form = ContactForm()
    return render(request, 'contact.html', {'form': form})



# ----------------- Reviews -----------------

def show_reviews(request): # show an index of all the reviews
    reviews = Review.objects.all() # reviews will make a query for all reviews to be rendered to the index
    return render(request, 'reviews/index.html', {
        'reviews': reviews
    })

def view_review(request, review_id): # this will show a details page of ONE review
    review = Review.objects.get(id=review_id) # review, is equal to the id of one review, based on the reviews id, in which was included reviews query, and looped into separate reviews with their id's
    return render(request, 'reviews/view_review.html', {
        'review': review
    })

class PostReview(CreateView):
    model = Review
    fields = ['name', 'note']

    success_url = '/reviews'

class UpdateReview(UpdateView):
    # I only want users to be able change the note
    model = Review
    fields = ['note']

class DeleteReview(DeleteView):
    model = Review
    success_url = '/reviews'
    
# ----------------- Collections Home & Create -----------------

class CollectionForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = AllCollections
        fields = ['collection', 'user']

class SuperUserRequired(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class CreateCollection(SuperUserRequired, CreateView):
    model = AllCollections
    form_class = CollectionForm
    success_url = '/collections'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DeleteCollection(SuperUserRequired, DeleteView):
    model = AllCollections
    success_url = '/collections'

# ----------------- End  -----------------

# ----------------- Collections page -----------------
# create individual portrait reviews
# each collection is to render all photos in that collections one-to-many relationship
def collections(request):
    collections = AllCollections.objects.all()
    return render(request, 'collections.html', {'collections': collections})

def view_collection(request, collection_id):
    collection = AllCollections.objects.get(id=collection_id)
    return render(request, 'collections/view_collection.html', {'collection': collection})

def my_collections(request, user_id):
    collections = AllCollections.objects.filter(user_id=user_id)
    return render(request, 'collections/my_collections.html', {'collections': collections, 'user_id': user_id})

# create a custom function to upload an image to AWS
@login_required
def upload_photo(request, collection_id):
    photo_file = request.FILES.get('photo-file', None)

    if photo_file:
        # if present, we'll use this to create  a ref to the boto3
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        # CREATE A UNIQUE KEY FOR OUR PHOTOS
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # we're going to use try... except which is like try...catch in js
        # to handle the situation if anything should go wrong
        try:
            # if success
            s3.upload_fileobj(photo_file, S3_BUCKET, key)
            # build the full url setting to upload s3
            url = f'{S3_BASE_URL}{S3_BUCKET}/{key}'
            # if our upload(that used boto3) was succesful
            # we want to use that photo locations to create a Photo model
            photo = UploadPhoto(url=url, collection_id=collection_id)
            # save the instance to the database
            photo.save()
        # except is our catch
        except Exception as error:
            # pring an error message
            print('Error uploading image', error)
            return redirect('collections')
    return redirect('collections')



