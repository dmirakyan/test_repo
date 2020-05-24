from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime
from rango.bing_search import run_query

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


def get_category_list(max_results=0, starts_with=''): 
    category_list = []
    # category_list = Category.objects.filter(name__istartswith=starts_with)
    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)
    
    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results] 
    
    return category_list

class CategorySuggestionView(View): 
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''

        print(suggestion)
        category_list = get_category_list(max_results=8, starts_with=suggestion)
        # category_list = ['test','test2']
        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')
        return render(request, 'rango/categories.html',{'categories': category_list})

class AddPageFromSearch(View):
    @method_decorator(login_required)
    def get(self, request):
        
        title = request.GET['title']
        url = request.GET['url']
        category_id = request.GET['category_id']
        
        
        try:
            # category = Category.objects.get(slug=request.GET['category_name'])
            category = Category.objects.get(id=int(category_id))
            # slug = Category.objects.get(id=int(category_id)).values_list('slug')
        except Category.DoesNotExist:
            return HttpRespose('Error - category not found')
        
        except ValueError:
            return HttpRespose('Error - badCategoryId')

        category_name_slug = category.slug
        # slug =  getattr(category, 'slug')
        # category_name_slug = category.['slug']



        p = Page.objects.get_or_create(category=category, title=title, url=url)
        pages = Page.objects.filter(category=category).order_by('-views')

        return render(request, 'rango/page_listing.html', {'pages': pages})
        # return render(request, 'rango/category.html', category_name_slug=slug)
       


class AboutView(View):
    def get(self,request):
        context_dict = {}

        visitor_cookie_handler(request)
        # context_dict['visits'] = request.session['visits']

        response = render(request, 'rango/about.html', context_dict)
        return response

class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DiesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)

        category.likes = category.likes +1
        category.save()
        return HttpResponse(category.likes)

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine
    context_dict = {}
    context_dict['result_list'] = []
    context_dict['previous_query'] = []

    try: 
        # Can we find a category name slug with the given name>
        # If we can't, the .get() method raises a DoesNotExist exception
        # The .get() method returns one model instance or raises an exception
        category =  Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages
        # The filter() will return a list of page objects or an empty list
        pages =  Page.objects.filter(category=category).order_by('-views')[:5]

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        context_dict['category'] = category
    
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    

    if request.method == 'POST':
        query = request.POST['query'].strip()
        previous_query = query
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['previous_query'] = previous_query

    # Go render the response and return it to the client
    response = render(request,'rango/category.html', context=context_dict)
    return response 


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

def search(request):
    result_list = []
    previous_query = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        previous_query = query
        if query:
            result_list = run_query(query)
    response = render(request, 'rango/search.html', {'result_list':result_list, 'previous_query':previous_query} )
    return response

def goto_url(request):
    page_id = None
    if request.method == 'GET':
        page_id = request.GET.get('page_id')
    # category =  Category.objects.get(slug=category_name_slug)
    try:
        page =  Page.objects.get(id=page_id)
        page.views = page.views + 1
        page.save()
        return redirect(page.url)
    except:
        page_id = None 
        return redirect(reverse('rango/index.html'))


@login_required
def initialize_profile(request):
    # registered=False
    context_dict = {}

    if request.method =='POST':
        profile_form = UserProfileForm(request.POST)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
        else:
            print(form.errors)
        return redirect(reverse('rango:index'))
        
    else:
        profile_form = UserProfileForm()
        context_dict['profile_form'] = profile_form
        # context_dict['profile_completed'] = True
        response = render(request,'rango/profile_registration.html',context = context_dict)
        return response

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
                                'picture': user_profile.picture})
        
        return (user, user_profile, form)
    
    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rango/prof.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
                form.save(commit=True)
                return redirect('rango:prof', user.username)
        else:
            print(form.errors)
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rango/prof.html', context_dict)

# class ProfileView(View):
#     def get_user_details(self,username):
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return None
        
#         user_profile = UserProfile.objects.get_or_create(user=user)[0]
#         form = UserProfileForm()
    
#     @method_decorator(login_required)
#     def get(self, request, username):
#         try:
#             (user, user_profile, form) = self.get_user_details(username)
#         except TypeError:
#             return redirect(reverse('rango:index'))
        
#         context_dict = {'user_profile': user_profile,
#                         'selected_user': user,
#                         'form': form}
        
#         return render(request, 'rango/profile.html', context_dict)

#     @method_decorator(login_required)
#     def post(self, request, username):
#         try:
#             (user, user_profile, form) = self.get_user_details(username)
#         except TypeError:
#             return redirect(reverse('rango:index'))

#         form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

#         if form.is_valid():
#             form.save(commit=True)
#             return redirect('rango:profile', user.username)
        
#         else: 
#             print(form.errors)
        
#         context_dict = {'user_profile': user_profile,
#                         'selected_user': user,
#                         'form': form}
        
#         response = render(request, 'rango/profile.html', context = context_dict)
#         return response
 


