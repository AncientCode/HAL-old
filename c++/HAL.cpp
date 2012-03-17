#include "stdafx.h"
#include "HALBot.h"

int main(int argc, char* argv[]) {
    puts("                        --------------------------");
    puts("                                   HAL");
    puts("                        --------------------------");
    puts("                            By: Joseph Tyrrell");
    puts("");
    puts("Initializing...");
    try {
        HALBot bot("data", true);
        string input, output;
        while (true) {
            cerr << "<-- ";
            if (!getline(cin, input))
                break;
            output = bot.Ask(input);
            cerr << "--> ";
            cout << output << endl;
        }
    } catch (exception& e) {
        cout << e.what() << endl;
    }
}
