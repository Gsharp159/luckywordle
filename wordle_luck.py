import statistics as stats
from wordfreq import word_frequency as wf
from sigfig import round
from colorama import Fore, Style, Back
import math
import os
import scipy.stats
from time import process_time


# if the final word is green, enter the yellow and greens 
# from the second to last guess, and all the grays from all prior guesses
# 
# not for entering the final guess
greens = ['', 'a', '', 'e', '']
yellows = ['', '', '', '', '']
grays = ['s', 'r', 'c', 'b', 'n', 'd']

#MAKE SURE AFTER ENTERING CURRENT GUESS TO UPDATE COLORS OR COMBINATIONS WONT WORK
#(if incorrect word, but you can put in for final word if you want to know how good your second to last was)
cur_guess = 'soily' #word directly before the correct final or most recent guess
correct_word = '' #either the correct guess or the most recent guess

#all valid words after given letters
valids = []
all_words = []

#longest process so optimize later
def genValids(Gs=['', '', '', '', ''], Ys=['', '', '', '', ''], Grs=[]):

    v = []

    with open('Resources/valid-wordle-words.txt', 'r') as file:
        while (True): #bro theres gotta be a way that isnt this
            cflag = False

            line = file.readline().strip().lower()

            if not line:
                break
            
            #check grays
            for letter in Grs:
                if letter in line:
                    cflag = True

            #check greens
            for i in range(5):
                if Gs[i] == '':
                    continue

                if Gs[i] != line[i]:
                    cflag = True

            #if 2 yellows are the same letter is broken? fix
            #check yellows
            for i in range(5):
                if Ys[i] == line[i]:
                    cflag = True
                    continue #is this necessary
                
                elif not Ys[i] in line:
                    cflag = True

            if not cflag:
                v.append(line)

    return v

def checkValids(Gs, Ys, Grs, list):

    v = []

    #allow it to see all grays so it isnt dumb
    Grs += grays

    #write optimally
    for word in list:

        cflag = False #flag if word is invalid

        #check grays
        for letter in Grs:
            if letter in word:
                cflag = True

        #check greens
        for i in range(5):
            if Gs[i] == '':
                continue

            if Gs[i] != word[i]:
                cflag = True

        #if 2 yellows are the same letter is broken? fix
        #check yellows
        for i in range(5):
            if Ys[i] == word[i]:
                cflag = True
                continue #is this necessary
            
            elif not Ys[i] in word:
                cflag = True

        if not cflag:
            v.append(word)

    return v

#must know correct word
def getColors(word, correct=correct_word):

    locgreens = ['', '', '', '', '']
    locyellows = ['', '', '', '', '']
    locgrays = [] 

    for i in range(len(word)-1):
        if word[i] == correct[i]:
            locgreens[i] = word[i]
        if word[i] != correct[i] and word[i] in correct and not word[i] in locgreens:
            locyellows[i] = word[i]
        else:
            if not word[i] in correct:
                locgrays.append(word[i])

    return(locgreens, locyellows, locgrays)

def getColorsTotals(word, knowCorrectWord=False):
    total_green = 0
    total_yellow = 0
    deltagray = [] #list of new grays in word

    #fix
    if not knowCorrectWord:
        for i in range(5):
            if greens[i] != '':
                total_green += 1
            if yellows[i] != '':
                total_yellow += 1
        return (total_green, total_yellow)

    confgreen = []
    for i in range(5):
        if word[i] == correct_word[i]:
            total_green += 1
            confgreen.append(word[i])
        if word[i] != correct_word[i] and word[i] in correct_word:
            total_yellow += 1 if not word[i] in confgreen else 0 #check if is false yellow (valet, talea, last a is a false yellow)
        if not word[i] in correct_word and not word[i] in grays:
            deltagray.append(word[i])

    return (total_green, total_yellow, deltagray)

def getAR(word_list):
    valids = word_list
    total_letters = len(word_list) * 5
    totals = [0] * 26
    appearance_rate = {'a': 0, 'b' : 0, 'c': 0, 'd' : 0, 'e': 0, 'f' : 0, 'g': 0, 'h' : 0, 
                       'i': 0, 'j' : 0, 'k': 0, 'l' : 0, 'm': 0, 'n' : 0, 'o': 0, 'p' : 0, 
                       'q': 0, 'r' : 0, 's': 0, 't' : 0, 'u': 0, 'v' : 0, 'w': 0, 'x' : 0, 'y' : 0, 'z' : 0}

    for word in word_list:
        for letter in word:
            totals[ord(letter) - 97] += 1

    #can be simplified
    i = 0
    for key in appearance_rate:
        if totals[i] == 0:
            i += 1
            continue
        else:
            appearance_rate[key] = totals[i]/total_letters
            i += 1

    return(appearance_rate)


