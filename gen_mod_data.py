import io, os, re
from os.path import isfile, join
from time import strftime, gmtime
import datetime
import requests
import json
import brotli
import files
import requests
import sys
from dotenv import load_dotenv

runAll = False
if ( len(sys.argv) > 1 and "-all" in sys.argv[1] ):
    runAll = True

load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR")#"output"
if OUTPUT_DIR == None:
    OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


# directoryPath = os.path.dirname(os.path.abspath(__file__))+"\\output\\"
nl = "\n"
cTime = datetime.datetime.now()
timestamp = cTime.strftime("%Y-%m-%d %H:%M:%S") + " Timezone: UTC"+ strftime("%z", gmtime()) + " (" + strftime("%Z", gmtime()) + ")"

# Preferences:
outFileName = "mod_list" +"-"+ files.timestamp()
OUTPUT_FILE = join(OUTPUT_DIR, outFileName)

#functions
def queryNikkyCFGraphQL():
    url = "https://curse.nikky.moe/graphql"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = json.dumps({"query":"""{
  addons(gameId: 432, category: "Fabric") {
    id
    name
    slug
    summary
    categories {
      categoryId
      avatarUrl
      name
    }
    authors {
      id
      name
      url
    }
    dateReleased
    dateModified
    downloadCount
    files {
      displayName
      gameVersion
    }
  }
}
    """})
    return requests.post(url, headers=headers, data=data)

cfUrlPrefix = "https://www.curseforge.com/minecraft/mc-mods/"
def getLatestSupportedVersion(mod):
    def toNum(s):
        try:
            return float(s)
        except ValueError:
            return 0.0
    def latestInList(versList):
        latestVers = 'Unknown'
        def versionOrd(vers):
            nums = vers.split('.')
            weight = 100000
            out = 0
            for x in nums:
                strNum = ''.join(list(filter(str.isdigit, x)))
                out += toNum(strNum)*weight
                weight /= 100
            return out
        latestVersNum = 0
        for x in versList:
            cVersNum = versionOrd(x)
            if (cVersNum > latestVersNum):
                latestVersNum = cVersNum
                latestVers = x
        return latestVers
    #latestVers = latestInList([vers["gameVersion"] for vers in mod["gameVersionLatestFiles"]])
    
    #if latestVers == 'Unknown':
    filesVersList = []
    for file in mod["files"]:
        filesVersList.extend(file["gameVersion"])
    latestVers = latestInList(filesVersList)

    return latestVers
        
# def appendNameDescLinkGQL(modList, outList):
#     for mod in modList:
#         authors = ["[{}]({})".format(author["name"], author["url"]) for author in mod["authors"]]
#         strAuthors = ''
#         for i in range(len(authors)):
#             strAuthors += authors[i]
#             if (i < len(authors)-1):
#                 strAuthors += ', '
#         outList.append(((
#             mod["name"],
#             mod["summary"],
#             mod["slug"],
#             strAuthors,
#             "{:,}".format(int(mod["downloadCount"])),
#             getLatestSupportedVersion(mod)
#         )))
#     def byName(elem):
#         return elem[0].lower()
#     outList.sort(key=byName)

# def graphQLToList(gqlData):
#     print("Generating Mod List from GraphQL data...")
#     outList = list()
#     modlist = gqlData["data"]["addons"]
#     appendNameDescLinkGQL(modlist, outList)
#     return outList
def ynInput(msg=""):
    if (runAll):
        return True
    if (len(msg) > 0):
        print(msg + " (y/n): ")
    inStr = ""
    while inStr != 'y' and inStr != 'n':
        inStr = input().lower()
    return inStr == 'y'

categories = []
def categoriesFromResponse(response_data):
    global categories
    temp_categories = {}
    mods = response_data["data"]["addons"]
    for mod in mods:
        new_categories = []
        for cat in mod["categories"]:
            # if not categories.has_key(cat["categoryId"]):
            # I think this VVV alone is faster, but check performance.
            cat_id = cat["categoryId"]
            temp_categories[cat_id] = cat
            new_categories.append(cat_id)
        # Remove duplicate categories, because apparently thats a thing.
        res = []
        [res.append(x) for x in new_categories if x not in res] 

        mod["categories"] = res

    count = 0
    for key, val in temp_categories.items():
        # if not val in categories:
        categories.append(val)
        temp_categories[key] = count
        count += 1
    for mod in mods:
        cats = mod["categories"]
        for i in range(len(cats)):
            cats[i] = temp_categories[cats[i]]


def formatResponse(response_data):
    mods = response_data["data"]["addons"]
    for mod in mods:
        mod["downloadCount"] = int(mod["downloadCount"])


label = "mod_list"
file_name = str(OUTPUT_FILE)+"-text_response.json"
file_name_min = str(OUTPUT_FILE)+".min.json"
file_name_min_br = str(OUTPUT_FILE)+".min.json.br"

if ynInput("Update local data from NikkyCF?"):
    print("Beginning download...")
    gqlResponse = queryNikkyCFGraphQL()
    print("Download complete")
    mod_data = gqlResponse.json()
    with open(file_name, "w+", encoding="utf-8") as outFile:
        outFile.write(gqlResponse.text)
else:
    nikkyResponseFileName = input("Enter path to response file: ")
    with open(nikkyResponseFileName, 'r', encoding="utf-8") as file:
        mod_data = json.load(file)


categoriesFromResponse(mod_data)
formatResponse(mod_data)

out_data = {
    "mods": mod_data["data"]["addons"],
    "categories": categories
}

with open(file_name_min, "w+", encoding="utf-8") as outFile:
    json.dump(out_data, outFile)
    
with open(file_name_min, "rb") as inFile:
    with open(file_name_min_br, "wb+") as outFile:
        rawdata = inFile.read()
        rawdatalen = len(rawdata)/1024
        compressed = brotli.compress(rawdata)
        compressedlen = len(compressed)/1024
        outFile.write(compressed)
        savings = (rawdatalen-compressedlen)
        savingsPercent = savings/rawdatalen*100
#        fstr = '%.2f'
#        print("Compression complete. Compressed file is {fstr%savings} KB ({fstr%savingsPercent}%) smaller than the original. ({fstr%compressedlen} KB vs {fstr%rawdatalen} KB)" % (, , , ,))

