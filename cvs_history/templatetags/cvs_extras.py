from django import template
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def split(str, splitter=","):
    return str.split(splitter)

@register.filter(is_safe=True)
def cvsauthor(authors, authorMap, seperator="<br/>"):
    htmls = []
    authors = authors.split(",")
    for author in authors:
        html = """<a href="/cvs/%s" target="_blank">""" % author
        authorName = authorMap[author]
        if not authorName:
            authorName = author
        html += authorName
        html += "</a>"
        htmls.append(html)

    result = seperator.join(htmls)
    return mark_safe(result)