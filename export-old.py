from pysword.modules import SwordModules
modules = SwordModules('WLC.zip')
found_modules = modules.parse_modules()
bible = modules.get_bible_from_module('WLC')
output = bible.get(books=['micah'])
with open('micah.txt','w') as file:
    file.write(output)