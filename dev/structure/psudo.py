"""
Först behöver den hämta och ladda en fil med path
Steg 1: 
    v0.1
        - API tar filens path och läser innehållet.

    v0.x
        - I förlängningen kan det vara en URL eller filuppladdning.
        - Filen kan vara i olika format (txt, csv, json etc.)
        - Beroende på formatet, använd lämplig parser för att läsa innehållet.
        - Då behöver jag extrahera suffixen från filnamnet för att välja formaterare
            alternativt använda magic numbers för att identifiera filtypen. alternativt ta argument

@dataclass(frozen=True)
class File:
    path: str
    content: str


stage 2:
    v0.1
        - Läs rad för rad och sök efter mönster, detta mönster kan tas som argument.

@dataclass
class PatternBit:
    pattern: str  exempelvis:
        - '"""{name}' 
        - "def {name}:{annotation}" 
        - "class {name}:{annotation}"
        - "@{name}{annotation}"
        - "#{comment}"
        - egentligen är det "{prefix}{name}{suffix}" där prefix och suffix kan vara valfria
        - i min modell kommer dessa vara {category}{name}[{annotation} 
            sedan är dessa tre olika tre olika värden som kan mappas till:

Här är funktioner som tar denna datan och kategoriserar den mot nästa data objekt via att retunera detta objekt från pattern funktionen. Detta är den som kategoriserar datan att sedan tolkas vidare mot Documentation, CodeBlock, etc

@dataclass
class ExtractedData:
    category: Prefix # e.g '"""', 'def ', 'class', '@decorator'
        - Alla dessa skapar en ny kontext som i sig kan ha andra kontexter inuti sig.
    name: str  # e.g 'MyClass', 'my_function', 'my_variable, 'dataclass',
    annotation: str  # e.g ': Type', '(arg1: Type1, arg2: Type2) -> ReturnType', '= DefaultValue'
    comment: str  # e.g 'This is a comment'


här skapas sedan då extracted data 





undra om architech skulle kunna fungera på något vis där man använder privata attribut, dvs tar in raw data, lagrar det i de vanliga attributen kör min codex pipeline och sedan kan retunera ett annat dataobject som classen själv definierar.
"""


