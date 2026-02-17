import numpy as np
import matplotlib.pyplot as plt


class Beams:
    def __init__(self, L):
        self.L = L  # Length of the beam
        self.supports = []  # List to hold support positions
        self.loads = []  # List to hold applied loads
        self.reactions = None

    def add_point_load(self, value, position):
        if not (0 <= position <= self.L):
            raise ValueError("Load position must be within the beam length.")
        self.loads.append(('point loads', value, position))

    def add_distributed_load(self, value, start, end):
        if not (0 <= start < end <= self.L):
            raise ValueError(
                "Distributed load positions must be within the beam length and start must be less than end.")
        self.loads.append(('distributed loads', value, start, end))

    def add_torque(self, value, position):
        if not (0 <= position <= self.L):
            raise ValueError("Torque position must be within the beam length.")
        self.loads.append(('Torque', value, position))

    def add_simple_support(self, position):
        if not (0 <= position <= self.L):
            raise ValueError(
                "Support position must be within the beam length.")
        self.supports.append(('simple support', position))

    def add_fixed_support(self, position):
        if position != 0 and position != self.L:
            raise ValueError(
                "Support position must be only on the right or left of the beams.")
        self.supports.append(('fixed support', position))

    def add_roller_support(self, position):
        if not (0 <= position <= self.L):
            raise ValueError(
                "Support position must be within the beam length.")
        self.supports.append(('roller support', position))

    def validate_structure(self):
        unknowns_by_support = {
            'fixed support': 3,
            'simple support': 2,
            'roller support': 1
        }
        total_unknowns = 0
        for support in self.supports:
            name = support[0]
            if name in unknowns_by_support:
                total_unknowns += unknowns_by_support[name]
            else:
                raise ValueError(f"Unknown support type: {name}")
        if total_unknowns == 3:
            return True
        else:
            raise ValueError(
                "The structure is not statically determinate. Total unknowns must equal 3.")

    def show_information(self):
        print(f'Beam Length: {self.L} m')
        print(f'number of supports: {len(self.supports)}')
        for i, support in enumerate(self.supports, start=1):
            print(
                f'Support {i}: {support[0]} at position {support[1]} m')
        for y, load in enumerate(self.loads, start=1):
            print(f'Load {y}: {load}')

    def reinitialize_calculations(self):
        self.reactions = None


class Simply_Supported_Beam(Beams):
    def __init__(self, L):
        super().__init__(L)

    def supports_validation(self):
        for support in self.supports:
            if support[0] not in ('simple support', 'roller support'):
                raise ValueError(
                    "Simply Supported Beam can only have simple and roller supports.")
        if len(self.supports) != 2:
            raise ValueError(
                "Simply Supported Beam must have exactly two supports.")

    def calculate_reactions(self):
        self.supports_validation()
        A_pos = self.supports[0][1]
        B_pos = self.supports[1][1]
        L = B_pos - A_pos
        R_A = 0.0
        R_B = 0.0
        Fy = 0.0
        Ma = 0.0
        for load in self.loads:
            if load[0] == 'point loads':
                F = load[1]
                x = load[2]
                Fy += F
                Ma += F * (x - A_pos)
            elif load[0] == 'distributed loads':
                w = load[1]
                a = load[2]
                b = load[3]
                length = b - a
                F = w * length
                x_centroid = (a + b) / 2
                Fy += F
                Ma += F * (x_centroid - A_pos)
            elif load[0] == 'Torque':
                Ma += load[1]
        R_B = -Ma / L
        R_A = -Fy - R_B
        self.reactions = {'R_A': R_A, 'R_B': R_B, 'ΣFy': Fy, 'ΣMa': Ma}
        return self.reactions


