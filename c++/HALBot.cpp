#include "stdafx.h"
#include "HALBot.h"
#include "helper.h"
#include "exception.h"
#include "console.h"

#ifdef WIN32
#   ifndef WIN32_LEAN_AND_MEAN
#       define WIN32_LEAN_AND_MEAN
#   endif
#   include <wincrypt.h>
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
                    regex reg(word_boundary+regex_replace(key, wildcard2regex, string("\\b(.*)\\b"))+word_boundary,
                              regex_constants::ECMAScript|regex_constants::icase/*|
                              regex_constants::optimize*/);
                    HALdataEntry entry(key, reg, replies, thinkset);
                    data.push_back(entry);
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
    // Macro
    InitMacro(username);
    
    // Generic Answer
    //read_into_sequence(generic_answer, path + "\\generic.chal", "generic answers", write);
    //generic_answer.push_back("I can't seem to understand.");
    
    // Learning File
    learn_file.open(path+"\\learn.dat", ios_base::out|ios_base::app);
    
    // Computer Readable Substitition
    string line;
    string readable_subst_path(path + "\\readable.chal");
    vector<string> readable_subst_temp;
    if (write)
        cout << "Reading " << readable_subst_path << " for Computer Readable Substitition...\r";
    fstream readable_subst_file(readable_subst_path);
    auto tab = boost::is_any_of("\t");
    if (write)
        if (readable_subst_file.is_open())
            cout << endl;
        else
            cout << "WARNING: Failed to open " << readable_subst_path << " for Computer Readable Substitition!!!" << endl;
    if (readable_subst_file.is_open()) {
        while (getline(readable_subst_file, line)) {
            boost::split(readable_subst_temp, line, tab);
            if (readable_subst_temp.size() != 2) {
                cout << "Syntax Error: near " << line << endl;
                continue;
            }
            readable_subst[readable_subst_temp[0]] = readable_subst_temp[1];
        }
    }
    
    // Word Removal
    read_into_sequence(word_removal, path + "\\remove.chal", "word removal", write);
    
    cout << flush;
    
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

string HALBot::Ask(const string& question_) {
    string question(regex_replace(question_, space_normalize, string(" ")));
    for (auto i = readable_subst.cbegin(); i != readable_subst.cend(); ++i)
        boost::algorithm::ireplace_all(question, i->first, i->second);
    for (auto i = word_removal.cbegin(); i != word_removal.cend(); ++i)
        boost::algorithm::ireplace_all(question, *i, "");
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

void HALBot::InitMacro(const string& username) {
    /*if (username.empty()) {
        string username(getenv("USERNAME"));
        ConPrompt("Enter your name", username);
        macros["$USERNAME$"] = username;
    } else
        macros["$USERNAME$"] = username;
    macros["$USER$"] = macros["$USERNAME$"];
    int age = uniform_int_distribution<>(15, 40)(rng);
    macros["$AGE$"]           = int2str(age);
    macros["$GENDER$"]        = "male";
    macros["$GENUS$"]         = "robot";
    macros["$SPECIES$"]       = "chatterbot";
    macros["$NAME$"]          = "HAL";
    macros["$MASTER$"]        = "Tudor and Guanzhong";
    macros["$BIRTHPLACE$"]    = "Toronto";
    macros["$FAVORITEFOOD$"]  = "electricity";
    macros["$FAVORITECOLOR$"] = "blue";*/
}

void HALBot::UpdateMacro() {
    /*macros["$DATE$"]     = strftime("%B %d, %Y");
    macros["$TIME$"]     = strftime("%H:%M:%S");
    macros["$DATETIME$"] = strftime("%H:%M:%S on %B %d, %Y");
    macros["$ISOTIME$"]  = strftime("%Y-%m-%dT%H:%M:%S");*/
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

void HALBot::Learn(const string& question, const string& answer) {
    HALanswerList list;
    list.push_back(answer);
    Learn(question, list);
}

void HALBot::Learn(const string& question, const HALanswerList& answers) {
    string key(question);
    if (simple_word_subst.empty())
        InitWordSubst();
    for (auto i = simple_word_subst.cbegin(); i != simple_word_subst.cend(); ++i)
        boost::algorithm::ireplace_all(key, i->first, i->second);

    regex reg(regex_replace(key, wildcard2regex, string("(.*)")),
              regex_constants::ECMAScript|regex_constants::icase);
    HALdataEntry entry(key, reg, answers, "");
    data.push_back(entry);
    //datalist.insert(key);
    learn_file << '#' << key << '\n';
    for (auto i = answers.cbegin(); i != answers.cend(); ++i)
        learn_file << *i << '\n';
    learn_file << endl;
}

void HALBot::InitWordSubst() {
    simple_word_subst["the"] = "*";
    simple_word_subst["there"] = "*";
    simple_word_subst["they"] = "*";
    simple_word_subst["then"] = "*";
    simple_word_subst["their"] = "*";
    simple_word_subst["them"] = "*";
    simple_word_subst["this"] = "*";
    simple_word_subst["won't"] = "will not";
    simple_word_subst["shan't"] = "shall not";
    simple_word_subst["haven't"] = "have not";
    simple_word_subst["can't"] = "can not";
}
