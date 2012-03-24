#pragma once
#ifndef id06517314_2B45_4617_9A228B18BEED9043
#define id06517314_2B45_4617_9A228B18BEED9043

#include "stdafx.h"

typedef boost::fast_pool_allocator<string> string_pool;
//typedef forward_list<string, string_pool> HALanswerList;
typedef list<string, string_pool> HALanswerList;
typedef boost::fast_pool_allocator<HALanswerList> HALanswerList_pool;
//typedef unordered_map<string, HALanswerList, HALanswerList_pool> HALintel;
// HALdataEntry: Key, Regex, Answer List, Thinkset
typedef tuple<string, regex, HALanswerList, string> HALdataEntry;
typedef boost::fast_pool_allocator<HALdataEntry> HALdataEntry_pool;
typedef list<HALdataEntry, HALdataEntry_pool> HALintel;
typedef unordered_set<string> HALintelList;
//typedef tuple<regex, string> HALMacroListEntry;
//typedef map<string, HALMacroListEntry> HALMacroList;
typedef map<string, string> HALMacroList;
typedef vector<string> HALWordList;

class HALBot {
public:
    HALBot() {}
    HALBot(const string& path, bool write=false);
    HALBot(const string& path, const string& username, bool write=false);
    void Initialize(const string& path, const string& username="", bool write=false);
    string Ask(const string& question);
    void Learn(const string& question, const string& answer);
    void Learn(const string& question, const HALanswerList& answer);
#ifdef BUILD_PYTHON
    void Learn(const string& question, const boost::python::list& answer) {
        HALanswerList answers;
        for (int i = 0; i < boost::python::len(answer); ++i)
            answers.push_back(boost::python::extract<string>(answer[i]));
        Learn(question, answers);
    }
#endif
    ~HALBot();
protected:
    HALintel data;
    mt19937 rng;
    //HALintelList datalist;
    HALMacroList macros;
    HALMacroList simple_word_subst;
    HALMacroList readable_subst;
    HALWordList generic_answer;
    HALWordList word_removal;
    fstream learn_file;
    string prev_thinkset;
    
    static const regex wildcard2regex;
    static const regex caret_replace;
    static const regex space_normalize;
    static const string word_boundary;
    
    void InitMacro(const string& username);
    void InitWordSubst();
    void UpdateMacro();
    string Format(string answer, string matched);
private:
};

#endif
