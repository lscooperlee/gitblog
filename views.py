from django.shortcuts import render

from django.http import Http404
from django.conf import settings

import os
import pypandoc
import re
import math
import functools
from datetime import datetime

setting = {
    "title": "Create or Die",
    "subtitle": ""
}

SITE_ROOT = settings.MEDIA_ROOT
BLOG_DIR = "{}/gitblog/".format(settings.MEDIA_ROOT)


class Cache:

    def __init__(self):
        self._cache = {}

    def get(self, key, condition, action):
        try:
            oldcond, oldcontent = self._cache[key]
            if not condition or condition > oldcond:
                self._cache[key] = condition, action()
        except:
            self._cache[key] = condition, action()

        _, content = self._cache[key]
        return content


contentCache = Cache()


def read_file(filename):
    content = ""

    with open(filename, 'r') as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            return ""

    if not content:
        return ""

    return content


def get_markdown_title(filename):
    with open(filename, 'r') as f:
        return extract_markdown_title(f.read())


def extract_markdown_title(content):
    for l in content.splitlines():
        l = l.strip()
        if l.startswith("#"):
            return l.strip("#")

    return "undefined"


def get_slug(filename):
    return os.path.basename(filename)


def gen_markdown_content(filename, content):
    extradir = os.path.splitext(filename)[0]
    bibfile = "{0}/bib.bib".format(extradir)

    pdoc_args = ["--mathjax", "--highlight-style", "pygments",
                 "--filter=pandoc-eqnos",
                 "--filter=pandoc-fignos"]

    # pdoc_args = ["-s"] # for stand alone css style file

    if os.path.exists(bibfile):
        pdoc_args += ["--bibliography={0}".format(bibfile),
                      "--filter=pandoc-citeproc"]

    entry = {}

    entry['slug'] = get_slug(filename)
    body_html = pypandoc.convert_text(source=content,
                                      format="markdown",
                                      to="html5",
                                      extra_args=pdoc_args)

    entry["body_html"] = body_html
    entry["pub_date"] = datetime.fromtimestamp(os.path.getmtime(filename))
    entry["author"] = "me"
    entry["title"] = extract_markdown_title(content)

    return entry


def get_cached_content(filename, content):
        key = filename
        condition = os.path.getmtime(filename)
        action = functools.partial(gen_markdown_content, filename, content)

        return contentCache.get(key, condition, action)


def content_decorator_image_filter(*args, **kwargs):

    substr = "/media/gitblog/"

    def decor(content):
        p = re.compile(r'(?P<id>!\[.*\])\((?P<url>.*?)(\)|\s+.*\))')
        ret = p.findall(content)
        file_list = [x[1] for x in ret if not re.match(r'^https?://', x[1])]

        for i in file_list:
            newname = os.path.join(substr, i)
            content = content.replace(i, newname)

        return content

    return decor


def file_decorator_createtime_filter(*args, **kwargs):

    def decor(file_list):
        file_list.sort(key=os.path.getmtime, reverse=True)
        return file_list

    return decor


def file_decorator_markdown_filter(*args, **kwargs):

    def decor(file_list):
        return [f for f in file_list
                if f.endswith(".markdown") or f.endswith(".md")]

    return decor


def file_decorator_page_filter(*args, **kwargs):

    def decor(file_list):
        article_num = int(kwargs['article_num'])

        if article_num == 0:
            return file_list

        page_num = int(kwargs['page_num'])

        if len(file_list) > page_num * article_num:
            file_list = file_list[(page_num-1) * article_num:
                                  page_num * article_num]
        elif len(file_list) > (page_num - 1) * article_num:
            file_list = file_list[(page_num-1) * article_num:]
        else:
            file_list = []

        return file_list

    return decor


def file_decorator_login_filter(request, *args, **kwargs):

    def decor(file_list):
        if request.user.is_authenticated():
            return file_list
        else:
            return [f for f in file_list
                    if not os.path.basename(f).startswith("_")]

    return decor


FILE_DECORATORS = [file_decorator_createtime_filter,
                   file_decorator_login_filter,
                   file_decorator_markdown_filter,
                   file_decorator_page_filter]
CONTENT_DECORATORS = [content_decorator_image_filter]


def get_recent_articles(request, **kwargs):

    if 'article_num' not in kwargs:
        kwargs['article_num'] = 0

    blog_dirs = [BLOG_DIR]
    file_list = [os.path.join(p, f) for p in blog_dirs for f in os.listdir(p)
                 if os.path.isfile(os.path.join(p, f))]

    for Decorator in FILE_DECORATORS:
        decor = Decorator(request, **kwargs)
        file_list = decor(file_list)

    latest_articles = [{"title": get_markdown_title(f), "slug": get_slug(f)}
                       for f in file_list]

    return latest_articles


def gitblog_index(request, **kwargs):

    if 'article_num' not in kwargs:
        kwargs['article_num'] = 5

    if 'page_num' not in kwargs:
        kwargs['page_num'] = 1

    blog_dirs = [BLOG_DIR]
    file_list = [os.path.join(p, f) for p in blog_dirs for f in os.listdir(p)
                 if os.path.isfile(os.path.join(p, f))]

    # Wrong, FIX ME
    total_page = (math.ceil(len(file_list) / kwargs['article_num']))

    for Decorator in FILE_DECORATORS:
        decor = Decorator(request, **kwargs)
        file_list = decor(file_list)

    entry_list = []
    for f in file_list:
        c = read_file(f)
        for Decorator in CONTENT_DECORATORS:
            decor = Decorator(request, **kwargs)
            c = decor(c)

        entry_list.append(get_cached_content(f, c))

    page = {
            "total": str(total_page),
            "current": kwargs['page_num'],
            "pages": [str(i) for i in range(1, total_page + 1)],
            }

    c = {
            "entry_list": entry_list,
            "recent_posts": get_recent_articles(request),
            "page": page,
        }

    return render(request, "gitblog/gitblog_index.html", c)


def gitblog_entry(request, slug):
    try:
        filename = BLOG_DIR + slug
        c = read_file(filename)
        for Decorator in CONTENT_DECORATORS:
            decor = Decorator()
            c = decor(c)

        entry = get_cached_content(filename, c)
    except:
        raise Http404()

    e = {
            "entry": entry,
            "recent_posts": get_recent_articles(request),
        }

    return render(request, "gitblog/gitblog_entry.html", e)
