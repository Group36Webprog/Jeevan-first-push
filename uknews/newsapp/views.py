from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile, Article, Comment
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
import json
import os

import random

from django.core.mail import send_mail


def random_article():
    category = ["Sport", "Finance", "Entertainment", "World"]
    for i in range(10):
        print(i)
        chosen_category = random.choice(category)
        article_name = chosen_category + " " + str(i)
        article_description = "This is the desription for article {}".format(
            chosen_category)
        Article.objects.create(
            article_name=article_name,
            article_category=chosen_category,
            article_description=article_description
        )
    return


def mainpage(request):
    return render(request, "newsapp/mainpage.html", {})


def edit_comment(request):
    if not request.user.is_authenticated:
        context = {
            "message": "You need to be logged in to post a comment on any article. "}
        return HttpResponse(json.dumps(context), content_type="application/json")

    new_comment = request.GET.get('new_comment', None)
    comment_id = request.GET.get('comment_id', None)
    print("comment_id", comment_id)

    comment = Comment.objects.get(id=int(comment_id))
    comment.comment_text = new_comment
    comment.save(update_fields=['comment_text'])

    context = {"comment": serializers.serialize("json", [comment, ])}
    return HttpResponse(json.dumps(context), content_type="application/json")


def create_comment(request):
    if not request.user.is_authenticated:
        context = {
            "message": "You need to be logged in to post a comment on any article. "}
        return HttpResponse(json.dumps(context), content_type="application/json")

    comment_text = request.GET.get('comment', None)
    article_id = request.GET.get('article_id', None)
    user = User.objects.get(id=int(request.user.pk))
    article = Article.objects.get(id=int(article_id))

    comment = Comment.objects.create(
        user=user,
        article=article,
        comment_text=comment_text
    )
    context = {"comment": serializers.serialize(
        "json", [comment, ]), "user": serializers.serialize("json", [user, ])}
    return HttpResponse(json.dumps(context), content_type="application/json")


def article_page(request, article_id):
    article = Article.objects.get(id=article_id)
    all_comments = Comment.objects.filter(
        article=article).order_by('-comment_created_time')
    context = {"article": article,
               "all_comments": all_comments}
    return render(request, "newsapp/articlepage.html", context)


def delete_comment(request):
    comment_id = request.GET.get('comment_id', None)

    Comment.objects.filter(id=int(comment_id)).delete()
    context = {"status": "OK"}
    return HttpResponse(json.dumps(context), content_type="§application/json")


def get_distinct_categories(request):
    # Display the categories in the nav bar for all the users.
    # So the users can browse thorugh each article by category.
    unique_categories = list(Article.objects.all().values_list(
        'article_category', flat=True).distinct())
    unique_categories.sort()
    response = {"unique_categories": unique_categories}
    return HttpResponse(json.dumps(response), content_type="application/json")


def get_favourite_categories(request):
    profile = Profile.objects.get(user=request.user.pk)
    favourite_categories = profile.favourite_category.split(
        ",") if profile.favourite_category else []
    favourite_categories.sort()
    response = {"favourite_categories": favourite_categories}
    return HttpResponse(json.dumps(response), content_type="application/json")


def auth_login(request):
    if request.method == "POST" and "login_account" in request.POST:
        email_address = request.POST["email_address"]
        password = request.POST["password"]

        if not request.POST.get('remember_me', None):
            # User checked remember me option.
            request.session.set_expiry(0)

        user = authenticate(username=email_address, password=password)
        if user:
            login(request, user)
            return redirect('newsapp:mainpage')
        else:
            context = {
                "message": "Oops! There's an issue with your credentials!"}
            return render(request, "newsapp/login.html", context)

    return render(request, "newsapp/login.html", {})


def auth_logout(request):
    logout(request)
    return redirect('newsapp:auth_login')


def browse_category(request, category_value):
    print(category_value)
    articles = Article.objects.filter(
        article_category__icontains=category_value)
    print(articles)
    return render(request, "newsapp/mainpage.html", {"articles": articles})


def like_article(request):
    if not request.user.is_authenticated:
        response = {"message": "Please login to like this article."}
        return HttpResponse(json.dumps(response), content_type="application/json")

    user = User.objects.get(id=int(request.user.pk))
    article_id = request.GET.get('article_id', None)
    article = Article.objects.get(id=int(article_id))
    liked = Article.objects.filter(article_likes__id=user.pk)

    if(article not in liked):
        user.article_likes.add(article)
    else:
        user.article_likes.remove(article)

    response = {"article": serializers.serialize("json", [article, ]), }
    return HttpResponse(json.dumps(response), content_type="application/json")


def create_account(request):
    if request.method == "POST" and "create_account" in request.POST:
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email_address = request.POST["email_address"]
        password = request.POST["password"]
        date_of_birth = request.POST["date_of_birth"]

        # Creating User model and a profile for this user.

        # Checking if an account already created with the email.

        if User.objects.filter(username=email_address).exists():
            context = {"message": "Error creating account. Email already used."}
            return render(request, "newsapp/registration.html", context)

        new_user = User.objects.create_user(
            username=email_address,
            email=email_address,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        new_profile = Profile.objects.create(
            user=new_user, date_of_birth=date_of_birth)

        # Sending a welcome email to the user.
        send_register_email(email_address, first_name)

    context = {"message": "Account created successfully!"}
    return render(request, "newsapp/registration.html", context)

    return render(request, "newsapp/registration.html", {})


def profile(request):
    if not request.user.is_authenticated:
        return redirect('newsapp:auth_login')

    profile = Profile.objects.get(user=request.user.pk)

    print(profile.picture.name)
    print()

    if request.method == "POST" and "delete_picture" in request.POST:
        if profile.picture:
            previous_image = os.path.join(
                settings.MEDIA_ROOT, profile.picture.name)
            if os.path.exists(previous_image):
                os.remove(previous_image)

    if request.method == "POST" and "new_picture" in request.POST:
        if "my-file-selector" in request.FILES:
            if profile.picture:
                previous_image = os.path.join(
                    settings.MEDIA_ROOT, profile.picture.name)
                if os.path.exists(previous_image):
                    os.remove(previous_image)

            new_picture = request.FILES["my-file-selector"]
            profile.picture = new_picture
            profile.save(update_fields=['picture'])

    unique_categories = Article.objects.all().values_list(
        'article_category', flat=True).distinct()
    context = {"profile": profile, "unique_categories": unique_categories}
    return render(request, "newsapp/profile.html", context)


def update_categories(request):
    new_categories = request.GET.getlist('new_categories[]', None)
    new_categories = ','.join(new_categories)
    Profile.objects.filter(user=request.user.pk).update(
        favourite_category=new_categories)
    response = {"message": "Your category has been updated successfully!"}
    return HttpResponse(json.dumps(response), content_type="application/json")


def send_register_email(emailTo, name):
    print("SENDING EMAIL TO: " + emailTo)

    message = 'Dear ' + name + ' ,'\
        '\n\nWelcome to the greatest UK News App. You can find all the latest updates right here!\n\nRegards,\nHuzefa & Jeevan'

    send_mail('Thank you for registering to UK News App!', message,
              settings.EMAIL_HOST_USER, [emailTo], fail_silently=False,)
