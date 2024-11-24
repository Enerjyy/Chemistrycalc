import tkinter as tk
from tkinter import scrolledtext
import concurrent.futures
import pubchempy as pcp
from itertools import product
import time

def generate_formulas(elements, max_atoms=3):
    formulas = []
    for combination in product(range(1, max_atoms + 1), repeat=len(elements)):
        formula = ''
        for count, element in zip(combination, elements):
            if count == 1:
                formula += element
            else:
                formula += f'{element}{count}'
        formulas.append(formula)
    return formulas

def search_compound(formula):
    try:
        compounds = pcp.get_compounds(formula, 'formula')
        if not compounds:
            return []
        result = []
        for compound in compounds:
            name = getattr(compound, 'iupac_name', None) or \
                   getattr(compound, 'synonyms', [None])[0] or "Неизвестное соединение"
            cid = compound.cid
            formula = getattr(compound, 'molecular_formula', 'Нет данных')
            weight = getattr(compound, 'molecular_weight', 'Нет данных')
            smiles = getattr(compound, 'isomeric_smiles', 'Нет данных')
            result.append(f"{name} (CID: {cid}) - Формула: {formula}, Вес: {weight}")
        return result
    except Exception as e:
        print(f"Произошла ошибка при поиске для формулы {formula}: {e}")
        return []

def search_formulas_multiprocessing(elements):
    formulas = generate_formulas(elements)
    results = []
    valid_formulas = [formula for formula in formulas if is_valid_formula(formula)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_formula = {executor.submit(search_compound, formula): formula for formula in valid_formulas}
        for future in concurrent.futures.as_completed(future_to_formula):
            formula = future_to_formula[future]
            try:
                result = future.result()
                if result:
                    results.extend(result)
            except Exception as exc:
                print(f'Произошла ошибка при поиске для формулы {formula}: {exc}')
    return results

def is_valid_formula(formula):
    import re
    pattern = re.compile(r'^[A-Za-z0-9]+$')
    return bool(pattern.match(formula))

def start_search():
    elements_input = elements_entry.get()
    elements = elements_input.split()
    results_text.delete(1.0, tk.END)
    start_time = time.time()
    found_compounds = search_formulas_multiprocessing(elements)
    if found_compounds:
        for compound in found_compounds:
            results_text.insert(tk.END, f"{compound}\n")
    else:
        results_text.insert(tk.END, "Не найдено соединений.\n")
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    results_text.insert(tk.END, f"\nПоиск завершен. Время выполнения: {elapsed_time} секунд.\n")

root = tk.Tk()
root.title("Поиск химических соединений")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

elements_label = tk.Label(frame, text="Введите химические элементы, разделенные пробелами (например: C H O):")
elements_label.grid(row=0, column=0, padx=5, pady=5)

elements_entry = tk.Entry(frame, width=30)
elements_entry.grid(row=1, column=0, padx=5, pady=5)

search_button = tk.Button(frame, text="Поиск", command=start_search)
search_button.grid(row=2, column=0, padx=5, pady=10)

results_text = scrolledtext.ScrolledText(root, width=80, height=20)
results_text.pack(padx=10, pady=10)

root.mainloop()
