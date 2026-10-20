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
  updated = 2026-10-20
  title = "Today's Litany"
  style = "dark"
  lines = [
    { lead = "Cat upon the kebab", text = "ride for us.", strong = true },
    { lead = "The ticket, folded small", text = "stay folded.", strong = true },
    { lead = "The coat, hung on its hook", text = "keep the pocket.", strong = true },
    { lead = "The journey, already made", text = "be remembered.", strong = true },
  ]

[[panels]]
  id = "signs"
  updated = 2026-10-19
  title = 'Signs & Wonders This Week'
  lines = [
    { text = "One (1) kitten, chest-deep, not asked to finish" },
    { text = "Two (2) wraps, one inverted, no complaint filed" },
    { text = "One (1) crossing button, worn smooth at the one spot" },
    { text = "One (1) stool, facing the wall, by no ruling" },
  ]

[[panels]]
  id = "calendar"
  updated = 2026-10-20
  title = 'Calendar of Feasts'
  style = 'gold'
  lines = [
    { lead = "Tue", text = "the Folded Ticket" },
    { lead = "Thu", text = "the Kept Lid" },
    { lead = "Sat", text = "the Held Door" },
  ]
  note = 'loose, but in order'
+++
