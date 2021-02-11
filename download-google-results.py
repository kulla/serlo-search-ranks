#!python

import os
import json
import random
import sys
import time

from datetime import datetime, timedelta

sys.path.insert(0, "/home/kulla/workspace/foss/google-search-api")

import googleapi

def main():
    with open(os.path.join(os.path.dirname(__file__), "keywords.json"), "r") as f:
        keywords = json.load(f)

    for keyword in keywords:
        makeDownload(keyword)

def makeDownload(keyword, retry=0):
    lastDownload = getLastDownloadTime(keyword)

    if lastDownload != None and datetime.now() - lastDownload < timedelta(days=3):
        print("Omit: %s" % keyword)
        return

    print("Download: %s" % keyword)
    results = googleapi.standard_search.search(keyword, 5)
    results = [parseResult(x) for x in results]

    if len(results) < 10:
        if retry < 3:
            print("Retry: %s" % keyword)
            retry += 1
            time.sleep(10 * 2**retry)
            makeDownload(keyword, retry)
        else:
            print("Abort: %s" % keyword)
    else:
        print("Success: %s (%s results)" % (keyword, len(results)))
        targetName = "%s.json" % datetime.now().isoformat()
        target = os.path.join(getDownloadDir(keyword), targetName)

        os.makedirs(getDownloadDir(keyword), exist_ok=True)

        with open(target, "w") as f:
            json.dump(results, f, indent=2)

        time.sleep(random.uniform(2,10))

def parseResult(result):
    return {
        "name": result.name,
        "link": result.link,
        "description": result.description,
        "googleLink": result.google_link,
        "page": result.page,
        "index": result.index
    }

def getLastDownloadTime(keyword):
    downloadDir = getDownloadDir(keyword)

    if not os.path.isdir(downloadDir):
        return None

    files = os.listdir(downloadDir)
    times = [ datetime.fromisoformat(os.path.splitext(x)[0]) for x in files]

    return max(times) if len(times) > 0 else None

def getDownloadDir(keyword):
    return os.path.join(os.path.dirname(__file__), "results", keyword[0], keyword)

if __name__ == "__main__":
    main()
