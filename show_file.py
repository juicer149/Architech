@dataclass(frozen=True)
class RawUser:
    name: str
    age: str

@dataclass(frozen=True)
class User:
    name: str
    age: int

class UserPipeline:
    name = Codex(
        SET >> strip >> validate_name,
        write=Output(dest=User)
    )

#tanken är mer att det ska funka såhär:
"""
Den funkar så att den Phase.X (e.g Phase.SET och Phase.GET osv är det som är kopplat till
routing via descriptors, WRITE använder Phase.SET men byter default parametrarna för 
write: Output(dest, hook, ev tillåter att man kan lämna ex type_fileter och default
till @ SEMANTICS/Output(type_filter=..., default=... osv) att överskriva config,
eller ange dem direkt i PhaseConfig som då defaults med möjlighet att överskriva vissa parametrar via @ Output/SEMANTICS.
"""
SET = PhaseConfig(...) # bättre namn på denna hade kanske kunant vara CodexSetup eller liknande?
WRITE = PhaseConfig(...) 

ERROR = Output(...)
WARNING = Output(...)

UserNameSanitizer = Codex( SET >> is_string << to_string >> strip >> length(min=1, max=25) >> to_lowercase @ ERROR )
UserNamePipeline = Codex( WRITE(dest=User.name) << UserNameSanitizer @ ERROR )
# alternativt hade denna kunnat skrivas som:
UserNamePipeline = Codex( WRITE(dest=User.name) << SET >> is_string << to_string >> strip >> length(min=1, max=25) >> to_lowercase @ ERROR )

UserAgeSanitizer = Codex( SET >> is_int << to_int >> in_range(0, 125) @ ERROR )
UserAgeControl = Codex( SET >> in_range(8, 65) @ WARNING )
# För denna ska ERROR vara för om WRITE inte funkar då UserAge har ERROR semantik och 
# UserAgeControl bara har WARNING semantik
# sedan har då pipeline ERROR semantik för om skrivningen inte funkar.
UserAgePipeline = Codex( WRITE(dest=User.age) << UserAgeSanitizer << UserAgeControl @ ERROR )
# skulle kunnat lagt in något som dest_type för att ge en hint om vad för typ den ska skriva till
# kan där ha inbyggda för ex class, file, db_table, json_schema osv sen, men fortfarande
# möjlighet att skriv egna posthooks osv och därmed också inte behöva ange dest_type om man bygger
# egen logik, men inom architech så är detta normen för att underlätta automatisering, snabba checks osv.

dataclass(frozen=True)
class RawUser:
    name: str = UserNamePipeline # Alternativt att man här skrev hela Codex(...) direkt,
    # hade till och med kunnat skriva som Codex( PhaseConfig(...) >> is_string << to_string >> ... @ Output(...) ) osv.
    age: str = UserAgePipeline

@dataclass(frozen=True)
class User:
    name: str
    age: int


# Ett annat verkligt exempel:

IS_INT = is_int << to_int @ ERROR
Argon2TimeCostPipeline = Codex(
    SET >> IS_INT >> in_range(1, 10) @ ERROR
    SET >> in_range(2, 8) @ WARNING
    WRITE(dest=Argon2Policy.time_cost) @ ERROR
)
Argon2TimeCostPipeline = Codex(
    SET >> is_int << to_int >> in_range(1, 10) @ ERROR
    WRITE(dest=Argon2Backend.time_cost) @ ERROR
)


class Argon2Policy:
    time_cost: int = Argon2TimeCostPipeline
    memory_cost: # ... 
    parallelism: # ...


class Argon2Backend:
    time_cost: int
    memory_cost: int
    parallelism: int

    def __call__(self, password):
        # Använd self.time_cost, self.memory_cost, self.parallelism för att hasha lösenordet
        pass

# eller om man vill slå ihop dem kan man het enkelt göra såhär:
class Argon2:
    policy: Argon2Policy
    backend: Argon2Backend

    def __post_init__(self):
        self.backend.time_cost = self.policy.time_cost
        self.backend.memory_cost = self.policy.memory_cost
        self.backend.parallelism = self.policy.parallelism

    def __call__(self, password):
        return self.backend(password)

#alternativt:


class Argon2:
    time_cost: int = Argon2TimeCostPipeline # fast här ändrar man så när man skriver
    # Codex(...) så har den ingen dest vilket gör att den skriver tillbaka till det
    # egna attributet som standard för SET om den har write=Output(enabled=True).
    memory_cost: int = Argon2MemoryCostPipeline
    parallelism: int = Argon2ParallelismPipeline

    def __call__(self, password):
        # Använd self.time_cost, self.memory_cost, self.parallelism för att hasha lösenordet
        pass

# på detta viset så behövs bara en fil, en klass, som visar hela flödet och automatiserar
# validering och sanitering av indata samt applicering av policy till backend i samma klass
# men utan att det blir kladdigt med massor av extra LOC osv.
