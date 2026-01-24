"""
RDM Poutres - Bibliothèque pour l'analyse des poutres isostatiques
"""

import numpy as np
import matplotlib.pyplot as plt


class PoutreBase:  # ✅ Convention: PascalCase pour les noms de classe
    """Classe de base pour les poutres isostatiques."""

    def __init__(self, L, nom="Poutre sans nom"):
        """
        Initialise une poutre de longueur L.

        Parameters
        ----------
        L : float
            Longueur de la poutre (m)
        nom : str
            Nom identificatif de la poutre
        """
        self.L = L  # Longueur
        self.nom = nom
        self.appuis = []  # Liste des appuis
        self.charges = []  # Liste des charges
        self.reactions = None  # ✅ Initialiser à None
        self._sections_calculées = False  # ✅ Flag pour optimisation

    # =================== MÉTHODES DE CHARGES ===================

    def ajouter_charge_concentree(self, valeur, position, nom=""):
        """
        Ajoute une charge concentrée.

        Parameters
        ----------
        valeur : float
            Valeur de la charge (N). Positive vers le bas
        position : float
            Position de la charge (m). Doit être dans [0, L]
        nom : str, optional
            Identification de la charge
        """
        # ✅ Validation de la position
        if not 0 <= position <= self.L:
            raise ValueError(
                f"Position {position}m hors de la poutre [0, {self.L}]")

        self.charges.append({
            'type': 'concentree',
            'valeur': valeur,
            'position': position,
            'nom': nom or f"P{valeur}N@{position}m"
        })
        self._sections_calculées = False  # ✅ Réinitialise les calculs

    def ajouter_charge_repartie(self, valeur, debut, fin, nom=""):
        """
        Ajoute une charge uniformément répartie.

        Parameters
        ----------
        valeur : float
            Intensité (N/m). Positive vers le bas
        debut : float
            Début de la charge (m)
        fin : float
            Fin de la charge (m)
        nom : str, optional
            Identification de la charge
        """
        # ✅ Validation
        if not 0 <= debut <= fin <= self.L:
            raise ValueError(
                f"Intervalle [{debut}, {fin}] invalide pour poutre [0, {self.L}]")

        self.charges.append({
            'type': 'repartie',
            'valeur': valeur,
            'debut': debut,
            'fin': fin,
            'nom': nom or f"q{valeur}N/m_{debut}-{fin}m"
        })
        self._sections_calculées = False

    def ajouter_moment_concentre(self, valeur, position, nom=""):  # ✅ Nom plus clair
        """
        Ajoute un moment concentré (couple).

        Parameters
        ----------
        valeur : float
            Intensité (N.m). Positif si anti-horaire
        position : float
            Position (m). Doit être dans [0, L]
        nom : str, optional
            Identification du moment
        """
        if not 0 <= position <= self.L:
            raise ValueError(
                f"Position {position}m hors de la poutre [0, {self.L}]")

        self.charges.append({
            'type': 'moment',
            'valeur': valeur,  # ✅ Même clé 'valeur' pour cohérence
            'position': position,
            'nom': nom or f"M{valeur}N.m@{position}m"
        })
        self._sections_calculées = False

    # =================== MÉTHODES D'APPUIS ===================

    def ajouter_appui_simple(self, position):
        """
        Ajoute un appui simple (articulation).

        Parameters
        ----------
        position : float
            Position de l'appui (m)
        """
        self._ajouter_appui('simple', position)

    def ajouter_encastrement(self, position):
        """
        Ajoute un encastrement.

        Parameters
        ----------
        position : float
            Position de l'encastrement (m)
        """
        self._ajouter_appui('encastrement', position)

    def _ajouter_appui(self, type_appui, position):
        """Méthode interne pour ajouter un appui."""
        if not 0 <= position <= self.L:
            raise ValueError(f"Position {position}m hors de la poutre")

        self.appuis.append({
            'type': type_appui,
            'position': position
        })
        self._sections_calculées = False

    # =================== MÉTHODES DE VALIDATION ===================

    def _valider_structure(self):
        """Vérifie si la structure est statiquement déterminée."""
        n_appuis = len(self.appuis)
        n_charges = len(self.charges)

        if n_appuis < 2:
            raise ValueError(
                f"Nombre d'appuis insuffisant: {n_appuis} (minimum 2)")

        # Compte les degrés de liberté bloqués
        degres_bloques = 0
        for appui in self.appuis:
            if appui['type'] == 'simple':
                degres_bloques += 1  # Bloque translation verticale
            elif appui['type'] == 'encastrement':
                degres_bloques += 2  # Bloque translation + rotation

        if degres_bloques < 2:
            raise ValueError(
                f"Structure instable: {degres_bloques} degrés bloqués")

        return True

    # =================== MÉTHODES UTILITAIRES ===================

    def afficher_info(self):
        """Affiche les informations de la poutre."""
        print(f"\n{'='*60}")
        print(f"INFORMATIONS - {self.nom}")
        print(f"{'='*60}")
        print(f"Longueur: {self.L} m")
        print(f"Appuis: {len(self.appuis)}")
        for i, appui in enumerate(self.appuis, 1):
            print(f"  {i}. {appui['type']} à x={appui['position']}m")
        print(f"Charges: {len(self.charges)}")
        for i, charge in enumerate(self.charges, 1):
            if charge['type'] == 'concentree':
                print(
                    f"  {i}. {charge['nom']}: {charge['valeur']}N à x={charge['position']}m")
            elif charge['type'] == 'repartie':
                print(
                    f"  {i}. {charge['nom']}: {charge['valeur']}N/m de x={charge['debut']} à {charge['fin']}m")
            elif charge['type'] == 'moment':
                print(
                    f"  {i}. {charge['nom']}: {charge['valeur']}N.m à x={charge['position']}m")
        print(f"{'='*60}")

    def _reinitialiser_calculs(self):
        """Réinitialise les résultats des calculs."""
        self.reactions = None
        self._sections_calculées = False


