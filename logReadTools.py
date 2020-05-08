import re
import sys

def failWithMessage(message):
    print(message)
    assert(False)
    sys.exit(message)
    

def assertArgumentIsNotFileName(argument):
    startString = "Argument \"" + argument + "\" may be a filename instead of a file string"
    if len(argument) < 100:
        failWithMessage(startString + " argument is under 100 chars")
    else:
        extract = argument[:min(len(argument), 4000)]
        if not "\n" in extract:
            failWithMessage(startString + " couldnt fine new line in the first bit")
            
    
def readFileToString(file):
    with open(file, 'r') as file:
        return file.read().replace('\n', '\n')


def getFirstLastLineList(fileString):
    assertArgumentIsNotFileName(fileString)
    wholeLog = fileString
    breakSeq = "--------------------------------------------------"
    falseBreakSeq = "=================================================="
    wholeLog = wholeLog.replace(falseBreakSeq, breakSeq)
    progress = 0
    
    result = []
    
    while (True):
        startMarker = wholeLog.find(breakSeq, progress)
        endStartMarker = wholeLog.find("\n", startMarker + 1)
        startLine = wholeLog[endStartMarker:wholeLog.find("\n", endStartMarker + 1)].strip()
        if (startMarker is -1):
            #print(startMarker)
            #print(progress)
            #print(wholeLog[progress:progress+10])
            break
        endMarker = wholeLog.find(breakSeq, startMarker + 1)
        assert(startMarker != endMarker)
        progress = endMarker
        endLineStart = wholeLog.rfind("\n", startMarker, endMarker - 1)
        assert(endLineStart > startMarker)
        lastLine = wholeLog[endLineStart:endMarker].strip()
        assert(len(lastLine) > 2)
        passed = lastLine.find("PASS") != -1
        if (len(startLine) < 10):
            break
        
        summary = ""
        if not passed:
            if (endMarker is -1):
                summary += "INCOMPLETE!"
            else:
                summary += "FAILED!"
        else:
            summary += "PASSED!"
            

        
        testnum = int(re.findall(r'^\D*(\d+)', startLine)[0])
        result.append({"startLine": startLine, "lastLine": lastLine, "passed": passed, "testnum": testnum, "summary": summary, "startMarker":startMarker, "endMarker":endMarker})
    
    return result
    

