#!/usr/bin/env python

import scraperwiki
import requests
import re
import lxml.html
from datetime import datetime
import time

def clean_xml(x):
    x = re.sub(r'<link rel="self" href="/client" />',r'<link href="http://catalog.dclibrary.orghttps//catalog.dclibrary.org/client/rss/hitlist/dcpl/"/>',x)
    x = re.sub(r'rel="alternate" type="html" href="https://catalog.dclibrary.org/client/en_US/dcpl/search/detailnonmodal\?qf=.*ent%3A%2F%2FSD_ILS%2F0%2FSD_ILS%3A(\d+).*',r'href="https://catalog.dclibrary.org/client/en_US/dcpl/search/detailnonmodal/ent:$002f$002fSD_ILS$002f0$002fSD_ILS:\1/ada?"/>',x)
    x = re.sub(r'ent://SD_ILS/0/SD_ILS:(\d+)',r'https://catalog.dclibrary.org/client/en_US/dcpl/search/detailnonmodal/ent:$002f$002fSD_ILS$002f0$002fSD_ILS:\1/ada',x)
    x = re.sub(r'http://catalog.dclibrary.orghttps://catalog.dclibrary.org/client/en_US/dcpl/dcpl/ps\$003d1000\?dt=list',r'http://catalog.dclibrary.orghttps//catalog.dclibrary.org/client/en_US/dcpl/dcpl/ps$003d1000?dt=list',x)
    x = re.sub(r'(\d+)/ada</id>',r'\1/ada</id>\n\t\t<ils>\1</ils>',x)
    return x



formats = ["BOOK%09Books"]
libraries = ["ANACOSTIA%09Anacostia+Neighborhood+Library"]
#,"BENNING%09Dorothy+I.+Height%2FBenning+Neighborhood+Library", "ANACOSTIA%09Anacostia+Neighborhood+Library", "CAP-VIEW%09Capitol+View+Neighborhood+Library", "CHEVYCHASE%09Chevy+Chase+Neighborhood+Library", "CLEVE-PARK%09Cleveland+Park+Neighborhood+Library", "DEANWOOD%09Deanwood+Neighborhood+Library", "FR-GREGORY%09Francis+A.+Gregory+Neighborhood+Library", "SHEPARK-JT%09Juanita+E.+Thornton+%2F+Shepherd+Park+Neighborhood+Library", "LAMD-RIGGS%09Lamond-Riggs+Neighborhood+Library", "ML-KING%09Martin+Luther+King+Jr.+Memorial+Library", "MTPLEASANT%09Mt.+Pleasant+Neighborhood+Library", "NORTHEAST%09Northeast+Neighborhood+Library", "NORTHWEST1%09Northwest+One+Neighborhood+Library", "PALISADES%09Palisades+Neighborhood+Library", "PARKLANDS%09Parklands-Turner+Neighborhood+Library", "PETWORTH%09Petworth+Neighborhood+Library", "ROSEDALE%09Rosedale+Neighborhood+Library", "SCHOOLPBEC%09School+Pilot+Charter+BEC", "SOUTHEAST%09Southeast+Neighborhood+Library", "SOUTHWEST%09Southwest+Neighborhood+Library", "TAKOMA-PK%09Takoma+Park+Neighborhood+Library", "TENLEY%09Tenley-Friendship+Neighborhood+Library", "WT-DANIEL%09Watha+T.+Daniel%2FShaw++Neighborhood+Library", "WESTEND%09West+End+Neighborhood+Library", "BELLEVUE%09William+O.+Lockridge%2FBellevue+Neighborhood+Library", "WOODRIDGE%09Woodridge+Neighborhood+Library"]
audiences = ["ADULT%09Adults"]
#, "JUVENILE%09Children", "YOUNGADULT%09Teens"]
pubyears = ["2015"]
#,"2014"]

try:
    scraperwiki.sql.execute('DROP TABLE `current`')
except:
    print 'No current table to drop'
    
i=0
for f in formats:
    for a in audiences:
        for p in pubyears:
            for l in libraries:
                print i
                i=i+1
                print l+" "+p+" "+a
                html = scraperwiki.scrape("https://catalog.dclibrary.org/client/rss/hitlist/dcpl/qf=LIBRARY%09Library%091%3A"+l+"&qf=PUBDATE%09Publication+Date%09"+p+"%09"+p+"&qf=ITEMCAT2%09Audience%091%3A"+a+"&qf=FORMAT%09Bibliographic+Format%09"+f)
                root = lxml.html.fromstring(clean_xml(html))
                j=0
                k=0
                for entry in root.cssselect('feed entry'):
                    current = {
                        'title' : entry[0].text_content(),
                        'url' : entry.xpath('child::link/@href')[0],
                        'ils' : entry.xpath('child::ils/text()')[0],
                        'pub' : str(p),
                        'format' : re.sub(r'.*09',r'',str(f)),
                        'audience' : re.sub(r'.*09',r'',str(a)),
                        'pubDate' : str(datetime.now())
                        }
                    if len(scraperwiki.sql.select("* from store where ils=(?)", (current['ils'])))==0:
                        k=k+1
                        scraperwiki.sql.save(unique_keys=['ils'], data=current,table_name="current")
                        scraperwiki.sql.save(unique_keys=['ils'], data={'ils' : current['ils'], 'scrape_date' : current['pubDate']},table_name="store")
                    else:
                        j=j+1
                print str(k)+" added\n"+str(j)+" already in catalog\n"
                time.sleep(5)

