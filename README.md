# Advanced Log Viewer - Beta
A python based cross-platform log viewer with powerful features like historical summaries and advanced highlighting.

## Why this tool?
1. You should never have to scroll backwards in a log to determine your state at a current line
2. Extensive state update printing crowds your log
3. Highlighting

#### Screenshot
![Full Screenshot](https://raw.githubusercontent.com/CalebKierum/Advanced-Log-Viewer/master/Images/Entire%20Screen.png)

### Warning
This is a beta software. I wrote this very quickly while also trying to get through University coursework. It is littered with typos and probably errors too. There will be bugs. Some of them may crash the software, others may cause the console to subtly print out warnings, others may cause correct input. For the most part it will be correct but if something really does not make sense make sure to look at the log in a different viewer or ignore the top view.

## ToDo List
- Add ctrl+f
- Add jumpt to line
- Add stable upper log viewing
- Implement moveable divider in upper log
- Make more general (EX: move classMonitoringTools out of classMonitoringTools)

## Feature List

### Highlighting
Right out of the box you can view any log with highlighting.

Highlighting allows you to right click on any word or after highlighting some text and highlight all instances of a word. They can also be unhighlited from this menu.

![Highlighting](https://raw.githubusercontent.com/CalebKierum/Advanced-Log-Viewer/master/Images/Higlight.png)


### Summary View
On the top of the window you may place summary.

## Getting Started

Clone the repository and set up git lfs
```
git clone https://github.com/CalebKierum/Advanced-Log-Viewer.git
cd Advanced-Log-Viewer
brew install git-lfs
git lfs install
```

Then make sure you have the necessary python dependencies by pip installing them
```
setuptools
```
And then get tkinter set up by following [their instructions](https://tkdocs.com/tutorial/install.html)



### Getting started with highlighting

TBD

### Adding summary views

## Special Usages
### Java

TBD

#### DSLabs

![DSLabsUsage](https://raw.githubusercontent.com/CalebKierum/Advanced-Log-Viewer/master/Images/Console%20Summary.png)

This tool was specifically designed for this use case. To plug in your project all you need to do is add statements into the logging code so that the extra lines are printed out. You will want to join all output by piping it into a file
```
./run-tests.py --assertions -g FINEST --lab 2 &> testAll.log  
```
Then open the log inside of this program
```
python3 dslabs/ds_log_view.py testAll.log
```
Follow the instructions given by the console to open it up!

To populate the upper view you will need to add the `dslabs/Plugin/Alt.java` to your code and make calls to it.

##### Attaching State Updates
State updates track any value you want to conceptually follow. So for example if I wanted to monitor what each server was doing at a given line in the log I could do `ALT.log("Server", address(), "state", "primary")` or `ALT.log("Server", address(), "state", "backup")` and the value `Server.server1.state` would be tracked. So all you need to do is make calls to `ALT.log(...)` which can take any length of arguments. 

![State Updates](https://raw.githubusercontent.com/CalebKierum/Advanced-Log-Viewer/master/Images/State%20Update%20Monitoring.png)

##### Attaching Class Updates
This framework can also track your Node's and every variable (including private) within them. Essentially you need to pass the node into the framework with `ALT.trackNode(object)` at some point... preferably in the constructor. For the most part ALT will take care of everything as it holds a weak reference so it should not effect tests.

Please note that the framework has the option to serialize/deserialize this object at will. If you are worried about that happening and still want to keep the trace add the following method to your class
```
    private void readObject(java.io.ObjectInputStream in)
            throws IOException, ClassNotFoundException {
        in.defaultReadObject();
        ALT.trackNode(this);
    }
```

Now in order to decrease printing you do have to call `refresh()` every time you want ALT to check and report new values. I recommend calling refresh from the end of every message handler etc.

![Class Updates](https://raw.githubusercontent.com/CalebKierum/Advanced-Log-Viewer/master/Images/Object%20Update%20Monitoring.png)

## Feature Requests
Please open any and all feature requests as Issues

## Bugs
Please do report any and all errors you find. If it crashes or behaves incorrectly I would much appreciate hearing about it.

## Contributing
Submit a pull request! I would love any and all help with this. If you know how to beautify the code in any way I appreciate that greatly. I am fairly new to python so may not be doing this right.
