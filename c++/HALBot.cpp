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

HALBot::HALBot(const string& path, bool write) {
    this->Initialize(path, "", write);
}

HALBot::HALBot(const string& path, const string& username, bool write) {
    this->Initialize(path, username, write);
}

const regex HALBot::wildcard2regex("\\s*\\*\\s*", regex_constants::ECMAScript|regex_constants::optimize);
const regex HALBot::caret_replace("\\^", regex_constants::ECMAScript|regex_constants::optimize);
const regex HALBot::space_normalize("\\s+", regex_constants::ECMAScript|regex_constants::optimize);
const string HALBot::word_boundary("\\b");
// .* to match blanks...
const string HALBot::rewildcard("\\b(.+)\\b");
const string HALBot::boundary_begin("(?:\\b|^)");
const string HALBot::boundary_end("(?:\\b|$)");

template<class sequence>
void read_into_sequence(sequence& data, const string& file, const string& purpose, bool write=true) {
    string line;
    if (write)
        cout << "Reading " << file << " for " << purpose << "...\r";
    fstream stream(file);
    if (write)
        if (stream.is_open())
            cout << '\n';
        else
            cout << "WARNING: Failed to open " << file << " for " << purpose << "!!!" << endl;
    if (stream.is_open())
        while (getline(stream, line))
            data.push_back(line);
}

void HALBot::Initialize(const string& path, const string& username, bool write) {
    // Initialize the data structure
    HALanswerList replies;
    string key, thinkset;
    list<string> files;
    //GetDirContents(path, files);
    MatchFile(path+"\\*.hal", files);
    fstream file;
    char temp[1024];

    for (auto i = files.cbegin(); i != files.cend(); ++i) {
        file.open(path+"\\"+*i);
        if (write)
            cout << "Parsing file " << *i << "......\n";
        //if (!file)
            //throw new IOException(string("Can't open file: ")+*i);
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
                        string error = "Invalid Regex: "+key+" in file '"+*i+"', ignored!";
#ifdef WIN32
                        if (!write)
                            MessageBox(NULL, error.c_str(), "Regex Error!", MB_ICONWARNING);
                        else
#endif
                            cout << error << '\n';
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
        key.clear();
        thinkset.clear();
        replies.clear();
        file.close();
    }

    if (write)
        cout << flush;
    
    // Learning File
    //learn_file.open(path+"\\learn.dat", ios_base::out|ios_base::app);
    
    // Initialize RNG
    rng.seed(rngsource());
}

void trim(string& str) {
    boost::algorithm::trim(str);
}

inline void clean_possible(const string& question, vector<tuple<string, string, size_t, string> >& possible) {
    int best = 0xFFFFFFFF;
    for (auto i = possible.cbegin(); i < possible.cend(); ++i) {
        //if (get<1>(*i).length() < best)
        //  best = get<1>(*i).length();
        if (question.length() - get<2>(*i) < best)
            best = question.length() - get<2>(*i);
    }
    for (auto i = possible.begin(); i < possible.end();) {
        //if (get<1>(*i).length() > best) {
        boost::algorithm::trim(get<1>(*i));
        if (question.length() - get<2>(*i) > best) {
            i = possible.erase(i);
        } else if (get<0>(*i).find("^") != string::npos && !get<1>(*i).length()) {
            i = possible.erase(i);
        } else {
            ++i;
        }
    }
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

string HALBot::Ask(const string& question_) {
    string question(regex_replace(question_, space_normalize, string(" ")));
    // Name, Wildcard, Magnitude of Specificness (migher = more), Thinkset
    typedef tuple<string, string, size_t, string> entry;
    vector<entry> possible, best_possible;
    smatch results;
    for (auto i = data.cbegin(); i != data.cend(); ++i) {
        if (regex_search(question, results, get<1>(*i))) {
            const HALanswerList &answers = get<2>(*i);
            if (!prev_thinkset.empty() && get<3>(*i) == prev_thinkset) {
                for (auto j = answers.cbegin(); j != answers.cend(); ++j)
                    best_possible.push_back(entry(*j, results[1], get<0>(*i).length(), get<3>(*i)));
            } else {
                for (auto j = answers.cbegin(); j != answers.cend(); ++j)
                    possible.push_back(entry(*j, results[1], get<0>(*i).length(), get<3>(*i)));
            }
        }
    }
    if (best_possible.empty() && possible.empty()) {
        //return "I can't seem to understand.";
        //size_t index = uniform_int_distribution<size_t>(0, generic_answer.size()-1)(rng);
        //return Format(generic_answer[index], "");
        return "$RAISE_HALCANNOTHANDLE$";
    } else {
        clean_possible(question, best_possible);
        clean_possible(question, possible);
        if (!best_possible.empty())
            possible = best_possible;
        
        size_t index = uniform_int_distribution<size_t>(0, possible.size()-1)(rng);
        string &answer = get<0>(possible[index]);
        string &matched = get<1>(possible[index]);
        if (answer.find("|") != string::npos) {
            vector<string> answers;
            boost::split(answers, answer, boost::is_any_of("|"));
            for_each(answers.begin(), answers.end(), trim);
            for (auto i = answers.begin(); i < answers.end(); ++i) {
                if (i->front() == '>')
                    *i = Ask(i->c_str()+1);
            }
            string ans;
            for (auto i = answers.cbegin(); i < answers.cend(); ++i)
                ans += *i + " ";
            ans.pop_back();
            return ans;
        }
        if (answer.front() == '>')
            return Ask(answer.c_str()+1);
        prev_thinkset = get<3>(possible[index]);
        return Format(answer, matched);
    }
}

string HALBot::Format(string answer, string matched) {
    /*UpdateMacro();
    for (auto i = macros.cbegin(); i != macros.cend(); ++i)
        //answer = regex_replace(answer, get<0>(i->second), get<1>(i->second));
        boost::algorithm::replace_all(answer, i->first, i->second);*/
    boost::algorithm::trim(matched);
    answer = regex_replace(answer, caret_replace, matched);
    return answer;
}

HALBot::~HALBot() {
    boost::singleton_pool<boost::fast_pool_allocator_tag, sizeof(string)>::release_memory();
    boost::singleton_pool<boost::fast_pool_allocator_tag, sizeof(HALanswerList)>::release_memory();
    boost::singleton_pool<boost::fast_pool_allocator_tag, sizeof(HALdataEntry)>::release_memory();
}