#getAR(valids)
#print(getAR(valids))
#current scoring is by average appearance rate of letters in valid words
def scoreAR(word, word_list):
    

    word_score = 0

    for letter in word:
        if letter in grays or letter in yellows or letter in greens:
            continue
        else:
            word_score += (getAR(word_list)[letter])

    #percentage avg appearance rate
    #return ((word_score/5)*100)

    #normalized
    if word_score == 0:
        return(0)
    else:
        return(1/((word_score/5)*100))

def scoreSmart(word):

    wfScore = math.log(wf(word, 'en') * 100 / 0.00251)
    letScore = scoreWordRaw(word)
    ARScore = scoreAR(word)

    cowf = 1
    cols = 0.2
    coars = 3

    return((cowf*wfScore)*(cols*letScore)*(coars*ARScore))

def getYellowCoef(k, n):
    yellow_coefficient = 1

    total = (math.factorial(k)/math.factorial(k-n))
    sigma = 0 #if n=1
    if n == 2:
        sigma = ((n*(math.factorial(k-1)/math.factorial(k-n))))
    if n > 2:
        for i in range(1, n): #python subtracts 1 from max val automatically
            sigma += (((-1)**(i-1)) * (n*(math.factorial(k-i)/math.factorial(k-n))))
            print(sigma, i)
    final = (-1)**n if n != 0 else 0

    yellow_coefficient = total - sigma + final

    return yellow_coefficient

#returns remaining valid combinations given colors
def combinations(guess, knowCorrectWord=False):
    k = len(guess)
    ny = getColorsTotals(guess, knowCorrectWord)[1] #total yellow
    ng = getColorsTotals(guess, knowCorrectWord)[0] #total green
    ngray = (len(grays) + len(getColorsTotals(guess, knowCorrectWord)[2]))

    return (getYellowCoef((k-ng), ny) * ((26-ngray)**(k-(ng+ny))))

#dont need to regenerate full list every time
def scoreCom(word, word_list):
    com_list = []
    for word in valids:
        com_list.append((word, int(combinations(word, True)), len(checkValids(getColors(word)[0], getColors(word)[1], (grays + getColors(word)[2]), valids))))

    print(com_list)

#rework so u can manual inp greens and yellows and such so as not require correct as arg
#also will b v slow because looping over list and each word twice because wordelim call 
#returns (surprisal, expected surprisal / info gain / h)
def infoScore(guess, correct, word_list):
    #these are giving incorrect values
    after = wordsElim(guess, correct, word_list)[1]
    difference = wordsElim(guess, correct, word_list)[0]
    before = after + difference

    uBefore = math.log(before, 2)
    uAfter = 0 if after == 0 else math.log(after, 2)

    gain = (uBefore - uAfter)
    return (gain)

v = genValids(greens, yellows, grays)
def getExpectedInfo(guess, word_list, valid=v):
    #guess=word to be checked, word_list=list of words to iterate over treating each as correct, valid=workaround ignore

    #remains = []

    #for cor in word_list:

    #    rem = wordsElim(guess, cor, valid)[1] #using valids rn to try speed up
    #    remains.append(0 if rem <= 0 else math.log(rem, 2)) #len rem = number of rmaining words given guess and a random correct word


    if len(word_list) == 0:
        return 0

    remains = []
    def func(corct):
        rem = wordsElim(guess, corct, valid)[1]# - 0 if guess in valid else 1 #using valids rn to try speed up
        return (1 if rem <= 0 else math.log(rem, 2)) #len rem = number of rmaining words given guess and a random correct word

    remains = map(func, word_list)

    #remains = map(str.upper, word_list)

    #iterator = (s.upper() for s in oldlist)


    return(stats.fmean(list(remains)))




