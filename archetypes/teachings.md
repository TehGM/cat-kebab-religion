+++
# The title of the daily teaching.
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
date = {{ .Date }}
draft = true
# A short one-line summary shown on lists and used for meta description.
summary = ''
tags = []
+++

<!--
  The teaching (LLM-generated article body) goes here as Markdown.
  Custom inline components are invoked via shortcodes, e.g. {{%/* verse */%}} ... {{%/* /verse */%}}
-->
