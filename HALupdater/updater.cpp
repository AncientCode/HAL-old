#include <stdio.h>
#include <process.h>
#include <objbase.h>
#include <shlwapi.h>
#include <lzma/7z.h>
extern "C" {
#include <lzma/7zAlloc.h>
}
#include <lzma/7zCrc.h>
#include <lzma/7zFile.h>
#include <lzma/7zVersion.h>

#pragma comment(lib, "lzma.lib")
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "urlmon.lib")

static ISzAlloc g_Alloc = { SzAlloc, SzFree };

static int Buf_EnsureSize(CBuf *dest, size_t size)
{
    if (dest->size >= size)
        return 1;
    Buf_Free(dest, &g_Alloc);
    return Buf_Create(dest, size, &g_Alloc);
}

#ifndef _WIN32

static Byte kUtf8Limits[5] = { 0xC0, 0xE0, 0xF0, 0xF8, 0xFC };

static Bool Utf16_To_Utf8(Byte *dest, size_t *destLen, const UInt16 *src, size_t srcLen)
{
    size_t destPos = 0, srcPos = 0;
    for (;;)
    {
        unsigned numAdds;
        UInt32 value;
        if (srcPos == srcLen)
        {
            *destLen = destPos;
            return True;
        }
        value = src[srcPos++];
        if (value < 0x80)
        {
            if (dest)
                dest[destPos] = (char)value;
            destPos++;
            continue;
        }
        if (value >= 0xD800 && value < 0xE000)
        {
            UInt32 c2;
            if (value >= 0xDC00 || srcPos == srcLen)
                break;
            c2 = src[srcPos++];
            if (c2 < 0xDC00 || c2 >= 0xE000)
                break;
            value = (((value - 0xD800) << 10) | (c2 - 0xDC00)) + 0x10000;
        }
        for (numAdds = 1; numAdds < 5; numAdds++)
            if (value < (((UInt32)1) << (numAdds * 5 + 6)))
                break;
        if (dest)
            dest[destPos] = (char)(kUtf8Limits[numAdds - 1] + (value >> (6 * numAdds)));
        destPos++;
        do
        {
            numAdds--;
            if (dest)
                dest[destPos] = (char)(0x80 + ((value >> (6 * numAdds)) & 0x3F));
            destPos++;
        }
        while (numAdds != 0);
    }
    *destLen = destPos;
    return False;
}

static SRes Utf16_To_Utf8Buf(CBuf *dest, const UInt16 *src, size_t srcLen)
{
    size_t destLen = 0;
    Bool res;
    Utf16_To_Utf8(NULL, &destLen, src, srcLen);
    destLen += 1;
    if (!Buf_EnsureSize(dest, destLen))
        return SZ_ERROR_MEM;
    res = Utf16_To_Utf8(dest->data, &destLen, src, srcLen);
    dest->data[destLen] = 0;
    return res ? SZ_OK : SZ_ERROR_FAIL;
}
#endif

static SRes Utf16_To_Char(CBuf *buf, const UInt16 *s, int fileMode)
{
    int len = 0;
    for (len = 0; s[len] != '\0'; len++);

    #ifdef _WIN32
    {
        int size = len * 3 + 100;
        if (!Buf_EnsureSize(buf, size))
            return SZ_ERROR_MEM;
        {
            char defaultChar = '_';
            BOOL defUsed;
            int numChars = WideCharToMultiByte(fileMode ?
                    (AreFileApisANSI() ? CP_ACP : CP_OEMCP) : CP_OEMCP,
                    0, (LPCWSTR)s, len, (char *)buf->data, size, &defaultChar, &defUsed);
            if (numChars == 0 || numChars >= size)
                return SZ_ERROR_FAIL;
            buf->data[numChars] = 0;
            return SZ_OK;
        }
    }
    #else
    fileMode = fileMode;
    return Utf16_To_Utf8Buf(buf, s, len);
    #endif
}

