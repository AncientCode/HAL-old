#include <iostream>
#include <cmath>
#include <vector>
#include <string>
#include "equation.h"
#include <mpreal.h>
#include <sstream>

using std::size_t;
using std::vector;
using std::string;
using std::stringstream;

/**
 * Performs the specified operation against the
 * argument strings. The operation is dependant on
 * the value of op.
 */
string doOperation(const string& lhs, char op, const string& rhs) {
    mpfr::mpreal bdLhs(lhs);
    mpfr::mpreal bdRhs(rhs);
    mpfr::mpreal temp;

    switch(op) {
    case '^':
        temp = pow(bdLhs, bdRhs);
        break;
    case '*':
        temp = bdLhs * bdRhs;
        break;
    case '/':
        temp = bdLhs / bdRhs;
        break;
    case '+':
        temp = bdLhs + bdRhs;
        break;
    case '%':
        temp = fmod(bdLhs, bdRhs);
        break;
    }
    return temp.toString();
}
 
/**
 * Returns the string with its enclosing paranthesis
 * stripped from it.
 */
void correctedString(string& arg) {
    size_t pos1 = arg.find_first_of("(");
    size_t pos2 = arg.find_last_of(")");

    if (pos1 >= 0 && pos1 < arg.length() && pos2 >= 0 && pos2 <= arg.length())
        arg[pos1] = arg[pos2] = ' ';
}

/**
 * Remove spaces from the argument string.
 */
void removeSpaces(string& argu) {
    string temp;
    for (auto i = argu.cbegin(); i < argu.cend(); ++i)
        if (*i != ' ')
            temp += *i;
    argu = temp;
}

/**
 * The brains of the program.
 * Solves expressions by using recursion for complex expressions.
 */
string parse(string expression) {
    correctedString(expression);
    removeSpaces(expression);
    string finalExpression;

    bool operatorEncountered = true;
    for (size_t i = 0; i < expression.length(); i++) {
        if (expression[i] == '(') {
            string placeHolder = "(";    
            int valuesCounted = 1;    
            operatorEncountered = false;
            for (size_t j = i + 1; valuesCounted != 0; j++) {    
                if (expression[j] == '(')    
                    valuesCounted++;
                else if (expression[j] == ')')    
                    valuesCounted--;
                placeHolder += expression[j];
            }
         
            string evaluatedString = parse(placeHolder); 
            finalExpression += evaluatedString;    
            i += (placeHolder.length() - 1); 
        } else {
            if (expression[i] == '-' && operatorEncountered == false)
                finalExpression += '+';
         
            finalExpression += expression[i];
            if (expression[i] == '+' || expression[i] == '/' ||
                expression[i] == '^' || expression[i] == '*' ||
                expression[i] == '%' || expression[i] == '-')
                    operatorEncountered = true;
            else if (expression[i] != ' ')
                operatorEncountered = false;
        }
    }

    removeSpaces(finalExpression);    
    string perfectExpression;
 
    for (size_t i = 0; i < finalExpression.length(); i++) {    
        if ((i + 1) < finalExpression.length())    
            if (finalExpression[i] == '-' && finalExpression[i + 1] == '-')
                i += 2;    
        perfectExpression += finalExpression[i];    
    }
    finalExpression = perfectExpression;
 
    vector<string> totalNumbers;
    vector<char> totalOperations;    
    // cout << finalExpression << endl;    

    for (size_t i = 0; i < finalExpression.length(); i++) {
        if (finalExpression[i] >= '0' && finalExpression[i] <= '9' ||
            finalExpression[i] == '-' || finalExpression[i] == '.') {    
            string temp;
            for (size_t j = i; j < finalExpression.length(); j++) {    
                if (finalExpression[j] >= '0' && finalExpression[j] <= '9' ||
                    finalExpression[j] == '-' || finalExpression[j] == '.') {
                        temp += finalExpression[j];    
                } else break;
            }
            totalNumbers.push_back(temp);    
            i += temp.length() == 0 ? 0 : (temp.length() - 1);    
        } else if (finalExpression[i] == '*' || finalExpression[i] == '/' ||
                   finalExpression[i] == '^' || finalExpression[i] == '+' ||
                   finalExpression[i] == '%') {
            totalOperations.push_back(finalExpression[i]);
        }
    }

    calculate(totalNumbers, totalOperations, "^");
    calculate(totalNumbers, totalOperations, "*/%");
    calculate(totalNumbers, totalOperations, "+");
    return totalNumbers[0];
}
 
/**
 * Calculates the numbers in the first vector using the operands in the 2nd vector,
 * based on the expressions allowed which are determined by the string argument.
 */
void calculate(vector<string>& totalNumbers, vector<char>& totalOperations, const string& arg) {
    for (size_t i = 0; i < totalOperations.size(); ++i) {
        if (arg.find(totalOperations[i]) != arg.npos) {
            totalNumbers[i] = doOperation(totalNumbers[i], totalOperations[i], totalNumbers[i + 1]);
            size_t oldNumberLength = totalNumbers.size();
            size_t oldOperatorLength = totalOperations.size();
            size_t nextNumberLength = oldNumberLength - 1;
            size_t nextOperatorLength = oldOperatorLength - 1;
            size_t sCount = 0;
            size_t oCount = 0;
            vector<string> temp1 (nextNumberLength);
            vector<char> temp2 (nextOperatorLength);

            for (size_t j = 0; j < oldNumberLength; ++j) {
                if (j != i + 1)
                temp1[sCount++] = totalNumbers[j];
                if (j != i && j < oldOperatorLength)
                temp2[oCount++] = totalOperations[j];
            }
            totalNumbers = temp1;
            totalOperations = temp2;
            --i;
        }
    }
}
 
/**
 * Returns true if the equation is solvable (not really),
 * returns false otherwise.
 *
 * This function is truly a misnomer, because more restrictions
 * should be put in place.
 */
bool isSolvable(const string& eq) {
    int paranthesisCount = 0;
    for(size_t i = 0; i < eq.length(); i++) {
        if (eq[i] == '(')    
            paranthesisCount++;    
        else if (eq[i] == ')')    
            paranthesisCount--;    
        if (paranthesisCount < 0)
            return false;
    }
    return paranthesisCount == 0;
}

bool is_num(char ch) {
    switch (ch) {
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            return true;
        default:
            return false;
    }
}

string AddMultiplication(const string& str) {
    string out;
    out.reserve(str.length()+10);
    for (auto i = str.cbegin(); i < str.cend(); ++i) {
        if (*i == '(')
            if (is_num(out[out.length()-1]) || out[out.length()-1] == ')')
                out.push_back('*');
        out.push_back(*i);
    }
    return out;
}

/**
 * An attempt to solve a string-expression, given
 * a precision value.
 */
string solve(const string& eq, int prec) {
    mpfr::mpreal::default_prec = 128;
    if (isSolvable(eq)) {
        // cout << eq << endl;
        
        string value;
        value += '(';
        value += eq;
        value += ')';
        
        stringstream ss;
        //ss.setf(0, ios::floatfield);
        //ss.precision(prec);
        ss << parse(AddMultiplication(value));
        return ss.str();
    } else return "";
}

string generateEquation(const string& equation) {
    const static string operators("/*-+!%^()");
    const static string numbers("0123456789");
    string out;
    out.reserve(equation.length());
    for (auto i = equation.cbegin(); i < equation.cend(); ++i) {
        if (operators.find(*i) != string::npos)
            out.push_back(*i);
        else if (numbers.find(*i) != string::npos)
            out.push_back(*i);
    }
    return out;
}
