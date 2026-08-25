{{- /* Filenames are date-prefixed (2026-08-25-slug.md) so a repeated slug can
       never overwrite an older teaching. The prefix is for the filesystem only:
       `slug` strips it back off, so the URL reads /teachings/2026-08-25/slug/
       rather than repeating the date. */ -}}
{{- $slug := replaceRE `^\d{4}-\d{2}-\d{2}-` "" .File.ContentBaseName -}}
+++
title = '{{ replace $slug "-" " " | title }}'
# The last segment of the URL. Keep it set, or the date lands in it twice.
slug = '{{ $slug }}'
date = {{ .Date }}
draft = true
# Shown on the homepage and in the archive. One or two sentences.
summary = ''
# The italic line under the title. Optional.
standfirst = ''
# A filename from assets/img/cat/ — see data/images.toml, whose `depicts` and
# `keywords` describe every image, for choosing one. Leave it out and the
# teaching has no picture, which is allowed but not how these are usually done.
# image = 'Screenshot_62.png'
caption = ''
seal = 'Vibes confirmed'
# feast = 'Feast of the Rooster'
# note = 'a handwritten aside at the foot'
tags = []
+++

Open here. The first paragraph takes an illuminated initial automatically.

<!--
  Article components — use only where the writing calls for one. See the README.
  {{</* part num="I" title="Of the Honking" */>}}
  {{%/* pullquote */%}} … {{%/* /pullquote */%}}
  {{</* scripture cite="From the Book of Wraps, IV" */>}} … {{</* /scripture */>}}
  {{%/* testimony by="Sr. Halina" */%}} … {{%/* /testimony */%}}
  {{</* doctrine */>}}Name | gloss{{</* /doctrine */>}}
  {{</* litany label="Said together" */>}}Call | response{{</* /litany */>}}
  {{%/* marginnote note="…" */%}} … {{%/* /marginnote */%}}
  {{</* practice do="…" avoid="…" */>}}
  {{%/* decree */%}} … {{%/* /decree */%}}
  {{%/* commentary */%}} … {{%/* /commentary */%}}
-->
