Did it happen, if somebody was interested in your Python script, you wanted to share, but you had no idea how to do it? Because it requires Python installed for the user with all the necessary dependencies. Additionally, the black console window of the application scares people who are far from programming. Fortunately, there are ways to build a simple GUI and pack the script into an executable file (EXE-file in case of Windows, for example). This is what I would like to share with you below. Having a certain example, step by step we will consider how to transform a raw Python console application into an executable file that is ready to distribute.

The repository with the files and configurations we are considering below are represented here: https://github.com/fomalhaut88/count-lines

## Step 1. Writing an application

Let our program count the total number of lines for the files with specified extensions and located in a given folder. This can be helpful, for example, to estimate the quantity of code for different programming languages in a project. It can be easily developed, here is an implementation in Python (file `count_lines_script.py`):

```python
import os


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


if __name__ == "__main__":
    result = count_lines(r'C:\Users\alexander\Development\gui-args-framework', 
                         ext_list=['py'], recursive=True)
    print(result)
```

## Step 2. Build a GUI

The disadvantage of the script above is the need to modify it every time when we need to run it for a different folder, different extensions and other options. Therefore it is time to think about a convenient GUI. And in this case [gui-args-framework](https://pypi.org/project/gui-args-framework/) may help, that creates a window of the application with all the necessary interactive elements by several modifications.

To install `gui-args-framework` run:

```
pip install gui-args-framework
```

The changes that we need to make in our script (file `count_lines_gui.py`):

```python
...

from gui_args_framework.args_window import ArgsWindow
from gui_args_framework.fields import DirectoryField, StringField, BooleanField

...

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
```

As we can see in the example, it was enough to write down some parameters for the window and bind the function `count_lines` to the handler `main`, that is run in the GUI. Full documentation of [gui-args-framework](https://github.com/fomalhaut88/gui-args-framework) is available by the link.

## Step 3. Compile into an executable file

In order to compile the project into a single executable file, we can use [Pyinstaller](https://pypi.org/project/pyinstaller/). It can be installed by following command:

```
pip install pyinstaller
```

After that we need a configuration `count-lines.spec`:

```python
# -*- mode: python -*-

block_cipher = None

datas = []
a = Analysis(['count_lines_gui.py'],
             pathex=[],
             binaries=None,
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='count-lines',
          debug=False,
          strip=False,
          upx=True,
          console=False)
```

To compile we run:

```
pyinstaller count-lines.spec
```

Once it is done, the executable file will appear in the folder `dist`. Actually, it is enough for distribution. Although, in case of Windows, we may need to make our program installable. And this is what **Step 4** is about.

## Step 4. Create a Windows installer

To create a setup wizard we are using [Inno Setup](https://jrsoftware.org/isinfo.php) (it can be downloaded and installed from the official website). And we also need the configuration `count-lines.iss`:

```
; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Count Lines"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Your name"
#define MyAppURL "https://example.com/"
#define MyAppSnakeName "count-lines"
#define MyAppExeName "count-lines.exe"
#define MyAppId "F0A1B35B-41D5-4542-B9B3-413795B3447F"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{{#MyAppId}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=.\dist
OutputBaseFilename={#MyAppSnakeName}64-setup-{#MyAppVersion}
; SetupIconFile=.\{#MyAppSnakeName}.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: ".\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
```

For every new application it is necessary to edit first lines of the configuration (started with `#define`), so the application will have the correct name, version, etc. Pay attention at the option `MyAppId`, this is a unique ID, that is used by Windows to distinguish applications. It must be different for different applications and the same for different versions of one application. To generate a new value of `MyAppId` there are many ways. Here is how to do it with Python:

```
python -c "from uuid import uuid4; print(str(uuid4()).upper())"
```

Once the configuration file is ready, run this command to create a setup wizard:

```
iscc count-lines.iss
```

After that in the folder `dist` the installer `count-lines64-setup-0.1.0.exe` will appear. It can be uploaded to [Source Forge](https://sourceforge.net/) or anywhere else.
