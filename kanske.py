
hade man inte kunnat göra något config objekt för dsl som ex anger hierarki nivåer?
alltså att i Codex har man ett config objekt som ger vilken level allt olika architokens etc har
Det kanske hade kunnat förenkla exempelvis CLUSTER < PHASE < CODEX 
och att dem automatiskt har sin hierarki för varandra, dvs att
för just codex då gäller att ett cluster är lägsta nivån. En Codex innehåller phases som i sin tur innehåller clusters etc.
Men att detta vet inte dsl i sig utan den vet bara om hierarkin via att Codex
har ett config objekt som anger detta som då har olika ArchiTokens placerade i 
olika nivåer för denna, skulle kunna vara så enkelt som via en Tuple, där man avgör att 
index 0 är lägsta nivån, index 1 är nästa nivå osv. Sedan är då just Cluster ArchiToken
medan phase och codex är ArchiCollections. Dvs att man skiljer på modellerna för ArchiToken och ArchiCollection? ev att man hade infört en factory i dsl som skapar dessa strukturerade pipelines via att dem tar 
in config objektet som anger hierarkinivåer, och därefter då skapar rätt pipelines med rätt ArchiTokens och ArchiCollections på rätt nivåer osv?
