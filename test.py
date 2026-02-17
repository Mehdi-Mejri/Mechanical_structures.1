# test_simple.py
import PyRDM as pyrdm

poutre1 = pyrdm.Simply_Supported_Beam(L=5)
poutre1.add_roller_support(0)
poutre1.add_simple_support(5)
poutre1.add_point_load(-1000, 2)

print("Poutre de 5m avec charge de 1000N à 2m")
reactions1 = poutre1.calculate_reactions()
print(f"Réaction gauche: {reactions1['R_A']:.2f} N")
print(f"Réaction droite: {reactions1['R_B']:.2f} N")
print(f"Somme des forces: {reactions1['ΣFy']:.2f} N")
diagram = pyrdm.Diagramm(poutre1)
diagram.plot()
diagram.print_summary()
