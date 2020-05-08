from logReadTools import *

startDelimiter = "<<<"
endDelimiter = ">>>"
updateDelimiter = ","

# Implements monitoring on strings like <<<key.path=this,key.value=two>> as complete lines
# Or inside or at the end of the line

def getStateDictionary(fileStr, startChar, endChar):
    assert(startChar is not -1)
    assert(endChar is not -1)
    
    if (endChar is 0):
        endChar = len(fileStr)
    
    buildUp = {}
    progress = startChar
    while True:
        startIndex = fileStr.find(startDelimiter, progress)
        endIndex = fileStr.find(endDelimiter, startIndex)
        if (startIndex > endChar or startIndex < startChar):
            startIndex = -1
        
        if (endIndex > endChar or endIndex < startChar):
            endIndex = -1
            
        if startIndex is -1:
            break
        if endIndex is -1:
            print("ALERT! Found a classMonitoring delimiter that did not have an end... may be an error")
            break
        
        reportContent = fileStr[startIndex + len(startDelimiter):endIndex]
        parts = reportContent.split(updateDelimiter)
        if (len(parts) == 0):
            print("ALERT! Generally a class monitoring statement should have at least one update")
        for part in parts:
            if not "=" in part:
                print("ALERT! There is a statent inside of a clas monitoring thing that does not have an equals... sketchy")
                continue
            if "," in part:
                print("ALERT! There shouldnt be two commas by eachother in a class monitoring statement..... sketchy")
            
            pieces = part.split("=")
            assert(len(pieces) == 2)
            buildUp[pieces[0]] = pieces[1]
            
        progress = endIndex
    
    return buildUp

def stringStatementOfDictionary(dictionary):
    build = startDelimiter
    first = True
    for key in dictionary:
        if first:
            first = False
        else:
            build += updateDelimiter
        build += key + "=" + dictionary[key]
    build += endDelimiter
    return build

def evidenceOfClassMonitoringInString(theString):
    #print("LOoking for evidence in " + theString + " FOUND (" + str(theString.find(startDelimiter)) + " and " + str(theString.find(endDelimiter)))
    if (theString.find(startDelimiter) == -1):
        return False
    if (theString.find(endDelimiter) == -1):
        return False
    return theString.find(startDelimiter) < theString.find(endDelimiter)

def cleanClassMonitoringFromString(theString):
    start = theString.find(startDelimiter)
    end = theString.find(endDelimiter)
    result = theString[0:start] + theString[end + len(endDelimiter):]
    assert(result.find(startDelimiter) == -1)
    return result


def getPlaceholder():
    return startDelimiter + "Placeholder" + endDelimiter

def UnitTest():
    assert(cleanClassMonitoringFromString("<<<HELLO>>>") == "")
    assert(cleanClassMonitoringFromString("bef<<<HELLO>>>aft") == "befaft")
    assert(cleanClassMonitoringFromString("<<<HELLO>>>aft") == "aft")
    assert(cleanClassMonitoringFromString("bef<<<HELLO>>>aft") == "befaft")
    assert(cleanClassMonitoringFromString("bef <<<HELLO>>> aft") == "bef  aft")
    assert(cleanClassMonitoringFromString("<<<>>>") == "")
    assert(cleanClassMonitoringFromString("bef<<<>>>aft") == "befaft")
    assert(cleanClassMonitoringFromString("<<<>>>aft") == "aft")
    assert(cleanClassMonitoringFromString("bef<<<>>>aft") == "befaft")
     
UnitTest()