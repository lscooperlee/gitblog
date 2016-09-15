from django.shortcuts import redirect, get_object_or_404, get_list_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import views as auth_views
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

import glob
import os
import pypandoc

setting={
    "title":"Create or Die",
    "subtitle":""
}

def read_all(filename = None):
    allfiles=[]

    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

    if not filename:
        allfiles = glob.glob("{}/blogs/*/*.markdown".format(SITE_ROOT))
        allfiles.sort(key = os.path.getmtime)

    alllist=[]

    pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments"]

    for f in allfiles:
        print(f)
        entry={}
        body_html = pypandoc.convert(source=f, to="html5", extra_args=pdoc_args)
        
        entry["body_html"] = body_html
        alllist.append(entry)

    return alllist


def gitblog_index(request):

    all_list = read_all()

    paginator=Paginator(all_list,10)
    page=request.GET.get('page')
    try:
        entry_list=paginator.page(page)
    except PageNotAnInteger:
        entry_list=paginator.page(1)
    except EmptyPage:
        entry_list=paginator.page(paginator.num_pages)

    c = {"entry_list": entry_list,
         "setting": setting,
        }
    return render(request, "gitblog/gitblog_index.html", c)

#
#def cblog_entry(request, slug):
#    try:
#        entry=Entry.objects.get(id=id)
#        comments=Comment.objects.filter(entry=entry)
#    except:
#        raise Http404()
#
#    commentform=CommentForm()
#    c = {
#            "entry": entry,
#            "commentform":commentform,
#            "comment_list":comments,
#            "category_list": Category.objects.all(),
#            "setting": setting,
#        }
#    return render(request, "cblog/cblog_entry.html", c)
#
#
#
#def cblog_category(request, category_id=None):
#    if category_id:
#        category_list=get_list_or_404(Category, id=category_id)
#    else:
#        category_list=Category.objects.all()
#
#    category_info_list=[]
#    for c in category_list:
#        if  request.user.is_authenticated():
#            cate_info={'category':c, 'entries':Entry.objects.filter(categories=c)}
#        else:
#            cate_info={'category':c, 'entries':Entry.objects.filter(categories=c, isdraft=False)}
#        category_info_list.append(cate_info)
#
#    reqcontext={
#                    "category_list":category_info_list,
#                    "setting":setting
#                }
#    return render(request, "cblog/cblog_category.html",reqcontext)
#
#def cblog_datelist_article(request, year=None):
#    if year:
#        if request.user.is_authenticated():
#            datelist=[{'year': year, 'entries':get_list_or_404(Entry, pub_date__year=year)}]
#        else:
#            datelist=[{'year': year, 'entries':get_list_or_404(Entry, pub_date__year=year,isdraft=False)}]
#
#    else:
#        datelist=[]
#        if request.user.is_authenticated():
#            dates=Entry.objects.all().datetimes('pub_date','year', order='DESC')
#        else:
#            dates=Entry.objects.filter(isdraft=False).datetimes('pub_date','year', order='DESC')
#
#        for d in dates:
#            entrylist=Entry.objects.filter(pub_date__year=d.year)
#            datedict={}
#            if entrylist:
#                datedict['year']=d.year
#                datedict['entries']=entrylist
#                datelist.append(datedict)
#
#    reqcontext={
#        "article_year_list": datelist,
#        "setting":setting
#    }
#    return render(request, "cblog/cblog_articlelist.html",reqcontext)
#
#