class Poutre2AppuisSimples(PoutreBase):
    """Poutre sur 2 appuis simples (isostatique)."""

    def __init__(self, L, nom="Poutre sur 2 appuis"):
        super().__init__(L, nom)  # ✅ Appel au parent
        self._validation_specifique()

    def _validation_specifique(self):
        """Validation spécifique aux 2 appuis simples."""
        if len(self.appuis) != 2:
            # Auto-ajout des appuis aux extrémités
            self.ajouter_appui_simple(0)
            self.ajouter_appui_simple(self.L)
            print(f"⚠️  Appuis auto-ajoutés: simple à x=0 et x={self.L}m")

    def calculer_reactions(self):
        """
        Calcule les réactions aux appuis pour 2 appuis simples.

        Returns
        -------
        dict
            {'R_A': float, 'R_B': float, 'position_A': float, 'position_B': float}
        """
        # ✅ Vérification du type d'appui
        for appui in self.appuis:
            if appui['type'] != 'simple':
                raise ValueError(
                    "Cette classe ne supporte que les appuis simples")

        if len(self.appuis) != 2:
            raise ValueError("Exactement 2 appuis requis pour cette poutre")

        # Tri des appuis
        appuis_tries = sorted(self.appuis, key=lambda x: x['position'])
        pos_A, pos_B = appuis_tries[0]['position'], appuis_tries[1]['position']
        L_eff = pos_B - pos_A  # ✅ Distance entre appuis

        # Initialisation
        somme_Fy = 0.0      # Somme des forces verticales
        somme_M_A = 0.0     # Somme des moments par rapport à A

        for charge in self.charges:
            if charge['type'] == 'concentree':
                F = charge['valeur']
                pos = charge['position']
                bras = pos - pos_A
                somme_Fy += F
                somme_M_A += F * bras

            elif charge['type'] == 'repartie':
                q = charge['valeur']
                x1, x2 = charge['debut'], charge['fin']
                F_tot = q * (x2 - x1)          # Force totale
                x_centre = (x1 + x2) / 2       # Centre de gravité
                bras = x_centre - pos_A
                somme_Fy += F_tot
                somme_M_A += F_tot * bras

            elif charge['type'] == 'moment':
                M = charge['valeur']
                # ✅ UN MOMENT N'AFFECTE PAS LA SOMME DES FORCES VERTICALES
                # Mais affecte la somme des moments
                somme_M_A += M

        # ✅ Équations d'équilibre:
        # ΣM_A = 0 → R_B * L_eff + somme_M_A = 0
        # ΣFy = 0 → R_A + R_B + somme_Fy = 0

        R_B = -somme_M_A / L_eff
        R_A = -somme_Fy - R_B

        self.reactions = {
            'R_A': R_A,
            'R_B': R_B,
            'position_A': pos_A,
            'position_B': pos_B,
            'ΣFy': somme_Fy,
            'ΣM_A': somme_M_A
        }

        # ✅ Vérification numérique
        tolerance = 1e-10
        verif_Fy = R_A + R_B + somme_Fy
        verif_M = R_B * L_eff + somme_M_A

        if abs(verif_Fy) > tolerance or abs(verif_M) > tolerance:
            print(f"⚠️  Vérification: ΣFy={verif_Fy:.2e}, ΣM={verif_M:.2e}")

        print(f"✅ Réactions calculées: R_A={R_A:.2f}N, R_B={R_B:.2f}N")
        return self.reactions

    def effort_tranchant(self, x):
        """
        Calcule l'effort tranchant V(x) à la position x.

        Parameters
        ----------
        x : float
            Position le long de la poutre (m)

        Returns
        -------
        float
            Effort tranchant (N). Convention: Positif si tend la partie gauche vers le haut
        """
        if self.reactions is None:
            self.calculer_reactions()

        pos_A = self.reactions['position_A']
        pos_B = self.reactions['position_B']

        # ✅ Convention RDM: V(x) positif si tend la partie gauche vers le haut
        # Donc: V(x) = -R_A - ΣF à gauche de x
        V = -self.reactions['R_A']

        for charge in self.charges:
            if charge['type'] == 'concentree':
                if charge['position'] <= x:
                    V -= charge['valeur']  # ✅ Moins car vers le bas

            elif charge['type'] == 'repartie':
                x1, x2 = charge['debut'], charge['fin']
                q = charge['valeur']

                if x2 <= x:
                    # Charge entièrement à gauche
                    V -= q * (x2 - x1)
                elif x1 < x:
                    # Charge partiellement à gauche
                    V -= q * (x - x1)

        return V

    def moment_flechissant(self, x):
        """
        Calcule le moment fléchissant M(x) à la position x.

        Parameters
        ----------
        x : float
            Position le long de la poutre (m)

        Returns
        -------
        float
            Moment fléchissant (N.m). Convention: Positif si fibres inférieures tendues
        """
        if self.reactions is None:
            self.calculer_reactions()

        pos_A = self.reactions['position_A']

        # ✅ Convention RDM: M(x) positif si fibres inférieures tendues
        M = -self.reactions['R_A'] * (x - pos_A)  # ✅ Moins pour convention

        for charge in self.charges:
            if charge['type'] == 'concentree':
                if charge['position'] <= x:
                    bras = x - charge['position']
                    M -= charge['valeur'] * bras  # ✅ Moins

            elif charge['type'] == 'repartie':
                x1, x2 = charge['debut'], charge['fin']
                q = charge['valeur']

                if x2 <= x:
                    # Charge entièrement à gauche
                    centre = (x1 + x2) / 2
                    bras = x - centre
                    M -= q * (x2 - x1) * bras
                elif x1 < x:
                    # Charge partiellement à gauche
                    x_partiel = min(x, x2)
                    centre = (x1 + x_partiel) / 2
                    bras = x - centre
                    M -= q * (x_partiel - x1) * bras

            elif charge['type'] == 'moment':
                if charge['position'] <= x:
                    M -= charge['valeur']  # ✅ Moins pour convention

        return M

    def effort_normal(self, x):
        """
        Calcule l'effort normal N(x) à la position x.

        Parameters
        ----------
        x : float
            Position le long de la poutre (m)

        Returns
        -------
        float
            Effort normal (N). Positif en traction
        """
        # Pour une poutre droite sans charge axiale
        return 0.0

    def calculer_toutes_sections(self, n_points=100):
        """
        Calcule les efforts sur toute la longueur.

        Parameters
        ----------
        n_points : int
            Nombre de points de calcul

        Returns
        -------
        dict
            {'x': array, 'V': array, 'M': array, 'N': array}
        """
        x = np.linspace(0, self.L, n_points)
        V = np.array([self.effort_tranchant(xi) for xi in x])
        M = np.array([self.moment_flechissant(xi) for xi in x])
        N = np.array([self.effort_normal(xi) for xi in x])

        return {
            'x': x,
            'V': V,
            'M': M,
            'N': N,
            'L': self.L,
            'nom': self.nom
        }


