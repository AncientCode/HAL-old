// stdafx.h : 标准系统包含文件的包含文件，
// 或是经常使用但不常更改的
// 特定于项目的包含文件
//

#pragma once
#ifndef id267FA845_F869_47EC_BE910E8ABD8E1705
#define id267FA845_F869_47EC_BE910E8ABD8E1705

//#include "targetver.h"
// C++
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <fstream>
#include <list>
#include <map>
#include <forward_list>
#include <tuple>
#include <exception>
#include <stdexcept>
#include <random>

// Workaround a GCC problem, std::regex not fully implemented
#ifdef __GNUC__
#   include <boost/regex.hpp>
    using boost::regex;
    //using boost::regex_constants;
    namespace std {
        namespace regex_constants {
            typedef boost::regex_constants::syntax_option_type syntax_option_type;

            static const syntax_option_type normal = boost::regex_constants::normal;
            static const syntax_option_type ECMAScript = boost::regex_constants::ECMAScript;
            static const syntax_option_type JavaScript = boost::regex_constants::JavaScript;
            static const syntax_option_type JScript = boost::regex_constants::JScript;
            static const syntax_option_type perl = boost::regex_constants::perl;
            static const syntax_option_type basic = boost::regex_constants::basic;
            static const syntax_option_type sed = boost::regex_constants::sed;
            static const syntax_option_type extended = boost::regex_constants::extended;
            static const syntax_option_type awk = boost::regex_constants::awk;
            static const syntax_option_type grep = boost::regex_constants::grep;
            static const syntax_option_type egrep = boost::regex_constants::egrep;
            static const syntax_option_type icase = boost::regex_constants::icase;
            static const syntax_option_type nosubs = boost::regex_constants::nosubs;
            static const syntax_option_type optimize = boost::regex_constants::optimize;
            static const syntax_option_type collate = boost::regex_constants::collate;
        }
    }
    using boost::smatch;
    using boost::regex_error;
#else
#   include <regex>
#endif

// Boost
#include <boost/pool/pool_alloc.hpp>
#include <boost/algorithm/string.hpp>

#ifdef BUILD_PYTHON
#   include <boost/python.hpp>
#endif

#ifdef WIN32
#   include <windows.h>
#endif

using namespace std;

#endif
