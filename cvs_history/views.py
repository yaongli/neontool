from django.shortcuts import render
from django.views.generic import ListView
from .models import CvsHistory, Engineer, Jira
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render_to_response

# Create your views here.

def getEngineerMap():
    # Add in a QuerySet
    EngineerList = Engineer.objects.all()
    EngineerMap = {}
    for engineer in EngineerList:
        cvs_name = engineer.cvs_name
        EngineerMap[cvs_name] = engineer.name

    return EngineerMap

class CvsHistoryList(ListView):
    model = CvsHistory

    def get_queryset(self):
        return CvsHistory.objects.all()[0:100]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CvsHistoryList, self).get_context_data(**kwargs)
        # Add in a QuerySet
        context['engineer_map'] = getEngineerMap()
        return context

class CvsHistoryAuthorList(ListView):
    model = CvsHistory

    def get_queryset(self):
        author = self.args[0]
        return CvsHistory.objects.filter(author=author)[0:100]

class LastTenJiraView(View):

    def get(self, request, *args, **kwargs):
        tempResult = Jira.objects.all()[0:10];

        LastTenJiraList = []
        for item in tempResult:
            jiraId = str(item.name)
            jira = {}
            jira['id'] = jiraId.upper()
            jiraItems = CvsHistory.objects.filter(jira=jiraId)
            jiraFiles = []

            for jiraItem in jiraItems:
                file = jiraItem.file
                if file not in jiraFiles:
                    jiraFiles.append(file)

            jiraFiles.sort()
            jira['author'] = item.author
            jira['files'] = jiraFiles
            jira['lastUpdate'] = item.first_update
            jira['firstUpdate'] = item.last_update
            LastTenJiraList.append(jira)

        return render_to_response('cvs_history/jira_list.html',
                                  {'jiraList': LastTenJiraList,
                                   'engineer_map': getEngineerMap()
                                  })

class JiraList(ListView):
    model = Jira
    template_name = 'cvs_history/jiralist_list.html'

    def get_queryset(self):
        return Jira.objects.all()[0:100]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JiraList, self).get_context_data(**kwargs)
        context['engineer_map'] = getEngineerMap()
        return context

class JiraView(View):
    """
    Query a jira info
    """
    def get(self, request, *args, **kwargs):
        jira_id = args[0]
        EngineerList = Engineer.objects.all()
        EngineerMap = {}
        for engineer in EngineerList:
            cvs_name = engineer.cvs_name
            EngineerMap[cvs_name] = engineer

        Jira = {}
        Jira['id'] = jira_id.upper()
        jiraItems =  CvsHistory.objects.filter(jira=jira_id)
        jiraAuthors = []
        jiraFiles = []
        jiraLastUpdate = None
        jiraFirstUpdate = None
        for jiraItem in jiraItems:
            author = jiraItem.author
            if EngineerMap.has_key(author):
                author = EngineerMap[author].name
            if author not in jiraAuthors:
                jiraAuthors.append(author)
            file = jiraItem.file
            if file not in jiraFiles:
                jiraFiles.append(file)
            updateTime = jiraItem.updatetime
            if jiraLastUpdate == None or jiraLastUpdate < updateTime:
                jiraLastUpdate = updateTime
            if jiraFirstUpdate == None or jiraFirstUpdate > updateTime:
                jiraFirstUpdate = updateTime

        jiraFiles.sort()
        Jira['authors'] = jiraAuthors
        Jira['files'] = jiraFiles
        Jira['lastUpdate'] = jiraLastUpdate
        Jira['firstUpdate'] = jiraFirstUpdate
        return render_to_response('cvs_history/jira_detail.html', {'jira': Jira})