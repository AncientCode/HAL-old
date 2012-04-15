#include "stdafx.h"
#include "HALBot.h"
#include "helper.h"
#include "exception.h"
#include "console.h"

#ifdef WIN32
#   ifndef WIN32_LEAN_AND_MEAN
#       define WIN32_LEAN_AND_MEAN
#   endif
#   include <windows.h>
#   include <wincrypt.h>
#   pragma comment(lib, "user32.lib")
#else
#   include <ctime>
#endif

inline unsigned rngsource() {
#ifdef WIN32
    unsigned num;
    HCRYPTPROV crypt;
    CryptAcquireContext(&crypt, NULL, NULL, PROV_RSA_FULL, CRYPT_SILENT);
    CryptGenRandom(crypt, sizeof(unsigned), (byte*)&num);
    CryptReleaseContext(crypt, 0);
    return num;
#else
    return time(NULL);
#endif
}

const regex HALBot::wildcard2regex("\\s*\\*\\s*", regex_constants::ECMAScript|regex_constants::optimize);
const regex HALBot::caret_replace("\\^", regex_constants::ECMAScript|regex_constants::optimize);
const regex HALBot::space_normalize("\\s+", regex_constants::ECMAScript|regex_constants::optimize);
const string HALBot::word_boundary("\\b");
// .* to match blanks...
const string HALBot::rewildcard("\\b(.+)\\b");
const string HALBot::boundary_begin("(?:\\b|^)");
const string HALBot::boundary_end("(?:\\b|$)");

HALBot::HALBot() {
    // Initialize RNG
    rng.seed(rngsource());
}

string HALBot::LoadFile(const string& filename) {
    fstream file(filename);
    if (!file.is_open())
        return "Can't open file "+filename;
    HALanswerList replies;
    string key, thinkset;
    string error;
    char temp[1024];
    while (file.getline(temp, 1024, '\n')) {
        switch (temp[0]) {
        case '%':
            // New Thinkset
            thinkset = temp+1;
            break;
        case '#':
            // New Command
            if (!key.empty()) {
                try {
                    regex reg(boundary_begin+regex_replace(key, wildcard2regex, rewildcard)+boundary_end,
                              regex_constants::ECMAScript|regex_constants::icase/*|
                              regex_constants::optimize*/);
                    HALdataEntry entry(key, reg, replies, thinkset);
                    data.push_back(entry);
                } catch (regex_error) {
                    error += "Invalid Regex: "+key+" in file '"+filename+"', ignored!"+'\n';
                }
                replies.clear();
                //datalist.insert(key);
            }
            key = temp+1;
            if (key[0] == '_') {
                key[0] = '.';
                key[1] = '*';
            }
            break;
        case '\0':
            break;
        default:
            //replies.push_front(temp);
            replies.push_back(temp);
        }
    }
    file.close();
    return error;
}

#ifdef BUILD_PYTHON
boost::python::tuple HALBot::pyAsk(const string& question) {
    // Name, Wildcard, Magnitude of Specificness (migher = more), Thinkset
    smatch results;
    boost::python::list best_possible, possible;
    for (auto i = data.cbegin(); i != data.cend(); ++i) {
        if (regex_search(question, results, get<1>(*i))) {
            const HALanswerList &answers = get<2>(*i);
            boost::python::list submatches, ans;
            //for (auto i = results.cbegin(); i != results.cend(); ++i)
            //for (size_t k = 1; k < results.length(); ++k)
            for (size_t k = 0; k < results.length(); ++k)
                //if (results[k] != "") // Remove empty
                    submatches.append(string(results[k]));
            for (auto j = answers.cbegin(); j != answers.cend(); ++j)
                ans.append(*j);
            if (!prev_thinkset.empty() && get<3>(*i) == prev_thinkset)
                best_possible.append(boost::python::make_tuple(get<0>(*i), get<3>(*i), ans, submatches));
            else
                possible.append(boost::python::make_tuple(get<0>(*i), get<3>(*i), ans, submatches));
        }
    }
    return boost::python::make_tuple(best_possible, possible);
}
#endif

HALBot::~HALBot() {
    boost::singleton_pool<boost::fast_pool_allocator_tag, sizeof(string)>::release_memory();
    boost::singleton_pool<boost::fast_pool_allocator_tag, sizeof(HALanswerList)>::release_memory();
    boost::singleton_pool<boost::fast_pool_allocator_tag, sizeof(HALdataEntry)>::release_memory();
}
