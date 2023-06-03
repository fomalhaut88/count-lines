Бывало ли у вас такое, что вашим Python скриптом кто-то заинтересовался и вам хотелось им поделиться, но вы не знали, как это сделать? Ведь для запуска нужно, чтобы у пользователя был установлен Python необходимой версией, да ещё и со всеми зависимостями. Плюс, чёрное окно консольного приложения зачастую наводит ужас на людей, далёких от программирования. К счастью, есть способы сделать простой графический интерфейс и запаковать скрипт в исполняемый файл (например, EXE для Windows). Именно об этом и пойдёт речь ниже. Мы на конкретном примере шаг за шагом разберём, как превратить сырое приложение на Python в устанавливаемую утилиту, готовую к распространению.

Репозиторий с файлами скриптов и конфигураций, о которых идёт речь ниже, размещён здесь: https://github.com/fomalhaut88/count-lines

## Шаг 1. Пишем приложение

Пусть наша программа считает суммарное количество строк в файлах определённых форматов, находящихся в указанной папке. Это может быть полезно, например, для оценки количества кода на разных языках в каком-либо проекте. Здесь всё просто, вот пример реализации на Python (файл `count_lines_script.py`):

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

## Шаг 2. Создаём графический интерфейс

Недостатком скрипта является необходмость вносить изменения всякий раз, когда требуется запустить его для новой папки, нового списка расширений и других параметров. Поэтому самое время подумать об удобном графическом интерфейсе. И в этом нам поможет мой специальный фреймворк [gui-args-framework](https://pypi.org/project/gui-args-framework/), который несколькими дополнениями создаёт окно программы с нужными интерактивными элементами.

Для установки `gui-args-framework` необходимо выполнить:

```
pip install gui-args-framework
```

Изменения, которые необходимо сделать в коде (файл `count_lines_gui.py`):

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

Как мы видим в примере, оказалось достаточным вписать необходимые параметры для создания окна и привязать написанную выше функцию `count_lines` к логике, запускаемой в графическом интерфейсе. Полную документацию [gui-args-framework](https://github.com/fomalhaut88/gui-args-framework) можно посмотреть, перейдя по ссылке.

## Шаг 3. Компилируем в исполняемый файл

Для того, чтобы запаковать проект в один исполняемый файл, воспользуемся утилитой [Pyinstaller](https://pypi.org/project/pyinstaller/). Её можно установить командой:

```
pip install pyinstaller
```

Далее нам понадобится скрипт с конфигурацией для сборки `count-lines.spec`:

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

Запуск сборки осуществляется командой:

```
pyinstaller count-lines.spec
```

После этого исполняемый файл появится в папке `dist`. В принципе он уже готов для распространения. Ho в случае Windows нам может потребоваться сделать программу устанавливаемой. И этому посвящён **Шаг 4**.

## Шаг 4. Создаём установщик для Windows

Для создания установщика воспользуемся [Inno Setup](https://jrsoftware.org/isinfo.php) (установить можно с официального сайта). И нам потребуется файл конфигурации `count-lines.iss`:

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

Для каждого нового приложения необходимо отредаркировать первые строки (начинающиеся с `#define`), чтобы задать правильные значения для названия приложения, версии и тд. Особое внимание следует обратить на `MyAppId` - это уникальный ID, через которое Windows различает приложения. Он должен быть разным для разных приложений и одинаковым для разных версий одного и того же приложения. Сгенерировать новое значение `MyAppId` можно многими способами. Вот один из них с помощью Python:

```
python -c "from uuid import uuid4; print(str(uuid4()).upper())"
```

После того, как файл конфигурации приготовлен, запаковать приложение можно следующей командой:

```
iscc count-lines.iss
```

После этого в папке `dist` появится установочный файл `count-lines64-setup-0.1.0.exe`. Его можно разместить на [Source Forge](https://sourceforge.net/) или где бы то ни было ещё.
