import concurrent.futures
import pubchempy as pcp
from itertools import product
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

def generate_formulas(elements, max_atoms=2):
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
            result.append(f"{name} (CID: {cid}) - Формула: {formula}, Вес: {weight}, SMILES: {smiles}")
        return result
    except Exception as e:
        print(f"Произошла ошибка при поиске для формулы {formula}: {e}")
        return []

def search_formulas_multiprocessing(elements):
    formulas = generate_formulas(elements)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_formula = {executor.submit(search_compound, formula): formula for formula in formulas}
        for future in concurrent.futures.as_completed(future_to_formula):
            formula = future_to_formula[future]
            try:
                result = future.result()
                if result:
                    results.extend(result)
            except Exception as exc:
                print(f'Произошла ошибка при поиске для формулы {formula}: {exc}')
    return results

@app.route('/find_combinations', methods=['POST'])
def find_combinations():
    data = request.get_json()
    elements = data.get('symbols', [])
    
    if not elements:
        return jsonify({"error": "Нет выбранных элементов!"}), 400
    
    start_time = time.time()
    found_compounds = search_formulas_multiprocessing(elements)
    end_time = time.time()

    elapsed_time = round(end_time - start_time, 2)
    
    if found_compounds:
        return jsonify({
            "combinations": found_compounds,
            "execution_time": elapsed_time
        })
    else:
        return jsonify({
            "combinations": "Не найдено соединений.",
            "execution_time": elapsed_time
        })

if __name__ == '__main__':
    app.run(debug=True)