class PoutreEncastree(PoutreBase):
    """Poutre encastrée à une extrémité (console)."""

    def __init__(self, L, nom="Poutre encastrée", position_encastrement=0):
        """
        Initialise une poutre encastrée.

        Parameters
        ----------
        L : float
            Longueur de la poutre (m)
        nom : str
            Nom de la poutre
        position_encastrement : float, optional
            Position de l'encastrement (0 ou L), par défaut 0
        """
        super().__init__(L, nom)

        if position_encastrement not in [0, self.L]:
            raise ValueError("L'encastrement doit être à x=0 ou x=L")

        self.position_encastrement = position_encastrement
        self.ajouter_encastrement(position_encastrement)

    def calculer_reactions(self):
        """
        Calcule les réactions à l'encastrement.

        Returns
        -------
        dict
            {'R': float, 'M': float, 'position': float}
            R: réaction verticale (N), positive vers le haut
            M: moment d'encastrement (N.m), positif anti-horaire
        """
        # Vérifie qu'il y a exactement un encastrement
        if len(self.appuis) != 1 or self.appuis[0]['type'] != 'encastrement':
            raise ValueError(
                "Cette classe nécessite exactement un encastrement")

        encastrement = self.appuis[0]
        pos_enc = encastrement['position']

        # Initialisation
        somme_Fy = 0.0      # Somme des forces verticales
        somme_M_enc = 0.0   # Somme des moments par rapport à l'encastrement

        for charge in self.charges:
            if charge['type'] == 'concentree':
                F = charge['valeur']
                pos = charge['position']
                bras = pos - pos_enc  # Distance par rapport à l'encastrement
                somme_Fy += F
                somme_M_enc += F * bras

            elif charge['type'] == 'repartie':
                q = charge['valeur']
                x1, x2 = charge['debut'], charge['fin']
                F_tot = q * (x2 - x1)          # Force totale
                x_centre = (x1 + x2) / 2       # Centre de gravité
                bras = x_centre - pos_enc      # Distance du centre à l'encastrement
                somme_Fy += F_tot
                somme_M_enc += F_tot * bras

            elif charge['type'] == 'moment':
                M = charge['valeur']
                pos = charge['position']
                # Le moment s'ajoute directement à la somme des moments
                somme_M_enc += M

        # Pour l'équilibre:
        # ΣFy = 0 → R + ΣF = 0 → R = -ΣF
        # ΣM_enc = 0 → M_enc + ΣM = 0 → M_enc = -ΣM

        R = -somme_Fy       # Réaction verticale à l'encastrement
        M_enc = -somme_M_enc  # Moment d'encastrement

        self.reactions = {
            'R': R,
            'M_enc': M_enc,
            'position': pos_enc,
            'ΣFy': somme_Fy,
            'ΣM_enc': somme_M_enc
        }

        # Vérification numérique
        tolerance = 1e-10
        verif_Fy = R + somme_Fy
        verif_M = M_enc + somme_M_enc

        if abs(verif_Fy) > tolerance or abs(verif_M) > tolerance:
            print(f"⚠️  Vérification: ΣFy={verif_Fy:.2e}, ΣM={verif_M:.2e}")

        print(f"✅ Réactions à l'encastrement (x={pos_enc}m):")
        print(f"   R = {R:.2f} N {'↑' if R > 0 else '↓'}")
        print(f"   M = {M_enc:.2f} N.m {'↶' if M_enc > 0 else '↷'}")

        return self.reactions

    def effort_tranchant(self, x):
        """
        Calcule l'effort tranchant V(x).

        Convention: V(x) positif si tend la partie gauche vers le haut.
        Pour une poutre encastrée à gauche:
        - À gauche d'une section: partie fixe (encastrement) à gauche
        - V(x) = -R - ΣF entre encastrement et x
        """
        if self.reactions is None:
            self.calculer_reactions()

        pos_enc = self.reactions['position']
        R = self.reactions['R']

        # Position relative par rapport à l'encastrement
        if self.position_encastrement == 0:  # Encastrement à gauche
            # Convention: V(x) = -R - ΣF entre 0 et x
            V = -R

            for charge in self.charges:
                if charge['type'] == 'concentree':
                    if pos_enc <= charge['position'] <= x:
                        V -= charge['valeur']

                elif charge['type'] == 'repartie':
                    x1, x2 = charge['debut'], charge['fin']
                    q = charge['valeur']

                    # Partie de la charge entre encastrement et x
                    debut_eff = max(pos_enc, x1)
                    fin_eff = min(x, x2)

                    if debut_eff < fin_eff:
                        V -= q * (fin_eff - debut_eff)

        else:  # Encastrement à droite (x = L)
            # Pour encastrement à droite, on inverse la convention
            # Partie gauche est la partie libre
            V = 0  # À gauche de l'encastrement, pas de réaction

            for charge in self.charges:
                if charge['type'] == 'concentree':
                    if x <= charge['position'] <= pos_enc:
                        V += charge['valeur']  # Inverse le signe

                elif charge['type'] == 'repartie':
                    x1, x2 = charge['debut'], charge['fin']
                    q = charge['valeur']

                    # Partie de la charge entre x et encastrement
                    debut_eff = max(x, x1)
                    fin_eff = min(pos_enc, x2)

                    if debut_eff < fin_eff:
                        V += q * (fin_eff - debut_eff)

        return V

    def moment_flechissant(self, x):
        """
        Calcule le moment fléchissant M(x).

        Convention: M(x) positif si fibres inférieures tendues.
        """
        if self.reactions is None:
            self.calculer_reactions()

        pos_enc = self.reactions['position']
        R = self.reactions['R']
        M_enc = self.reactions['M_enc']

        if self.position_encastrement == 0:  # Encastrement à gauche
            # M(x) = -M_enc - R*(x - pos_enc) - Σ(M des charges entre 0 et x)
            M = -M_enc - R * (x - pos_enc)

            for charge in self.charges:
                if charge['type'] == 'concentree':
                    if pos_enc <= charge['position'] <= x:
                        bras = x - charge['position']
                        M -= charge['valeur'] * bras

                elif charge['type'] == 'repartie':
                    x1, x2 = charge['debut'], charge['fin']
                    q = charge['valeur']

                    # Partie de la charge entre encastrement et x
                    debut_eff = max(pos_enc, x1)
                    fin_eff = min(x, x2)

                    if debut_eff < fin_eff:
                        centre = (debut_eff + fin_eff) / 2
                        bras = x - centre
                        intensite = q * (fin_eff - debut_eff)
                        M -= intensite * bras

                elif charge['type'] == 'moment':
                    if pos_enc <= charge['position'] <= x:
                        M -= charge['valeur']

        else:  # Encastrement à droite
            # Pour encastrement à droite (x = L):
            # M(x) = Σ(M des charges entre x et L)
            M = 0

            for charge in self.charges:
                if charge['type'] == 'concentree':
                    if x <= charge['position'] <= pos_enc:
                        bras = charge['position'] - x
                        M += charge['valeur'] * bras

                elif charge['type'] == 'repartie':
                    x1, x2 = charge['debut'], charge['fin']
                    q = charge['valeur']

                    # Partie de la charge entre x et encastrement
                    debut_eff = max(x, x1)
                    fin_eff = min(pos_enc, x2)

                    if debut_eff < fin_eff:
                        centre = (debut_eff + fin_eff) / 2
                        bras = centre - x
                        intensite = q * (fin_eff - debut_eff)
                        M += intensite * bras

                elif charge['type'] == 'moment':
                    if x <= charge['position'] <= pos_enc:
                        M += charge['valeur']

        return M

    def effort_normal(self, x):
        """
        Calcule l'effort normal N(x).

        Returns
        -------
        float
            Effort normal (N). Positif en traction.
        """
        # Pas d'effort axial pour une poutre droite sans charge axiale
        return 0.0

    def trouver_maximum_moment(self, n_points=500):
        """
        Trouve la position et valeur du moment maximal.

        Returns
        -------
        tuple
            (x_max, M_max, type)
        """
        x = np.linspace(0, self.L, n_points)
        moments = np.array([self.moment_flechissant(xi) for xi in x])

        idx_max = np.argmax(moments)
        idx_min = np.argmin(moments)

        # Retourne les extrema absolus
        if abs(moments[idx_max]) >= abs(moments[idx_min]):
            return x[idx_max], moments[idx_max], 'max'
        else:
            return x[idx_min], moments[idx_min], 'min'

    def afficher_resultats(self, n_points=11):
        """Affiche les résultats pour plusieurs positions."""
        positions = np.linspace(0, self.L, n_points)

        print(f"\n{'='*60}")
        print(f"RÉSULTATS DÉTAILLÉS - {self.nom}")
        print(f"{'='*60}")
        print(f"{'x (m)':<10} {'V (N)':<15} {'M (N.m)':<15}")
        print(f"{'-'*40}")

        for x in positions:
            V = self.effort_tranchant(x)
            M = self.moment_flechissant(x)
            print(f"{x:<10.2f} {V:<15.2f} {M:<15.2f}")

        # Trouve et affiche le moment maximal
        x_max, M_max, typ = self.trouver_maximum_moment()
        print(f"\n📊 Moment {typ}: {M_max:.2f} N.m à x = {x_max:.3f} m")

        # Vérifications aux extrémités
        if self.position_encastrement == 0:
            V_0 = self.effort_tranchant(0)
            M_0 = self.moment_flechissant(0)
            print(f"À l'encastrement (x=0): V={V_0:.2f} N, M={M_0:.2f} N.m")
            print(
                f"À l'extrémité libre (x={self.L}): V={self.effort_tranchant(self.L):.2f} N, M={self.moment_flechissant(self.L):.2f} N.m")
        else:
            V_L = self.effort_tranchant(self.L)
            M_L = self.moment_flechissant(self.L)
            print(
                f"À l'extrémité libre (x=0): V={self.effort_tranchant(0):.2f} N, M={self.moment_flechissant(0):.2f} N.m")
            print(
                f"À l'encastrement (x={self.L}): V={V_L:.2f} N, M={M_L:.2f} N.m")

        print(f"{'='*60}")