class Fixed_Beam(Beams):
    def __init__(self, L):
        super().__init__(L)

    def supports_validation(self):
        if len(self.supports) != 1:
            raise ValueError("Fixed Beam must have exactly one fixed support.")

        support_type, support_position = self.supports[0]
        if support_type != 'fixed support':
            raise ValueError("Fixed Beam can only have a fixed support.")

        if support_position not in [0, self.L]:
            print(
                f"Warning: Fixed support at position {support_position} is not at beam end")

    def calculate_reactions(self):
        self.supports_validation()

        A_pos = self.supports[0][1]
        Fy = 0.0
        Ma = 0.0

        for load in self.loads:
            if load[0] == 'point loads':
                F = load[1]
                x = load[2]
                Fy += F
                Ma += F * (x - A_pos)

            elif load[0] == 'distributed loads':
                w = load[1]
                a = load[2]
                b = load[3]
                length = b - a
                F = w * length
                x_centroid = (a + b) / 2
                Fy += F
                Ma += F * (x_centroid - A_pos)

            elif load[0] == 'Torque':
                Ma += load[1]

        R_A = -Fy
        M_A = -Ma

        self.reactions = {
            'R_A': R_A,
            'M_A': M_A,
            'ΣFy': Fy,
            'ΣMa': Ma
        }

        return self.reactions


