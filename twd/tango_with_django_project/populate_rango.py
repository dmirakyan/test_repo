import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                                'tango_with_django_project.settings')

import django 
django.setup()
from rango.models import Category, Page

def populate():
    # First, we will create lists of dictionaries
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # Thtrough each data structure, and add the data to our models.

    python_pages = [
        {'title': 'Official Python Tutorial',
        'url':'https://docs.python.orgg/3/tutorial/',
        'views':30},
        {'title': 'How to think like a Computer Scientist',
        'url':'http://www.greenteapress.com/thinkpython/',
        'views':56},
        {'title': 'Learn Python in 10 minutes',
        'url':'http://www.korokithakis.net/tutorials/python',
        'views':2}]

    django_pages = [
        {'title':'Official Django Tutorial',
        'url':'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
        'views':1},
        {'title':'Django Rocks',
        'url':'http://www.djangorocks.com/',
        'views':2},
        {'title':'How to Tango with Django',
        'url':'http://www.tangowithdjango.com/',
        'views':124} ]

    other_pages = [
        {'title':'Bottle',
        'url':'http://bottlepy.org/docs/dev/',
        'views':35},
        {'title':'Flask',
        'url':'http://flask.pocoo.org',
        'views':43}]

    random_pages = [
        {'title':'Page1',
        'url':'http://www.google.com',
        'views':35},
        {'title':'Page2',
        'url':'http://www.google.com',
        'views':30},]
    
    cats = {'Python': {'pages':python_pages,'views':128, 'likes':64},
            'Django': {'pages': django_pages, 'views':64, 'likes':32},
            'Perl': {'pages': [],'views':64, 'likes':32},
            'PHP': {'pages': [],'views':64, 'likes':32},
            'Prolog': {'pages': [],'views':64, 'likes':32},
            'PostScript': {'pages': [],'views':64, 'likes':32},
            'Programming': {'pages': [],'views':64, 'likes':32},
            'Other Frameworks': {'pages': random_pages,'pages':other_pages, 'views':32, 'likes':16}}

    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all the associated pages for that category
    for cat, cat_data in cats.items():
        c = add_cat(cat,cat_data['views'],cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c,p['title'],p['url'],p['views'])
    
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')

def add_page(cat,title,url,views):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p

def add_cat(name,likes=0,views=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

# Start execution here!

if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
