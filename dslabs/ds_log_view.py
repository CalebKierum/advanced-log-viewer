#https://www.instructables.com/id/Create-a-Simple-Python-Text-Editor/
import tkinter as tk
from tkinter import font
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
import sys
import signal
import time
import heiarchical_dictionary_tools
import copy

assert len(sys.argv) > 1

import log_read_tools

settings = {}
reportArgs = ""
argIndex = 1

def __getNextArgOrAsk(message):
    global argIndex
    if (argIndex < len(sys.argv)):
        value = sys.argv[argIndex]
        argIndex += 1
        if ("X" is not value):
            print(message + value)
            return value

    return input(message)

def getNextArgOrAsk(message):
    global reportArgs
    res = __getNextArgOrAsk(message)
    if (res != "X"):
        reportArgs += res + " "
    return res

filename = getNextArgOrAsk("Which Filename: ")
print("Preparing to open file " + filename + "...")

# Step 1 summarize the results in this log
#   You should be able to
#       What tests are in this?
#       Is the test passed, failed, unknown
#       Does the test have an assert or an error in it
logFileString = log_read_tools.read_file_to_string(filename)
print("Finished reading the file")
print("Working on summary")

# Step 1a get the log split up into summary parts
testBreakup = log_read_tools.get_first_last_line_list(logFileString)
#result.append({"startLine": startLine, "lastLine": lastLine, "passed": passed, "testnum": testnum, "summary": summary})
#startLine, lastLine, passed, testnum, summary, startMarker, endMarker
print("======== SUMMARY ========\n")
if len(testBreakup) is 0:
    settings["multipleTests"] = False
    print("This log appears to only contain one test")
    foundAssert = "Assert.java" in logFileString
    foundFailure = "[SEVERE ]" in logFileString
    if foundAssert:
        print("There may be an assert in the file")
    if foundFailure:
        print("There may be a [SEVERE ]in the file")
else:
    settings["multipleTests"] = True
    failCount = 0
    passCount = 0
    incompleteCount = 0
    buildReport = ""
    for rec in testBreakup:
        #x.count('\n')
        theSlice = logFileString[rec["startMarker"]:rec["endMarker"]]
        numLines = theSlice.count("\n")
        foundAssert = "Assert.java" in theSlice
        foundFailure = "[SEVERE ]" in theSlice
        name = rec["startLine"]
        testNumStr = str(rec["testnum"])
        result = rec["summary"]
        if "FAILED" in result:
            failCount += 1
        elif "PASSED" in result:
            passCount += 1
        else:
            incompleteCount += 1

        addendumStr = ""
        if foundAssert or foundFailure:
            addendumStr += "!!!!"
        if foundAssert:
            addendumStr += "[Found assert]"
        if foundFailure:
            addendumStr += "[Found SEVERE"

        reportStr = testNumStr + ". " + result + " " + name + "\t" + "(" + str(numLines) + " lines)\t" + addendumStr
        buildReport += "\t" + reportStr + "\n"
    print(buildReport)
    print(str(passCount) + " passing\t" + str(failCount) + " failing\t" + str(incompleteCount) + " incomplete")

print("\n=======================")

print("Please note! This software is vulnerable to bugs and issues. Do not assume it is working properly")
print("Please note! In order to operate rhobustly this must be run with a dslabs log and you must not print strings such as")
print("====== (repeated), ------- (repeated)")
print("Additionally avoid the following strings in variable names containing \".\",  \",\",  \"=\" best if those are not in strings printed either")
print("")

# Step 2 Figure out the intent. Which log do they want to see
import state_monitoring_tool

class_monitor = state_monitoring_tool.StateMonitoringTool()
state_monitor = state_monitoring_tool.StateMonitoringTool(start_delimiter="${", end_delimiter="}$", level_separator="|")

hasClassTracing = False
has_state_tracing = False
hasLogSizeIssues = False
theBreakupSlice = None
if settings["multipleTests"] is True:
    while (not "testIndex" in settings):
        testNum = getNextArgOrAsk("Which test would you like to view: ")
        settings["testNum"] = testNum
        for idx, part in enumerate(testBreakup):
            if (str(part["testnum"]) == testNum):
                settings["testIndex"] = idx
                theBreakupSlice = part
                break

        if (not "testIndex" in settings):
            print("Couldnt find a test with that num.. try again")

    # NOTE: Should accomodate when testNum does not equal an index!
    theSlice = logFileString[theBreakupSlice["startMarker"]:theBreakupSlice["endMarker"]]
    hasLogSizeIssues = theSlice.count("\n") > 10000
    hasClassTracing = class_monitor.evidence_of_monitoring_in_string(theSlice)
    has_state_tracing = state_monitor.evidence_of_monitoring_in_string(theSlice)
