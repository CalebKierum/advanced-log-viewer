class StateMonitoringTool:

    def __init__(self, start_delimiter = "<<<", end_delimiter = ">>>", update_separator = ",", level_separator = ".", placeholder_text="Placeholder"):
        self.start_delimiter = start_delimiter
        self.end_delimiter = end_delimiter
        self.update_separator = update_separator
        self.placeholder_text = placeholder_text
        self.level_separator = level_separator


    def evidence_of_monitoring_in_string(self, the_string):
        """Checks if string contains evidence of monitoring"""
        if the_string.find(self.start_delimiter) == -1:
            return False
        if the_string.find(self.end_delimiter) == -1:
            return False
        return the_string.find(self.start_delimiter) < the_string.find(self.end_delimiter)

    def clean_monitoring_from_string(self, theString):
        """Removes monitoring statements from string"""
        start = theString.find(self.start_delimiter)
        end = theString.find(self.end_delimiter)
        result = theString[0:start] + theString[end + len(self.end_delimiter):]
        assert result.find(self.start_delimiter) == -1
        return result


    def get_placeholder(self):
        """Returns the placeholder string"""
        return self.start_delimiter + self.placeholder_text + self.end_delimiter


    # Implements monitoring on strings like <<<key.path=this,key.value=two>> as complete lines
    # Or inside or at the end of the line
    def get_state_dictionary(self, file_str, start_char, end_char):
        """Returns a dictionary representation a summary of all class updates in file from
        start_char to end_char. Set end_char to 0 if it should look to end"""
        assert start_char is not -1
        assert end_char is not -1

        if end_char == 0:
            end_char = len(file_str)

        build_up = {}
        progress = start_char
        while True:
            start_index = file_str.find(self.start_delimiter, progress)
            end_index = file_str.find(self.end_delimiter, start_index)
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

            report_content = file_str[start_index + len(self.start_delimiter):end_index]
            parts = report_content.split(self.update_separator)
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

    def string_statement_of_dictionary(self, dictionary):
        """Returns a string version of the class monitoring dictionary"""
        build = self.start_delimiter
        first = True
        for key in dictionary:
            if first:
                first = False
            else:
                build += self.update_separator
            build += key + "=" + dictionary[key]
        build += self.end_delimiter
        return build


    # Converts classMonitoringDict to this format
    def heiarchical_dict_of_state_monitoring_dictionary(self, state_monitoring_dict):
        dictionary = state_monitoring_dict
        heiarchical_dictionary = {}
        for key in dictionary:
            parts = key.split(self.level_separator)
            if len(parts) == 0:
                parts = [key]
            assert len(parts) > 0

            relevant_dictionary = heiarchical_dictionary
            for num, part in enumerate(parts):
                is_last = num == (len(parts) - 1)
                if not part in relevant_dictionary:
                    if is_last:
                        relevant_dictionary[part] = dictionary[key]
                    else:
                        relevant_dictionary[part] = {}
                else:
                    if not isinstance(relevant_dictionary[part], dict):
                        if not is_last:
                            print("WARNING! Invalid input in this classMonitoringDict")
                            print("WARNING! Cant have multiple keypath depths \n\tex: apple.banana=cranberry, apple=walnut as those two paths have different lenghts\n\tIn this case the key path apple has both a depth of 0 AND 1")
                            print("WARNING! Cant have multiple keypath depths \n\tex: apple.banana.pineapple=cranberry, apple.banana=walnut as those two paths have different lenghts\n\tIn this case the key path apple.banana has both a depth of 0 AND 1")
                            print("\nWE WILL PROBABLY CRASH")
                relevant_dictionary = relevant_dictionary[part]

        return heiarchical_dictionary








def __unit_test():
    monitor = StateMonitoringTool()
    assert monitor.clean_monitoring_from_string("<<<HELLO>>>") == ""
    assert monitor.clean_monitoring_from_string("bef<<<HELLO>>>aft") == "befaft"
    assert monitor.clean_monitoring_from_string("<<<HELLO>>>aft") == "aft"
    assert monitor.clean_monitoring_from_string("bef<<<HELLO>>>aft") == "befaft"
    assert monitor.clean_monitoring_from_string("bef <<<HELLO>>> aft") == "bef  aft"
    assert monitor.clean_monitoring_from_string("<<<>>>") == ""
    assert monitor.clean_monitoring_from_string("bef<<<>>>aft") == "befaft"
    assert monitor.clean_monitoring_from_string("<<<>>>aft") == "aft"
    assert monitor.clean_monitoring_from_string("bef<<<>>>aft") == "befaft"

__unit_test()
