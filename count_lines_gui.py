import os

from gui_args_framework.args_window import ArgsWindow
from gui_args_framework.fields import DirectoryField, StringField, BooleanField


def _check_ext(name, ext_list):
    if ext_list:
        # The given name ends with any of the extensions in the given list
        return any(name.endswith('.' + ext) for ext in ext_list)
    else:
        # If no list of extensions provided we return True
        return True


def _get_lines_count(path):
    try:
        with open(path) as f:
            # This for-loop iterates lines as a generator,
            # so it is an efficient way to count the total number of lines
            return sum(1 for _ in f)
    except UnicodeDecodeError:
        # We return 0 if the file can't be opened normally as a text
        return 0


def count_lines(folder, ext_list=None, recursive=False):
    # Result variable
    result = 0

    # Loop for files and directories inside of the given folder
    for name in os.listdir(folder):
        # Path to the file
        path = os.path.join(folder, name)

        # If item is a file check its extension and increase the result
        if os.path.isfile(path):
            if _check_ext(name, ext_list):
                result += _get_lines_count(path)

        # Else if item is a directory and recursive flag is set we count the number
        # of lines recursively and add it to the result
        elif recursive and os.path.isdir(path):
            result += count_lines(path, ext_list=ext_list, recursive=recursive)

    # Return the result
    return result


class TestWindow(ArgsWindow):
    title = "Count lines"
    args = [
        DirectoryField(name='folder', label='Path to folder'),
        StringField(name='ext_list', 
                    label='Extensions separated by | (example: txt|py)',
                    required=False),
        BooleanField(name='recursive', label='Recursive', default=True),
    ]
    description = "This program calculates total number of lines " \
                  "of the files in the given folder."

    def main(self, this):
        result = count_lines(
            this['folder'],
            ext_list=this['ext_list'].split('|'),
            recursive=this['recursive'],
        )
        this.message(f"Total number of lines: {result}")


if __name__ == "__main__":
    TestWindow.run()