else:
    settings["testNum"] = "N/A"
    settings["testIndex"] = "N/A"
    hasLogSizeIssues = logFileString.count("\n") > 10000
    hasClassTracing = class_monitor.evidence_of_monitoring_in_string(logFileString)
    has_state_tracing = state_monitor.evidence_of_monitoring_in_string(logFileString)

print()
print("Will print below if there is anything interseting about the log.....VVVV")
if (hasLogSizeIssues):
    print("This log is over 10k lines")

if (not hasClassTracing):
    print("No class tracking seen")

if (not has_state_tracing):
    print("No log tracing seen")

# Step 3 Determine various settings
import settings_management
specificSubSettings = [
    {"shortName":"Show In Main Log", "longName":"You can hide these statements while still having them active in the top window", "default": False, "relevancy": False, "subSettings":[
        {"shortName":"Leave Placeholder", "longName":"If a statement is hidden a placeholder is left", "default": True, "relevancy": False, "subSettings":[]}
    ]},
    {"shortName":"Include Past", "longName":"Sometimes state from previous runs is relevant if it is you can include a summary statement", "relevancy": False, "default": True, "subSettings":[]},
]
mainSettings = [
    {"shortName":"Top View", "longName": "Show a view on top that can show more detail", "default": True, "relevancy":"OR", "subSettings":[
       {"shortName":"Class Update Summary", "longName":"Show automatic tracking", "default": True, "relevancy": "CLASS", "subSettings":specificSubSettings},
        {"shortName":"Log Trace", "longName":"Show automatic log tracking", "default": True, "relevancy": "LOG", "subSettings":specificSubSettings}
    ]},
    {"shortName":"Remember Highlights", "longName":"You can highlight with right clicks. With this on your highlighted words will be saved", "default": True, "relevancy": False, "subSettings":[]},
    {"shortName":"Truncate To 10k lines", "longName":"Truncate the log view to 10,000 lines", "default": True, "relevancy": "SIZE",  "subSettings":[]},
]
settings_management.printDescriptions(mainSettings)
specificSettings = settings_management.defaultSettingsFromArray(mainSettings)
happy = False
while (not happy):
    settings_management.printSettingsArray(mainSettings, [hasLogSizeIssues, has_state_tracing, hasClassTracing, has_state_tracing or hasClassTracing], specificSettings)
    checkIfHappy = getNextArgOrAsk("Do you like the settings as set [Y/n]: ")
    if (len(checkIfHappy) != 1):
        print("Invalid input....")
    elif ("y" in checkIfHappy.lower()):
        happy = True
    else:
        print("Valid format:1.1=Y,2=N")
        commandStr = getNextArgOrAsk("Please input a command string: ")
        specificSettings = settings_management.commandChanges(commandStr, specificSettings, mainSettings)

assert(happy)
print("GREAT!")


settings = {**settings, **specificSettings}

# Step 4 Prepare the log for this thing
# GOAL Prepare 2 things (of hidden things)
# 1 Main Log
# 1 Side Log
print("Preparing... this may take awhile", end = '')

# Step 4a prepare the log and the pre log
preLogText = ""
logText = ""
if len(testBreakup) is 0:
    logText = logFileString
else:
    rec = testBreakup[settings["testIndex"]]
    logText = logFileString[rec["startMarker"]:rec["endMarker"]]
    if (settings["userSettings.Top View.Class Update Summary.Include Past"] or settings["userSettings.Top View.Log Trace.Include Past"]):
        preLogText = logFileString[0:rec["startMarker"]]

print("a", end = '')

# Step 4b prepare the pre log (if there is one)
summaryLines = ""
if (len(preLogText) > 0):
    summaryLines += "####### Collapsed Previous Summary #######" + "\n"
    if (settings["userSettings.Top View.Class Update Summary.Include Past"]):
        summaryLines += class_monitor.string_statement_of_dictionary(class_monitor.get_state_dictionary(preLogText, 0, 0)) + "\n"
    if (settings["userSettings.Top View.Log Trace.Include Past"]):
        summaryLines += state_monitor.string_statement_of_dictionary(state_monitor.get_state_dictionary(preLogText, 0, 0)) + "\n"
    summaryLines += "##########################################" + "\n"
print("b", end = '')

# Step 4c truncate the lines if needed
if (settings["userSettings.Truncate To 10k lines"]):
    progress = 0
    count = 0
    while True:
        progress = logText.find("\n", progress)
        count += 1
        if (count > 10000 or progress == -1):
            break
        progress += 1

    if (count > 10000):
        print("Did truncate")
        logText = logText[0:progress]
print("c", end = '')


