#!/usr/bin/python
# File Name : data.py
# Purpose : Collection of linguistic data not found in other areas of the Reconcile code base.
# Creation Date : 05-10-2011
# Last Modified : Mon 02 Dec 2013 01:30:19 PM MST
# Created By : Nathan Gilbert
#

#different types of determiners
alt_determiners = ("another", "other", "somebody else", "different")
articles = ("a", "an", "the")
cardinals = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "fifty", "infinite")
partitives = ("many", "much", "few", "little", "couple", "several", "most")
demonstratives = ("this", "that", "these", "those", "which", "yonder", "yon")
disjunctives = ("either", "neither")
distributives = ("each", "every")
electives = ("any", "either", "whichever")
equatives = ("same", "the same","equivalent")
evaluatives = ("such", "that", "so")
#exclamative = ("what eyes!")
existentials = ("some", "any")
relatives = ("who", "that","which", "what", "whom", "where", "when", "whose")
multals = ("a lot of", "many", "several", "much", "a lot", "alot")
negatives = ("no", "neither")
paucals = ("a few", "a little", "some")
#personals = ("we teachers", "you guys")
possessives = ("my", "your", "our", "his", "her", "its", "their")
quantifiers = ("all", "few", "many", "several", "some", "every", "each", "any", "no")
sufficiency = ("enough", "sufficient", "plenty")
uniquitives = ("the only", "single")
universals = ("all", "both")

#what is implemented inside of reconcile
reconcile_determiners = ("a", "an", "the", "this", "these", "that", "those")
acronym_killers       = ("la", "le", "for", "of")

#titles as repesented in Reconcile
titles = ("Mr.", "President", "vice", "Senator", "Correspondent", "Mrs.", "Ms.", "Dr.",
    "Speaker", "Mister", "Governor", "Chairman", "Professor", "Minister", "Mayor", "Congressman", "Commissioner",
    "Ambassador", "Attorney", "Lady", "Prosecutor", "Leader", "Spokesman", "Secretary", "Representative",
    "Millionaire", "Executive", "Officer", "Lieutenant", "Inspector", "Front-Runner", "Comedienne", "Columnist",
    "Businessman", "Senators", "Essayist", "Director", "Captain", "Actress", "Lawyer", "Chief", "Actor", "Republican",
    "Quarterback", "Publicist", "Principal", "Paramedic", "Legislator", "Sergeant ", "Reverend", "Reporter",
    "Official", "Diplomat", "Colonel", "Brother", "Writer", "Warden", "Mother", "Madame", "Madam", "Author", "Rev.",
    "Miss", "Father", "Democrat", "Republican", "official", "representative", "spokesman", "spokesperson",
    "spokeswoman", "chief", "head", "mr.", "mr", "messrs", "messrs.", "ms.", "ms", "mrs.", "mrs", "dr.", "dr", "prof.",
    "prof", "rev", "rev.", "rep.", "rep", "reps.", "reps", "sen.", "sen", "sens.", "sens", "gov.", "gov", "gen.",
    "gen", "maj.", "maj", "col.", "col", "lt.", "lt", "sgt.", "sgt",
    "president")

#determiner amalgamate classes
definite_determiners = cardinals + demonstratives + equatives + evaluatives + relatives + possessives + uniquitives #exclamatives and personals too
indefinite_determiners = disjunctives + electives + existentials + relatives + negatives + universals
articles_definite = definite_determiners + articles

#forms of 'to be'
to_be = ("is", "to be", "am", "are", "was", "were", "being", "been", "be")

#stop verbs for same_verb heuristic
stop_verbs = ("said", "have")

#pronouns 
#TODO: organize this better
FIRST_PER = ("i", "we", "us", "our")
ALL_PRONOUNS = ("all","another", "any", "anybody","anyone", "anything", "both",
"each", "each other", "either", "everybody", "everyone", "everything", "few",
"he", "her", "hers", "herself", "him", "himself", "his", "it", "its",
"itself", "little", "many", "me", "mine", "more", "most", "much", "myself",
"neither", "no one", "nobody", "none", "nothing", "one", "one another",
"other", "others", "ourselves", "several", "she", "some", "somebody",
"someone", "something", "that", "theirs", "them", "themselves", "these",
"they", "this", "those", "what", "whatever", "which", "whichever",
"who", "whoever", "whom", "whomever", "whose", "you", "yours", "yourself",
"yourselves", "their", "your", "my")+FIRST_PER

