import re
import sys

def fail_with_message(message):
    print(message)
    assert False
    sys.exit(message)


def assert_argument_is_not_file_name(argument):
    start_string = "Argument \"" + argument + "\" may be a filename instead of a file string"
    if len(argument) < 100:
        fail_with_message(start_string + " argument is under 100 chars")
    else:
        extract = argument[:min(len(argument), 4000)]
        if not "\n" in extract:
            fail_with_message(start_string + " couldnt fine new line in the first bit")


def read_file_to_string(file_name):
    with open(file_name, 'r') as file:
        return file.read().replace('\n', '\n')


def get_first_last_line_list(fileString):
    assert_argument_is_not_file_name(fileString)
    whole_log = fileString
    break_seq = "--------------------------------------------------"
    false_break_seq = "=================================================="
    whole_log = whole_log.replace(false_break_seq, break_seq)
    progress = 0

    result = []

    while True:
        start_marker = whole_log.find(break_seq, progress)
        end_start_marker = whole_log.find("\n", start_marker + 1)
        start_line = whole_log[end_start_marker:whole_log.find("\n", end_start_marker + 1)].strip()
        if start_marker is -1:
            break

        end_marker = whole_log.find(break_seq, start_marker + 1)
        assert start_marker != end_marker
        progress = end_marker
        end_line_start = whole_log.rfind("\n", start_marker, end_marker - 1)
        assert end_line_start > start_marker
        last_line = whole_log[end_line_start:end_marker].strip()
        assert len(last_line) > 2
        passed = last_line.find("PASS") != -1
        if len(start_line) < 10:
            break

        summary = ""
        if not passed:
            if end_marker == -1:
                summary += "INCOMPLETE!"
            else:
                summary += "FAILED!"
        else:
            summary += "PASSED!"



        testnum = int(re.findall(r'^\D*(\d+)', start_line)[0])
        result.append({"startLine": start_line,
                       "lastLine": last_line,
                       "passed": passed,
                       "testnum": testnum,
                       "summary": summary,
                       "startMarker":start_marker,
                       "endMarker":end_marker})

    return result