static WRes MyCreateDir(const UInt16 *name)
{
    #ifdef USE_WINDOWS_FILE
    
    return CreateDirectoryW((LPCWSTR)name, NULL) ? 0 : GetLastError();
    
    #else

    CBuf buf;
    WRes res;
    Buf_Init((LPCWSTR)&buf);
    RINOK(Utf16_To_Char(&buf, name, 1));

    res =
    #ifdef _WIN32
    _mkdir((const char *)buf.data)
    #else
    mkdir((const char *)buf.data, 0777)
    #endif
    == 0 ? 0 : errno;
    Buf_Free(&buf, &g_Alloc);
    return res;
    
    #endif
}

static WRes OutFile_OpenUtf16(CSzFile *p, const UInt16 *name)
{
    #ifdef USE_WINDOWS_FILE
    return OutFile_OpenW(p, (LPCWSTR)name);
    #else
    CBuf buf;
    WRes res;
    Buf_Init(&buf);
    RINOK(Utf16_To_Char((LPCWSTR)&buf, name, 1));
    res = OutFile_Open(p, (const char *)buf.data);
    Buf_Free(&buf, &g_Alloc);
    return res;
    #endif
}

static SRes PrintString(const UInt16 *s)
{
    CBuf buf;
    SRes res;
    Buf_Init(&buf);
    res = Utf16_To_Char(&buf, s, 0);
    if (res == SZ_OK)
        fputs((const char *)buf.data, stdout);
    Buf_Free(&buf, &g_Alloc);
    return res;
}

static void UInt64ToStr(UInt64 value, char *s)
{
    char temp[32];
    int pos = 0;
    do
    {
        temp[pos++] = (char)('0' + (unsigned)(value % 10));
        value /= 10;
    }
    while (value != 0);
    do
        *s++ = temp[--pos];
    while (pos);
    *s = '\0';
}

static char *UIntToStr(char *s, unsigned value, int numDigits)
{
    char temp[16];
    int pos = 0;
    do
        temp[pos++] = (char)('0' + (value % 10));
    while (value /= 10);
    for (numDigits -= pos; numDigits > 0; numDigits--)
        *s++ = '0';
    do
        *s++ = temp[--pos];
    while (pos);
    *s = '\0';
    return s;
}

#define PERIOD_4 (4 * 365 + 1)
#define PERIOD_100 (PERIOD_4 * 25 - 1)
#define PERIOD_400 (PERIOD_100 * 4 + 1)

static void ConvertFileTimeToString(const CNtfsFileTime *ft, char *s)
{
    unsigned year, mon, day, hour, min, sec;
    UInt64 v64 = (ft->Low | ((UInt64)ft->High << 32)) / 10000000;
    Byte ms[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    unsigned t;
    UInt32 v;
    sec = (unsigned)(v64 % 60); v64 /= 60;
    min = (unsigned)(v64 % 60); v64 /= 60;
    hour = (unsigned)(v64 % 24); v64 /= 24;

    v = (UInt32)v64;

    year = (unsigned)(1601 + v / PERIOD_400 * 400);
    v %= PERIOD_400;

    t = v / PERIOD_100; if (t ==    4) t =    3; year += t * 100; v -= t * PERIOD_100;
    t = v / PERIOD_4;     if (t == 25) t = 24; year += t * 4;     v -= t * PERIOD_4;
    t = v / 365;                if (t ==    4) t =    3; year += t;             v -= t * 365;

    if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0))
        ms[1] = 29;
    for (mon = 1; mon <= 12; mon++)
    {
        unsigned s = ms[mon - 1];
        if (v < s)
            break;
        v -= s;
    }
    day = (unsigned)v + 1;
    s = UIntToStr(s, year, 4); *s++ = '-';
    s = UIntToStr(s, mon, 2);    *s++ = '-';
    s = UIntToStr(s, day, 2);    *s++ = ' ';
    s = UIntToStr(s, hour, 2); *s++ = ':';
    s = UIntToStr(s, min, 2);    *s++ = ':';
    s = UIntToStr(s, sec, 2);
}

void PrintError(char *sz)
{
    printf("\nERROR: %s\n", sz);
}

