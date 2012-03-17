#include "stdafx.h"

#pragma once
#ifndef id112E4CA5_4268_4317_B599598F90A9E262
#define id112E4CA5_4268_4317_B599598F90A9E262

class HALException : exception {
    std::string what_;
public:
    HALException() : what_("(Unknown Exception)") {}
    HALException(string what) : what_(what) {}
    virtual string what() {return what_;}
};

class IOException : public HALException {
public:
    IOException() : HALException() {}
    IOException(string what) : HALException(what) {}
};

#endif
