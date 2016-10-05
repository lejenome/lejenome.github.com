#!/bin/env python3

import os
import json
from datetime import datetime
from jinja2 import Template
import markdown

posts = None
tmpl = None
md = markdown.Markdown(output_format="html5",
                       extensions=["markdown.extensions.fenced_code",
                                   "markdown.extensions.codehilite"])
MAX_POSTS = 5

with open("posts.json") as posts_file:
    posts = json.load(posts_file)["files"]
with open(os.path.join(os.path.dirname(__file__), "post.html")) as tmpl_file:
    tmpl = Template(tmpl_file.read())

def load_post(post, index):
    post_file = open(post["url"])
    post["title"] = post_file.readline()[:-1]
    post_file.readline()
    post["body"] = md.convert(post_file.read())
    post["date"] = datetime.strptime(post["date"], "%Y/%m/%d").strftime(
        "%a %b %d %Y")
    post["index"] = index
    if index + 1 < len(posts):
        post["newer"] = posts[index + 1]['id']
    if index > 0:
        post["older"] = posts[index - 1]["id"]
    post_file.close()
    post["full_path"] = os.path.join("post", '.'.join([
        os.path.splitext(os.path.basename(post["url"]))[0], "html"]))
    post["min_path"] = os.path.join(
        "post", '.'.join([str(post["id"]), "html"]))

def load_posts():
    for index, post in enumerate(posts):
        load_post(post, index)

def gen_posts():
    for post in posts:
        page_data = {"index": post["index"]}
        if "newer" in post:
            page_data["newer"] = post["newer"]
        if "older" in post:
            page_data["older"] = post["older"]
        post_html = open(post["min_path"], "w")
        html = tmpl.render(posts=[post], page=page_data, page_type="post")
        post_html.write(html)
        try:
            os.symlink(post["min_path"], post["full_path"])
        except FileExistsError:
            pass

def gen_pages():
    posts_r = list(reversed(posts))
    for i in range(0, len(posts), MAX_POSTS):
        index = (i // 4) + 1
        page_posts = posts_r[i: i + MAX_POSTS]
        page_data = {"index": index}
        if i + MAX_POSTS < len(posts_r):
            page_data["older"] = str(index + 1)
        if i > 0:
            page_data["newer"] = str(index - 1)
        page_html = open(os.path.join("page", str(index) + ".html"), "w")
        html = tmpl.render(posts=page_posts, page=page_data, page_type="page")
        page_html.write(html)
    try:
        os.symlink("page/1.html", "page/index.html")
    except FileExistsError:
        pass
    try:
        os.symlink("page/1.html", "index.html")
    except FileExistsError:
        pass

if __name__ == "__main__":
    load_posts()
    gen_posts()
    gen_pages()