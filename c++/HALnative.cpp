#include "stdafx.h"
#include <boost/python.hpp>
#include "HALBot.h"
//#include "equation.h"

BOOST_PYTHON_MODULE(HALnative) {
    using namespace boost::python;
    //def("solve_equation", solve);
    //def("generate_equation", generateEquation);
    //def("check_bracket", isSolvable);
    //def("bracket_multiply", AddMultiplication);

    class_<HALBot, boost::noncopyable>("HALBot")
        //.def("Ask", &HALBot::Ask)
        .def("Ask", &HALBot::pyAsk)
        .def("LoadFile", &HALBot::LoadFile)
        .add_property("thinkset", &HALBot::pyGetThinkSet, &HALBot::pySetThinkSet)
    ;
}