# Step 4d split to lines
fullLog = summaryLines + logText
linesOfFullLog = fullLog.split("\n")
print("d", end = '')

# Step 4e prepare the side summaries

# Step 4e.a Read settings
classSummaries_On = settings["userSettings.Top View.Class Update Summary"]
classSummaries_AppearInLog = classSummaries_On and settings["userSettings.Top View.Class Update Summary.Show In Main Log"]
classSummaries_LeavePlaceholder = (not classSummaries_AppearInLog) and classSummaries_On and settings["userSettings.Top View.Class Update Summary.Show In Main Log.Leave Placeholder"]

stateTracking_On = settings["userSettings.Top View.Log Trace"]
stateTracking_AppearInLog = classSummaries_On and settings["userSettings.Top View.Log Trace.Show In Main Log"]
stateTracking_LeavePlaceholder = (not classSummaries_AppearInLog) and classSummaries_On and settings["userSettings.Top View.Log Trace.Show In Main Log.Leave Placeholder"]
# Step 4e.b Make assertions to check
if (classSummaries_LeavePlaceholder):
    assert(not classSummaries_AppearInLog)

# Step 4e.c Do the actual processing
#print("\nPRE: \n------------------------------\n" + "\n".join(linesOfFullLog) + "\n------------------------------")
specialLogUpdates = []
templist = []
while linesOfFullLog:
    line = linesOfFullLog.pop(0)
    displayLine = True

    isClassMonitoring = class_monitor.evidence_of_monitoring_in_string(line)
    if (isClassMonitoring):
        # 1. Clean the class monitoring out of the string
        cleanedLine = class_monitor.clean_monitoring_from_string(line).strip()
        hasOtherContent = len(cleanedLine) != 0
        if (classSummaries_On):
            classMonitoringDict = class_monitor.get_state_dictionary(line, 0, 0)
            heiarchicalMontoringDict = class_monitor.heiarchical_dict_of_state_monitoring_dictionary(classMonitoringDict)
            specialLogUpdates.append({"line":len(templist),"stateDict":heiarchicalMontoringDict, "reportTitle":"Object Update Montoring"})

        if (classSummaries_AppearInLog):
            if (classSummaries_LeavePlaceholder):
                line = cleanedLine + class_monitor.get_placeholder()
            # No changes
        else:
            if (classSummaries_LeavePlaceholder):
                line = cleanedLine + class_monitor.get_placeholder()
            else:
                line = cleanedLine

    is_state_tracing = state_monitor.evidence_of_monitoring_in_string(line)
    if (is_state_tracing):
        # 1. Clean the class monitoring out of the string
        cleanedLine = state_monitor.clean_monitoring_from_string(line).strip()
        hasOtherContent = len(cleanedLine) != 0
        if (stateTracking_On):
            classMonitoringDict = state_monitor.get_state_dictionary(line, 0, 0)
            heiarchicalMontoringDict = state_monitor.heiarchical_dict_of_state_monitoring_dictionary(classMonitoringDict)
            specialLogUpdates.append({"line":len(templist), "stateDict":heiarchicalMontoringDict, "reportTitle":"State Update Montoring"})

        if (stateTracking_AppearInLog):
            if (stateTracking_LeavePlaceholder):
                line = cleanedLine + state_monitor.get_placeholder()
            # No changes
        else:
            if (stateTracking_LeavePlaceholder):
                line = cleanedLine + state_monitor.get_placeholder()
            else:
                line = cleanedLine

    if (line == ""):
        displayLine = False

    if displayLine:
        templist.append(line)
while templist:
    linesOfFullLog.append(templist.pop(0))



#print("Post: \n------------------------------\n" + "\n".join(linesOfFullLog) + "\n------------------------------")
print("e", end = '')

print()
print("Done preparing!")

# Step 5 What display size
# Now we are ready! The goal is to do prep now before this
checkIfHappy = getNextArgOrAsk("Display will default to 600x800 unless you give a new size. Respond \'y\' if you like this or a new display size:")

width = 600
height = 800
if (checkIfHappy.lower() != 'y'):
    theString = checkIfHappy
    parts = theString.split("x")
    assert(len(parts) == 2)
    width = int(parts[0])
    height = int(parts[1])


print("Great! Lets open this puppy up")
print("Opening " + str(width) + "x" + str(height))

print("Note if you ever want to relaunch with these settings the arguments are " + reportArgs)
print("======== ARGUMENTS =======\n\n" + reportArgs + "\n\n=========")

# Step 6 Import old highlights

import advanced_log_view
advanced_log_view.open_display(width, height, linesOfFullLog, specialLogUpdates, settings["userSettings.Top View"], settings["userSettings.Remember Highlights"])