class Diagramm():
    def __init__(self, beam):
        self.beam = beam
        self.x = None
        self.V = None
        self.M = None

    def calculate_shear_moment(self, n_points=100000):
        """
        Calcule l'effort tranchant et le moment fléchissant le long de la poutre
        """

        self.x = np.linspace(0, self.beam.L, n_points)
        self.V = np.zeros_like(self.x)
        self.M = np.zeros_like(self.x)

        if self.beam.reactions is None:
            self.beam.calculate_reactions()

        for i, xi in enumerate(self.x):
            V_i = 0
            M_i = 0

            for j, support in enumerate(self.beam.supports):
                support_type, support_pos = support

                if xi >= support_pos:
                    if support_type == 'fixed support':

                        if 'R_A' in self.beam.reactions:
                            V_i += self.beam.reactions['R_A']
                            M_i += self.beam.reactions['R_A'] * \
                                (xi - support_pos)
                        if 'M_A' in self.beam.reactions:
                            M_i += self.beam.reactions['M_A']

                    elif support_type in ['simple support', 'roller support']:

                        if j == 0 and 'R_A' in self.beam.reactions:
                            V_i += self.beam.reactions['R_A']
                            M_i += self.beam.reactions['R_A'] * \
                                (xi - support_pos)
                        elif j == 1 and 'R_B' in self.beam.reactions:
                            V_i += self.beam.reactions['R_B']
                            M_i += self.beam.reactions['R_B'] * \
                                (xi - support_pos)

            for load in self.beam.loads:
                if load[0] == 'point loads':
                    F = load[1]
                    x_load = load[2]
                    if xi >= x_load:
                        V_i += F
                        M_i += F * (xi - x_load)

                elif load[0] == 'distributed loads':
                    w = load[1]
                    a = load[2]
                    b = load[3]

                    if xi > a:
                        if xi <= b:
                            length = xi - a
                            F_partial = w * length
                            V_i += F_partial
                            M_i += F_partial * (length / 2)
                        else:
                            length = b - a
                            F_total = w * length
                            V_i += F_total

                            M_i += F_total * (xi - (a + b) / 2)

                elif load[0] == 'Torque':
                    T = load[1]
                    x_torque = load[2]
                    if xi >= x_torque:
                        M_i += T

            self.V[i] = V_i
            self.M[i] = -M_i

    def plot(self, figsize=(12, 8)):
        """
        Trace les diagrammes d'effort tranchant et de moment fléchissant
        """
        if self.x is None:
            self.calculate_shear_moment()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        ax1.fill_between(self.x, 0, self.V, alpha=0.3,
                         color='blue', label='V(x)')
        ax1.plot(self.x, self.V, 'b-', linewidth=2)
        ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax1.set_xlabel('Position (m)')
        ax1.set_ylabel('Effort tranchant V (N)')
        ax1.set_title('Diagramme de l\'effort tranchant')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        self._add_key_points(ax1, self.V, 'V', 'blue')

        ax2.fill_between(self.x, 0, self.M, alpha=0.3,
                         color='red', label='M(x)')
        ax2.plot(self.x, self.M, 'r-', linewidth=2)
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('Position (m)')
        ax2.set_ylabel('Moment fléchissant M (Nm)')
        ax2.set_title('Diagramme du moment fléchissant')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        self._add_key_points(ax2, self.M, 'M', 'red')

        self._plot_supports(ax1)
        self._plot_supports(ax2)

        plt.tight_layout()
        plt.show()

        return fig, (ax1, ax2)

    def _add_key_points(self, ax, values, label, color):
        """
        Ajoute les valeurs aux points clés (max, min, appuis)
        """

        idx_max = np.argmax(values)
        idx_min = np.argmin(values)

        for idx in [idx_max, idx_min]:
            if idx > 0 and idx < len(self.x)-1:
                ax.plot(self.x[idx], values[idx], 'o',
                        color='green', markersize=6)
                ax.annotate(f'{label} = {values[idx]:.1f}',
                            (self.x[idx], values[idx]),
                            textcoords="offset points",
                            xytext=(0, 10 if values[idx] >= 0 else -15),
                            ha='center',
                            fontsize=8,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        for support in self.beam.supports:
            pos = support[1]
            idx = np.argmin(np.abs(self.x - pos))
            if idx > 0 and idx < len(self.x)-1:
                ax.plot(self.x[idx], values[idx], 'o',
                        color='purple', markersize=4)

    def _plot_supports(self, ax):
        """
        Ajoute la représentation des supports sur le graphique
        """
        ylim = ax.get_ylim()
        y_range = ylim[1] - ylim[0]
        y_pos = ylim[0] + 0.05 * y_range

        for support in self.beam.supports:
            support_type, pos = support

            if support_type == 'simple support':
                ax.plot(pos, y_pos, 'b^', markersize=10)
                ax.annotate('Appui simple', (pos, y_pos),
                            xytext=(0, 10), textcoords='offset points',
                            ha='center', fontsize=8)
            elif support_type == 'roller support':
                ax.plot(pos, y_pos, 'bo', markersize=8)
                ax.annotate('Appui roulant', (pos, y_pos),
                            xytext=(0, 10), textcoords='offset points',
                            ha='center', fontsize=8)
            elif support_type == 'fixed support':
                ax.plot(pos, y_pos, 'bs', markersize=8)
                ax.annotate('Encastrement', (pos, y_pos),
                            xytext=(0, 10), textcoords='offset points',
                            ha='center', fontsize=8)

    def get_max_values(self):
        """
        Retourne les valeurs maximales
        """
        if self.x is None:
            self.calculate_shear_moment()
        idx_max_V = np.argmax(np.abs(self.V))
        idx_max_M = np.argmax(np.abs(self.M))

        return {
            'V_max_abs': np.abs(self.V[idx_max_V]),
            'V_max_position': self.x[idx_max_V],
            'V_max': self.V[idx_max_V],
            'V_min': np.min(self.V),
            'M_max_abs': np.abs(self.M[idx_max_M]),
            'M_max_position': self.x[idx_max_M],
            'M_max': self.M[idx_max_M],
            'M_min': np.min(self.M)
        }

    def print_summary(self):
        """
        Affiche un résumé des résultats
        """
        if self.x is None:
            self.calculate_shear_moment()

        max_vals = self.get_max_values()

        print("\n" + "="*60)
        print("SUMMARY OF DIAGRAMMES".center(60))
        print("="*60)
        print(f"\nShear force:")
        print(f"  • Positive maximum : {max_vals['V_max']:.2f} N")
        print(f"  • Negative minimum : {max_vals['V_min']:.2f} N")
        print(
            f"  • Absolute maximum : {max_vals['V_max_abs']:.2f} N à {max_vals['V_max_position']:.2f} m")

        print(f"\nBending moment:")
        print(f"  • Positive maximum : {max_vals['M_max']:.2f} Nm")
        print(f"  • Negative minimum : {max_vals['M_min']:.2f} Nm")
        print(
            f"  • Absolute maximum : {max_vals['M_max_abs']:.2f} Nm à {max_vals['M_max_position']:.2f} m")
        print("\n" + "="*60)

    def export_data(self, filename="beam_data.csv"):
        """
        Exporte les données dans un fichier CSV
        """
        if self.x is None:
            self.calculate_shear_moment()

        import pandas as pd
        data = pd.DataFrame({
            'Position (m)': self.x,
            'Effort_tranchant (N)': self.V,
            'Moment_flechissant (Nm)': self.M
        })
        data.to_csv(filename, index=False)
        print(f"Données exportées vers {filename}")
