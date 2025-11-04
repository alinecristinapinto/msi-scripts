from collections import defaultdict

# --------------------------------------------------------------------------
# STOPWORDS GERAIS
# Palavras que sao "ruido" em perguntas do Stack Overflow
# --------------------------------------------------------------------------
GENERAL_STOPWORDS = {
    # Meta-linguagem do SO
    "hello", "hi", "thanks", "thank", "please", "help", 
    #"question", "problem", "issue", "answer", "example", "solution", # verificar resultados do bertopic (se polui)
    "anyone", "something", "anything", "however", "every",
    "follow", "following", # ex: "following code", "following error"
    
    # Verbos comuns (o que o usuario esta "tentando" fazer)
    "trying", "want", "need", "know", "like", "using", "use",
    "get", "getting", "run", "running", "work", "working",
    "find", "see", "look", "looking", "seems", "seem", "call", "called",
    "create", "creating", "understand",
    
    # Jargao genérico de programação
    # "code", "error", "file", "data",  # verificar resultados do bertopic (se polui)
    "im", "ive", "id", "its", "it", "is", "im", # contrações comuns
    "sure", "simple", "another", "new", "different", "able", "unable",
     "way", "also", "one", "two"
}

# --------------------------------------------------------------------------
# STOPWORDS ESPECIFICAS POR TAG
# O nome da proópria tag e suas variantes mais comuns
# --------------------------------------------------------------------------
TAG_SPECIFIC_STOPWORDS = {
    "julia": {"julia", "jl"},
    
    "r": {"r"}, 
    
    "dart": {"dart", "flutter"}, # Flutter é 99% do universo Dart no SO
    
    "bash": {"bash", "shell", "script", "scripts"}, 
    
    "python": {"python", "py"},
    
    "javascript": {"javascript", "js", "node", "nodejs"},
    
    "java": {"java"},
    
    "c#": {"csharp", "c#", ".net"},
}

# --------------------------------------------------------------------------
# DICIONARIO FINAL
# Combina as palavras gerais com as especificas de cada tag
# --------------------------------------------------------------------------

# Cria um defaultdict. Se a TAG nao for encontrada, ele retorna 
# o conjunto GERAL por padrao, o que evita erros.
STOPWORD_SETS = defaultdict(lambda: GENERAL_STOPWORDS)

# Itera sobre as tags especificas e cria o conjunto final para cada uma
for tag, specific_set in TAG_SPECIFIC_STOPWORDS.items():
    # .union() combina os dois conjuntos
    STOPWORD_SETS[tag] = GENERAL_STOPWORDS.union(specific_set)

STOPWORD_SETS["general"] = GENERAL_STOPWORDS