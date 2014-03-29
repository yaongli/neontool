from django.shortcuts import render
from django.views.generic import ListView
from .models import CvsHistory, Engineer, Jira
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render_to_response
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger

# Create your views here.

RECORDS_PER_PAGE = 10
RECORDS_PER_LISTPAGE = 50

def get_page(objs, page, perpage=RECORDS_PER_LISTPAGE):
    paginator = Paginator(objs, perpage)

    try:
        ret = paginator.page(page)
    except (EmptyPage, InvalidPage):
        ret = paginator.page(paginator.num_pages)

    return ret

def getEngineerMap():
    # Add in a QuerySet
    EngineerList = Engineer.objects.all()
    EngineerMap = {}
    for engineer in EngineerList:
        cvs_name = engineer.cvs_name
        EngineerMap[cvs_name] = engineer.name

    return EngineerMap

def add_page_range_to_context(context, show_pages=10):
    page_obj = context['page_obj']
    current_page = page_obj.number
    print current_page
    total_pages = page_obj.paginator.num_pages
    print total_pages
    show_page_range = range(1, show_pages + 1)
    if total_pages <= show_pages:
        show_page_range = range(1, total_pages+1)
    else:
        if current_page <= (show_pages / 2):
            show_page_range = range(1, show_pages+1)
        elif current_page > total_pages - (show_pages / 2):
            show_page_range = range(total_pages - show_pages, total_pages+1)
        else:
            show_page_range = range(current_page - (show_pages / 2), current_page + (show_pages / 2))

    context['show_page_range'] = show_page_range
    context['page_obj'] = page_obj

class CvsHistoryList(ListView):
    model = CvsHistory
    paginate_by = 50
    template_name = 'cvs_history/cvshistory_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CvsHistoryList, self).get_context_data(**kwargs)
        # Add in a QuerySet
        context['engineer_map'] = getEngineerMap()
        add_page_range_to_context(context)
        return context

class CvsHistoryAuthorList(ListView):
    model = CvsHistory
    template_name = 'cvs_history/cvshistoryauthor_list.html'

    def get_queryset(self):
        author = self.args[0]
        try:
            page = int(self.args[1])
        except:
            page = 1
        return get_page(CvsHistory.objects.filter(author=author), page)

class LastTenJiraView(View):

    def get(self, request, *args, **kwargs):
        try:
            page = int(self.args[0])
        except:
            page = 1
        #print "class LastTenJiraView(View): page=", page
        tempResult = get_page(Jira.objects.all(), page, 10)
        #print "len(result)=", len(tempResult)

        LastTenJiraList = []
        for item in tempResult.object_list:
            jiraId = str(item.name)
            #print jiraId
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
            tempResult.object_list = LastTenJiraList

        return render_to_response('cvs_history/jira_list.html',
                                  {'jiraList': tempResult,
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