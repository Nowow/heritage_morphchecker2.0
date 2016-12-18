import re
import pymorphy2
import nltk
import time
import sys
from prjscript import morphSplitnCheck
# from wordsplitter import get_morphs, raspil
sys.path.append('C:/Users/Ivankov/Documents/GitHub/heritage_morphchecker2.0/spellchecker')
from spell_checker import check_word


def load_affixes():
    with open('C:/Users/Ivankov/Documents/GitHub/heritage_morphchecker2.0/resources/ru_RU.aff',
              'r',
              encoding='UTF-8') as aff:
        affixes = []
        for line2 in aff:
            affixes.append(line2.split())
    return affixes

# создаёт словарь вида {(набор граммем):[окончание1, окончание2 ...]}


def gram_to_affix(afflines):
    grammar = {}
    grammar['NOUN.им.п.м.р.'] = set()
    grammar['ADJF.им.п.м.р.'] = set()
    grammar['ADJS.им.п.м.р.'] = set()
    grammar['VERB.инф.'] = set()

    for affix in afflines:
        if len(affix) > 4 and affix[0] == 'SFX':
            try:
                if affix[5].strip('()') in grammar:
                    flexion = re.sub('[//[a-zA-Z]]*', '', affix[3])  # нужно убрать символы после слэша
                    grammar[affix[5].strip('()')].add(flexion)
                else:
                    grammar[affix[5].strip('()')] = set()
                    flexion = re.sub('[//[a-zA-Z]]*', '', affix[3])  # нужно убрать символы после слэша
                    grammar[affix[5].strip('()')].add(flexion)
            except:
                continue

            # окончания им.п.м.р.
            tag = affix[5].strip('()')
            nmsg = affix[2]
            if tag.startswith('NOUN.'):
                # if nmsg[-1] in 'бвгджзйклмнпрстфхцчшщ':
                #   nmsg += '0'
                grammar['NOUN.им.п.м.р.'].add(nmsg)
            if tag.startswith('ADJF.'):
                # if nmsg[-1] in 'бвгджзйклмнпрстфхцчшщ':
                #  nmsg += '0'
                grammar['ADJF.им.п.м.р.'].add(nmsg)
            if tag.startswith('ADJS.'):
                # if nmsg[-1] in 'бвгджзйклмнпрстфхцчшщ':
                # nmsg += '0'
                grammar['ADJS.им.п.м.р.'].add(nmsg)
            if tag.startswith('VERB.'):
                grammar['VERB.инф.'].add(nmsg)

    no = {'ая', 'яя', 'ее', 'ое', 'и', 'ы', 'ев', 'ей', 'ем', 'ом', 'ов', 'ет'}
    minus = grammar['ADJF.им.п.м.р.'].difference(no)
    grammar['ADJF.им.п.м.р.'] = minus
    minus = grammar['NOUN.им.п.м.р.'].difference(no)
    grammar['NOUN.им.п.м.р.'] = minus
    no2 = {'и'}
    minus = grammar['VERB.инф.'].difference(no2)
    grammar['VERB.инф.'] = minus

    # ====================МОЖЕТ И НЕ ПРИГОДИТЬСЯ
    # для случаев типа "загрязненией", "фантазием"
    grammar['NOUN.ед.ч.т.п.'].add('ией')
    grammar['NOUN.ед.ч.т.п.'].add('ием')
    grammar['NOUN.мн.ч.р.п.'].add('иев')
    # для случаев типа "руссками"
    grammar['ADJF.мн.ч.т.п.'].add('ами')
    grammar['ADJF.мн.ч.т.п.'].add('имы')

    return grammar

# создаёт словарь корней и алломорфов


def load_allomorphs():
    with open('C:/Users/Ivankov/Documents/GitHub/heritage_morphchecker2.0/resources/morphodict.csv',
              'r',
              encoding='utf-8') as morphodict:
        whole = []

        for line in morphodict:
            inLine = line.split(';')
            whole.append(inLine)

        allomorphs = {}
        roots = set()
        for part in whole:
            if part[2] == 'корень':
                if part[4] != '':
                    allomorphs[part[0]] = part[4].replace('ё', 'е')
                else:
                    if part[0] not in allomorphs:
                        allomorphs[part[0]] = part[1].replace('ё', 'е')
                roots.add(part[1])
        # save = open('allom.txt', 'w', encoding='utf-8')
        # save.write(str(allomorphs))
        # save.close()
    return allomorphs, roots



