import tkinter as tk
from tkinter import font
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
import sys
import signal
import time
import heiarchical_dictionary_tools

DARK_COLOR = "#A598AA"
LIGHT_COLOR = "#D8D2DA"

HIGHLIGHT_COLORS = ["#ccff00", "#ce97fb", "#f6a5eb", "#fddf7e", "#9bfbe1",
                    "#67ebfa", "#a5b5f6", "#f1a8a9", "#f6c2a5", "#a8f6a5"]
highlight_index = -1
def getNewHighlight():
    global highlight_index
    highlight_index += 1
    highlight_index = highlight_index % len(HIGHLIGHT_COLORS)
    return HIGHLIGHT_COLORS[highlight_index]

__root = None
def setGlobalRoot(to):
    global __root
    __root = to

def getGlobalRoot():
    global __root
    return __root

def wordAppropriateOrNone(word):
    if len(word) < 3:
        return None
    return word


LIST_FILE_NAME = ".dontAddMeToGit"
file_obj  = open(LIST_FILE_NAME, "w")
file_obj.close()

def read_list():
    places = []

    # open file and read the content in a list
    with open(LIST_FILE_NAME, 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            current_place = line[:-1]

            # add item to the list
            places.append(current_place)
    return places


def write_list(thelist):
    with open(LIST_FILE_NAME, 'w') as filehandle:
        for listitem in thelist:
            filehandle.write('%s\n' % listitem)



# NOTE: Skip to bottom of file to see how to instantiate all this stuff
class TopWindow(tk.Text):
    def __init__(self, myroot, event=None, x=None, y=None, size=None, txt=None, *args, **kwargs):
        tk.Text.__init__(self, master=myroot, *args, **kwargs)
        self.font = font.Font(family="Helvetica Neue LT Com 55 Roman",size=10)
        self.insert(tk.INSERT, ' Overlay ')
        self.config(font=self.font)
        self.config(bg="#720058")
        self.config(foreground="white")
        #self.update_size(event=None)
        bindtags = list(self.bindtags())
        bindtags.insert(2, "custom")
        self.bindtags(tuple(bindtags))
        #self.bind_class("custom", "<Key>", self.update_size)
        self.config(height=6)
        self.lastText = ""
        self.special_reports = None

    def set_special_reports(self, special_reports):
        self.special_reports = special_reports

    def set_new_text(self, text):
        if (text != self.lastText):
            vw = self.yview()
            self.delete(1.0, "end")
            self.insert(tk.INSERT, text)
            #self.update_size(None)
            self.lastText = text
            self.yview_moveto(vw[0])

    def refresh(self, linenum):
        text_build = ""

        text_build = "Line: " + str(linenum) + "\n"

        if self.special_reports is not None:
            cumulative_build = {}
            for report in self.special_reports:
                assert("line" in report)
                assert("stateDict" in report)
                assert("reportTitle" in report)
                if (report["line"] > linenum):
                    break

                report_title = report["reportTitle"]
                if (not report_title in cumulative_build):
                    cumulative_build[report_title] = {}

                cumulative_build[report_title] = heiarchical_dictionary_tools.updatedDictAfterApply(cumulative_build[report_title], report["stateDict"])

            for key in sorted(cumulative_build.keys()):
                text_build += "------------  " + key + "  ------------\n"
                text_build += heiarchical_dictionary_tools.stringRepresentationOfHeiarchicalDictionary(cumulative_build[key])

        self.set_new_text(text_build)

# This is the main scrolled view
class BigFancyScrollableView():
    def __init__(self, root):
        self.txt = scrolledtext.ScrolledText(root, undo=True, wrap='none')
        self.txt['font'] = ('consolas', '12')

        # Set up tags
        self.txt.tag_configure("current_line", background=DARK_COLOR)
        self.txt.tag_configure("previous_lines", background=LIGHT_COLOR)
        self.txt.tag_configure("current_word", background="#ffb7b7")

        # No editing
        self.txt.configure(state='disabled')

        # Click behavior
        self.txt.bind("<1>", lambda event: self.txt.focus_set())

    def set_text(self, text):
        self.txt.configure(state='normal')
        self.txt.insert(tk.INSERT, str(text))
        self.txt.configure(state='disabled')


    def get_selected_word(self):
        try:
            return self.txt.selection_get()
        except Exception as e:
            return ""

    def get_highlighted_word(self):
        return self.txt.get("insert wordstart", "insert wordend")

    def highlight_string(self, word):
        highlighted_word = word
        color = getNewHighlight()
        tag = "highlight"+highlighted_word
        self.txt.tag_configure(tag, background=color)

        pattern = highlighted_word
        regexp = False

        self.txt.mark_set("matchStart", "1.0")
        self.txt.mark_set("matchEnd", "1.0")
        self.txt.mark_set("searchLimit", "end")

        count = tk.IntVar()
        while True:
            index = self.txt.search(pattern, "matchEnd", "searchLimit",
                                    count=count, regexp=regexp)
            if index == "":
                break
            if count.get() == 0:
                break # degenerate pattern which matches zero-length strings
            self.txt.mark_set("matchStart", index)
            self.txt.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.txt.tag_add(tag, "matchStart", "matchEnd")
        self.txt.tag_raise("sel")


    def un_highlight_string(self, word):
        highlightedWord = word
        tag = "highlight"+highlightedWord
        self.txt.tag_remove(tag, 1.0, "end")

    def refresh(self):
        self.txt.tag_remove("current_line", 1.0, "end")
        self.txt.tag_add("current_line", "insert linestart", "insert lineend+1c")

        self.txt.tag_remove("previous_lines", 1.0, "end")
        self.txt.tag_add("previous_lines", "1.0", "insert linestart")

        self.txt.tag_remove("current_word", 1.0, "end")
        if wordAppropriateOrNone(self.get_highlighted_word()):
            self.txt.tag_add("current_word", "insert wordstart", "insert wordend")

        self.txt.tag_raise("sel")


# The main container
class SmartLogView(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

    def prepare(self, linesOfView, specialReports, showPopUp, savingHighlight):
        self.linesOfView = linesOfView
        self.textOfView = "\n".join(linesOfView)
        # This is the main log view
        self.bigtext = BigFancyScrollableView(self)
        self.bigtext.set_text(self.textOfView)

        # This is the top window
        self._showPopUp = showPopUp
        if self._showPopUp:
            self.overlay = TopWindow(self)
            self.overlay.pack(fill=tk.BOTH, expand=True)
            self.overlay.set_special_reports(specialReports)

        self.bigtext.txt.pack(fill=tk.BOTH, expand=True)

        self.savingHighlight = savingHighlight

        self.lastLineNum = None
        self._update()


    def _update(self, interval=100):
        self.after(interval, self._update)
        self.bigtext.refresh()
        if self._showPopUp:
            linenum = -1
            index = self.bigtext.txt.count("1.0", "insert linestart+1c")[0]

            for idx, line in enumerate(self.linesOfView):
                index -= len(line)
                index -= 1
                if index < 0:
                    linenum = idx
                    break


            if index == -1:
                linenum = len(self.linesOfView) - 1

            if linenum != -1:
                if self.lastLineNum == None:
                    self.lastLineNum = linenum
                elif self.lastLineNum != linenum:
                    self.overlay.refresh(linenum)
                    self.lastLineNum = linenum


    # Highlighting thingsvvvvv
    def set_highlight_list(self, theList):
        self.highlightList = theList
        for item in theList:
            self.bigtext.highlight_string(item)

    def word_in_highlight_list(self, word):
        return word in self.highlightList

    def get_selected_word(self):
        return wordAppropriateOrNone(self.bigtext.get_selected_word())

    def get_highlighted_word(self):
        return wordAppropriateOrNone(self.bigtext.get_highlighted_word())

    def highlight_word(self, word):
        assert(not self.word_in_highlight_list(word))
        assert(wordAppropriateOrNone(word))
        self.highlightList.append(word)
        self.bigtext.highlight_string(word)
        self.update_write_if_should()

    def un_highlight_word(self, word):
        assert(self.word_in_highlight_list(word))
        self.highlightList.remove(word)
        self.bigtext.un_highlight_string(word)
        self.update_write_if_should()

    def un_highlight_duty(self, selected, highlighted):
        canidates = []

        for word in self.highlightList:
            if (selected is not None):
                if (selected.find(word) != -1 or word.find(selected) != -1):
                    canidates.append(word)
            if (highlighted is not None):
                if (highlighted.find(word) != -1 or word.find(highlighted) != -1):
                    canidates.append(word)


        theSet = set(canidates)
        if (selected is not None and selected in theSet):
            theSet.remove(selected)

        if (highlighted is not None and highlighted in theSet):
            theSet.remove(highlighted)

        return list(theSet)

    def update_write_if_should(self):
        if (self.savingHighlight):
            write_list(self.highlightList)



# The right click pop up handler
#https://stackoverflow.com/a/4552646/5183807
def right_click_handler(e):
    try:
        def rClick_highlight(e, strng, apnd=0):
            getGlobalRoot().highlightWord(strng)

        def rClick_unhighlight(e, strng, apnd=0):
            getGlobalRoot().unHighlightWord(strng)

        e.widget.focus()

        optionList = []


        highlighted = getGlobalRoot().getHighlightedWord()
        if highlighted is not None:
            if getGlobalRoot().wordInHighlightList(highlighted):
                optionList.append(('Un-Highlight:' + highlighted, lambda e=e: rClick_unhighlight(e, highlighted)))
            else:
                optionList.append(('Highlight:' + highlighted, lambda e=e: rClick_highlight(e, highlighted)))


        selected = getGlobalRoot().getSelectedWord()
        if selected is not None:
            if getGlobalRoot().wordInHighlightList(selected):
                optionList.append(('Un-Highlight:' + selected, lambda e=e: rClick_unhighlight(e, selected)))
            else:
                optionList.append(('Highlight:' + selected, lambda e=e: rClick_highlight(e, selected)))

        unhiglightDuty = getGlobalRoot().unHighlightDuty(selected, highlighted)
        for word in unhiglightDuty:
            if getGlobalRoot().wordInHighlightList(word):
                optionList.append(('Un-Highlight:' + word, lambda e=e: rClick_unhighlight(e, word)))

        popupWindow = tk.Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in optionList:
            popupWindow.add_command(label=txt, command=cmd)

        popupWindow.tk_popup(e.x_root+40, e.y_root+10, entry="0")

    except tk.TclError as e:
        print("Something wrong")
        print(str(e))
        pass

    return "break"



## THIS method is how you open this bohemuth!
def open_display(width, height, linesOfView, specialReports, showPopUp, useExistingHighlights):
    assert isinstance(width, int)
    assert isinstance(height, int)
    assert isinstance(linesOfView, list)
    assert isinstance(specialReports, list)
    assert isinstance(showPopUp, bool)
    assert isinstance(useExistingHighlights, bool)

    window = SmartLogView()
    window.prepare(linesOfView, specialReports, showPopUp, useExistingHighlights)
    setGlobalRoot(window)
    window.geometry(str(width) + "x" + str(height))
    window.resizable(True, True)

    existingHighlights = []
    if useExistingHighlights:
        existingHighlights = read_list()

    window.set_highlight_list(existingHighlights)

    # Bind the right click menu
    window.bind('<Button-2>',right_click_handler, add='')

    window.mainloop()
