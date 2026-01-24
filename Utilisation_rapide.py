import main as rdm

# Créer une poutre
poutre = rdm.Poutre2AppuisSimples(10, "Ma poutre")

# Ajouter des charges
poutre.ajouter_charge_concentree(1000, 5)

# Calculer
reactions = poutre.calculer_reactions()

# Tracer les diagrammes
diag = rdm.DiagrammesPoutre(poutre)
diag.tracer_diagrammes_complets()
