import requests
from pprint import pprint
from bs4 import BeautifulSoup
#from arepl_dump import dump
import re
from difflib import get_close_matches
import codecs
import unidecode
import string

'''
First get URL and make a request to that URL,
next use BeautifulSoup to get HTML resulted
Then: 
    -get word in question
    -get meaning of word
    -get relations with that word
'''

def SearchWordUrl(word):
    url = 'https://lexico.pt/' + word
    return url

def getSoup(url):
    page = requests.get(url)

    return(BeautifulSoup(page.content,'html.parser'))

###     Getting the main word we are looking for.

def getMainWord (soup):

    word = ''
    mainword = soup.find_all('h1', class_='title')
    for thing in mainword:
        word=thing.text

    return word

###     Getting meaning(s) of word and treating strings...
def getMeanings(soup):

    text = ''
    meanings = []
    # For each element div with class main-content found, find an element with id='significado' and add it to text
    for element in soup.find_all('div', class_='main-content'):
        text+= str(element.find(id='significado'))
    # split the text to get a list well divided
    text=text.split('<br/> <br/>')
    #for each line in text append the split result to meanings
    for line in text:
        meanings.append(line.split('<br/>'))
    #for each meaning get the correct text
    for index,meaning in enumerate(meanings):
        for jndex,indexes in enumerate(meaning):
            meanings[index][jndex] = BeautifulSoup(meanings[index][jndex],"html.parser").text
            #if 'Do latim:' in meanings[index][jndex]:
            #    del meanings[index][jndex]
    
    if 'Forma do ver' in meanings[0][0]:
        meanings.pop([0][0])

    #erase etymology garbage
    etymology = 0 
    for i in range(len(meanings)):
        for j in range(len(meanings[i])):
            if 'Etimologia'  in meanings[i][j] or 'Etm.' in meanings[i][j]:
                etymology = 1
            if etymology == 1:
                break
            
    if etymology == 1:
        meanings = meanings[0:i+1]
    
    #copy the arrays 
    wordType = meanings.copy()
    #for each meaning check if string has number and place it on wordType.
    # also remove the number and delete empty meanings
    hadNumbers = 0
    for i in range(len(meanings)):
        for j in range(len(meanings[i])):
            if hasNumber(meanings[i][j]):
                hadNumbers=1
                wordType[i] = meanings[i][0]
            meanings[i][j] = re.sub(r'([0-9])\.\s','',meanings[i][j])
            meanings[i][j] = meanings[i][j].replace('\'','`')
            if not meanings[i][j]:
                del meanings[i][j]

    #delete meanings copied to wordType
    try:
        if(hadNumbers):
            for i in range(len(wordType)):
                del meanings[i][0]
    except Exception as e:
        print('Error in getting meaning')
        print(e)

    meanings = [ele for ele in meanings if ele != []] 
    wordType = [ele for ele in wordType if ele != []]


    for i,word in enumerate(wordType):
        if 'v.' in word:
            wordType[i] = 'verbo'
        if 'n.' in word:
            wordType[i] = 'nome'
        if 'adj.' in word:
            wordType[i] = 'adjetivo'
        if 'adv.' in word:
            wordType[i] = 'adverbio'
        if 'art.' in word:
            wordType[i] = 'artigo'
        if 'det.' in word:
            wordType[i] = 'determinante'
        if not word:
            wordType[i] = 'vazio'

    

    return meanings,wordType

def hasNumber(string):
    return any(char.isdigit() for char in string)

###   Getting relations to word.

def getRelations(soup):
    synonyms = []
    antonyms = []
    for relation in soup.find_all('div',class_='card card-pl'):
        if 'Sinónimo' in str(relation.h2):
            synonyms=relation.p.text.split(',')
        if 'Antónimo' in str(relation.h2):
            antonyms=relation.p.text.split(',')

    for index,word in enumerate(synonyms):
        if ' ' in word:
            synonyms[index]=word[1:]
        synonyms[index] = unidecode.unidecode(synonyms[index])

    for index,word in enumerate(antonyms):
        if ' ' in word:
            antonyms[index]=word[1:]   
        antonyms[index] = unidecode.unidecode(antonyms[index])    

    return synonyms,antonyms


