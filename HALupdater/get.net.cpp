#include <stdio.h>
#include <process.h>
#include <windows.h>
#include <objbase.h>
#include <shlwapi.h>
#include <commctrl.h>
#pragma comment(lib, "lzma.lib")
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "urlmon.lib")
#pragma comment(lib, "comctl32.lib")

HINSTANCE g_hinst;
HWND hwndPB, hwnd;
const char g_szClassName[] = "DotNETDownloader";

char file[MAX_PATH];
char *url = "http://download.microsoft.com/download/7/B/6/7B629E05-399A-4A92-B5BC-484C74B5124B/dotNetFx40_Client_setup.exe";

class CCallback : public IBindStatusCallback  
{
public:
    CCallback() {}
    ~CCallback() {}
    ULONG max;
    STDMETHOD(OnStartBinding)(DWORD dwReserved, IBinding __RPC_FAR *pib) { return E_NOTIMPL; }
    STDMETHOD(GetPriority)(LONG __RPC_FAR *pnPriority) { return E_NOTIMPL; }
    STDMETHOD(OnLowResource)(DWORD reserved) { return E_NOTIMPL; }
    STDMETHOD(OnProgress)(ULONG ulProgress, ULONG ulProgressMax, ULONG ulStatusCode, LPCWSTR wszStatusText) {
        if (!(ulProgressMax|ulProgress))
            return E_NOTIMPL;
        max = ulProgressMax;
        //SendMessage(hwndPB, PBM_SETRANGE, 0, MAKELPARAM(0, ulProgressMax));
        //SendMessage(hwndPB, PBM_SETPOS, (WPARAM)ulProgress, 0);
        SendMessage(hwndPB, PBM_SETPOS, (WPARAM)((double)ulProgress/ulProgressMax*1000), 0);
        //printf(" Downloaded: %10d/%d   [%.2f%%]\r", ulProgress, ulProgressMax, ((double)ulProgress/ulProgressMax*100));
        return S_OK;
    }
    STDMETHOD(OnStopBinding)(HRESULT hresult, LPCWSTR szError) {
        SendMessage(hwnd, WM_CLOSE, 0, 0);
        return S_OK;
    }
    STDMETHOD(GetBindInfo)(DWORD __RPC_FAR *grfBINDF, BINDINFO __RPC_FAR *pbindinfo) { return E_NOTIMPL; }
    STDMETHOD(OnDataAvailable)(DWORD grfBSCF, DWORD dwSize, FORMATETC __RPC_FAR *pformatetc, STGMEDIUM __RPC_FAR *pstgmed) { return E_NOTIMPL; }
    STDMETHOD(OnObjectAvailable)(REFIID riid, IUnknown __RPC_FAR *punk) { return E_NOTIMPL; }
    STDMETHOD_(ULONG,AddRef)() { return 0; }
    STDMETHOD_(ULONG,Release)() { return 0; }
    STDMETHOD(QueryInterface)(REFIID riid, void __RPC_FAR *__RPC_FAR *ppvObject) { return E_NOTIMPL; }
};

CCallback callback;

