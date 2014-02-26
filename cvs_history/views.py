from django.shortcuts import render
from django.views.generic import ListView
from .models import CvsHistory

# Create your views here.
class CvsHistoryList(ListView):
    model = CvsHistory


