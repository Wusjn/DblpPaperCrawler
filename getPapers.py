import os
import sys


if len(sys.argv) <= 1:
    sys.exit(0)

seedUrl = sys.argv[1]

os.makedirs('crawledData')
os.system('rm crawledData/pubUrls.json')
os.system('scrapy crawl example -o crawledData/pubUrls.json -a seedUrl=' + seedUrl)
os.system('python downloadScripts/downloadPdf.py')