#ifdef USE_WINDOWS_FILE
#define kEmptyAttribChar '.'
static void GetAttribString(UInt32 wa, Bool isDir, char *s)
{
    s[0] = (char)(((wa & FILE_ATTRIBUTE_DIRECTORY) != 0 || isDir) ? 'D' : kEmptyAttribChar);
    s[1] = (char)(((wa & FILE_ATTRIBUTE_READONLY) != 0) ? 'R': kEmptyAttribChar);
    s[2] = (char)(((wa & FILE_ATTRIBUTE_HIDDEN) != 0) ? 'H': kEmptyAttribChar);
    s[3] = (char)(((wa & FILE_ATTRIBUTE_SYSTEM) != 0) ? 'S': kEmptyAttribChar);
    s[4] = (char)(((wa & FILE_ATTRIBUTE_ARCHIVE) != 0) ? 'A': kEmptyAttribChar);
    s[5] = '\0';
}
#else
static void GetAttribString(UInt32, Bool, char *s)
{
    s[0] = '\0';
}
#endif

int extractall(const char *file) {
    CFileInStream archiveStream;
    CLookToRead lookStream;
    CSzArEx db;
    SRes res;
    ISzAlloc allocImp;
    ISzAlloc allocTempImp;
    UInt16 *temp = NULL;
    size_t tempSize = 0;
    
    allocImp.Alloc = SzAlloc;
    allocImp.Free = SzFree;

    allocTempImp.Alloc = SzAllocTemp;
    allocTempImp.Free = SzFreeTemp;

    if (InFile_Open(&archiveStream.file, file)) {
        PrintError("can not open input file");
        return 1;
    }

    FileInStream_CreateVTable(&archiveStream);
    LookToRead_CreateVTable(&lookStream, False);
    
    lookStream.realStream = &archiveStream.s;
    LookToRead_Init(&lookStream);

    CrcGenerateTable();

    SzArEx_Init(&db);
    res = SzArEx_Open(&db, &lookStream.s, &allocImp, &allocTempImp);
    if (res == SZ_OK)
    {
        int listCommand = 0, testCommand = 0, extractCommand = 1, fullPaths = 1;
        if (res == SZ_OK)
        {
            UInt32 i;

            /*
            if you need cache, use these 3 variables.
            if you use external function, you can make these variable as static.
            */
            UInt32 blockIndex = 0xFFFFFFFF; /* it can have any value before first call (if outBuffer = 0) */
            Byte *outBuffer = 0; /* it must be 0 before first call for each new archive. */
            size_t outBufferSize = 0;    /* it can have any value before first call (if outBuffer = 0) */

            for (i = 0; i < db.db.NumFiles; i++)
            {
                size_t offset = 0;
                size_t outSizeProcessed = 0;
                const CSzFileItem *f = db.db.Files + i;
                size_t len;
                if (listCommand == 0 && f->IsDir && !fullPaths)
                    continue;
                len = SzArEx_GetFileNameUtf16(&db, i, NULL);

                if (len > tempSize)
                {
                    SzFree(NULL, temp);
                    tempSize = len;
                    temp = (UInt16 *)SzAlloc(NULL, tempSize * sizeof(temp[0]));
                    if (temp == 0)
                    {
                        res = SZ_ERROR_MEM;
                        break;
                    }
                }

                SzArEx_GetFileNameUtf16(&db, i, temp);
                if (listCommand)
                {
                    char attr[8], s[32], t[32];

                    GetAttribString(f->AttribDefined ? f->Attrib : 0, f->IsDir, attr);

                    UInt64ToStr(f->Size, s);
                    if (f->MTimeDefined)
                        ConvertFileTimeToString(&f->MTime, t);
                    else
                    {
                        size_t j;
                        for (j = 0; j < 19; j++)
                            t[j] = ' ';
                        t[j] = '\0';
                    }
                    
                    printf("%s %s %10s    ", t, attr, s);
                    res = PrintString(temp);
                    if (res != SZ_OK)
                        break;
                    if (f->IsDir)
                        printf("/");
                    printf("\n");
                    continue;
                }
                fputs(testCommand ?
                        "Testing        ":
                        "Extracting ",
                        stdout);
                res = PrintString(temp);
                if (res != SZ_OK)
                    break;
                if (f->IsDir)
                    printf("/");
                else
                {
                    res = SzArEx_Extract(&db, &lookStream.s, i,
                            &blockIndex, &outBuffer, &outBufferSize,
                            &offset, &outSizeProcessed,
                            &allocImp, &allocTempImp);
                    if (res != SZ_OK)
                        break;
                }
                if (!testCommand)
                {
                    CSzFile outFile;
                    size_t processedSize;
                    size_t j;
                    UInt16 *name = (UInt16 *)temp;
                    const UInt16 *destPath = (const UInt16 *)name;
                    for (j = 0; name[j] != 0; j++)
                        if (name[j] == '/')
                        {
                            if (fullPaths)
                            {
                                name[j] = 0;
                                MyCreateDir(name);
                                name[j] = CHAR_PATH_SEPARATOR;
                            }
                            else
                                destPath = name + j + 1;
                        }
        
                    if (f->IsDir)
                    {
                        MyCreateDir(destPath);
                        printf("\n");
                        continue;
                    }
                    else if (OutFile_OpenUtf16(&outFile, destPath))
                    {
                        PrintError("can not open output file");
                        res = SZ_ERROR_FAIL;
                        break;
                    }
                    processedSize = outSizeProcessed;
                    if (File_Write(&outFile, outBuffer + offset, &processedSize) != 0 || processedSize != outSizeProcessed)
                    {
                        PrintError("can not write output file");
                        res = SZ_ERROR_FAIL;
                        break;
                    }
                    if (File_Close(&outFile))
                    {
                        PrintError("can not close output file");
                        res = SZ_ERROR_FAIL;
                        break;
                    }
                    #ifdef USE_WINDOWS_FILE
                    if (f->AttribDefined)
                        SetFileAttributesW((LPCWSTR)destPath, f->Attrib);
                    #endif
                }
                printf("\n");
            }
            IAlloc_Free(&allocImp, outBuffer);
        }
    }
    SzArEx_Free(&db, &allocImp);
    SzFree(NULL, temp);

    File_Close(&archiveStream.file);
    if (res == SZ_OK)
    {
        printf("\nEverything is Ok\n");
        return 0;
    }
    if (res == SZ_ERROR_UNSUPPORTED)
        PrintError("decoder doesn't support this archive");
    else if (res == SZ_ERROR_MEM)
        PrintError("can not allocate memory");
    else if (res == SZ_ERROR_CRC)
        PrintError("CRC error");
    else
        printf("\nERROR #%d\n", res);
    return 1;
}

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
        if (!(ulProgressMax|ulProgress)) {
            return E_NOTIMPL;
        }
        max = ulProgressMax;
        printf(" Downloaded: %10d/%d   [%.2f%%]\r", ulProgress, ulProgressMax, ((double)ulProgress/ulProgressMax*100));
        return S_OK;
    }
    STDMETHOD(OnStopBinding)(HRESULT hresult, LPCWSTR szError) { return E_NOTIMPL; }
    STDMETHOD(GetBindInfo)(DWORD __RPC_FAR *grfBINDF, BINDINFO __RPC_FAR *pbindinfo) { return E_NOTIMPL; }
    STDMETHOD(OnDataAvailable)(DWORD grfBSCF, DWORD dwSize, FORMATETC __RPC_FAR *pformatetc, STGMEDIUM __RPC_FAR *pstgmed) { return E_NOTIMPL; }
    STDMETHOD(OnObjectAvailable)(REFIID riid, IUnknown __RPC_FAR *punk) { return E_NOTIMPL; }
    STDMETHOD_(ULONG,AddRef)() { return 0; }
    STDMETHOD_(ULONG,Release)() { return 0; }
    STDMETHOD(QueryInterface)(REFIID riid, void __RPC_FAR *__RPC_FAR *ppvObject) { return E_NOTIMPL; }
};

