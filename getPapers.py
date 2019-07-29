import os
import sys


if len(sys.argv) <= 1:
    sys.exit(0)

seedUrl = sys.argv[1]

if not os.path.exists('crawledData'):
    os.makedirs('crawledData')

os.system('rm crawledData/pubUrls.json')
os.system('rm -rf papers')
os.system('scrapy crawl example -o crawledData/pubUrls.json -a seedUrl=' + seedUrl)
os.system('python downloadScripts/downloadPdf.py')
