#pragma once
#ifndef id1FCC5427_838E_4612_8521B5B60FDB026D
#define id1FCC5427_838E_4612_8521B5B60FDB026D

#include <string>
#include <vector>

using std::string;
using std::vector;

string doOperation(const string&, char, const string&);
void correctedString(string&);
void removeSpaces(string&);
string parse(string expression);
bool isSolvable(const string&);
void calculate(vector<string>&, vector<char>&, const string&);
string solve(const string&, int = 50);
string AddMultiplication(const string& str);
string generateEquation(const string& equation);

#endif
