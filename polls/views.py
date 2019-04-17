"""
    `views.py`
    Contains views of `polls` application
"""

import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from polls.forms import PollForm, CommentForm
from polls.models import Poll, Question, Answer, Comment

def index(request):
    ''' Poll application index page '''
    # Get all `Poll` objects, add `question_count` attribute to each poll
    poll_list = Poll.objects.annotate(question_count=Count('question')).filter(question_count__gt=0)

    context = {
        'page_title': 'My Poll Page',
        'poll_list': poll_list,
    }

    return render(request, template_name='polls/index.html', context=context)

@login_required
@permission_required('polls.view_poll')
def detail(request, poll_id):
    ''' Poll application detail page '''
    poll = Poll.objects.get(pk=poll_id)

    context = {
        'poll': poll
    }

    # Notes: This will only be executed when receive `POST` request.
    if request.method == 'POST':
        for question in poll.question_set.all():
            choice_id = request.POST.get('question_' + str(question.id))

            if (choice_id != None):
                try:
                    answer = Answer.objects.get(question_id=question.id)
                    answer.choice_id = choice_id
                    answer.save()
                except Answer.DoesNotExist:
                    Answer.objects.create(choice_id=choice_id, question_id=question.id)

    return render(request, template_name='polls/detail.html', context=context)

@login_required
@permission_required('polls.add_poll')
def create(request):
    ''' Poll application new poll creation page'''
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = Poll.objects.create(
                title=form.cleaned_data.get('title'),
                start_date=form.cleaned_data.get('start_date'),
                end_date=form.cleaned_data.get('end_date'),
            )

            for i in range(form.cleaned_data.get('question_amount')):
                Question.objects.create(
                    text='Question {:02d}'.format(i + 1),
                    type='01',
                    poll=poll
                )
    else:
        form = PollForm()

    context = {
        'form': form
    }

    return render(request, template_name='polls/create.html', context=context)

@login_required
def comment(request, poll_id):
    ''' Poll application comment page '''
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            comment = Comment.objects.create(
                title=form.cleaned_data.get('title'),
                body=form.cleaned_data.get('body'),
                email=form.cleaned_data.get('email'),
                tel=form.cleaned_data.get('tel')
            )
    else:
        form = CommentForm()

    context = {
        'poll': Poll.objects.get(pk=poll_id),
        'form': form
    }

    return render(request, template_name='polls/comment.html', context=context)

def login_user(request):
    ''' Poll application login page '''
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')

        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Incorrect username or password.'

    next_url = request.GET.get('nexts')
    if (next_url):
        context['next_url'] = next_url

    return render(request, template_name='polls/login.html', context=context)

def logout_user(request):
    ''' Poll application logout '''
    logout(request)
    return redirect('index')

# Non-view functions
def load_data_from_sql(file_name):
    ''' Utility function, executes SQL query from SQL file '''
    file_path = os.path.join(os.path.dirname(__file__), 'sql/', file_name)
    sql_statement = open(file_path).read()

    with connection.cursor() as cursor:
        cursor.execute(sql_statement)
