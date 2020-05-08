import log_read_tools

START_DELIMITER = "<<<"
END_DELIMITER = ">>>"
UPDATE_DELIMITER = ","

# Implements monitoring on strings like <<<key.path=this,key.value=two>> as complete lines
# Or inside or at the end of the line

def get_state_dictionary(file_str, start_char, end_char):
    """Returns a dictionary representation a summary of all class updates in file from
     start_char to end_char. Set end_char to 0 if it should look to end"""
    assert start_char is not -1
    assert end_char is not -1

    if end_char == 0:
        end_char = len(file_str)

    build_up = {}
    progress = start_char
    while True:
        start_index = file_str.find(START_DELIMITER, progress)
        end_index = file_str.find(END_DELIMITER, start_index)
        if (start_index > end_char or start_index < start_char):
            start_index = -1

        if (end_index > end_char or end_index < start_char):
            end_index = -1

        if start_index is -1:
            break
        if end_index is -1:
            print("ALERT! Found a classMonitoring delimiter that did not have an end...\
                 may be an error")
            break

        report_content = file_str[start_index + len(START_DELIMITER):end_index]
        parts = report_content.split(UPDATE_DELIMITER)
        if len(parts) == 0:
            print("ALERT! Generally a class monitoring statement should have at least\
                 one update")
        for part in parts:
            if not "=" in part:
                print("ALERT! There is a statent inside of a clas monitoring thing that\
                     does not have an equals... sketchy")
                continue
            if "," in part:
                print("ALERT! There shouldnt be two commas by eachother in a class monitoring\
                    statement..... sketchy")

            pieces = part.split("=")
            assert len(pieces) == 2
            build_up[pieces[0]] = pieces[1]

        progress = end_index

    return build_up

def string_statement_of_dictionary(dictionary):
    """Returns a string version of the class monitoring dictionary"""
    build = START_DELIMITER
    first = True
    for key in dictionary:
        if first:
            first = False
        else:
            build += UPDATE_DELIMITER
        build += key + "=" + dictionary[key]
    build += END_DELIMITER
    return build

def evidence_of_class_monitoring_in_string(the_string):
    """Checks if string contains evidence of class monitoring"""
    if the_string.find(START_DELIMITER) == -1:
        return False
    if the_string.find(END_DELIMITER) == -1:
        return False
    return the_string.find(START_DELIMITER) < the_string.find(END_DELIMITER)

def clean_class_monitoring_from_string(theString):
    """Removes class monitoring statements from string"""
    start = theString.find(START_DELIMITER)
    end = theString.find(END_DELIMITER)
    result = theString[0:start] + theString[end + len(END_DELIMITER):]
    assert result.find(START_DELIMITER) == -1
    return result


def get_placeholder():
    """Returns the placeholder string"""
    return START_DELIMITER + "Placeholder" + END_DELIMITER

def __unit_test():
    assert clean_class_monitoring_from_string("<<<HELLO>>>") == ""
    assert clean_class_monitoring_from_string("bef<<<HELLO>>>aft") == "befaft"
    assert clean_class_monitoring_from_string("<<<HELLO>>>aft") == "aft"
    assert clean_class_monitoring_from_string("bef<<<HELLO>>>aft") == "befaft"
    assert clean_class_monitoring_from_string("bef <<<HELLO>>> aft") == "bef  aft"
    assert clean_class_monitoring_from_string("<<<>>>") == ""
    assert clean_class_monitoring_from_string("bef<<<>>>aft") == "befaft"
    assert clean_class_monitoring_from_string("<<<>>>aft") == "aft"
    assert clean_class_monitoring_from_string("bef<<<>>>aft") == "befaft"

__unit_test()
