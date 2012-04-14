#pragma once
#ifndef id06517314_2B45_4617_9A228B18BEED9043
#define id06517314_2B45_4617_9A228B18BEED9043

#include "stdafx.h"

typedef boost::fast_pool_allocator<char> char_pool;
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
    HALBot();
    void Initialize(const string& path, const string& username="", bool write=false);
    string Ask(const string& question);
    string LoadFile(const string& filename);
    //void Learn(const string& question, const string& answer);
    //void Learn(const string& question, const HALanswerList& answer);
#ifdef BUILD_PYTHON
    boost::python::tuple pyAsk(const string& question);
    void pySetThinkSet(const string& thinkset) {
        prev_thinkset = thinkset;
    }
    string pyGetThinkSet() {
        return prev_thinkset;
    }
#endif
    ~HALBot();
protected:
    HALintel data;
    mt19937 rng;
    //HALintelList datalist;
    //HALMacroList macros;
    //HALMacroList simple_word_subst;
    //HALMacroList readable_subst;
    //HALWordList generic_answer;
    //HALWordList word_removal;
    //fstream learn_file;
    string prev_thinkset;
    
    static const regex wildcard2regex;
    static const regex caret_replace;
    static const regex space_normalize;
    static const string word_boundary;
    static const string rewildcard;
    static const string boundary_begin;
    static const string boundary_end;
    
    //void InitMacro(const string& username);
    //void InitWordSubst();
    //void UpdateMacro();
    string Format(string answer, string matched);
private:
};

#endif
