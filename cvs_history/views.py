from django.shortcuts import render
from django.views.generic import ListView
from .models import CvsHistory
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render_to_response

# Create your views here.


class CvsHistoryList(ListView):
    model = CvsHistory


class CvsHistoryAuthorList(ListView):
    model = CvsHistory

    def get_queryset(self):
        author = self.args[0]
        return CvsHistory.objects.filter(author=author)



class LastTenJiraView(View):

    def get(self, request, *args, **kwargs):
        tempResult =  CvsHistory.objects.raw('select id, jira, updatetime from cvs_history group by jira order by updatetime desc limit 0, 10');
        LastTenJiraList = []
        for item in tempResult:
            jiraId = str(item.jira)
            Jira = {}
            Jira['id'] = jiraId.upper()
            jiraItems =  CvsHistory.objects.filter(jira=jiraId)
            jiraAuthors = []
            jiraFiles = []
            jiraLastUpdate = None
            jiraFirstUpdate = None
            for jiraItem in jiraItems:
                author = jiraItem.author
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
            LastTenJiraList.append(Jira)

        return render_to_response('cvs_history/jira_list.html', {'jiraList': LastTenJiraList})


