#include "stdafx.h"
#include "HALBot.h"
#include "helper.h"
#include "exception.h"
#include "console.h"

HALBot::HALBot(const string& path, bool write) {
    this->Initialize(path, "", write);
}

HALBot::HALBot(const string& path, const string& username, bool write) {
    this->Initialize(path, username, write);
}

const regex HALBot::wildcard2regex("\\s*\\*\\s*", regex_constants::ECMAScript|regex_constants::optimize);
const regex HALBot::caret_replace("\\^", regex_constants::ECMAScript|regex_constants::optimize);

void HALBot::Initialize(const string& path, const string& username, bool write) {
    // Initialize the data structure
    HALanswerList replies;
    string key;
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
            case '#':
                // New Command
                if (!key.empty()) {
                    regex reg(regex_replace(key, wildcard2regex, string("(.*)")),
                              regex_constants::ECMAScript|regex_constants::icase/*|
                              regex_constants::optimize*/);
                    HALdataEntry entry(key, reg, replies);
                    data.push_back(entry);
                    replies.clear();
                    datalist.insert(key);
                }
                key = temp+1;
                if (key[0] == '_') {
                    key[0] = '.';
                    key[1] = '*';
                }
                break;
            //case '>':
                /*string ptrkey(temp+1);
                if (datalist.count(ptrkey)) {

                }*/
            case '\0':
                break;
            default:
                //replies.push_front(temp);
                replies.push_back(temp);
            }
        }
        key.clear();
        replies.clear();
        file.close();
    }

    if (write)
        cout << flush;
    InitMacro(username);
}

void trim(string& str) {
    boost::algorithm::trim(str);
}

string HALBot::Ask(const string& question) {
    typedef tuple<string, string, size_t> entry;
    vector<entry> possible;
    smatch results;
    for (auto i = data.cbegin(); i != data.cend(); ++i) {
        if (regex_search(question, results, get<1>(*i))) {
            const HALanswerList &answers = get<2>(*i);
            for (auto j = answers.cbegin(); j != answers.cend(); ++j)
                possible.push_back(entry(*j, results[1], get<0>(*i).length()));
        }
    }
    if (possible.empty()) {
        return "I can't seem to understand.";
    } else {
        int best = 0xFFFFFFFF;
        for (auto i = possible.cbegin(); i < possible.cend(); ++i) {
            //if (get<1>(*i).length() < best)
            //  best = get<1>(*i).length();
            if (question.length() - get<2>(*i) < best)
                best = question.length() - get<2>(*i);
        }
        best += 3;
        for (auto i = possible.begin(); i < possible.end();) {
            //if (get<1>(*i).length() > best) {
            if (question.length() - get<2>(*i) > best) {
                i = possible.erase(i);
            } else {
                ++i;
            }
        }
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
        return Format(answer, matched);
    }
}

void HALBot::InitMacro(const string& username) {
    if (username.empty()) {
        string username(getenv("USERNAME"));
        ConPrompt("Enter your name", username);
        macros["$USERNAME$"] = username;
    } else
        macros["$USERNAME$"] = username;
    int age = uniform_int_distribution<>(15, 40)(rng);
    macros["$AGE$"]           = int2str(age);
    macros["$GENDER$"]        = "male";
    macros["$GENUS$"]         = "robot";
    macros["$SPECIES$"]       = "chatterbot";
    macros["$NAME$"]          = "HAL";
    macros["$MASTER$"]        = "Tudor and Guanzhong";
    macros["$BIRTHPLACE$"]    = "Toronto";
    macros["$FAVORITEFOOD$"]  = "Electricity";
    macros["$FAVORITECOLOR$"] = "Blue";
}

void HALBot::UpdateMacro() {
    /*macros["DATE"]     = HALMacroListEntry(regex("$DATE$"), strftime("%B %d, %Y"));
    macros["TIME"]     = HALMacroListEntry(regex("$TIME$"), strftime("%H:%M:%S"));
    macros["DATETIME"] = HALMacroListEntry(regex("$DATETIME$"), strftime("%H:%M:%S on %B %d, %Y"));
    macros["ISOTIME"]  = HALMacroListEntry(regex("$ISOTIME$"), strftime("%Y-%m-%dT%H:%M:%S"));*/
    macros["$DATE$"]     = strftime("%B %d, %Y");
    macros["$TIME$"]     = strftime("%H:%M:%S");
    macros["$DATETIME$"] = strftime("%H:%M:%S on %B %d, %Y");
    macros["$ISOTIME$"]  = strftime("%Y-%m-%dT%H:%M:%S");
}

string HALBot::Format(string answer, string matched) {
    UpdateMacro();
    for (auto i = macros.cbegin(); i != macros.cend(); ++i)
        //answer = regex_replace(answer, get<0>(i->second), get<1>(i->second));
        boost::algorithm::replace_all(answer, i->first, i->second);
    boost::algorithm::trim(matched);
    answer = regex_replace(answer, caret_replace, matched);
    return answer;
}

/*string HALBot::Ask(const string& question) {
    if (question.empty())
        return "Say something";
    try {
        Process(question);
    } catch (string ans) {
        return ans;
    }
}*/

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
        boost::algorithm::replace_all(key, i->first, i->second);

    regex reg(regex_replace(key, wildcard2regex, string("(.*)")),
              regex_constants::ECMAScript|regex_constants::icase);
    HALdataEntry entry(key, reg, answers);
    data.push_back(entry);
    datalist.insert(key);
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