class PoutreAppuiSimpleRouleau(PoutreBase):
    """Poutre avec 1 appui simple (articulation) + 1 appui à rouleau."""

    def __init__(self, L, nom="Poutre appui simple + rouleau"):
        """
        Initialise une poutre avec 1 appui simple + 1 appui à rouleau.

        Parameters
        ----------
        L : float
            Longueur de la poutre (m)
        nom : str
            Nom de la poutre
        """
        super().__init__(L, nom)
        # Par défaut: appui simple à gauche (x=0), rouleau à droite (x=L)
        self.ajouter_appui_simple(0)
        self._ajouter_appui_rouleau(L)

    def _ajouter_appui_rouleau(self, position):
        """
        Ajoute un appui à rouleau.

        Parameters
        ----------
        position : float
            Position de l'appui (m)
        """
        if not 0 <= position <= self.L:
            raise ValueError(f"Position {position}m hors de la poutre")

        self.appuis.append({
            'type': 'rouleau',
            'position': position
        })
        self._sections_calculées = False

    def configurer_appuis(self, pos_simple, pos_rouleau):
        """
        Configure les positions des appuis.

        Parameters
        ----------
        pos_simple : float
            Position de l'appui simple
        pos_rouleau : float
            Position de l'appui à rouleau
        """
        # Réinitialise les appuis
        self.appuis = []
        self.ajouter_appui_simple(pos_simple)
        self._ajouter_appui_rouleau(pos_rouleau)
        self._reinitialiser_calculs()

    def calculer_reactions(self):
        """
        Calcule les réactions aux appuis.

        Returns
        -------
        dict
            {'R_simple': float, 'R_rouleau': float, 
             'pos_simple': float, 'pos_rouleau': float}
        """
        # Vérifie qu'on a exactement 2 appuis: 1 simple + 1 rouleau
        if len(self.appuis) != 2:
            raise ValueError("2 appuis requis: 1 simple + 1 rouleau")

        # Compte les types d'appuis
        types_appuis = [appui['type'] for appui in self.appuis]
        if not ('simple' in types_appuis and 'rouleau' in types_appuis):
            raise ValueError(
                "Un appui doit être 'simple' et l'autre 'rouleau'")

        # Identifie les appuis
        appui_simple = None
        appui_rouleau = None

        for appui in self.appuis:
            if appui['type'] == 'simple':
                appui_simple = appui
            elif appui['type'] == 'rouleau':
                appui_rouleau = appui

        if appui_simple is None or appui_rouleau is None:
            raise ValueError("Appui simple et rouleau requis")

        pos_simple = appui_simple['position']
        pos_rouleau = appui_rouleau['position']

        # S'assure que simple est à gauche (pour convention)
        if pos_simple > pos_rouleau:
            # Inverse les rôles
            appui_simple, appui_rouleau = appui_rouleau, appui_simple
            pos_simple, pos_rouleau = pos_rouleau, pos_simple

        # Initialisation
        somme_Fy = 0.0      # Somme des forces verticales
        somme_M_simple = 0.0  # Somme des moments par rapport à l'appui simple

        for charge in self.charges:
            if charge['type'] == 'concentree':
                F = charge['valeur']
                pos = charge['position']
                bras = pos - pos_simple  # Distance par rapport à l'appui simple
                somme_Fy += F
                somme_M_simple += F * bras

            elif charge['type'] == 'repartie':
                q = charge['valeur']
                x1, x2 = charge['debut'], charge['fin']
                F_tot = q * (x2 - x1)          # Force totale
                x_centre = (x1 + x2) / 2       # Centre de gravité
                bras = x_centre - pos_simple   # Distance du centre à l'appui simple
                somme_Fy += F_tot
                somme_M_simple += F_tot * bras

            elif charge['type'] == 'moment':
                M = charge['valeur']
                # Le moment s'ajoute directement
                somme_M_simple += M

        # Distance entre les appuis
        distance = pos_rouleau - pos_simple

        # Équations d'équilibre:
        # 1) ΣFy = 0 → R_simple + R_rouleau + ΣF = 0
        # 2) ΣM_simple = 0 → R_rouleau * distance + ΣM_simple = 0

        # De 2): R_rouleau = -ΣM_simple / distance
        R_rouleau = -somme_M_simple / distance

        # De 1): R_simple = -ΣF - R_rouleau
        R_simple = -somme_Fy - R_rouleau

        self.reactions = {
            'R_simple': R_simple,
            'R_rouleau': R_rouleau,
            'pos_simple': pos_simple,
            'pos_rouleau': pos_rouleau,
            'distance': distance,
            'ΣFy': somme_Fy,
            'ΣM_simple': somme_M_simple
        }

        # Vérification numérique
        tolerance = 1e-10
        verif_Fy = R_simple + R_rouleau + somme_Fy
        verif_M = R_rouleau * distance + somme_M_simple

        if abs(verif_Fy) > tolerance or abs(verif_M) > tolerance:
            print(f"⚠️  Vérification: ΣFy={verif_Fy:.2e}, ΣM={verif_M:.2e}")

        print(f"✅ Réactions calculées:")
        print(
            f"   Appui simple (x={pos_simple}m): R = {R_simple:.2f} N {'↑' if R_simple > 0 else '↓'}")
        print(
            f"   Appui rouleau (x={pos_rouleau}m): R = {R_rouleau:.2f} N {'↑' if R_rouleau > 0 else '↓'}")

        return self.reactions

    def effort_tranchant(self, x):
        """
        Calcule l'effort tranchant V(x).

        Convention: V(x) positif si tend la partie gauche vers le haut.
        """
        if self.reactions is None:
            self.calculer_reactions()

        pos_simple = self.reactions['pos_simple']
        pos_rouleau = self.reactions['pos_rouleau']
        R_simple = self.reactions['R_simple']

        # Détermine quelle partie de la poutre on considère
        if x < pos_simple:
            # À gauche de l'appui simple → section isolée
            V = 0
        elif pos_simple <= x < pos_rouleau:
            # Entre les appuis
            # V(x) = -R_simple - ΣF entre appui simple et x
            V = -R_simple

            for charge in self.charges:
                if charge['type'] == 'concentree':
                    if pos_simple <= charge['position'] <= x:
                        V -= charge['valeur']

                elif charge['type'] == 'repartie':
                    x1, x2 = charge['debut'], charge['fin']
                    q = charge['valeur']

                    # Partie de la charge entre appui simple et x
                    debut_eff = max(pos_simple, x1)
                    fin_eff = min(x, x2)

                    if debut_eff < fin_eff:
                        V -= q * (fin_eff - debut_eff)
        else:
            # À droite de l'appui rouleau
            # Dans cette zone, la poutre est libre
            V = 0

        return V

    def moment_flechissant(self, x):
        """
        Calcule le moment fléchissant M(x).

        Convention: M(x) positif si fibres inférieures tendues.
        """
        if self.reactions is None:
            self.calculer_reactions()

        pos_simple = self.reactions['pos_simple']
        pos_rouleau = self.reactions['pos_rouleau']
        R_simple = self.reactions['R_simple']

        if x < pos_simple:
            # À gauche de l'appui simple → moment nul
            M = 0
        elif pos_simple <= x < pos_rouleau:
            # Entre les appuis
            # M(x) = -R_simple*(x - pos_simple) - Σ(M des charges entre simple et x)
            M = -R_simple * (x - pos_simple)

            for charge in self.charges:
                if charge['type'] == 'concentree':
                    if pos_simple <= charge['position'] <= x:
                        bras = x - charge['position']
                        M -= charge['valeur'] * bras

                elif charge['type'] == 'repartie':
                    x1, x2 = charge['debut'], charge['fin']
                    q = charge['valeur']

                    # Partie de la charge entre appui simple et x
                    debut_eff = max(pos_simple, x1)
                    fin_eff = min(x, x2)

                    if debut_eff < fin_eff:
                        centre = (debut_eff + fin_eff) / 2
                        bras = x - centre
                        intensite = q * (fin_eff - debut_eff)
                        M -= intensite * bras

                elif charge['type'] == 'moment':
                    if pos_simple <= charge['position'] <= x:
                        M -= charge['valeur']
        else:
            # À droite de l'appui rouleau → moment nul
            M = 0

        return M

    def effort_normal(self, x):
        """
        Calcule l'effort normal N(x).

        Returns
        -------
        float
            Effort normal (N). Positif en traction.
        """
        # Pas d'effort axial pour une poutre droite sans charge axiale
        return 0.0

    def positions_appuis(self):
        """Retourne les positions des appuis."""
        if self.reactions is None:
            self.calculer_reactions()

        return {
            'simple': self.reactions['pos_simple'],
            'rouleau': self.reactions['pos_rouleau']
        }

    def afficher_resultats(self, n_points=11):
        """Affiche les résultats pour plusieurs positions."""
        positions = np.linspace(0, self.L, n_points)

        print(f"\n{'='*60}")
        print(f"RÉSULTATS DÉTAILLÉS - {self.nom}")
        print(f"{'='*60}")

        # Affiche les positions des appuis
        appuis = self.positions_appuis()
        print(f"Appui simple: x = {appuis['simple']:.2f} m")
        print(f"Appui rouleau: x = {appuis['rouleau']:.2f} m")
        print(f"Portée: {appuis['rouleau'] - appuis['simple']:.2f} m")

        print(f"\n{'x (m)':<10} {'V (N)':<15} {'M (N.m)':<15}")
        print(f"{'-'*40}")

        for x in positions:
            V = self.effort_tranchant(x)
            M = self.moment_flechissant(x)
            print(f"{x:<10.2f} {V:<15.2f} {M:<15.2f}")

        # Points particuliers
        print(f"\n📊 Points particuliers:")

        # À gauche de l'appui simple
        if appuis['simple'] > 0:
            V_gauche = self.effort_tranchant(appuis['simple'] - 1e-6)
            print(f"Juste à gauche de l'appui simple: V = {V_gauche:.2f} N")

        # À droite de l'appui simple
        V_droite_simple = self.effort_tranchant(appuis['simple'] + 1e-6)
        M_simple = self.moment_flechissant(appuis['simple'])
        print(
            f"À l'appui simple: V = {V_droite_simple:.2f} N, M = {M_simple:.2f} N.m")

        # À l'appui rouleau
        V_rouleau = self.effort_tranchant(appuis['rouleau'] - 1e-6)
        M_rouleau = self.moment_flechissant(appuis['rouleau'])
        print(
            f"À l'appui rouleau: V = {V_rouleau:.2f} N, M = {M_rouleau:.2f} N.m")

        # À droite de l'appui rouleau
        if appuis['rouleau'] < self.L:
            V_droite_rouleau = self.effort_tranchant(appuis['rouleau'] + 1e-6)
            print(
                f"Juste à droite de l'appui rouleau: V = {V_droite_rouleau:.2f} N")

        print(f"{'='*60}")


