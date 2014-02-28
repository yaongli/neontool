from django.shortcuts import render
from django.views.generic import ListView
from .models import CvsHistory

# Create your views here.


class CvsHistoryList(ListView):
    model = CvsHistory


class CvsHistoryAuthorList(ListView):
    model = CvsHistory

    def get_queryset(self):
        author = self.args[0]
        return CvsHistory.objects.filter(author=author)

class JiraAuthorList(ListView):
    model = CvsHistory

    def get_queryset(self):
        author = self.args[0]
        return CvsHistory.objects.filter(author=author)


