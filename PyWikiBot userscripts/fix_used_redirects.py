import pywikibot
from pywikibot import pagegenerators
from pywikibot import i18n, textlib, pagegenerators
from pywikibot.bot import ExistingPageBot, SingleSiteBot
from pywikibot.tools import chars, deprecated_args
import re

site = pywikibot.Site()


class ReplaceBot(SingleSiteBot, ExistingPageBot):
    def __init__(self):
        super().__init__()
    
    def replace_text(self, page, find: str, repl: str):
        altered_text = textlib.replaceExcept(page.text, find, repl, [])
        if altered_text != page.text:
            self.userPut(page, page.text, altered_text)
            pywikibot.output("Replacement complete!")
        else:
            pywikibot.output("No links were found.")

    def fix_broken_redirects(self):
        for broken_redirect in site.broken_redirects():
            redirect_title = broken_redirect.title()
            target_title = re.search("\[\[(.*)\]\]", broken_redirect.text).group(1)
            target_title = target_title.split("|")[0]

            pywikibot.output(redirect_title + " ==> " + target_title)

            find_string = "\=" + re.escape(redirect_title) + "\|"
            repl_string = "=" + target_title + "|"

            for page in broken_redirect.backlinks(False):
                pywikibot.output("Replacing text in page: " + page.title())
                self.replace_text(page, find_string, repl_string)

    def fix_unbroken_redirects(self):
        for redirect in site.redirectpages():
            redirect_title = redirect.title()
            target_title = re.search("\[\[(.*)\]\]", redirect.text).group(1)
            target_title = target_title.split("|")[0]

            pywikibot.output(redirect_title + " == > " + target_title)

            # Optional! Use for finding lowercase links
            #redirect_title = redirect_title[:1].lower() + redirect_title[1:]

            find_string = "\[\[" + re.escape(redirect_title) + "\]\]"
            repl_string = "[[" + target_title + "|" + redirect_title + "]]"

            #find_string = "\[\[" + re.escape(redirect_title) + "\|"
            #repl_string = "[[" + target_title + "|"
                
            for page in redirect.backlinks(False):
                pywikibot.output("Replacing text in page: " + page.title())
                self.replace_text(page, find_string, repl_string)

bot = ReplaceBot()

site.login()
bot.fix_broken_redirects()
bot.fix_unbroken_redirects()
