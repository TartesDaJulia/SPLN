import requests
from pprint import pprint
from bs4 import BeautifulSoup
from arepl_dump import dump
import re

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
    for element in soup.find_all('div', class_='main-content'):
        text+= str(element.find(id='significado'))

    text=text.split('<br/> <br/>')

    for line in text:
        meanings.append(line.split('<br/>'))

    for index,meaning in enumerate(meanings):
        for jndex,indexes in enumerate(meaning):
            meanings[index][jndex] = BeautifulSoup(meanings[index][jndex],"html.parser").text

    return meanings

###     Getting relations to word.

def getRelations(soup):
    synonyms = []
    antonyms = []
    for relation in soup.find_all('div',class_='card card-pl'):
        if 'Sinónimo' in str(relation.h2):
            synonyms=relation.p.text.split(',')
        if 'Antónimo' in str(relation.h2):
            antonyms=relation.p.text.split(',')

    return synonyms,antonyms

def getAllWords(url):
    words = []
    starter = 'a'
    allSoup = getSoup(url)
    allSoup.find_all('div',id='ligacoes')

    #ry:
    #while(True):
    if(allSoup.find_all('div',class_='next')):
        allSoup = allSoup.find_all('div',class_='next')
        for elements in allSoup:
            print(elements.a['href'])
    #except:
    #    print('END OF WORDS')

def getWord(word):
    try:
        allSoup = getSoup('https://lexico.pt/' + word)
    
        allSoup.find_all('div',id='ligacoes')
    
        if(allSoup.find_all('div',class_='next')):
                allSoup = allSoup.find_all('div',class_='next')
                for elements in allSoup:
                    wordFound=elements.a['href']
        print('Got Word: '+ wordFound + '. From word: ' + word)
        getWord(wordFound)
        return wordFound
    except:
        print('END OF WORDS')

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
                            owl:oneOf ( :Adjetivo
                                        :Adverbio
                                        :Artigo
                                        :Conjucao
                                        :Interjeicao
                                        :Numeral
                                        :Preposicao
                                        :Pronome
                                        :Substantivo
                                        :Verbo
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

def setupStandardIndividuals(file):
    seperator = '''\n\n#################################################################
    #    Individuals
    #################################################################'''
    file.write(seperator)

    standardIndividuals = '''\n
    :Adjetivo rdf:type owl:NamedIndividual ,
                       :Type .\n
    :Adverbio rdf:type owl:NamedIndividual ,
                       :Type .\n
    :Artigo rdf:type owl:NamedIndividual ,
                     :Type .\n
    :Conjucao rdf:type owl:NamedIndividual ,
                       :Type .\n
    :Interjeicao rdf:type owl:NamedIndividual ,
                          :Type .\n
    :Numeral rdf:type owl:NamedIndividual ,
                      :Type .\n
    :Preposicao rdf:type owl:NamedIndividual ,
                         :Type .\n
    :Pronome rdf:type owl:NamedIndividual ,
                      :Type .\n
    :Substantivo rdf:type owl:NamedIndividual ,
                          :Type .\n
    :Verbo rdf:type owl:NamedIndividual ,
                :Type .'''
    file.write(standardIndividuals)

def handleOntology(name,mainword,meanings,synonyms,antonyms):
    file = open('Dicionario.ttl','w+')

    setupPrefixes(file,name)
    setupClasses(file)
    setupDataProperties(file)
    setupObjectProperties(file)
    setupStandardIndividuals(file)
    


    file.close()

### main
##queryWord = 'ufa'
url = SearchWordUrl('a')

soup = getSoup(url)

allSoup= getSoup(url)
allSoup = allSoup.find(id='ligacoes')

getWord('zulu')


mainword = getMainWord(soup)

meanings = getMeanings(soup)

synonyms,antonyms = getRelations(soup)

allWords = getAllWords(url)

ontologyName = 'Dicionario'

handleOntology(ontologyName,mainword,meanings,synonyms,antonyms)


## stop these variables from showing on AREPL
arepl_filter = ['element',
                'BeautifulSoup',
                'index',
                'indexes',
                'jndex',
                'meaning',
                'page',
                'relation'
                ,'text',
                'thing',
                'soup',
                'line']