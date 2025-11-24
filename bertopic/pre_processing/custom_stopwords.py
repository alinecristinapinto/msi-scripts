BOILERPLATE_WORDS = {
    'question', 'questions', 'follow', 'similar', 'asked', 'previous', 'answer', 'thanks', 'help', 
    'example', 'using', 'way', 'need', 'tried', 'trying', 'following', 'want', 'like', 'solution'
}

GENERIC_TECH_WORDS = {
    'data', 'value', 'values'
}

TAG_SPECIFIC_STOPWORDS = {
    "julia": {"julia", "jl"},
    "r": {
        "r", "rstudio", 
        "data", "frame", "dataframe", "df", "dt", "dataset", "table", 
        "column", "columns", "row", "rows", "variable", "variables",  
        "function", "code", "package", "library", "install",         
        "output", "error", "value", "values", "object", "plot" 
    }, 
    "dart": { 
        "dart", "flutter", "widget", "widgets", "app", "context",  
        "build", "child", "children", "return", "void", "override",
        "class", "statelesswidget", "statefulwidget", "import", "package"
    }, 
    "bash": {
        "bash", "shell", "script", "scripts", "sh",                 
        "command", "run", "running", "execute", "executing", "exec", 
        "terminal", "console", "prompt", "cli",                    
        "file", "files", "txt", "text", "line", "lines",           
        "output", "input", "directory", "folder", "path"            
    },
    "python": {
        "python", "py", "python3", 
        "file", "files", "txt", "csv", "excel", "output", "input", "print", 
        "read", "write", "open", "close", "load", "save", "path", "folder", "directory",
        "code", "script", "program", "line", "lines", "syntax", "pip", "install",
        "run", "running", "process", "command", "cmd", "terminal",
        "error", "issue", "problem", "fail", "failed", "fix", "solve", "solution",
        "work", "working", "help", "create", "make", "build", "get", "got", "take", 
        "try", "tried", "trying", "use", "using", "used", "need", "want", "know", 
        "find", "search", "change", "convert", "add", "remove", "delete", "update"
    },
    "javascript": {"javascript", "js", "node", "nodejs"},
    "java": {"java"},
    "c#": {"csharp", "c#", ".net"},
}

