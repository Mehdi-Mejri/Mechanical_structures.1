"""
EXEMPLES D'UTILISATION - Bibliothèque RDM Poutres
================================================

Ce fichier montre comment utiliser toutes les fonctionnalités
de la bibliothèque pour analyser différents types de poutres.
"""

import main as rdm
import matplotlib.pyplot as plt
import numpy as np

print("="*70)
print("EXEMPLES D'UTILISATION - BIBLIOTHÈQUE RDM POUTRES")
print("="*70)

# ============================================================================
# EXEMPLE 1 : POUTRE SUR 2 APPUIS SIMPLES - CAS CLASSIQUE
# ============================================================================


def exemple_1_poutre_2_appuis():
    """Poutre sur 2 appuis avec charge au centre."""

    print("\n" + "="*70)
    print("EXEMPLE 1 : POUTRE SUR 2 APPUIS - CHARGE AU CENTRE")
    print("="*70)

    # 1. Création de la poutre
    poutre = rdm.Poutre2AppuisSimples(
        L=6.0,
        nom="Poutre simplement appuyée - Charge centrale"
    )

    # 2. Ajout des charges
    poutre.ajouter_charge_concentree(
        valeur=1000,      # 1000 N vers le bas
        position=3.0,     # Au centre (3m)
        nom="Charge centrale"
    )

    # 3. Affichage des informations
    poutre.afficher_info()

    # 4. Calcul des réactions
    print("\n📊 CALCUL DES RÉACTIONS :")
    reactions = poutre.calculer_reactions()

    # 5. Calcul des efforts à des points spécifiques
    print("\n📈 EFFORTS AUX POINTS CLÉS :")
    points = [0, 1.5, 3.0, 4.5, 6.0]
    for x in points:
        V = poutre.effort_tranchant(x)
        M = poutre.moment_flechissant(x)
        print(f"  x = {x:4.1f} m : V = {V:7.1f} N, M = {M:7.1f} N.m")

    # 6. Création des diagrammes
    print("\n🎨 CRÉATION DES DIAGRAMMES...")
    diag = rdm.DiagrammesPoutre(poutre)

    # Diagrammes complets
    fig, axes, data = diag.tracer_diagrammes_complets(
        n_points=200,
        figsize=(14, 10)
    )

    # 7. Affichage du tableau récapitulatif
    diag.afficher_tableau_resultats()

    # 8. Export des diagrammes
    diag.exporter_diagrammes("exemple_1_diagrammes.png", dpi=150)

    plt.suptitle("EXEMPLE 1 : Poutre sur 2 appuis - Charge au centre",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return poutre, diag

# ============================================================================
# EXEMPLE 2 : POUTRE ENCASTRÉE - CONSOLE AVEC CHARGE RÉPARTIE
# ============================================================================


def exemple_2_poutre_encastree():
    """Poutre encastrée avec charge répartie uniforme."""

    print("\n" + "="*70)
    print("EXEMPLE 2 : POUTRE ENCASTRÉE - CHARGE RÉPARTIE")
    print("="*70)

    # 1. Création de la poutre encastrée à gauche
    poutre = rdm.PoutreEncastree(
        L=4.0,
        nom="Console avec charge répartie",
        position_encastrement=0  # Encastrement à gauche
    )

    # 2. Ajout d'une charge répartie sur toute la longueur
    poutre.ajouter_charge_repartie(
        valeur=300,      # 300 N/m vers le bas
        debut=0,
        fin=4.0,
        nom="Charge uniforme"
    )

    # 3. Ajout d'une charge ponctuelle au bout
    poutre.ajouter_charge_concentree(
        valeur=500,      # 500 N vers le bas
        position=4.0,    # À l'extrémité libre
        nom="Charge au bout"
    )

    poutre.afficher_info()

    # 4. Calcul des réactions
    print("\n📊 CALCUL DES RÉACTIONS À L'ENCASTREMENT :")
    reactions = poutre.calculer_reactions()

    # 5. Points de contrôle
    print("\n📈 POINTS DE CONTRÔLE :")
    for x in [0, 1.0, 2.0, 3.0, 4.0]:
        V = poutre.effort_tranchant(x)
        M = poutre.moment_flechissant(x)
        print(f"  x = {x:4.1f} m : V = {V:7.1f} N, M = {M:7.1f} N.m")

    # 6. Recherche du moment maximal
    x_max, M_max, typ = poutre.trouver_maximum_moment()
    print(f"\n💡 MOMENT MAXIMAL : {M_max:.1f} N.m à x = {x_max:.3f} m")

    # 7. Diagrammes
    diag = rdm.DiagrammesPoutre(poutre)
    fig, axes, data = diag.tracer_diagrammes_complets(figsize=(14, 10))

    diag.afficher_tableau_resultats()

    plt.suptitle("EXEMPLE 2 : Poutre encastrée - Charge répartie + concentrée",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return poutre, diag

# ============================================================================
# EXEMPLE 3 : POUTRE AVEC APPUI SIMPLE + ROULEAU - PORTE-À-FAUX
# ============================================================================


def exemple_3_porte_a_faux():
    """Poutre avec porte-à-faux des deux côtés."""

    print("\n" + "="*70)
    print("EXEMPLE 3 : POUTRE AVEC PORTE-À-FAUX")
    print("="*70)

    # 1. Création de la poutre
    poutre = rdm.PoutreAppuiSimpleRouleau(
        L=12.0,
        nom="Poutre avec porte-à-faux"
    )

    # 2. Configuration des appuis (pas aux extrémités)
    poutre.configurer_appuis(
        pos_simple=2.0,    # Appui simple à x=2m
        pos_rouleau=10.0   # Appui rouleau à x=10m
    )

    # 3. Ajout de charges variées
    # Charge sur porte-à-faux gauche
    poutre.ajouter_charge_concentree(
        valeur=800,
        position=1.0,
        nom="Charge gauche"
    )

    # Charge entre appuis
    poutre.ajouter_charge_repartie(
        valeur=150,
        debut=3.0,
        fin=7.0,
        nom="Charge répartie centre"
    )

    # Charge concentrée entre appuis
    poutre.ajouter_charge_concentree(
        valeur=1200,
        position=5.0,
        nom="Charge centre"
    )

    # Moment concentré
    poutre.ajouter_moment_concentre(
        valeur=600,        # 600 N.m anti-horaire
        position=8.0,
        nom="Moment"
    )

    # Charge sur porte-à-faux droit
    poutre.ajouter_charge_concentree(
        valeur=600,
        position=11.0,
        nom="Charge droite"
    )

    poutre.afficher_info()

    # 4. Calcul des réactions
    reactions = poutre.calculer_reactions()

    # 5. Affichage des positions des appuis
    positions = poutre.positions_appuis()
    print(f"\n📍 POSITIONS DES APPUIS :")
    print(f"  Simple : x = {positions['simple']:.2f} m")
    print(f"  Rouleau : x = {positions['rouleau']:.2f} m")
    print(
        f"  Portée entre appuis : {positions['rouleau'] - positions['simple']:.2f} m")

    # 6. Points stratégiques
    print("\n📈 POINTS STRATÉGIQUES :")
    points_strategiques = [0, 1.0, 2.0, 5.0, 8.0, 10.0, 11.0, 12.0]
    for x in points_strategiques:
        V = poutre.effort_tranchant(x)
        M = poutre.moment_flechissant(x)
        print(f"  x = {x:4.1f} m : V = {V:7.1f} N, M = {M:7.1f} N.m")

    # 7. Diagrammes
    diag = rdm.DiagrammesPoutre(poutre)
    fig, axes, data = diag.tracer_diagrammes_complets(figsize=(14, 10))

    diag.afficher_tableau_resultats()

    plt.suptitle("EXEMPLE 3 : Poutre avec porte-à-faux - Charges multiples",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return poutre, diag

# ============================================================================
# EXEMPLE 4 : CAS COMPLET AVEC TOUS TYPES DE CHARGES
# ============================================================================


def exemple_4_cas_complet():
    """Cas complet avec tous les types de charges."""

    print("\n" + "="*70)
    print("EXEMPLE 4 : CAS COMPLET AVEC TOUS TYPES DE CHARGES")
    print("="*70)

    poutre = rdm.Poutre2AppuisSimples(
        L=8.0,
        nom="Cas complet - Tous types de charges"
    )

    # 1. Charge concentrée positive (vers le bas)
    poutre.ajouter_charge_concentree(1500, 1.0, "P1 ↓")

    # 2. Charge concentrée négative (vers le haut)
    poutre.ajouter_charge_concentree(-800, 5.0, "P2 ↑")

    # 3. Charge répartie positive
    poutre.ajouter_charge_repartie(400, 2.0, 4.0, "q1 ↓")

    # 4. Charge répartie négative
    poutre.ajouter_charge_repartie(-200, 6.0, 7.0, "q2 ↑")

    # 5. Moment positif (anti-horaire)
    poutre.ajouter_moment_concentre(1200, 3.0, "M1 ↶")

    # 6. Moment négatif (horaire)
    poutre.ajouter_moment_concentre(-600, 6.5, "M2 ↷")

    poutre.afficher_info()

    # Calcul
    reactions = poutre.calculer_reactions()

    # Diagrammes simples (seulement V et M)
    diag = rdm.DiagrammesPoutre(poutre)
    fig, axes, data = diag.tracer_diagramme_simple(figsize=(12, 8))

    # Affichage des résultats aux points de charge
    print("\n📊 RÉSULTATS AUX POINTS DE CHARGE :")
    charges_positions = [1.0, 3.0, 5.0, 6.5]
    for x in charges_positions:
        V = poutre.effort_tranchant(x)
        M = poutre.moment_flechissant(x)
        print(f"  x = {x:4.1f} m : V = {V:7.1f} N, M = {M:7.1f} N.m")

    plt.suptitle("EXEMPLE 4 : Cas complet avec tous types de charges",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return poutre, diag

# ============================================================================
# EXEMPLE 5 : COMPARAISON DE DIFFÉRENTS CAS
# ============================================================================


def exemple_5_comparaison():
    """Comparaison de différentes configurations."""

    print("\n" + "="*70)
    print("EXEMPLE 5 : COMPARAISON DE CONFIGURATIONS")
    print("="*70)

    # Création de plusieurs poutres identiques mais de types différents
    L = 5.0
    F = 1000
    x_charge = 2.0

    # Cas A : Poutre sur 2 appuis simples
    poutre_A = rdm.Poutre2AppuisSimples(L, "Cas A: 2 appuis simples")
    poutre_A.ajouter_charge_concentree(F, x_charge)

    # Cas B : Poutre encastrée à gauche
    poutre_B = rdm.PoutreEncastree(L, "Cas B: Encastrée à gauche")
    poutre_B.ajouter_charge_concentree(F, x_charge)

    # Cas C : Poutre avec appui simple + rouleau
    poutre_C = rdm.PoutreAppuiSimpleRouleau(L, "Cas C: Simple + rouleau")
    poutre_C.ajouter_charge_concentree(F, x_charge)

    # Calcul pour toutes
    poutres = [poutre_A, poutre_B, poutre_C]

    fig, axes = plt.subplots(3, 3, figsize=(15, 12))

    for i, poutre in enumerate(poutres):
        # Calcul des réactions
        poutre.calculer_reactions()

        # Diagrammes
        diag = rdm.DiagrammesPoutre(poutre)
        data = diag.calculer_donnees_diagrammes(100)

        # Poutre et charges
        ax1 = axes[i, 0]
        diag._tracer_poutre_et_charges(ax1)
        ax1.set_title(poutre.nom, fontsize=11)

        # Diagramme V(x)
        ax2 = axes[i, 1]
        diag._tracer_diagramme_effort_tranchant(ax2, data)

        # Diagramme M(x)
        ax3 = axes[i, 2]
        diag._tracer_diagramme_moment_flechissant(ax3, data)

        # Affichage des réactions
        print(f"\n📋 {poutre.nom} :")
        if hasattr(poutre.reactions, 'get'):
            if 'R_A' in poutre.reactions:
                print(f"  R_A = {poutre.reactions['R_A']:.1f} N, "
                      f"R_B = {poutre.reactions['R_B']:.1f} N")
            elif 'R' in poutre.reactions:
                print(f"  R = {poutre.reactions['R']:.1f} N, "
                      f"M = {poutre.reactions.get('M_enc', 0):.1f} N.m")
            elif 'R_simple' in poutre.reactions:
                print(f"  R_simple = {poutre.reactions['R_simple']:.1f} N, "
                      f"R_rouleau = {poutre.reactions['R_rouleau']:.1f} N")

    plt.suptitle("COMPARAISON : Même charge, différents appuis",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return poutres

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================


def main():
    """Fonction principale qui exécute tous les exemples."""

    print("\n" + "="*70)
    print("DÉMARRAGE DES EXEMPLES")
    print("="*70)

    # Liste des exemples disponibles
    exemples = {
        "1": ("Poutre sur 2 appuis - Charge au centre", exemple_1_poutre_2_appuis),
        "2": ("Poutre encastrée - Charge répartie", exemple_2_poutre_encastree),
        "3": ("Poutre avec porte-à-faux", exemple_3_porte_a_faux),
        "4": ("Cas complet - Tous types de charges", exemple_4_cas_complet),
        "5": ("Comparaison de configurations", exemple_5_comparaison),
    }

    while True:
        print("\n📚 MENU DES EXEMPLES :")
        for key, (description, _) in exemples.items():
            print(f"  {key}. {description}")
        print("  T. TOUS les exemples")
        print("  Q. Quitter")

        choix = input("\n👉 Votre choix : ").strip().upper()

        if choix == 'Q':
            print("\n👋 Au revoir !")
            break
        elif choix == 'T':
            print("\n" + "="*70)
            print("EXÉCUTION DE TOUS LES EXEMPLES")
            print("="*70)
            for key, (description, fonction) in exemples.items():
                print(f"\n▶️  Exécution de l'exemple {key} : {description}")
                print("-"*50)
                try:
                    fonction()
                except Exception as e:
                    print(f"❌ Erreur dans l'exemple {key}: {e}")
            print("\n✅ Tous les exemples ont été exécutés !")
        elif choix in exemples:
            description, fonction = exemples[choix]
            print(f"\n▶️  Exécution de l'exemple {choix} : {description}")
            print("="*50)
            try:
                fonction()
            except Exception as e:
                print(f"❌ Erreur : {e}")
        else:
            print("❌ Choix invalide. Veuillez réessayer.")

    print("\n" + "="*70)
    print("FIN DES EXEMPLES")
    print("="*70)

# ============================================================================
# EXÉCUTION
# ============================================================================


if __name__ == "__main__":
    # Pour exécuter directement un exemple spécifique :
    # exemple_1_poutre_2_appuis()
    # exemple_2_poutre_encastree()
    # exemple_3_porte_a_faux()
    # exemple_4_cas_complet()
    # exemple_5_comparaison()

    # Ou exécuter le menu interactif :
    main()
