+++
title = 'Cat Kebab Religion'
description = 'The daily teachings of the Cat who rides the kebab.'

# The two small italic notes flanking the masthead.
earLeft = 'Weather in orbit:<br>rainbow, with lasers'
earRight = 'Price: one (1) kebab.<br>You may keep the kebab'
creed = '&#10022; TEACHINGS &#10022; SIGHTINGS &#10022; SACRED IMAGES &#10022;'

# The right-hand column. Each panel renders as a slip of paper.
#
#   id      what the slip is, for the daily writer: "litany", "signs" or
#           "calendar". Not rendered.
#   updated the day the slip was last rewritten. Not rendered; the writer
#           and scripts/teaching.py use it to tell what is due.
#   title   the heading, set in small caps.
#   style   "dark" (black card), "gold" (warm card), or omit for plain white.
#   lines   one entry per line of the slip. Each takes:
#             lead    optional; set before an em dash. The day, or the call.
#             text    the line itself. Markdown, so it may carry a link.
#             strong  true to set `text` bold — the response, or the feast
#                     that matters most this week.
#   note    optional; a handwritten scratch under the slip.
#   body    raw HTML, used only when `lines` is absent — for a panel that is
#           simply prose rather than a list.
#
# These change often, on a fixed rhythm: the litany daily, the calendar daily
# (written from data/calendar.toml; it opens with today, unless today has
# nothing on), Signs & Wonders every Monday. Rewrite a single line without
# touching the others.

[[panels]]
  id = "litany"
  updated = 2026-11-27
  title = "Today's Litany"
  style = "dark"
  lines = [
    { lead = "Cat upon the kebab", text = "ride for us.", strong = true },
    { lead = "The rooster, not asked", text = "carry on.", strong = true },
    { lead = "The look, four seconds long", text = "be kept in the drawer.", strong = true },
    { lead = "The comb, seen from below", text = "be thanked once.", strong = true },
  ]

[[panels]]
  id = "signs"
  updated = 2026-11-24
  title = 'Signs & Wonders This Week'
  lines = [
    { text = "One (1) name, called three times from the hall, noted on the landing, not answered" },
    { text = "One (1) tin, opened in the kitchen, answered from the far end of the house in four seconds" },
    { text = "One (1) drawer, shut and not opened, awaiting its day" },
    { text = "One (1) sunbeam, due Thursday, already on the floor and being stood beside" },
    { text = "One (1) rainbow, still attending, still not told" },
  ]

[[panels]]
  id = "calendar"
  updated = 2026-11-27
  title = 'Calendar of Feasts'
  style = 'gold'
  lines = [
    { lead = "Sat", text = "the Attending Rainbow" },
    { lead = "Mon", text = "the Folded Napkin" },
    { lead = "Thu", text = "the Cold Cup" },
  ]
  note = 'one more, for the end'
+++
