#include <process.h>
#include <windows.h>
#include <shlwapi.h>

#pragma comment(lib, "user32.lib")
#pragma comment(lib, "shlwapi.lib")

bool dir_exists(const char *dir) {
    DWORD ftyp = GetFileAttributes(dir);
    if (ftyp == INVALID_FILE_ATTRIBUTES)
        return false;  //something is wrong with your path!
    return (ftyp & FILE_ATTRIBUTE_DIRECTORY);
}

bool file_exists(const char *file) {
    DWORD ftyp = GetFileAttributes(file);
    if (ftyp == INVALID_FILE_ATTRIBUTES)
        return false;  //something is wrong with your path!
    return !(ftyp & FILE_ATTRIBUTE_DIRECTORY);
}

char *message = "You need .NET Framework 4.0 to run the better 'Launcher and Updater'.\n"
                "Click yes to install .NET and run the better version;\n"
                "Or click no to use the simpler version.";

int WinMain(HINSTANCE hInstance, HINSTANCE hPrevInst, LPSTR lpCommandLine, int nCmdShow) {
    char directory[MAX_PATH], buf[MAX_PATH], *ptr;
    GetModuleFileName(NULL, directory, MAX_PATH);
    ptr = PathFindFileName(directory);
    ptr[0] = '\0';
    PathCombine(buf, directory, "system");
    if (!dir_exists(buf))
        CreateDirectory(buf, NULL);
    SetCurrentDirectory(buf);

    ptr = getenv("WINDIR");
    PathCombine(buf, ptr, "Microsoft.NET\\Framework\\v4.0.30319");

    char *argv[2];
    check:
    if (dir_exists(buf)) {
        argv[0] = "HALupdater.exe";
        argv[1] = NULL;
        _spawnvp(_P_OVERLAY, argv[0], argv);
    } else {
        switch (MessageBox(NULL, message, "Install .NET?", MB_YESNO|MB_ICONQUESTION)) {
            case IDYES:
                argv[0] = "get.net.exe";
                argv[1] = NULL;
                _spawnvp(_P_WAIT, argv[0], argv);
                goto check;
                break;
            case IDNO:
                argv[0] = "updater.exe";
                argv[1] = NULL;
                _spawnvp(_P_OVERLAY, argv[0], argv);
                break;
        }
    }
}
