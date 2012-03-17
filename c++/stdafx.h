// stdafx.h : 标准系统包含文件的包含文件，
// 或是经常使用但不常更改的
// 特定于项目的包含文件
//

#pragma once
#ifndef id267FA845_F869_47EC_BE910E8ABD8E1705
#define id267FA845_F869_47EC_BE910E8ABD8E1705

#include "targetver.h"
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
#include <regex>
#include <exception>
#include <stdexcept>
#include <random>

// Boost
#include <boost/pool/pool_alloc.hpp>
#include <boost/algorithm/string.hpp>

#ifdef BUILD_PYTHON
#   include <boost/python.hpp>
#endif

#include <windows.h>

using namespace std;

#endif