def getWords(wordlist):
    iterations = 0
    exit = 0
    while exit == 0:
        try:
            allSoup = getSoup('https://lexico.pt/' + wordlist[iterations]+ '/')
            allSoup.find_all('div',id='ligacoes')

            if(allSoup.find_all('div',class_='next')):
                allSoup = allSoup.find_all('div',class_='next')
                for elements in allSoup:
                    wordFound=elements.a['href'][1:-1]
                if wordFound[0] != wordList[0][0]:
                    print (wordFound[0] + 'tem outra letra inicial que ' + wordList[0][0])
                    return
                print('Got Word: '+ wordFound + '. From word: ' + wordlist[iterations]+ '. In '+str(iterations+1) + ' iterations')
                wordlist.append(wordFound)
                saveWord(wordFound)
            iterations += 1
        except Exception as e: 
            print(e)
            print('Error getting words')
            print('On word ' + wordlist[iterations+1])
            print('Finished looking for words with ' + str(len(wordList)) + ' words')
            print('From '+wordList[0]+' to '+wordList[len(wordList)-1])
            exit = 1
    
    

def replaceWordTypes(wordTypes,word):
    types =['adjetivo','adverbio','artigo','conjuncao','determinante','interjeicao','preposicao','pronome','substantivo','verbo','nome','vazio' ]
    matches = []

    found = False
    cutoff = 0.4
            
    while found==False:
        try:
            for type in wordTypes:
                matches.append(get_close_matches(type,types,1,cutoff)[0])
                found = True          
        except Exception as e:
            cutoff=cutoff-0.1
            if cutoff < 0.1:
                    found = True
                    matches.append('vazio')
                    print('Cutoff')

    for index,match in enumerate(matches):
        if 'nome' in match:
            matches[index] = 'substantivo'

    return matches

'''
Now we need to setup the ontology,
need:
    prefixes
    classes
    objectProperties
    dataProperties
    individuals
'''

def setupPrefixes(file,name):
    prefixes = '@prefix : <http://www.tartesdajulia.com/ontologies/2020/'+name+'#> .'
    prefixes += '''\n@prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @base <http://www.tartesdajulia.com/ontologies/2020/Dicionario> .
                '''
    prefixes += '\n<http://www.tartesdajulia.com/ontologies/2020/'+name+'> rdf:type owl:Ontology .'

    file.write(prefixes)

def setupClasses(file):
    seperator = '''\n\n#################################################################
    #    Classes
    #################################################################'''

    file.write(seperator)

    wordTypesClass = '''\n
    :Type rdf:type owl:Class ;
      owl:equivalentClass [ rdf:type owl:Class ;
                            owl:oneOf ( :adjetivo
                                        :adverbio
                                        :artigo
                                        :conjucao
                                        :determinante
                                        :interjeicao
                                        :preposicao
                                        :pronome
                                        :substantivo
                                        :verbo
                                      )
                          ] .'''
    file.write(wordTypesClass)

    wordClass = '''\n\n:Word rdf:type owl:Class .'''
    file.write(wordClass)

def setupDataProperties(file):
    seperator = '''\n\n#################################################################
    #    Data properties
    #################################################################
    '''
    file.write(seperator)

    meaningDataProperty = '''\n:Significado rdf:type owl:DatatypeProperty ;
             rdfs:domain :Word .'''

    file.write(meaningDataProperty)

def setupObjectProperties(file):
    seperator = '''\n\n#################################################################
    #    Object Properties
    #################################################################''' 
    file.write(seperator)

    isSynonym = '''\n\n###  http://www.tartesdajulia.com/ontologies/2020/5/untitled-ontology-58#eSinonimo
    :eSinonimo rdf:type owl:ObjectProperty ,
                    owl:SymmetricProperty .'''

    file.write(isSynonym)

    isAntonym = '''\n\n###  http://www.tartesdajulia.com/ontologies/2020/5/untitled-ontology-58#eAntonimo
    :eAntonimo rdf:type owl:ObjectProperty ,
                    owl:SymmetricProperty .'''
    
    file.write(isAntonym)

    hasType ='''\n\n:temTipo rdf:type owl:ObjectProperty ;
         rdfs:domain :Word ;
         rdfs:range :Type .'''
        
    file.write(hasType)  