void error(char *str) {
    HANDLE hCon = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(hCon, &csbi);
    fflush(stdout);
    SetConsoleTextAttribute(hCon, FOREGROUND_RED|FOREGROUND_INTENSITY);
    printf("Error: %s\n", str);
    fflush(stdout);
    SetConsoleTextAttribute(hCon, csbi.wAttributes);
    exit(1);
}

bool split_string(const char *str, char *part1, char *part2, char sep) {
    int index;
    for (index = 0; *str != 0; ++str, ++index) {
        if (*str == sep)
            break;
        part1[index] = *str;
    }
    part2[++index] = '\0';
    ++str;
    strcpy(part2, str);
    return true;
}

int cmp_version(const char *ver1, const char *ver2) {
    char h1[10], h2[10], l1[10], l2[10];
    int i1, i2, m1, m2;
    split_string(ver1, h1, l1, '.');
    split_string(ver2, h2, l2, '.');
    
    i1 = atoi(h1);
    i2 = atoi(h2);
    
    if (i1 < i2)
        return -1;
    else if (i1 > i2)
        return 1;
    return strcmp(l1, l2);
}

inline bool FileExists(const char *fileName) {
    return 0xFFFFFFFF != GetFileAttributes(fileName);
}

inline void clrscr(void) {
    COORD coordScreen = { 0, 0 };  // upper left corner
    DWORD cCharsWritten;
    DWORD dwConSize;
    HANDLE hCon = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
      
    GetConsoleScreenBufferInfo(hCon, &csbi);
    dwConSize = csbi.dwSize.X * csbi.dwSize.Y;
    // fill with spaces
    FillConsoleOutputCharacter(hCon, ' ', dwConSize, coordScreen, &cCharsWritten);
    GetConsoleScreenBufferInfo(hCon, &csbi);
    FillConsoleOutputAttribute(hCon, csbi.wAttributes, dwConSize, coordScreen, &cCharsWritten);
    // cursor to upper left corner
    SetConsoleCursorPosition(hCon, coordScreen);
}

