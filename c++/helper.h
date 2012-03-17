#include "stdafx.h"

#pragma once
#ifndef id3B9D998A_EEB4_4144_BED91F3F69DEB2C6
#define id3B9D998A_EEB4_4144_BED91F3F69DEB2C6

//#include <dirent.h>
#include <ctime>

inline string strftime(const string& format, time_t time = std::time(NULL)) {
    char temp[128];
    struct tm *data = localtime(&time);
    strftime(temp, 128, format.c_str(), data);
    return temp;
}

inline string int2str(int a) {
    char temp[20];
    sprintf_s(temp, "%d", a);
    return temp;
}

template<class T>
void GetDirContents(const string& dir, T& output) {
    /*DIR *dp;
    struct dirent *dirp;
    if ((dp = opendir(dir.c_str())) == NULL) {
        IOException e("Can't open directory");
        throw e;
    }
    while (dirp = readdir(dp)) {
        if (strcmp(dirp->d_name, ".") ^ strcmp(dirp->d_name, ".."))
            continue;
        output.push_back(dirp->d_name);
    }
    closedir(dp);*/
}

template<class T>
bool MatchFile(const string& pattern, T& output) {
    WIN32_FIND_DATAA data;
    HANDLE find = INVALID_HANDLE_VALUE;
    find = FindFirstFileA(pattern.c_str(), &data);
    if (find == INVALID_HANDLE_VALUE)
        return false;
    do {
        if (!(data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY))
            output.push_back(data.cFileName);
    } while (FindNextFileA(find, &data));
    FindClose(find);
    return true;
}

inline string choppa(string str) {
    size_t found;
    static const string ws("\r\n \t\f");
    found = str.find_last_not_of(ws);
    if (found != string::npos)
        str.erase(found+1);
    else
        str.clear();            // str is all whitespace
    return str;
}

inline void choppa_in_place(string& str) {
    size_t found;
    static const string ws("\r\n \t\f");
    found = str.find_last_not_of(ws);
    if (found != string::npos)
        str.erase(found+1);
    else
        str.clear();
}

inline string choppa(string str, const string& ws) {
    size_t found;
    found = str.find_last_not_of(ws);
    if (found != string::npos)
        str.erase(found+1);
    else
        str.clear();            // str is all whitespace
    return str;
}

#endif