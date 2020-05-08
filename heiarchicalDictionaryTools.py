import copy

# This dictionary is the common format used for fancyLogView

# Converts classMonitoringDict to this format
def heiarchicalDictOfClassMonitoringDictionary(classMonitoringDict):
    dictionary = classMonitoringDict
    build = ""
    heiarchicalDictionary = {}
    for key in dictionary:
        parts = key.split(".")
        if len(parts) is 0:
            parts = [key]
        assert(len(parts) > 0)
        
        relevantDictionary = heiarchicalDictionary
        for num, part in enumerate(parts):
            isLast = num == (len(parts) - 1)
            if not part in relevantDictionary:
                if isLast:
                    relevantDictionary[part] = dictionary[key]
                else:
                    relevantDictionary[part] = {}
            else:
                if (not isinstance(relevantDictionary[part], dict)):
                    if (not isLast):
                        print("WARNING! Invalid input in this classMonitoringDict")
                        print("WARNING! Cant have multiple keypath depths \n\tex: apple.banana=cranberry, apple=walnut as those two paths have different lenghts\n\tIn this case the key path apple has both a depth of 0 AND 1")
                        print("WARNING! Cant have multiple keypath depths \n\tex: apple.banana.pineapple=cranberry, apple.banana=walnut as those two paths have different lenghts\n\tIn this case the key path apple.banana has both a depth of 0 AND 1")
                        print("\nWE WILL PROBABLY CRASH")
            relevantDictionary = relevantDictionary[part]
    
    return heiarchicalDictionary



def __updatedDictAfterApply(oldDict, newDict):
    for key in newDict.keys():
        if (key in oldDict):
            newIsDict = isinstance(newDict[key], dict)
            oldIsDict = isinstance(newDict[key], dict)
            
            # NOTE: One thing not suppored is mutliple kepath depths. See warnings printed in heiarchicalDictOfClassMonitoringDictionary
            # Something probably went wrong if you fail this assert
            assert(newIsDict == oldIsDict)
            
            if (newIsDict):
                __updatedDictAfterApply(oldDict[key], newDict[key])
            else:
                oldDict[key] = copy.deepcopy(newDict[key])
        else:
            oldDict[key] = copy.deepcopy(newDict[key])
    
def updatedDictAfterApply(oldDict, newDict):
    build = copy.deepcopy(oldDict)
    __updatedDictAfterApply(build, newDict)
    return build

def __printPrefix(num):
    build = ""
    for i in range(num):
        build += "    "
    return build

def __stringRepresentationOfHeiarchicalDictionary(prefix, highestPrefixSeen, heiarchicalDictionary):
    indent = 1
    build = ""
    if (not isinstance(heiarchicalDictionary, dict)):
        build += " = " + heiarchicalDictionary + "\n"
    else:
        for key in sorted(heiarchicalDictionary.keys()):
            value = heiarchicalDictionary[key]
            newPrefix = prefix
            newLine = ""
            if (not isinstance(value, dict) or len(value.keys()) == 1):
                newPrefix = 0
                if (not isinstance(value, dict)):
                    newLine = ""
                else:
                    newLine = "."
            else:
                newPrefix = highestPrefixSeen + indent
                newLine = "\n"
                
            build += __printPrefix(prefix) + key + newLine + __stringRepresentationOfHeiarchicalDictionary(newPrefix, max(newPrefix, highestPrefixSeen), value)
        
    return build
    
def stringRepresentationOfHeiarchicalDictionary(heiarchicalDictionary):
    return __stringRepresentationOfHeiarchicalDictionary(0, 0, heiarchicalDictionary)

def unitTests():
    dict1 = {"foo":"old","foo2.bar":"old2","foo2.baz.baz":"old3","foo2.baz.bazzle":"old4","golden.boy.is.shiny":"old6","golden.boy.ugly.hell":"old7"}
    dict2 = {"foo":"upd","foo2.bar":"upd2","foo2.baz.baz":"upd3","foo2.baz.bazzle":"upd4","golden.boy.is.shiny":"upd6","golden.boy.ugly.hell":"upd7"}
    dict3 = {"very":"little"}
    
    dict4 = {"very":"little", "foo":"old","foo2.bar":"old2","foo2.baz.baz":"old3","foo2.baz.bazzle":"old4","golden.boy.is.shiny":"old6","golden.boy.ugly.hell":"old7"}
    
    conv1 = heiarchicalDictOfClassMonitoringDictionary(dict1)
    conv2 = heiarchicalDictOfClassMonitoringDictionary(dict2)
    conv3 = heiarchicalDictOfClassMonitoringDictionary(dict3)
    
    conv4 = heiarchicalDictOfClassMonitoringDictionary(dict4)
    
    assert(conv1 == updatedDictAfterApply(conv2, conv1))
    assert(conv2 == updatedDictAfterApply(conv1, conv2))
    assert(conv2 == updatedDictAfterApply(conv2, conv2))
    assert(conv4 == updatedDictAfterApply(conv3, conv1))
    assert(conv4 == updatedDictAfterApply(conv1, conv3))
    
    dict5 = {"branches.right":"1", "branches.left":"2"}
    assert(stringRepresentationOfHeiarchicalDictionary(heiarchicalDictOfClassMonitoringDictionary(dict5)) == ("branches\n"+__printPrefix(1)+"left = 2\n"+__printPrefix(1)+"right = 1\n"))
    dict6 = {"branches.right":"1", "branches.left":"2","sub.branches.right":"1", "sub.branches.left":"2"}
    assert(stringRepresentationOfHeiarchicalDictionary(heiarchicalDictOfClassMonitoringDictionary(dict6)) == ("branches\n"+__printPrefix(1)+"left = 2\n"+__printPrefix(1)+"right = 1\n"+"sub.branches\n"+__printPrefix(1)+"left = 2\n"+__printPrefix(1)+"right = 1\n"))
    dict7 = {"lolla.likes.apples":"if they are raw", "lolla.likes.to.eat":"raw apples"}
    print(stringRepresentationOfHeiarchicalDictionary(heiarchicalDictOfClassMonitoringDictionary(dict7)))


    
unitTests()