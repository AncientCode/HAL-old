#include "stdafx.h"
#pragma once
#ifndef id381A3FD6_ED45_4CE4_B722F9D0C8D8ED41
#define id381A3FD6_ED45_4CE4_B722F9D0C8D8ED41

#include <conio.h>

string& ConPrompt(const string& prompt, string& result);
string ConPrompt(const string& prompt);
bool ConAsk(const string& prompt);
string ConGetPass(const string& prompt);
inline void ConPrint(const string& text) {
    for (auto i = text.cbegin(); i < text.end(); ++i)
        putch(*i);
}

#endif
