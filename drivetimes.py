import requests
import argparse
import datetime
from xml.etree import ElementTree

parser = argparse.ArgumentParser(description="")
parser.add_argument('-o','--origin',default="25507+Del+Mar+Ave,+Hayward,+CA+94542")
args = parser.parse_args()


def googleTimes():
    #origin = args.origin.replace(" ","+")
    apikey = 'AIzaSyCpEUwNl25D2pOhFeRLUJbuFAb32uRL6u8'
    origin = 'Interstate+238+&+Interstate+580,+California'
    destination = "Bowers+Ave,+Santa+Clara,+CA+95054"
    baseurl = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&key=%s&alternatives=true" % (origin,
                                                                                                        destination,
                                                                                                        apikey)
    results = {}
    try:
        r = requests.get(baseurl)
    except Exception, e:
        print "exception in request"
    else:
        for each in r.json()['routes']:
            results[each['summary']] = str(datetime.timedelta(seconds=each['legs'][-1]['duration']['value']))

    return results

def FOOorgTimes():
    routeres = {}
    routelist = [['800','301'],['800','278']]
    mappings ={'800':'92 and 880','301':'101 and GAP','278':'101 and 85'}
    baapikey = "30d1bbd8-a444-4d3d-9b8f-7d81b39ea6a1"
    ignorelist = ["I-880 S, I-280 N, CA-85 N",
                  "I-880 S, I-880 S-CA-237 W Ramp, CA-237 W, CA-237 W-US-101 N Ramp, US-101 N"]
    for each in routelist:
        onode = each[0]
        dnode = each[1]
        url = 'http://services.my511.org/traffic/getpathlist.aspx?token=%s&o=%s&d=%s' % (baapikey, onode, dnode)
        r = requests.get(url)
        tree = ElementTree.fromstring(r.content)
        for path in tree:
            summary = ''
            for segment in path[3]:
                summary += segment[0].text+", "
            summary = summary[:-2]
            if len(tree[0][4]) != 0:
                obstructions = len(path[4])
            else:
                obstructions = 0
            if summary not in ignorelist:
                routeres[summary] = {'origin':mappings[onode],
                                     'destination':mappings[dnode],
                                     'currentTravelTime':str(datetime.timedelta(minutes=float(tree[0][0].text))),
                                     'typicalTravelTime':str(datetime.timedelta(minutes=float(tree[0][1].text))),
                                     'miles':str(tree[0][2].text),
                                     'obstructions':obstructions}
    return routeres

def csvwriter(results):
    import csv
    with open('drivetimes.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for each in results['511']:
            writer.writerow([results['timestamp']]+
                            [results['511'][each]['origin']]+
                            [results['511'][each]['destination']]+
                            [each]+
                            [results['511'][each]['currentTravelTime']]+
                            [results['511'][each]['typicalTravelTime']]+
                            [results['511'][each]['miles']]+
                            [results['511'][each]['obstructions']])

def main():
    bulkResults = {}
    bulkResults['timestamp'] = str(datetime.datetime.now())
    #bulkResults['google'] = googleTimes()
    bulkResults['511'] = FOOorgTimes()
    print bulkResults
    csvwriter(bulkResults)

if __name__ == '__main__':
    main()