def setupStandardIndividuals(file):
    seperator = '''\n\n#################################################################
    #    Individuals
    #################################################################'''
    file.write(seperator)

    standardIndividuals = '''\n:adjetivo rdf:type owl:NamedIndividual ,
                       :Type .\n:adverbio rdf:type owl:NamedIndividual ,
                       :Type .\n:artigo rdf:type owl:NamedIndividual ,
                     :Type .\n:conjucao rdf:type owl:NamedIndividual ,
                     :Type .\n:determinante rdf:type owl:NamedIndividual ,
                       :Type .\n:interjeicao rdf:type owl:NamedIndividual ,
                          :Type .\n:preposicao rdf:type owl:NamedIndividual ,
                         :Type .\n:pronome rdf:type owl:NamedIndividual ,
                      :Type .\n:substantivo rdf:type owl:NamedIndividual ,
                          :Type .\n:verbo rdf:type owl:NamedIndividual ,
                :Type .'''
    file.write(standardIndividuals)

def handleOntology(name):
    file = open('Dicionario.ttl','w+')

    setupPrefixes(file,name)
    setupClasses(file)
    setupDataProperties(file)
    setupObjectProperties(file)
    setupStandardIndividuals(file)
    


    file.close()

def createIndividual(mainWord,types,meanings,synonyms,antonyms,ontologyName):
    file = codecs.open('Dicionario.ttl','a+','utf-8')

    header = '\n\n:' + mainWord +' rdf:type owl:NamedIndividual ,\n\t\t\t:Word ;'

    type = ''
    for i in range(len(types)):
        type += '\n\t\t:temTipo :' + types[i] +';'

    meaning = ''
    for i in range(len(types)):
        for j in range(len(meanings[i])):
            meaning +='\n\t\t:Significado \''+meanings[i][j]+'\' ;'

    antonym = ''
    for ant in antonyms :
        antonym += '\n\t\t:eAntonimo :' + ant +';'

    synonym = ''
    for syn in synonyms :
        antonym += '\n\t\t:eAntonimo :' + syn +';'

    file.write(header)
    file.write(type)
    file.write(meaning)
    file.write(antonym)
    file.write(synonym)
    file.write('.')
    file.close

def saveWord(word):
    url = SearchWordUrl(word)
    soup = getSoup(url)
    mainWord = getMainWord(soup)
    meanings,wordType = getMeanings(soup)
    wordType = replaceWordTypes(wordType,mainWord)
    synonyms,antonyms = getRelations(soup)
    createIndividual(mainWord,wordType,meanings,synonyms,antonyms,'Dicionario')

### main
#

url = SearchWordUrl('abaixo')
soup = getSoup(url)


allSoup= getSoup(url)
allSoup = allSoup.find(id='ligacoes')

mainword = getMainWord(soup)

meanings,wordType = getMeanings(soup)

wordType = replaceWordTypes(wordType,mainword)

synonyms,antonyms = getRelations(soup)

#createIndividual(mainword,wordType,meanings,synonyms,antonyms,'Dicionario')
### where the magic happens
ontologyName = 'Dicionario'

#handleOntology(ontologyName)

#wordList = ['buzinar']
#getWords(wordList)
#a,b,c,f,o,r
#'w','y','x','z'
#'s','t','u','v',
#'m','n','p','q',
#'a','b','c','d'
#alphabet= ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','y','x','z']
alphabet= ['pacatamente','q']


#alphabet = list(string.ascii_lowercase)

for letter in alphabet:
    wordList = [letter]
    getWords(wordList)

#for word in wordList:
#    url = SearchWordUrl(word)
#    soup = getSoup(url)
#    mainWord = getMainWord(soup)
#    meanings,wordType = getMeanings(soup)
#    wordType = replaceWordTypes(wordType,mainWord)
#    synonyms,antonyms = getRelations(soup)
#    createIndividual(mainWord,wordType,meanings,synonyms,antonyms,ontologyName)



#stop these variables from showing on AREPL
#repl_filter = ['element',
#                'BeautifulSoup',
#                'index',
#                'indexes',
#                'jndex',
#                'meaning',
#                'page',
#                'relation',
#                'text',
#                'thing',
#                'soup',
#                'line',
#                'allSoup',                ]