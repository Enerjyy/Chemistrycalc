import json
import itertools
import math
from tkinter import Tk, Label, Entry, Button, Text, END

### ПОДГРУЗКА ИНФЫ С JSON
def load_elements_from_json():
    with open("elements.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_acid_radicals_from_json():
    with open("acid_radicals.json", "r", encoding="utf-8") as f:
        return json.load(f)

elements_data = load_elements_from_json()
acid_radicals_data = load_acid_radicals_from_json()

### ОКСИДЫ
def find_oxide(elements):
    oxides = []
    
    if "O" in elements: 
        for el in elements:
            if el != "O" and el in elements_data:
                oxidation_in_oxides = elements_data[el].get("oxidation_in_oxides", {}).get("O", [])
                
                for oxidation_state in oxidation_in_oxides:
                    if oxidation_state != 0:
                        element_index = abs(oxidation_state)
                        oxygen_index = 2
                        compound = f"{el}{oxygen_index if element_index != 1 else ''}O{element_index if element_index != 1 else ''}"
                        oxides.append(compound)

    return oxides

### ПЕРОКСИДЫ
def find_peroxide(elements):
    peroxides = []
    if "O" in elements and len(elements) == 2:
        for el in elements:
            if el != "O":
                peroxides.append(f"{el}2O2")
    return peroxides

### ГИДРОКСИДЫ
def find_hydroxide(elements):
    hydroxides = []
    if "H" in elements and "O" in elements and len(elements) > 1:
        metals = ["Li", "Na", "K", "Rb", "Cs", "Be", "Mg", "Ca", "Sr", "Ba", "Ra", "Al", "Zn", "Cd", "Hg", "Pb", "Cu", "Ag", "Au", "Fe", "Ni", "Co", "Mn", "Cr", "Ti", "Mo", "W", "Zr", "Nb", "Ta", "Re", "Os", "Ir", "Pt", "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"]
        metals_in_elements = [el for el in elements if el in metals]
        for metal in metals_in_elements:
            oxidation_state = None
            for state in elements_data.get(metal, {}).get("oxidation_states", []):
                if state != 0:
                    oxidation_state = state
                    break
            if oxidation_state:
                hydroxide_count = abs(oxidation_state)
                hydroxides.append(f"{metal}(OH){hydroxide_count}")
    return hydroxides

### КИСЛОТЫ И СОЛИ 
### !!!РАБОТАЕТ ПЛОХО!!!
def find_acids_and_salts(elements):
    compounds = []
    filtered_radicals = {radical: info for radical, info in acid_radicals_data.items() if all(el in elements for el in radical)}
    if "H" in elements:
        for radical, info in filtered_radicals.items():
            charge = info["charge"]
            if charge < 0:
                n_hydrogens = abs(charge)
                compounds.append(f"H{n_hydrogens}{radical}")
    if any(el in elements for el in ["Na", "K", "Ca", "Mg", "Al", "Fe", "Cu", "Ag"]):
        for metal in elements:
            if metal in elements_data:
                for radical, info in filtered_radicals.items():
                    charge = info["charge"]
                    if charge < 0:
                        n_metals = abs(charge) // 1
                        if charge % 1 != 0:
                            n_metals += 1
                        compounds.append(f"{metal}{n_metals}{radical}")
                    else:
                        continue
    return compounds

### ОСТАЛЬНЫЕ СОЕДИНЕНИЯ И КОНЕЧНАЯ КОМПАНОВКА
def find_compounds(selected_elements):
    compounds = []
    selected_elements_sorted = sorted(selected_elements)
    oxidation_states = {el: elements_data[el]["oxidation_states"] for el in selected_elements_sorted}
    for states in itertools.product(*oxidation_states.values()):
        total_charge = sum(states)
        if total_charge == 0:
            compound = ""
            for el, state in zip(selected_elements_sorted, states):
                compound += f"{el}{'' if abs(state) == 1 else abs(state)}"
            if all(el in compound for el in selected_elements_sorted):
                compounds.append(compound)
    compounds.extend(find_oxide(selected_elements_sorted))
    compounds.extend(find_peroxide(selected_elements_sorted))
    compounds.extend(find_hydroxide(selected_elements_sorted))
    compounds.extend(find_acids_and_salts(selected_elements_sorted))
    unique_compounds = list(set(compounds))
    filtered_compounds = [compound for compound in unique_compounds if all(el in compound for el in selected_elements_sorted)]
    return filtered_compounds if filtered_compounds else ["Нет возможных соединений"]

### ИНТЕРФЕЙС
def main():
    def find_and_display_compounds():
        input_elements = entry.get().replace(" ", "").split(',')
        compounds = find_compounds(input_elements)
        output_field.delete(1.0, END)
        output_field.insert(END, "\n".join(compounds))

    root = Tk()
    root.title("Химический калькулятор соединений")

    Label(root, text="Введите элементы (например, Na, O, H):").grid(row=0, column=0)

    entry = Entry(root, width=30)
    entry.grid(row=1, column=0)

    Button(root, text="Найти соединения", command=find_and_display_compounds).grid(row=2, column=0)

    output_field = Text(root, height=10, width=50)
    output_field.grid(row=3, column=0)

    root.mainloop()

if __name__ == "__main__":
    main()