void runfile() {
    //CreateProcess("HALgui.exe");
    //clrscr();
    if (FileExists("HALgui.exe")) {
        char *argv[2];
        argv[0] = "HALgui.exe";
        argv[1] = NULL;
        _spawnvp(_P_OVERLAY, "HALgui.exe", argv);
    } else if (FileExists("HAL.exe")) {
        system("HAL.exe");
        exit(0);
    } else {
        MessageBox(NULL, "Your package is incomplete: you need to have HALgui.exe or HAL.exe", "Fatal Error", MB_ICONERROR|MB_SYSTEMMODAL|MB_TOPMOST);
        exit(0);
    }
}

int main() {
    char directory[MAX_PATH];
    GetModuleFileName(NULL, directory, MAX_PATH);
    char *ptr = PathFindFileName(directory);
    ptr[0] = '\0';
    SetCurrentDirectory(directory);
    //puts(directory);
    
    GUID guid;
    char *tempdir, version_file[MAX_PATH], archive_file[MAX_PATH], buf[MAX_PATH], url[MAX_PATH];
    //char *urlformat = "http://dl.halbot.co.cc/HAL_PE_%.3f.7z";
    char *urlformat = "http://dl.halbot.co.cc/HAL_PE_%s.7z";
    char *version_url = "http://dl.halbot.co.cc/latest.update";
    char version[10], uuid[40], current[10];
    CCallback callback;
    FILE *file;
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
    strcat(buf, ".txt");
    //puts(buf);
    PathCombine(version_file, tempdir, buf);
    //puts(version_file);
    
    printf("Latest Version:  ");
    if (URLDownloadToFile(NULL, version_url, version_file, 0, NULL) != S_OK)
        error("Can't get the latest version");
    
    file = fopen(version_file, "r");
    fgets(version, 10, file);
    fclose(file);
    puts(version);
    DeleteFile(version_file);
    
    file = fopen("version.halconfig", "r");
    if (!file) {
        strcpy(current, "0.010");
        printf("Current Version: (not installed)\n", current);
    } else {
        fgets(current, 10, file);
        fclose(file);
        printf("Current Version: %s\n", current);
    }
    
    if (cmp_version(current, version) >= 0) {
        puts("It appears like you have the latest version, executing it...");
        runfile();
    }
    
    printf("Found update:    %s\n", version);
    
    //puts(urlformat);
    sprintf_s(url, sizeof(url), urlformat, version);
    strcpy(buf, uuid);
    strcat(buf, ".7z");
    PathCombine(archive_file, tempdir, buf);
    printf("Downloading %s\n to %s\n", url, archive_file);
    URLDownloadToFile(NULL, url, archive_file, 0, &callback);
    printf(" Downloaded: %10d/%d   [%.2f%%]\n", callback.max, callback.max, 100.0);
    puts("\n--Extracting--");
    extractall(archive_file);
    puts("--Finished--");
    DeleteFile(archive_file);
    runfile();
}
