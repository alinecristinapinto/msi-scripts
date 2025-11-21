# --------------------------------------------------------------------------
# STOPWORDS GERAIS
# Palavras que sao "ruido" em perguntas do Stack Overflow
# --------------------------------------------------------------------------

BOILERPLATE_WORDS = {
    'question', 'follow', 'similar', 'asked', 'previous', 'answer', 'thanks', 'help', 
    'example', 'using', 'way', 'need', 'tried', 'trying', 'following', 'want', 'like'
}

GENERIC_TECH_WORDS = {
    'data', 'value', 'values'
}

# --------------------------------------------------------------------------
# STOPWORDS ESPECIFICAS POR TAG
# O nome da proópria tag e suas variantes mais comuns
# --------------------------------------------------------------------------

TAG_SPECIFIC_STOPWORDS = {
    "julia": {"julia", "jl"},
    "r": {"r"}, 
    "dart": {"dart", "flutter"}, 
    "bash": {"bash", "shell", "script", "scripts"}, 
    "python": {"python", "py"},
    "javascript": {"javascript", "js", "node", "nodejs"},
    "java": {"java"},
    "c#": {"csharp", "c#", ".net"},
}