class DiagrammesPoutre:
    """Classe spécialisée pour le traçage des diagrammes RDM."""

    def __init__(self, poutre):
        """
        Initialise avec une poutre.

        Parameters
        ----------
        poutre : PoutreBase ou sous-classe
            Poutre déjà configurée avec appuis et charges
        """
        self.poutre = poutre
        self.fig = None
        self.axes = None

    def calculer_donnees_diagrammes(self, n_points=500):
        """
        Calcule les données pour tous les diagrammes.

        Parameters
        ----------
        n_points : int
            Nombre de points de calcul

        Returns
        -------
        dict
            Données complètes pour le traçage
        """
        # Vérifie que les réactions sont calculées
        if self.poutre.reactions is None:
            self.poutre.calculer_reactions()

        # Points de calcul
        x = np.linspace(0, self.poutre.L, n_points)

        # Calcule les efforts
        V = np.array([self.poutre.effort_tranchant(xi) for xi in x])
        M = np.array([self.poutre.moment_flechissant(xi) for xi in x])
        N = np.array([self.poutre.effort_normal(xi) for xi in x])

        # Trouve les points particuliers
        points_particuliers = self._trouver_points_particuliers(x, V, M)

        return {
            'x': x,
            'V': V,
            'M': M,
            'N': N,
            'points': points_particuliers,
            'L': self.poutre.L,
            'nom': self.poutre.nom
        }

    def _trouver_points_particuliers(self, x, V, M):
        """
        Trouve les points intéressants pour l'affichage.
        """
        points = {
            'V_zero': [],  # Points où V(x) = 0
            'M_extrema': [],  # Extrema de M(x)
            'charges': [],  # Positions des charges
            'appuis': []   # Positions des appuis
        }

        # Points où V(x) change de signe (M extremum)
        for i in range(1, len(V)):
            if V[i-1] * V[i] < 0:  # Changement de signe
                # Interpolation pour trouver le zéro exact
                x_zero = x[i-1] - V[i-1] * (x[i] - x[i-1]) / (V[i] - V[i-1])
                M_zero = np.interp(x_zero, x, M)
                points['V_zero'].append((x_zero, M_zero))

        # Extrema locaux de M
        if len(M) > 2:
            for i in range(1, len(M)-1):
                if (M[i] > M[i-1] and M[i] > M[i+1]) or \
                   (M[i] < M[i-1] and M[i] < M[i+1]):
                    points['M_extrema'].append((x[i], M[i]))

        # Positions des appuis
        for appui in self.poutre.appuis:
            points['appuis'].append(appui['position'])

        # Positions des charges concentrées
        for charge in self.poutre.charges:
            if charge['type'] == 'concentree':
                points['charges'].append(charge['position'])
            elif charge['type'] == 'moment':
                points['charges'].append(charge['position'])

        return points

    def _tracer_poutre_et_charges(self, ax):
        """Trace la poutre et les charges."""
        L = self.poutre.L

        # Ligne de la poutre
        ax.plot([0, L], [0, 0], 'k-', linewidth=3, label='Poutre')

        # Appuis
        for appui in self.poutre.appuis:
            x_appui = appui['position']
            type_appui = appui['type']

            if type_appui == 'simple':
                # Triangle pour appui simple
                triangle = np.array([[x_appui, -0.1],
                                     [x_appui-0.05*L, 0],
                                     [x_appui+0.05*L, 0]])
                ax.fill(triangle[:, 0], triangle[:, 1], 'blue', alpha=0.5)
                ax.text(x_appui, -0.15, 'Simple', ha='center', fontsize=9)

            elif type_appui == 'encastrement':
                # Rectangle plein pour encastrement
                rect = plt.Rectangle((x_appui-0.03*L, -0.12),
                                     0.06*L, 0.12,
                                     color='red', alpha=0.7)
                ax.add_patch(rect)
                ax.text(x_appui, -0.18, 'Encastrement',
                        ha='center', fontsize=9)

            elif type_appui == 'rouleau':
                # Rouleau (cercle)
                circle = plt.Circle((x_appui, 0), 0.03*L,
                                    color='green', alpha=0.7)
                ax.add_patch(circle)
                ax.text(x_appui, -0.15, 'Rouleau', ha='center', fontsize=9)

        # Charges
        for i, charge in enumerate(self.poutre.charges):
            if charge['type'] == 'concentree':
                x_charge = charge['position']
                F = charge['valeur']

                # Flèche pour la charge
                if F > 0:  # Vers le bas
                    ax.arrow(x_charge, 0.05, 0, -0.1,
                             head_width=0.02*L, head_length=0.02*L,
                             fc='red', ec='red', linewidth=2)
                    ax.text(x_charge, 0.12, f'{abs(F):.0f} N',
                            ha='center', color='red', fontweight='bold')
                else:  # Vers le haut
                    ax.arrow(x_charge, -0.05, 0, 0.1,
                             head_width=0.02*L, head_length=0.02*L,
                             fc='blue', ec='blue', linewidth=2)
                    ax.text(x_charge, -0.15, f'{abs(F):.0f} N',
                            ha='center', color='blue', fontweight='bold')

            elif charge['type'] == 'repartie':
                x1, x2 = charge['debut'], charge['fin']
                q = charge['valeur']

                # Flèches multiples pour charge répartie
                n_fleches = 10
                x_fleches = np.linspace(x1, x2, n_fleches)

                for xf in x_fleches:
                    if q > 0:  # Vers le bas
                        ax.arrow(xf, 0.02, 0, -0.08,
                                 head_width=0.01*L, head_length=0.01*L,
                                 fc='orange', ec='orange', alpha=0.7)
                    else:  # Vers le haut
                        ax.arrow(xf, -0.02, 0, 0.08,
                                 head_width=0.01*L, head_length=0.01*L,
                                 fc='cyan', ec='cyan', alpha=0.7)

                # Texte au centre
                x_centre = (x1 + x2) / 2
                ax.text(x_centre, 0.15 if q > 0 else -0.15,
                        f'{abs(q):.0f} N/m',
                        ha='center', color='darkorange' if q > 0 else 'darkcyan',
                        fontweight='bold')

                # Ligne horizontale
                y_line = 0.1 if q > 0 else -0.1
                ax.plot([x1, x2], [y_line, y_line],
                        color='orange' if q > 0 else 'cyan', linewidth=2)

            elif charge['type'] == 'moment':
                x_moment = charge['position']
                M = charge['valeur']

                # Double flèche pour le moment
                if M > 0:  # Anti-horaire
                    # Cercle avec flèche
                    circle = plt.Circle((x_moment, 0.15), 0.03*L,
                                        fill=False, ec='purple', linewidth=2)
                    ax.add_patch(circle)
                    # Flèche sur le cercle
                    ax.arrow(x_moment + 0.03*L, 0.15,
                             0.01*L, 0.01*L,
                             head_width=0.015*L, head_length=0.015*L,
                             fc='purple', ec='purple')
                else:  # Horaire
                    circle = plt.Circle((x_moment, -0.15), 0.03*L,
                                        fill=False, ec='purple', linewidth=2)
                    ax.add_patch(circle)
                    ax.arrow(x_moment - 0.03*L, -0.15,
                             -0.01*L, -0.01*L,
                             head_width=0.015*L, head_length=0.015*L,
                             fc='purple', ec='purple')

                ax.text(x_moment, 0.25 if M > 0 else -0.25,
                        f'{abs(M):.0f} N.m',
                        ha='center', color='purple', fontweight='bold')

        ax.set_xlim(-0.1*L, 1.1*L)
        ax.set_ylim(-0.3, 0.3)
        ax.set_title(f"{self.poutre.nom} - Longueur: {L:.2f} m",
                     fontsize=14, fontweight='bold')
        ax.set_xlabel("Position x (m)")
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

    def _tracer_diagramme_effort_tranchant(self, ax, data):
        """Trace le diagramme de l'effort tranchant."""
        x, V = data['x'], data['V']

        # Tracé principal
        ax.plot(x, V, 'r-', linewidth=2, label='V(x)')

        # Remplissage
        ax.fill_between(x, 0, V, where=(V >= 0),
                        color='red', alpha=0.3, interpolate=True)
        ax.fill_between(x, 0, V, where=(V < 0),
                        color='blue', alpha=0.3, interpolate=True)

        # Ligne zéro
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)

        # Points où V=0
        for x_zero, M_zero in data['points']['V_zero']:
            ax.plot(x_zero, 0, 'ko', markersize=6)
            ax.annotate(f'x={x_zero:.2f}m',
                        xy=(x_zero, 0),
                        xytext=(0, 15),
                        textcoords='offset points',
                        ha='center',
                        bbox=dict(boxstyle="round,pad=0.3",
                                  fc="yellow", alpha=0.7))

        # Valeurs aux appuis
        for x_appui in data['points']['appuis']:
            V_appui = np.interp(x_appui, x, V)
            ax.plot(x_appui, V_appui, 'go', markersize=8)
            ax.text(x_appui, V_appui + 0.05*max(abs(V)) if V_appui >= 0 else V_appui - 0.05*max(abs(V)),
                    f'{V_appui:.1f} N',
                    ha='center', fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

        ax.set_title("Effort Tranchant V(x)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Position x (m)")
        ax.set_ylabel("V(x) [N]")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        # Affiche les valeurs extrêmes
        V_max, V_min = np.max(V), np.min(V)
        ax.text(0.02, 0.98, f'Vmax = {V_max:.1f} N',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="red", alpha=0.3))
        ax.text(0.02, 0.90, f'Vmin = {V_min:.1f} N',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="blue", alpha=0.3))

    def _tracer_diagramme_moment_flechissant(self, ax, data):
        """Trace le diagramme du moment fléchissant."""
        x, M = data['x'], data['M']

        # Tracé principal
        ax.plot(x, M, 'b-', linewidth=2, label='M(x)')

        # Remplissage
        ax.fill_between(x, 0, M, where=(M >= 0),
                        color='blue', alpha=0.3, interpolate=True)
        ax.fill_between(x, 0, M, where=(M < 0),
                        color='red', alpha=0.3, interpolate=True)

        # Ligne zéro
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)

        # Points où V=0 (extrema de M)
        for x_zero, M_zero in data['points']['V_zero']:
            ax.plot(x_zero, M_zero, 'ko', markersize=8,
                    markerfacecolor='yellow')
            ax.annotate(f'M={M_zero:.1f} N.m\nx={x_zero:.2f}m',
                        xy=(x_zero, M_zero),
                        xytext=(10, 10),
                        textcoords='offset points',
                        ha='left',
                        bbox=dict(boxstyle="round,pad=0.3",
                                  fc="yellow", alpha=0.8))

        # Extrema locaux
        for x_ext, M_ext in data['points']['M_extrema']:
            if (x_ext, M_ext) not in data['points']['V_zero']:
                ax.plot(x_ext, M_ext, 'mo', markersize=6)

        # Valeurs aux appuis
        for x_appui in data['points']['appuis']:
            M_appui = np.interp(x_appui, x, M)
            ax.plot(x_appui, M_appui, 'go', markersize=8)
            ax.text(x_appui, M_appui + 0.05*max(abs(M)) if M_appui >= 0 else M_appui - 0.05*max(abs(M)),
                    f'{M_appui:.1f} N.m',
                    ha='center', fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

        ax.set_title("Moment Fléchissant M(x)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Position x (m)")
        ax.set_ylabel("M(x) [N.m]")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        # Affiche les valeurs extrêmes
        M_max, M_min = np.max(M), np.min(M)
        ax.text(0.02, 0.98, f'Mmax = {M_max:.1f} N.m',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="blue", alpha=0.3))
        ax.text(0.02, 0.90, f'Mmin = {M_min:.1f} N.m',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="red", alpha=0.3))

    def _tracer_diagramme_effort_normal(self, ax, data):
        """Trace le diagramme de l'effort normal."""
        x, N = data['x'], data['N']

        if np.all(N == 0):
            # Pas d'effort normal
            ax.text(0.5, 0.5, "Pas d'effort axial\n(N(x) = 0 pour toutes les sections)",
                    ha='center', va='center', transform=ax.transAxes,
                    fontsize=11, style='italic')
        else:
            ax.plot(x, N, 'g-', linewidth=2, label='N(x)')
            ax.fill_between(x, 0, N, color='green', alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
            ax.set_ylabel("N(x) [N]")
            ax.legend(loc='upper right')

        ax.set_title("Effort Normal N(x)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Position x (m)")
        ax.grid(True, alpha=0.3)

    def tracer_diagrammes_complets(self, n_points=500, figsize=(14, 12)):
        """
        Trace tous les diagrammes dans une figure unique.

        Parameters
        ----------
        n_points : int
            Nombre de points de calcul
        figsize : tuple
            Taille de la figure

        Returns
        -------
        tuple
            (figure, axes, données)
        """
        # Calcule les données
        data = self.calculer_donnees_diagrammes(n_points)

        # Crée la figure
        self.fig, self.axes = plt.subplots(4, 1, figsize=figsize)

        # 1. Poutre et charges
        self._tracer_poutre_et_charges(self.axes[0])

        # 2. Effort tranchant
        self._tracer_diagramme_effort_tranchant(self.axes[1], data)

        # 3. Moment fléchissant
        self._tracer_diagramme_moment_flechissant(self.axes[2], data)

        # 4. Effort normal
        self._tracer_diagramme_effort_normal(self.axes[3], data)

        plt.tight_layout()

        return self.fig, self.axes, data

    def tracer_diagramme_simple(self, n_points=500, figsize=(10, 8)):
        """
        Trace seulement V(x) et M(x) (version simplifiée).
        """
        data = self.calculer_donnees_diagrammes(n_points)

        fig, axes = plt.subplots(2, 1, figsize=figsize)

        # Effort tranchant
        axes[0].plot(data['x'], data['V'], 'r-', linewidth=2)
        axes[0].fill_between(data['x'], 0, data['V'],
                             where=(data['V'] >= 0),
                             color='red', alpha=0.3)
        axes[0].fill_between(data['x'], 0, data['V'],
                             where=(data['V'] < 0),
                             color='blue', alpha=0.3)
        axes[0].set_title("Effort Tranchant V(x)")
        axes[0].set_xlabel("Position x (m)")
        axes[0].set_ylabel("V(x) [N]")
        axes[0].grid(True, alpha=0.3)
        axes[0].axhline(y=0, color='k', linestyle='-', alpha=0.5)

        # Moment fléchissant
        axes[1].plot(data['x'], data['M'], 'b-', linewidth=2)
        axes[1].fill_between(data['x'], 0, data['M'],
                             where=(data['M'] >= 0),
                             color='blue', alpha=0.3)
        axes[1].fill_between(data['x'], 0, data['M'],
                             where=(data['M'] < 0),
                             color='red', alpha=0.3)
        axes[1].set_title("Moment Fléchissant M(x)")
        axes[1].set_xlabel("Position x (m)")
        axes[1].set_ylabel("M(x) [N.m]")
        axes[1].grid(True, alpha=0.3)
        axes[1].axhline(y=0, color='k', linestyle='-', alpha=0.5)

        plt.tight_layout()
        return fig, axes, data

    def exporter_diagrammes(self, filename, dpi=300):
        """
        Exporte les diagrammes en image.

        Parameters
        ----------
        filename : str
            Nom du fichier (avec extension .png, .jpg, .pdf)
        dpi : int
            Résolution de l'image
        """
        if self.fig is None:
            self.tracer_diagrammes_complets()

        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"✅ Diagrammes exportés vers: {filename}")

    def afficher_tableau_resultats(self):
        """Affiche un tableau récapitulatif des résultats."""
        data = self.calculer_donnees_diagrammes()

        print(f"\n{'='*80}")
        print(f"TABLEAU RÉCAPITULATIF - {self.poutre.nom}")
        print(f"{'='*80}")

        # Points particuliers
        print("\n📊 POINTS PARTICULIERS:")
        if data['points']['V_zero']:
            print("  Points où V(x) = 0 (M(x) extremum):")
            for x_zero, M_zero in data['points']['V_zero']:
                print(f"    x = {x_zero:.3f} m → M = {M_zero:.2f} N.m")
        else:
            print("  Aucun point où V(x) = 0")

        # Valeurs extrêmes
        print(f"\n📈 VALEURS EXTRÊMES:")
        print(f"  Effort tranchant: Vmax = {np.max(data['V']):.2f} N, "
              f"Vmin = {np.min(data['V']):.2f} N")
        print(f"  Moment fléchissant: Mmax = {np.max(data['M']):.2f} N.m, "
              f"Mmin = {np.min(data['M']):.2f} N.m")

        # Réactions
        print(f"\n⚖️  RÉACTIONS AUX APPUIS:")
        for appui in self.poutre.appuis:
            x_app = appui['position']
            V_app = np.interp(x_app, data['x'], data['V'])
            M_app = np.interp(x_app, data['x'], data['M'])
            print(f"  {appui['type']} à x={x_app:.2f}m: "
                  f"V={V_app:.2f} N, M={M_app:.2f} N.m")

        print(f"{'='*80}")