DWORD WINAPI DownloadFileThread(LPVOID param) {
    URLDownloadToFile(NULL, url, file, 0, &callback);
    return 0;
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    RECT rcClient;
    int cyVScroll;
    static INITCOMMONCONTROLSEX iccex;
    iccex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    iccex.dwICC = ICC_PROGRESS_CLASS;
    switch(msg) {
        case WM_CREATE:
            InitCommonControlsEx(&iccex);
            GetClientRect(hwnd, &rcClient);
            cyVScroll = GetSystemMetrics(SM_CYVSCROLL);
            hwndPB = CreateWindowEx(0, PROGRESS_CLASS,
                                    NULL, WS_CHILD | WS_VISIBLE, 
                                    rcClient.left, 
                                    rcClient.bottom - cyVScroll, 
                                    rcClient.right, cyVScroll, 
                                    hwnd, (HMENU) 0, g_hinst, NULL);
            //SendMessage(hwndPB, PBM_SETRANGE, 0, MAKELPARAM(0,100));
            SendMessage(hwndPB, PBM_SETRANGE, 0, MAKELPARAM(0,1000));
            SendMessage(hwndPB, PBM_SETPOS, (WPARAM)0, 0);
            //URLDownloadToFile(NULL, url, file, 0, &callback);
            CreateThread(NULL, 0, DownloadFileThread, NULL, 0, NULL);
            break;
        case WM_CLOSE:
            DestroyWindow(hwnd);
            break;
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

//int main() {
int WinMain(HINSTANCE hInstance, HINSTANCE hPrevInst, LPSTR lpCommandLine, int nCmdShow) {
    g_hinst = hInstance;
    WNDCLASSEX wc;
    MSG Msg;
    GUID guid;
    char uuid[40], buf[MAX_PATH], *tempdir;
    
    CoCreateGuid(&guid);
    tempdir = getenv("TEMP");
    sprintf_s(uuid, sizeof(uuid), "{%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X}",
              guid.Data1, guid.Data2, guid.Data3,
              guid.Data4[0], guid.Data4[1],
              guid.Data4[2], guid.Data4[3],
              guid.Data4[4], guid.Data4[5],
              guid.Data4[6], guid.Data4[7]);
    strcpy(buf, uuid);
    strcat(buf, ".exe");
    PathCombine(file, tempdir, buf);

    //Step 1: Registering the Window Class
    wc.cbSize        = sizeof(WNDCLASSEX);
    wc.style         = 0;
    wc.lpfnWndProc   = WndProc;
    wc.cbClsExtra    = 0;
    wc.cbWndExtra    = 0;
    wc.hInstance     = hInstance;
    wc.hIcon         = LoadIcon(NULL, IDI_APPLICATION);
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
    wc.lpszMenuName  = NULL;
    wc.lpszClassName = g_szClassName;
    wc.hIconSm       = LoadIcon(NULL, IDI_APPLICATION);

    if (!RegisterClassEx(&wc))  {
        MessageBox(NULL, "Window Registration Failed!", "Error!",
                   MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    // Step 2: Creating the Window
    hwnd = CreateWindowEx(WS_EX_CLIENTEDGE, g_szClassName, "Downloading .NET Framework Installer",
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 500, 60,
        NULL, NULL, hInstance, NULL);
    if (hwnd == NULL) {
        MessageBox(NULL, "Window Creation Failed!", "Error!",
            MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    // Step 3: The Message Loop
    while(GetMessage(&Msg, NULL, 0, 0) > 0) {
        TranslateMessage(&Msg);
        DispatchMessage(&Msg);
    }
    char *argv[3];
    argv[0] = file;
    argv[1] = "/norestart";
    argv[2] = NULL;
    _spawnvp(_P_WAIT, file, argv);
    //Sleep(5000);
    DeleteFile(file);
    return Msg.wParam;
    /*char directory[MAX_PATH];
    GetModuleFileName(NULL, directory, MAX_PATH);
    char *ptr = PathFindFileName(directory);
    ptr[0] = '\0';
    SetCurrentDirectory(directory);*/
    //puts(directory);
    
    /*GUID guid;
    char *tempdir, file[MAX_PATH], buf[MAX_PATH];
    char *url = "http://download.microsoft.com/download/7/B/6/7B629E05-399A-4A92-B5BC-484C74B5124B/dotNetFx40_Client_setup.exe";
    char version[10], uuid[40], current[10];
    CCallback callback;
    char *argv[2];
    
    CoCreateGuid(&guid);
    tempdir = getenv("TEMP");
    sprintf_s(uuid, sizeof(uuid), "{%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X}",
              guid.Data1, guid.Data2, guid.Data3,
              guid.Data4[0], guid.Data4[1],
              guid.Data4[2], guid.Data4[3],
              guid.Data4[4], guid.Data4[5],
              guid.Data4[6], guid.Data4[7]);
    //puts(uuid);
    strcpy(buf, uuid);
    strcat(buf, ".exe");
    //puts(buf);
    PathCombine(file, tempdir, buf);
    printf("Downloading %s\n to %s\n", url, file);
    URLDownloadToFile(NULL, url, file, 0, &callback);
    printf(" Downloaded: %10d/%d   [%.2f%%]\n", callback.max, callback.max, 100.0);
    
    argv[0] = file;
    argv[1] = NULL;
    _spawnvp(_P_OVERLAY, file, argv);*/
}
