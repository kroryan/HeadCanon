import pywikibot
from pywikibot import i18n

site = pywikibot.Site()

site.login()

msg = "removing /Legends from page title"

for page in site.allpages('!', '',0):
    if page.title()[-8:] == '/Legends':
        old_title = page.title()
        new_title = old_title[:-8]

        pywikibot.output('Moving page [[{}]] to [[{}]]'.format(old_title, new_title))
        page.move(new_title, reason=msg, noredirect=True)