#fix yellows in here
#reowrk so u can manual inp freens and yellows n suich so not require correct as arg
def wordsElim(guess, correct, word_list):
    valids = word_list
    before = len(valids)
    #newValids = []
    total = 0

    if guess == correct:
        return (before, 1)

    #use written function for this pls
    guess_greens = ['', '', '', '', '']
    guess_yellows = ['', '', '', '', '']
    guess_grays = []

    for i in range(5):
        if guess[i] == correct[i]:
            guess_greens[i] = guess[i]
        if guess[i] in correct and not guess[i] == correct[i]:
            guess_yellows[i] = guess[i]
        elif not guess[i] in correct:
            guess_grays.append(guess[i])

    for word in valids:
        cflag = True
        for i in range(5):
            if word[i] in grays or word[i] in guess_grays:
                cflag = False
                continue
            if (not guess_greens[i] == '') and (guess_greens[i] != word[i]):
                cflag = False
                continue
            if not guess_yellows[i] in word:
                cflag = False
                continue

        if cflag:
            #newValids.append(word)
            total += 1

    return((before - total, total))

#inefficient rewrite
def scoreFreq():
    global freqs, freqs_normal, freqs_unlinked, over_threshold_unlinked
    freqs = []
    freqs_normal = []

    max = 0.00251
    min = 0
    #min can be 1.02e-08 if want non zero value

    def normal(x, min, max):
        #x = math.log(x, 10)
        #uncomment for nonzero values
        #min = math.log(min, 10)
        #max = math.log(max, 10)
        return(((x-min) * 100) / (max - min))

    freqs.sort(reverse=True, key=lambda a : a[1])

    #current line is at the bottom 5500 words (pretty generous)
    threshold = normal(2.95e-08, min, max)

    for word in valids:
        freq = round(normal((wf(word, 'en')), min, max), decimals=3)
        freqs.append((word, round(wf(word, 'en'), decimals=3)))
        freqs_normal.append((word, freq, (freq > threshold)))

    freqs_unlinked = []
    over_threshold_unlinked = []
    for thing in freqs_normal:
        freqs_unlinked.append(thing[1])
        over_threshold_unlinked.append(thing[2])

#todo
def combinatorialRank():
    #before = combinations(guess, correct)
    global com_rank
    com_rank = []

    for word in valids:
        com_rank.append((word, combinations(word, correct_word)))

    com_rank.sort(reverse=True, key=lambda a : a[1])

#= single data point, data = full set
def zscore(x, data):
    mean = stats.mean(data)
    std = stats.stdev(all_scores)
    return((x-mean)/std)

#later add left and right options
def pvalue(z):
    return(scipy.stats.norm.sf(abs(z)))

#guess being the correct word or most recent
def printStats(guess, scoremethod, word_list):

    valids = word_list
    os.system('')

    #scoreGuess(guess), scoreWordRaw(), etc
    #scoreFunc = scoreWordRaw(guess)
    score = scoreAR(guess, valids)
    print(score, 'score')
    difference = round(score - (stats.mean(all_scores)), decimals=3)

    print(Fore.LIGHTYELLOW_EX, 'Your guess: ', cur_guess, (Fore.GREEN + ' (correct)') if cur_guess == correct_word else (Fore.RED + ' (incorrect)'), Style.RESET_ALL)

    print('VALID WORDS', Fore.GREEN, valids[0:10], ('... [' + valids[len(valids)-1] + ']') if len(valids) > 10 else '', Style.RESET_ALL)

    print(' ', 'SCORE', Fore.CYAN, all_scores_rounded[0:10], ('... [' + str(all_scores_rounded[len(all_scores_rounded)-1]) + ']') if len(all_scores_rounded) > 10 else '', Style.RESET_ALL)

    print(' ', 'FREQUENCY', Fore.CYAN, freqs_unlinked[0:10], ('... [' + str(freqs_unlinked[len(freqs_unlinked)-1]) + ']') if len(freqs_unlinked) > 10 else '', Style.RESET_ALL)

    print('    ', 'USABLE', Fore.CYAN, over_threshold_unlinked[0:10], ('... [' + str(over_threshold_unlinked[len(over_threshold_unlinked)-1]) + ']') if len(over_threshold_unlinked) > 10 else '', Style.RESET_ALL)

    print(Fore.LIGHTMAGENTA_EX, '-----------------------------------------------', Style.RESET_ALL)

    print('Number of remaining words: ', Fore.CYAN, len(valids), Style.RESET_ALL)

    print('Random guess chance: ' + Fore.CYAN + str(round((1/len(valids) * 100), decimals=2)) + '%' + Style.RESET_ALL)

    print(Fore.LIGHTMAGENTA_EX, '------------------AR-SCORE---------------------', Style.RESET_ALL)

    print('Average score: ' + Fore.CYAN + str(round(stats.mean(all_scores), decimals=3)) + Style.RESET_ALL)

    #print('Standard Deviation: ' + Fore.CYAN + str(round(stats.stdev(all_scores), decimals=3)) + Style.RESET_ALL)

    print('Variance: ' + Fore.CYAN + str(round((stats.stdev(all_scores) ** 2), decimals=3)) + Style.RESET_ALL)

    print('Your guess score: ' + Fore.CYAN + str(score) + Style.RESET_ALL)

    print('Difference from mean: ' + Fore.CYAN + ('+' if difference > 0 else '') + str(difference) + Style.RESET_ALL)

    #print('Z Score: ' + Fore.CYAN + str(round(zscore(score, all_scores), decimals=3)) + Style.RESET_ALL)

    #print('P Value(%): ', Fore.CYAN, round(100-(pvalue(zscore(score, all_scores)))*100, decimals=3), '%', Style.RESET_ALL)

    #print('Combinations eliminated: ', Fore.CYAN, combinations(cur_guess, correct_word), Style.RESET_ALL)

    print('Words eliminated: ', Fore.CYAN, wordsElim(cur_guess, correct_word, word_list)[0], Style.RESET_ALL, '\n')


















