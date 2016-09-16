from django.shortcuts import redirect, get_object_or_404, get_list_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import views as auth_views
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.utils.text import slugify

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

def read_file(filename):
    content=""

    with open(filename,'r') as f:
        try:
            content=f.read()
        except UnicodeDecodeError:
            return ""

    if not content:
        return ""

    return content

def get_markdown_title(filename):
    with open(filename,'r') as f:
        return extract_markdown_title(f.read())

def extract_markdown_title(content):
    for l in content.splitlines():
        l=l.strip()
        if l.startswith("#"):
            return l.strip("#")

    return "undefined"

def get_slug(filename):
    return filename.split(os.path.sep)[-1]


def gen_markdown_content(filename, content, cache_dir = "/tmp/gitblog"):
    pdoc_args = ["--mathjax", "--highlight-style", "pygments"]
    #pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments"]

    entry={}

    entry['slug'] = get_slug(filename)

    body_html = pypandoc.convert_text(source=content, format = "markdown", to="html5", extra_args=pdoc_args)

    entry["body_html"] = body_html
    entry["pub_date"] = datetime.fromtimestamp(os.path.getmtime(filename))
    entry["author"] = "me"
    entry["title"] = extract_markdown_title(content)

    return entry

def content_decorator_image_filter(*args, **kwargs):

    substr = "/media/gitblog/"
    def decor(content):
        p=re.compile(r'(?P<id>!\[.*\])\((?P<url>.*?)(\)|\s+.*\))')
        ret=p.findall(content)
        file_list=[ x[1] for x in ret if not re.match(r'^https?://',x[1])]

        for i in file_list:
            newname=os.path.join(substr, i)
            content=content.replace(i, newname)

        return content

    return decor

def file_decorator_page_filter(*args, **kwargs):

    page_num = 1
    article_num = 10

    def decor(file_list):
        file_list.sort(key = os.path.getmtime, reverse = True)

        if article_num == 0:
            return file_list

        if len(file_list) > page_num*article_num:
            file_list = file_list[(page_num-1) * article_num : page_num*article_num]
        elif len(file_list) > (page_num - 1) * article_num:
            file_list = file_list[(page_num-1) * article_num :]
        else:
            file_list = []

        return file_list

    return decor

def get_recent_articles(articlenum = 5):

    blog_dirs = [BLOG_DIR]
    file_list = [ os.path.join(p, f) for p in blog_dirs
                    for f in os.listdir(p)
                    if os.path.isfile(os.path.join(p, f)) ]

    latest_articles = [{"title": get_markdown_title(f), "slug": get_slug(f)}
            for f in file_list]

    return latest_articles


FILE_DECORATORS = [file_decorator_page_filter]
CONTENT_DECORATORS = [content_decorator_image_filter]

def gitblog_index(request, *args, **kwargs):

    article_num = 5
    page_num = kwargs['page_num']

    blog_dirs = [BLOG_DIR]
    file_list = [ os.path.join(p, f) for p in blog_dirs
                    for f in os.listdir(p)
                    if os.path.isfile(os.path.join(p, f)) ]

    for Decorator in FILE_DECORATORS:
        decor = Decorator(args, kwargs)
        file_list = decor(file_list)

    entry_list = []
    for f in file_list:
        c = read_file(f)
        for Decorator in CONTENT_DECORATORS:
            decor = Decorator(args, kwargs)
            c = decor(c)

        entry_list.append(gen_markdown_content(f, c))

    total_page = (math.ceil(len(entry_list) / article_num))
    page = {
            "total" : str(total_page),
            "current" : page_num,
            "pages" : [str(i) for i in range(1, total_page + 1)],
            }

    c = {
            "entry_list" : entry_list,
            "recent_posts" : get_recent_articles(),
            "page" : page,
        }

    return render(request, "gitblog/gitblog_index.html", c)


def gitblog_entry(request, slug):
    try:
        filename = BLOG_DIR + slug
        c = read_file(filename)
        for Decorator in CONTENT_DECORATORS:
            decor = Decorator(args, kwargs)
            c = decor(c)

        entry = gen_markdown_content(filename, c)
    except:
        raise Http404()

    e = {
            "entry": entry,
            "recent_posts": get_recent_articles(),
        }

    return render(request, "gitblog/gitblog_entry.html", e)
