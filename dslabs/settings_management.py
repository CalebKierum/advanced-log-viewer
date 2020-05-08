
relevancyArray = [
    "SIZE",
    "LOG",
    "CLASS",
    "OR"
]
def validateSetting(setting):
    assert(isinstance(setting, dict))
    assert("shortName" in setting)
    assert("longName" in setting)
    assert("default" in setting)
    assert("relevancy" in setting)
    assert("subSettings" in setting)
    
    ss = setting["subSettings"]
    assert(isinstance(ss, list))
    
    rel = setting["relevancy"]
    if (rel != False):
        assert(rel in relevancyArray)
        
    assert("." not in setting["shortName"])
    
    
def __printSettingsArray(prefix, settingsArray, relevancyBools, relevant, specificSettings, path):
    build = ""
    assert(len(relevancyBools) == len(relevancyArray))
    
    for idx, setting in enumerate(sorted(settingsArray, key = lambda i: i['shortName'])):
        validateSetting(setting)
        # Print this setting
        if (relevant and setting["relevancy"] != False):
            relevant = relevancyBools[relevancyArray.index(setting["relevancy"])]
        
        relevancyStr = ""
        if (not relevant):
            relevancyStr = "(Not Relevant)"
            
            
        findPath = path + "." + setting["shortName"]
        assert(findPath in specificSettings)
        currentSetting = specificSettings[findPath]
        currentSettingStr = "YES"
        if not currentSetting:
            currentSettingStr = "NO"
            
        build += prefix + str(idx + 1) + ". " + setting["shortName"] + ": " + currentSettingStr + "  " + relevancyStr + "\n"
        
        # Print its subsetting
        if (len(setting["subSettings"]) > 0):
            build += __printSettingsArray(prefix + "\t", setting["subSettings"], relevancyBools, relevant, specificSettings, findPath)
        
    return build
        

def printSettingsArray(settingsArray, relevancyBools, specificSettings):
    printStr = __printSettingsArray("", settingsArray, relevancyBools, True, specificSettings, "userSettings")
    print()
    print(printStr)


def __printDescriptions(settingsArray):
    for idx, setting in enumerate(sorted(settingsArray, key = lambda i: i['shortName'])):
        validateSetting(setting)
        print(setting["shortName"] + "->" + setting["longName"])
        if (len(setting["subSettings"]) > 0):
            __printDescriptions(setting["subSettings"])
            

def printDescriptions(settingsArray):
    print("====== Descriptions =====")
    __printDescriptions(settingsArray)
    print("=========================")
    
    
def __defaultSettingsFromArray(settingsArray, path, build):
    for setting in settingsArray:
        specificPath = path + "." + setting["shortName"]
        build[specificPath] = setting["default"]
        
        if (len(setting["subSettings"]) > 0):
            __defaultSettingsFromArray(setting["subSettings"], specificPath, build)
        
    
def defaultSettingsFromArray(settingsArray):
    build = {}
    __defaultSettingsFromArray(settingsArray, "userSettings", build)
    return build
    
   
def __processChangeSettingTo(settingsArray, userPath, setTo, settings, depth, path):
    if (depth == len(userPath)):
        print("Setting " + path + " to " + str("y" in setTo))
        settingsArray[path] = "y" in setTo
        return
    
    choice = int(userPath[depth])
    for idx, setting in enumerate(sorted(settings, key = lambda i: i['shortName'])):
        if (choice == idx + 1):
            __processChangeSettingTo(settingsArray, userPath, setTo, setting["subSettings"], depth + 1, path + "." + setting["shortName"])
            return
    print("Doesnt appear to be a valid setting")
    assert(False)
    
    
def processChangeSettingTo(settingsArray, userPath, setTo, settings):
    __processChangeSettingTo(settingsArray, userPath, setTo, settings, 0, "userSettings")
     
def commandChanges(happy, settingsArray, settings): 
    parts = happy.split(",")
    for part in parts:
        lowerPart = part.lower()
        assert("=" in lowerPart)
        partParts = lowerPart.split("=")
        assert("=" in lowerPart)
        assert(len(partParts) == 2)
        assert("y" is partParts[1] or "n" is partParts[1])
        processChangeSettingTo(settingsArray, partParts[0].split("."), partParts[1], settings)
    print("Processed these changes")
    return settingsArray