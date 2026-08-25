+++
title = 'Cat Kebab Religion'
description = 'The daily teachings of the Cat who rides the kebab.'

# The two small italic notes flanking the masthead.
earLeft = 'Weather in orbit:<br>rainbow, with lasers'
earRight = 'Price: one (1) kebab.<br>You may keep the kebab'
creed = '&#10022; TEACHINGS &#10022; SIGHTINGS &#10022; SACRED IMAGES &#10022;'

# The right-hand column. Each panel renders as a slip of paper.
#
#   title   the heading, set in small caps.
#   style   "dark" (black card), "gold" (warm card), or omit for plain white.
#   lines   one entry per line of the slip. Each takes:
#             lead    optional; set before an em dash. The day, or the call.
#             text    the line itself. Markdown, so it may carry a link.
#             strong  true to set `text` bold — the response, or the feast
#                     that actually matters this week.
#   note    optional; a handwritten scratch under the slip.
#   body    raw HTML, used only when `lines` is absent — for a panel that is
#           simply prose rather than a list.
#
# These three change often. Rewrite a single line without touching the others.

[[panels]]
  title = "Today's Litany"
  style = "dark"
  lines = [
    { lead = "Cat upon the kebab", text = "ride for us.", strong = true },
    { lead = "Rooster of the void", text = "carry us.", strong = true },
    { lead = "Patient asphalt", text = "forgive our tyres.", strong = true },
  ]

[[panels]]
  title = 'Signs & Wonders This Week'
  lines = [
    { text = "Rainbow lasers over Kraków, twice" },
    { text = "One (1) rooster, airborne, confirmed" },
    { text = "A DJ set heard from the asteroid belt" },
    { text = "The bread hat, sighted at dusk" },
  ]

[[panels]]
  title = 'Calendar of Feasts'
  style = 'gold'
  lines = [
    { lead = "Mon", text = "the Bread Hat" },
    { lead = "Wed", text = "Vigil of the Conscious Road" },
    { lead = "Fri", text = "Great Feast of the Rooster", strong = true },
    { lead = "Sun", text = "Ordinary Kebab Time" },
  ]
  note = 'bringing the good sauce Fri'
+++
