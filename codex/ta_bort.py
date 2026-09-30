
def to_argon_backend(output_value, context):
    # Custom hook to transform output for Argon backend
    Argon2Backend.time_cost = output_value

def print_output(output_value, context):
    print(f"Warning: {output_value}")

ERROR = Output(label="Error", is_exception=True, timing=Timing.Cluster, effect=Effect.INHERENT, default=TimeCostException(), use_default=True)
WARNING = Output(label="Warning", is_exception=True, timing=Timing.CLUSTER, effect=Effect.CUSTOM, default=TimeCostWarning(), use_default=True, hook=print_output)

TO_ARGON_BACKEND = Output(effect=Effect.CUSTOM, timing=Timing.CLUSTER, hook=to_argon_backend, default=2, use_default=True, is_exception=False, type_filter=int)

IS_INT = Codex( SET >> is_int >> to_int @ ERROR )

TIME_COST_HARD_RULES = Codex( SET >> IS_INT >> in_range(0, 10) @ ERROR) 

TIME_COST_SAFE_TEST = Codex( SET >> in_range(2, 8) @ WARNING )

class Argon2Policy:
    """ Snapshot of raw input stays in policy, but normalized output goes to backend class """
    time_cost = Codex(  TIME_COST_SAFE_TEST,
                        TIME_COST_HARD_RULES @ TO_ARGON_BACKEND,
                      )
    ...

class Argon2Backend:
    time_cost
    ...

# men även att man kan skriva såhär då utan att routa till annan klass

class Argon2:
    """ Here the value is transformed inside the same class and written to self """
    time_cost = Codex(  TIME_COST_SAFE_TEST, 
                        TIME_COST_HARD_RULES,
                        )
    ...

    def __call__(self):
        ...