# проверяет, совпадают ли корни или алломорфы


def is_allomorph(lemma, root, variant_root, allomorph_dict):
    if lemma in allomorph_dict:  # если лемма есть в словаре Кузнецовой
        # регулярка - список алломорфов для леммы (вод|важд|вед)
        regexp = '^(' + re.sub('[0-9]', '', allomorph_dict[lemma]) + ')'
        print('Возможные алломорфы корня %s: %s \n' % (root, regexp))

        if re.match(regexp, root) != None and re.match(regexp, variant_root) != None:
            sys.stdout.write('Корень ' + root + ' - алломорф корня ' + variant_root + '\n')
            return True              
        else:
            sys.stdout.write('Не аллломорф' + '\n')
            if root == variant_root:
                sys.stdout.write('Один и тот же корень' + '\n')
                return True
            
            else:
                sys.stdout.write(root + ' не равно ' + variant_root + '\n')
                sys.stdout.write('Корни разные' + '\n')
                return False
    else:
        sys.stdout.write('Леммы нет в словаре Кузнецовой' + '\n')
        if root == variant_root:
            sys.stdout.write('Один и тот же корень' + '\n')
            return True
        else:
            sys.stdout.write(root + ' не равно ' + variant_root + '\n')
            sys.stdout.write('Корни разные' + '\n')
            return False

#получает одну лемму для нескольких словоформ
def one_lemma_only(lst):
    lemmaSet = set()
    for one in lst:
        one = re.sub('[^а-яА-Я]', ' ', one)
        parse = morph.parse(one)[0]
        lemma = parse.normalized.word.replace('ё', 'е')
        #lemma = lemmatize(one).replace('\n', '')
        lemmaSet.add(lemma)
    return list(lemmaSet) 
    
#ищет код в файле dic    
def code_finder(given):
    with open('C:/Users/Ivankov/Documents/GitHub/heritage_morphchecker2.0/resources/ru_RU.dic', 'r', encoding='UTF-8') as dic:
        codes = []
        for line in dic:
            if line.startswith(given + '/') == True:           
                codes = re.findall('[A-Za-z]{2}', line) #код состоит из 2 латинских букв
        if not codes:
            sys.stdout.write('Слова ' + given + ' нет в словаре aff\n')
    return codes       

#создаёт для кода в файле dic список кортежей по файлу aff [(заменяемая часть, заменяющая часть, условие)]   
def code_to_rules(code, codelines):
    allRules = []
    for affix2 in codelines:
        if len(affix2) > 5 and affix2[1] == code:
            old = affix2[2]
            new = re.sub('[//[a-zA-Z]]*', '', affix2[3]) #нужно убрать символы после слэша
            condition = affix2[4]
            gram = affix2[5].strip('()')
            allRules.append((old, new, condition, gram)) 
    return allRules

# находит граммемы для окончания
def what_gram(flex, dict_):
    grams = set()
    for key in dict_:
        for b in dict_[key]:
            if b == flex:
                grams.add(key)
    return grams

def sample(filename):
    err = open(filename, 'r', encoding='utf-8')
    wordsInLine = []
    for errline in err:
        wordsInLine.append(errline.split())   

    errors = {}
    for word in wordsInLine:
        errors[word[0]] = []
        for var in range(1, len(word)):  
            errors[word[0]].append(word[var])

    return errors

def spellcheck(word_to_check):
    correct = False
    if naivecheck(word_to_check) == True:
        print('Всё правильно: %s' %word_to_check)
        errors = {word_to_check: word_to_check} 
        print(errors)        
        correct = True        
    else:
        spellchecked = check_word(word_to_check, ' ', ' ', 
                                  accent_mistakes={}, big_ru={},  
                                  multiword=False )['mistake']
        errors = {word_to_check: spellchecked}
    return errors, correct

