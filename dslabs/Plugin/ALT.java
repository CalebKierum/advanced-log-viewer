package dslabs.primarybackup;

import java.util.HashMap;
import dslabs.framework.*;
import java.util.*;
import java.io.*;
import java.lang.reflect.*;

class ALTPriv {

    static void internalLog(String str) {
        System.out.println("[INTERNAL LOGGER]" + str);
    }


    private static Set<Node> weakNodeHashSet = Collections.newSetFromMap(
            new WeakHashMap<Node, Boolean>());
    static synchronized void logNode(Node node) {
        weakNodeHashSet.add(node);
        refreshNodeLog();
    }



    private static Set<String> newSetWithRemoved(Set<String> motherList, Set<String> removalList) {
        Set<String> build = new HashSet<String>(motherList);
        build.removeAll(removalList);

        //System.out.println("FANCY REMOVE ALL " + motherList.toString() + " - " + removalList.toString() + " = " + build.toString());
        return build;
    }
    private static Set<String> newSetWithIntersected(Set<String> motherList, Set<String> removalList) {
        Set<String> build = new HashSet<String>(motherList);
        build.retainAll(removalList);

        //System.out.println("FANCY REMOVE ALL " + motherList.toString() + " - " + removalList.toString() + " = " + build.toString());
        return build;
    }


    // Manage removal and adding of nodes
    private static Set<String> oldAddresses = new HashSet<String>();
    private static String logThis = "";
    private static void reportUpdatedServerValue(String address, String variable, String value, String debug) {
        logThis += address + "." + variable + "=" + value + " & ";
    }
    private static void reportUpdatedServerValue(String address, String variable, String value) {
        reportUpdatedServerValue(address, variable, value, "UPDATED!");
    }
    static synchronized void refreshNodeLog() {
        logThis = "";
        Set<String> currentTrackedNodes = new HashSet<String>();
        for (Node n : weakNodeHashSet) {
            currentTrackedNodes.add(n.address().toString());
        }

        // Prepare to report updated infos
        HashMap<String, String> oldInfos = new HashMap<String, String>();
        for (String key : nodeLog.keySet()) {
            oldInfos.put(key, nodeLog.get(key).get(INFOSTR));
        }

        Set<String> deletedNodes = newSetWithRemoved(oldAddresses, currentTrackedNodes);
        for (String s : deletedNodes) {
            HashMap<String, String> theNodeLog = nodeLog.get(s);
            assert(theNodeLog != null);
            theNodeLog.put(INFOSTR, "Allegedly Deleted/Removed");
            nodeLog.put(s, theNodeLog);
        }
        oldAddresses = currentTrackedNodes;

        for (Node n : weakNodeHashSet) {
            String s = n.address().toString();
            if (nodeLog.get(s) == null) {
                HashMap<String, String> make = new HashMap<String, String>();
                make.put(INFOSTR, "New To Log");
                nodeLog.put(s, make);
            } else {
                nodeLog.get(s).put(INFOSTR, "");
            }
            assert(nodeLog.get(s) != null);
            assert(nodeLog.get(s).get(INFOSTR) != null);

            String mes = processLogUpdatesForNode(n);
            HashMap<String, String> current = nodeLog.get(s);
            assert(current.get(INFOSTR) != null);
            assert(nodeLog.get(s) != null);
            assert(nodeLog.get(s).get(INFOSTR) != null);
            current.put(INFOSTR,  nodeLog.get(s).get(INFOSTR) + mes);
            nodeLog.put(s, current);
        }

        // Report updated infos
        Set<String> newKeys = newSetWithRemoved(nodeLog.keySet(), oldInfos.keySet());
        for (String s : newKeys) {
            reportUpdatedServerValue(s, INFOSTR,  nodeLog.get(s).get(INFOSTR), "INFO NEW");
        }

        for (String s : oldInfos.keySet()) {
            String older = oldInfos.get(s);
            String newer = nodeLog.get(s).get(INFOSTR);
            if (!older.equals(newer)) {
                reportUpdatedServerValue(s, INFOSTR,  "\"" + older + "\""  + "->" + "\""  + newer + "\"" , "INFO UPDATED");
            }
        }

        if (logThis.equals("")) {
            //System.out.println("NO UPDATES");
        } else {
            //System.out.println("UPDATES\n" + logThis + "DONE");
            String p = "<<<" + logThis.substring(0, logThis.length() - 3) + ">>>";
            System.out.println(p);
        }
    }

