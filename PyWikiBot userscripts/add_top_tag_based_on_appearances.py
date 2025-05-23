import pywikibot
from pywikibot import pagegenerators
from pywikibot import i18n, textlib, pagegenerators
from pywikibot.bot import ExistingPageBot, SingleSiteBot
from pywikibot.tools import chars, deprecated_args
import re

site = pywikibot.Site()

strings_to_find = [
    "==Appearances==\n*''[[Star Wars: The Old Republic]]'' {{1st}} {{Hologram}}\n\n"
]
tag_to_add = "old"
starting_from = "!"

class FinderBot(SingleSiteBot, ExistingPageBot):
    def __init__(self):
        super().__init__()
    
    def replace_text(self, page, find: str, repl: str):
        altered_text = textlib.replaceExcept(page.text, find, repl, [])
        if altered_text != page.text:
            self.userPut(page, page.text, altered_text)
            pywikibot.output("Replacement complete!")
        else:
            pywikibot.output("Top template already has an argument!")

    def find(self):
        for page in site.allpages(starting_from, "", 0):
            for string in strings_to_find:
                if string in page.text:
                    pywikibot.output(page.title())
                    self.replace_text(page, "{{Top}}", "{{Top|" + tag_to_add + "}}")

bot = FinderBot()
site.login()
bot.find()
