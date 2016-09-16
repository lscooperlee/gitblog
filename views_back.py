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
import re
import math
from datetime import datetime

setting={
    "title":"Create or Die",
    "subtitle":""
}

SITE_ROOT = settings.MEDIA_ROOT
BLOG_DIR = "{}/gitblog/".format(settings.MEDIA_ROOT)

def parse_local_file(filename, substr):
    content=""

    with open(filename,'r') as f:
        try:
            content=f.read()
        except UnicodeDecodeError:
            return ""

    if not content:
        return ""

    p=re.compile(r'(?P<id>!\[.*\])\((?P<url>.*?)(\)|\s+.*\))')
    ret=p.findall(content)
    file_list=[ x[1] for x in ret if not re.match(r'^https?://',x[1])]

    for i in file_list:
        newname=os.path.join(substr, i)
        content=content.replace(i, newname)

    return content

def extract_markdown_title(filename):
    with open(filename,'r') as f:
        for l in f:
            l=l.strip()
            if l.startswith("#"):
                return l.strip("#")

    return None

def get_slug(filename):
    print(filename)
    return filename.split(os.path.sep)[-1]


def read_markdown_file(filename, cache_dir = "/tmp/gitblog"):
    pdoc_args = ["--mathjax", "--highlight-style", "pygments"]
    #pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments"]

    entry={}

    entry['slug'] = get_slug(filename)
    print("slug ", entry["slug"])

    content = parse_local_file(filename, "/media/gitblog/")

    body_html = pypandoc.convert_text(source=content, format = "markdown", to="html5", extra_args=pdoc_args)

    entry["body_html"] = body_html
    entry["pub_date"] = datetime.fromtimestamp(os.path.getmtime(filename))
    entry["author"] = "me"

    return entry


def get_markdown_filelist(dirname, pagenum = 1, articlenum = 10):
    allfiles=[]

    filelist = "{}/*.markdown".format(dirname)

    allfiles = glob.glob(filelist)
    allfiles.sort(key = os.path.getmtime, reverse = True)

    if articlenum == 0:
        return allfiles

    if len(allfiles) > pagenum*articlenum:
        allfiles = allfiles[(pagenum-1) * articlenum : pagenum*articlenum]
    elif len(allfiles) > (pagenum - 1) * articlenum:
        allfiles = allfiles[(pagenum-1) * articlenum :]
    else:
        allfiles = []

    return allfiles


def read_markdown_files(dirname, pagenum = 1, articlenum = 10):

    allfiles = get_markdown_filelist(dirname, pagenum, articlenum)
    alllist=[ read_markdown_file(f) for f in allfiles ]

    return alllist

def get_recent_articles(dirname, articlenum = 5):
    filelist = get_markdown_filelist(dirname, 1, articlenum)
    print(filelist)
    latest_articles = [{"title": extract_markdown_title(f), "slug": get_slug(f)}
            for f in filelist]

    return latest_articles


def gitblog_index(request, pagenum = 1):

    article_num = 5
    entry_list = read_markdown_files(BLOG_DIR, int(pagenum), article_num)
    article_list = get_recent_articles(BLOG_DIR, 0)

    total_page = (math.ceil(len(article_list) / article_num))
    page = {
            "total" : str(total_page),
            "current" : pagenum,
            "pages" : (str(i) for i in range(1, total_page + 1)),
            }

    c = {
            "entry_list" : entry_list,
            "recent_posts" : article_list,
            "page" : page,
        }
    return render(request, "gitblog/gitblog_index.html", c)


def gitblog_entry(request, slug):
    try:
        entry = read_markdown_file(BLOG_DIR + slug)
        article_list = get_recent_articles(BLOG_DIR, 0)
    except:
        raise Http404()

    c = {
            "entry": entry,
            "recent_posts": article_list,
        }

    return render(request, "gitblog/gitblog_entry.html", c)
