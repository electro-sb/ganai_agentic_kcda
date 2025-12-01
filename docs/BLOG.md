---
layout: page
title: Blog
permalink: /blog/
---

# Project Blog

{% for post in site.posts %}
- [{{ post.title }}]({{ post.url }}) <br>
  {{ post.date | date: "%Y-%m-%d" }}
{% endfor %}