HARD_PRONOUNS = ("they", "them", "their", "its", "it", "our", "we")
RPRONOUNS = ("he", "she", "hers", "his", "i", "we", "our", "him")
POSSESSIVES = ("mine", "yours", "his", "hers", "its", "ours", "theirs", "whose")
REFLEXIVES = ("myself", "yourself", "himself", "herself", "itself",
              "ourselves", "yourselves", "themselves")
REL_PRONOUNS = ("there", "here")
ALL_REL = ALL_PRONOUNS+REL_PRONOUNS

THIRD_PERSON = ("he", "him", "she")
IT = ("it")
THIRD_PERSON_PLURAL = ("they", "them")
THIRD_SINGULAR_POSSESSIVES = ("his", "her")
IT_POSSESSIVE = ("its")
THIRD_PLURAL_POSSESSIVES = ("theirs")

dates = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
         "sunday", "january", "february", "march", "april","may", "june",
         "july", "august", "september", "october", "november","december",
         "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov",
         "dec")

muc4_months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
               "Sept", "Oct", "Nov", "Dec")

#adverbs 
time_adverbs = ("often", "seldom", "immediately", "last week", "today",
"daily", "meanwhile", "now", "then", "late", "last", "lastly", "never", "last\
year", "sometimes")
manner_adverbs = ("slowly", "very", "badly", "beautifully", "fluently")
place_adverbs = ("here", "downstairs", "around")
cause_adverbs = ("consequently", "therefore")
modal_adverbs = ("probably", "evidently")

def number_agreement(number1, number2):
    """Returns true if the two number types match in agreement."""

    if number1 == "PLURAL" and number2 == "PLURAL":
        return True
    elif number1 == "SINGLE" and number2 == "SINGLE":
        return True
    elif number1 == "UNKNOWN" or number2 == "UNKNOWN":
        return True
    else:
        return False

def gender_agreement(gender1, gender2):
    """Returns true if the two gender types match in agreement."""

    if (gender1 == "MASC") \
            and gender2 in ("MASC", "EITHER", "UNKNOWN"):
        return True
    elif (gender1 == "FEMININE") \
            and gender2 in ("FEMININE", "EITHER", "UNKNOWN"):
        return True
    elif (gender1 in ("EITHER","UNKNOWN")) \
            and gender2 in ("MASC", "FEMININE", "EITHER", "UNKNOWN"):
        return True
    else:
        return False

def semantic_agreement(annot1, annot2):
    """ Returns True if both match in semantic constraints """

    #check for dates
    if (annot1.getATTR("date") == "NONE") \
            and (annot2.getATTR("date") != "NONE"):
            return False
    elif (annot2.getATTR("date") == "NONE") \
            and (annot1.getATTR("date") != "NONE"):
            return False

    #check for the remaining semantic constraints
    if annot1.getATTR("semantic") == annot2.getATTR("semantic"):
        return True
    elif (annot1.getATTR("synsets") != []) \
            and (annot2.getATTR("synsets") != []) \
            and (annot1.getATTR("synsets")[0] == annot2.getATTR("synsets")[0]):
        return True
    elif (annot1.getATTR("pronoun") != "NONE") \
            and (annot2.getATTR("semantic") == "PERSON"):
        return True
    elif (annot2.getATTR("pronoun") != "NONE") \
            and (annot1.getATTR("semantic") == "PERSON"):
        return True
    else:
        return False

    return False

breakWords = ("a", "of", "in", "to", "at", "on", "by", "for", "against",
              "released", "whose", "who", "with", "this", "driving",
              "elected", "distributed", "that", "as", "which", "@", "based",
              "following", "surrounding", "had", "have")