def naivecheck(word_to_check):
    with open('C:/Users/Ivankov/Documents/GitHub/heritage_morphchecker2.0/resources/All_Forms+.txt', 'r', encoding='utf-8') as file:
        all_forms = file.read().split()
    if word_to_check in all_forms:
        return True

affix_dict = load_affixes()
gram_dict = gram_to_affix(affix_dict)
allomorph_dict = load_allomorphs()
initial_forms = ['NOUN.им.п.м.р.', 'ADJF.им.п.м.р.', 'ADJS.им.п.м.р.', 'VERB.инф.']
stemmer = nltk.stem.snowball.RussianStemmer(ignore_stopwords=False)
morph = pymorphy2.MorphAnalyzer()



# e = sample('testset_corrections.txt')



def morphcheck(errors, correct):

    if correct == True:
        output = errors
    else:
        
        start_time = time.time()
              
        output = {}
        
        for error in errors:
            print('\nСлово с ошибкой: %s' % error)
            
            output[error] = set()

            # Word Splitting
            morphs = morphSplitnCheck(error)
            stem = stemmer.stem(error) 
            root = morphs.root
            flexion = morphs.postfix

            # затыкаем кое-какие дыры        
            flexion = re.sub('^н', '', flexion)        
            if re.search('^(ющ|ящ|ущ|ащ|щ|вш)', flexion) == True:
                flexion = re.sub('^(ющ|ящ|ущ|ащ|щ|вш)', '', flexion)

            print('Корень: ' + root)
            print('Окончание: ' + flexion)    

            # Grammeme Search
            tags = what_gram(flexion, gram_dict) 
            print('Окончание - показатель: ' + str(tags))
            if not tags:
               print('Окончание отсутствует \n')

            # Lemma Identification
            variants = one_lemma_only(errors[error])
            
            for variant in variants:
                print('\nВариант исправления: ' + variant)
                parsed = morph.parse(variant)[0]
                # lemma = parsed.normalized.word.replace('ё', 'е')
                
                lemma = variant           
                pos = parsed.tag.POS

                # затыкаем дыры в словаре .aff
                if stem == 'лучш':
                    lemma = 'лучший'    
                    pos = 'ADJF'

                if pos == 'PRTF':
                    pos = 'ADJF'  
                    lemma = parsed.inflect({'sing', 'nomn'}).word.replace('ё', 'е')

                if pos == 'INFN':
                    pos = 'VERB' 

                if lemma in ['живой', 'молодая', 'прошлое', 'настоящее', 'прямая']:
                    parsed = morph.parse(variant)
                    for p in parsed:
                        if p.tag.pos == 'ADJF':
                            lemma = p.normalized.word.replace('ё', 'е')
                            pos = p.tag.POS
                            continue

                if lemma == 'сосед':
                    lemma = 'соседи'

               # Wrong Root Filter
                variant_morphs = morphSplitnCheck(variant)
                variant_root = variant_morphs.root
                print('Корень варианта:' + variant_root)     

                # проверям на алломорфизм, берём список алломорфов, лемму варианта, корень ошибки, корень варианта
                if is_allomorph(lemma, root, variant_root, allomorph_dict[0]) == True:

                    # Wrong pos Filter
                    right_pos = []
                    for tag in tags:
                        if pos != None:
                            if tag.startswith(pos): 
                                right_pos.append(tag)  
                        else:
                            print('pos = None')
                    
                    for a_tag in right_pos:
                        if a_tag in initial_forms: #если окончание указывает на начальную форму
                            needed = lemma #то правильная форма - это лемма и есть
                            output[error].add(needed) 

                    # Reconstruction
                    codes = code_finder(lemma)
                    for code in codes:
                        for rule in code_to_rules(code, affix_dict):
                            old, new, condition, grams = rule
                            for right_tag in right_pos:
                                if right_tag in grams:
                                    if re.search(condition + '$', lemma) != None:
                                        needed = re.sub(old.replace('0', '') + '$', new, lemma)
                                        output[error].add(needed.replace('0', ''))    

        """with open('output.txt', 'a', encoding = 'utf-8') as outfile:
            for out in output:
                print(str(out) + ' ' + str(output[out]) + '\n')        
                outfile.write(str(out) + ' ' + str(output[out]) + '\n')"""
 
        print(time.time() - start_time)
    return output
