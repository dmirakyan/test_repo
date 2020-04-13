from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    # Query The database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to teh template engine
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)

    # Render the response and send it back
    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
    
    visitor_cookie_handler(request)
    context_dict = {'boldmessage': 'This tutorial has been put together by Banksy'}
    context_dict['visits'] = request.session['visit']
    return render(request,'rango/about.html',context=context_dict)

    # response = HttpResponse()
    # response.write('Rango says here is the about page. </br>')
    # response.write("<a href='/rango/'>Index</a>")
    # return response

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine
    context_dict = {}

    try: 
        # Can we find a category name slug with the given name>
        # If we can't, the .get() method raises a DoesNotExist exception
        # The .get() method returns one model instance or raises an exception
        category =  Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages
        # The filter() will return a list of page objects or an empty list
        pages =  Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        context_dict['category'] = category
    
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    
    # Go render the response and return it to the client
    return render(request,'rango/category.html', context=context_dict)

def add_category(request):
    if request.user.is_authenticated==True:
        form = CategoryForm()
        # A HTTP POST?
        if request.method == 'POST':
            form = CategoryForm(request.POST)

                # Have we been provided with a valid form?
            if form.is_valid():
                    # Save the new category to the database.
                cat = form.save(commit=True)
                print(cat,cat.slug)
                return redirect('/rango/')      
            else:
                print(form.errors)
        return render(request, 'rango/add_category.html', {'form':form})     
    else: 
        return HttpResponse("Only registered users can add things")
 
def add_page(request, category_name_slug):
    if request.user.is_authenticated==True:
        try:
            category = Category.objects.get(slug=category_name_slug)
        except:
            category = None
        if category is None:
            return redirect('/rango/')
        form =  PageForm()
        if request.method == 'POST':
            form = PageForm(request.POST)
            if form.is_valid():
                if category:
                    page = form.save(commit=False)
                    page.category = category
                    page.views = 0
                    page.save()
                    return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
            else:
                print(form.errors) 
        context_dict = {'form':form, 'category':category}
        return render(request,'rango/add_page.html', context=context_dict)
    else: 
        return HttpResponse("Only registered users can add things")

# def register(request):
#     registered = False

#     if request.method == 'POST':
#         user_form = UserForm(request.POST)
#         profile_form = UserProfileForm(request.POST)

#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()

#             profile = profile_form.save(commit=False)
#             profile.user = user

#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
            
#             profile.save()
#             registered = True
        
#         else:
#             print(user_form.errors,profile_form.errors)
#     else: 
#         user_form = UserForm()
#         profile_form = UserProfileForm()
    
#     return render(request,
#                 'rango/register.html', 
#                 context = {
#                     'user_form':user_form,
#                     'prifle_form':profile_form,
#                     'registered':registered})

        
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(username=username, password=password)

#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return redirect(reverse('rango:index'))
#             else:
#                 return HttpResponse("Your Rango account is disabled.")
#         else:
#             print(f"Invalid login details: {username}, {password}")
#             return HttpResponse("Invalid login details supplied.")
#     else:
#         return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request,'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visit_count = int(get_server_side_cookie(request,'visit', '1'))
    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    visit_count = visit_count + 1
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visit_count = visit_count + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
        # Update/set the visits cookie
    request.session['visit'] = visit_count