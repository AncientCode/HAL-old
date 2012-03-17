#include "stdafx.h"
#include <boost/python.hpp>
#include "HALBot.h"
#include "equation.h"

BOOST_PYTHON_MODULE(HALnative) {
    using namespace boost::python;
    def("solve_equation", solve);
    def("generate_equation", generateEquation);
    def("check_bracket", isSolvable);
    def("bracket_multiply", AddMultiplication);
    
    void (HALBot::*LearnStr)(const string&, const string&) = &HALBot::Learn;
    void (HALBot::*LearnList)(const string&, const boost::python::list&) = &HALBot::Learn;
    
    class_<HALBot, boost::noncopyable>("HALBot", init<const std::string&, const std::string&>())
        .def(init<const std::string&, const std::string&, bool>())
        .def("Ask", &HALBot::Ask)
        .def("Learn", LearnStr)
        .def("Learn", LearnList)
    ;
}
