#include "stdafx.h"
#include "console.h"
#include <conio.h>

string& ConPrompt(const string& prompt, string& result) {
    ConPrint(prompt);
    ConPrint(": ");
    ConPrint(result);
    char ch;
    while (true) {
        ch = getch();
        switch (ch) {
        case '\r':
        case '\n':
            goto finish_prompt;
            break;
        case '\003':
            ConPrint("\r\n");
            exit(0);
            break;
        case '\b':
            if (!result.empty()) {
                ConPrint("\b \b");
                result.pop_back();
            }
            break;
        default:
            putch(ch);
            result.push_back(ch);
        }
    }
finish_prompt:
    ConPrint("\r\n");
    return result;
}