    // Each node needs to update the node log
    private static HashMap<String, HashMap<String, String>> nodeLog = new HashMap<String, HashMap<String, String>>();
    private static final String INFOSTR = "INFO";
    private static synchronized String processLogUpdatesForNode(Node n) {
        String build = "";

        HashMap<String, String> currentFieldValues = getInfoOn(n);
        String a = n.address().toString();
        HashMap<String, String> oldLoggedFields = nodeLog.get(a);
        assert(oldLoggedFields != null);

        Set<String> currentFields = new HashSet<String>(currentFieldValues.keySet());
        Set<String> lastFields = new HashSet<String>(oldLoggedFields.keySet());
        currentFields.remove(INFOSTR);
        lastFields.remove(INFOSTR);

        // newFields
        Set<String> newFields = newSetWithRemoved(currentFields,lastFields);
        if (newFields.size() > 0) {
            build += "| New Field |";
        }
        for (String s : newFields) {
            assert(newFields.size() != 0);
            reportUpdatedServerValue(a, s, currentFieldValues.get(s), "FIELD NEW");
            oldLoggedFields.put(s, currentFieldValues.get(s));
        }

        // removedFields
        Set<String> removedFields = newSetWithRemoved(lastFields,currentFields);
        if (removedFields.size() > 0) {
            build += "| Removed Fields |";
        }
        for (String s : removedFields) {
            reportUpdatedServerValue(a, s, "DELETED!?", "FIELD DELETE");
            oldLoggedFields.remove(s);
        }

        // continuedFields
        Set<String> continuedFields = newSetWithIntersected(currentFields,lastFields);
        for (String s : continuedFields) {
            String older = oldLoggedFields.get(s);
            String newer = currentFieldValues.get(s);
            if (!older.equals(newer)) {
                reportUpdatedServerValue(a, s, newer, "FIELD UPDATED");
                oldLoggedFields.put(s, newer);
            }
        }

        nodeLog.put(a, oldLoggedFields);

        return build;
    }

    // Each node uses refelction to get info
    private static synchronized HashMap<String, String> getInfoOn(Node n) {
        Set<Field> allFields = new HashSet<Field>();

        Class<?> current = n.getClass();
        while(current != null && current.getSuperclass()!=null) { // we don't want to process Object.class
            // do something with current's fields


            Field[] currentClassFields = current.getDeclaredFields();
            for (Field field : currentClassFields) {
                allFields.add(field);
            }


            //current = current.getSuperclass();
            current = null;
        }

        HashMap<String, String> build = new HashMap<String, String>();
        for (Field f : allFields) {
            try {
                f.setAccessible(true);
                if (!f.getName().startsWith("$")) {
                    String value = ALT.objPrint(f.get(n));
                    if (ALT.LOGAPPLICAION || !value.contains("application=")) {
                        build.put(f.getName(), value);
                    }
                }
            } catch (Exception e) {
                System.out.println("ERR " + e.toString());
            }
        }
        return build;
    }
}

public class ALT {
    public static final boolean LOGAPPLICAION = false;

    public static boolean AvoidRepeats = false;
    private static HashMap<String, String> avoidingRepeatsTable = new HashMap<String, String>();

    // Logs a list of objects
    // Will only log CHANGES to the LAST value passed in
    // Ex: printing Server server1 ViewNum 1 should be done with log("Server", address().toString(), "ViewNum", viewNum)
    //     And an updated value will only be printed if this method is called with new argument values (EX new viewNum)
    public static void log(Object ... args) {
        String build = "";
        String preLast = "";
        String last = "";
        boolean first = true;
        for (int i = 0; i < args.length; i++) {
            Object obj = args[i];
            String description = objPrint(obj);

            if (first) {
                first = false;
            } else {
                if (i == args.length - 1) {
                    build += "=";
                } else {
                    build += "|";
                }
            }

            build += description;
            if (i == args.length - 2) {
                preLast = build;
            } else if (i == args.length - 1) {
                last = description;
            }
        }

        if (AvoidRepeats) {
            if (avoidingRepeatsTable.get(preLast) != null) {
                if (avoidingRepeatsTable.get(preLast).equals(last)) {
                    return;
                }
            }
        }

        String prt = "${" + build + "}$";
        System.out.println(prt);
        if (AvoidRepeats) {
            avoidingRepeatsTable.put(preLast, last);
        }
    }

    // If the condition fails the program will stop
    public static void fatalassert(boolean condition) {
        if (!condition) {
            Thread.dumpStack();
            System.exit(0);
            assert(false);
        }
    }

    // Refreshes the list of tracked nodes and logs new values if needed
    // Somewhat expensive method to call
    public static synchronized void refresh() {
        ALTPriv.refreshNodeLog();
    }


    // Adds a node to the tracking list
    // NOTE: Some objects get deserialized/reserialized so make sure to attach to
    // those methods if necessary
    public static void trackNode(Node node) {
        ALTPriv.logNode(node);
    }

    public static String objPrint(Object o) {
        if (o == null) {
            return "null";
        }
        return o.toString();
    }
}