def mainPost():
    valids = genValids(greens, yellows, grays) #generates valid word list
    scoreFreq() #generates frequency value for each word
    scoreFunc = scoreAR #defines a scoring metric for printstats to use

    global all_scores, all_scores_rounded
    all_scores = []
    all_scores_rounded = []
    #for word in valids:
        #all_scores.append(scoreFunc(word, valids))

    #for thing in all_scores:
        #all_scores_rounded.append(round(thing, decimals=3))

    #printStats(cur_guess, scoreFunc, valids)

    #print(max(all_scores), valids[all_scores.index(max(all_scores))])

    valids.sort(reverse=True, key=lambda a : wf(a, 'en'))
    print('SORTED BY WF', Fore.GREEN, valids[0:10], ('... [' + valids[len(valids)-1] + ']') if len(valids) > 10 else '', Style.RESET_ALL)

    #print(wordsElim(cur_guess, correct_word, valids))
    #print(infoScore(cur_guess, correct_word, valids))

    gains = []
    for word in valids:
        gains.append((infoScore(word, correct_word, valids), word))

    #print(gains)

    gains.sort(reverse=True, key=lambda a : a[0])
    print([gain[1] for gain in gains])

    #print(getExpectedInfo('alert', valids))
    #print(infoScore('alert', correct_word, valids))

    exgains = []
    for word in valids:
        exgains.append((getExpectedInfo(word, valids), word))

    print(exgains)

    exgains.sort(reverse=False, key=lambda a : a[0])
    print([exgain[1] for exgain in exgains])







def mainPre():
    valids = genValids(greens, yellows, grays) #generates valid word list
    all_words = genValids()

    scoringlist = []
    if len(valids) >= 100:
        scoringlist = valids
    else:
        scoringlist = all_words

    #manual override
    scoringlist = all_words

    exgains = []
    for word in scoringlist:
        h = getExpectedInfo(word, valids)
        exgains.append((h, word))

        print(word, h)

    #instead of going over all words, why not only some, so between valids and all (semi valids)

    #exgains = list(map(lambda w: getExpectedInfo(w, valids), all_words))
    #print('maps done, checking', len(exgains), 'words')

    exgains.sort(reverse=False, key=lambda a : a[0])

    tops = []
    maxScore = exgains[0][0]
    for eval in exgains:
        if eval[1] in valids and eval[0] == maxScore:
            tops.sort(reverse=True, key=lambda a : wf(a[1], 'en'))
            tops.insert(0, eval)
            break

        if eval[0] == maxScore:
            tops.append(eval)


    print(Fore.GREEN, 'TOP 10 WORDS', Style.RESET_ALL, [top[1] for top in tops[0:10]])
    print(Fore.GREEN, 'TOP 10 SCORES', Style.RESET_ALL, [round(top[0], decimals=3) for top in tops][0:10])

    equals = 0
    lucky_guess = 'itchy'
    lucky_info = getExpectedInfo(lucky_guess, valids)
    for eval in exgains:
        if eval[0] <= lucky_info:
            equals += 1

    print(equals, 'words as good as or better than', )
    print('PROBABILITY AT THIS STAGE', (100/equals), '%')
    print('Improbability of this is equivalent to', round(-1*(math.log((1/equals))/math.log(2)), decimals=3), 'consecutive coin flips')
    




#mainPost()
mainPre()
