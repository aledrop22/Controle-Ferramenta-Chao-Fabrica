# --- DADOS COMUNS COMPARTILHADOS ENTRE FERRAMENTAS.PY E APP_QUALIDADE.PY ---

# --- DADOS DA FÁBRICA (Operadores, Setores e Máquinas) ---
setores_operadores = {
    "Usinagem": ["Alex", "Leandro", "Pedro Henrique", "Rodrigo", "Vinícius", "Márcio", "Gabriel", "Lucas", "Jadson"],
    "Produção": ["Sr. Luis", "Luis", "Pablo", "Felipe", "Amadeus"],
    "Manutenção": ["Nilson", "Marcos", "Renato"],
    "Estoque": ["Elias", "Lucas", "Victor", "Rafael"],
    "Expedição": ["Karina", "Deise", "Frank", "Giulia", "Adriano", "Ismael"]
}

maquinas_lista = [
    "Selecione...", "GL 01", "GL 02", "CNC 01", "CNC 02",
    "FRESA 01", "FRESA 02", "TORNO 01", "TORNO 02", "TORNO 03",
    "PRODUÇÃO", "EXPEDIÇÃO", "ESTOQUE", "MANUTENÇÃO", "PCP"
]

# --- DADOS DO INVENTÁRIO PADRÃO ---
estoque = {
    'Porca Calibradora': [
        '5/8" x 18UNF', '3/4" x 10 UNC',
        'M8 x 1,25', 'M10 x 1,0', 'M10 x 1,5',
        'M12 x 1,0', 'M12 x 1,5', 'M12 x 1,75',
        'M15 x 1,0', 'M17 x 1,0',
        'M14 x 1,5', 'M16 x 1,5',
        'M18 x 1,5',
        'M20 x 1,0', 'M20 x 1,5',
        'M24 x 1,5', 'M24 x 3,0',
        'M25 x 1,0', 'M25 x 1,5', 'M30 x 1,5',  
        'M38 x 1,5', 'M40 x 1,5', 'M40 x 2,0',
        'M42 x 2,0', 'M45 x 1,5',
        'M50 x 1,5', 'M55 x 1,5', 'M55 x 2,0',
        'M60 x 1,5', 'M60 x 2,0',
        'M66 x 2,0', 'M85 x 2,0'
    ],
    'Micrômetro': [
        '0 - 25', '25 - 50', '50 - 75', '75 - 100', '100 - 125',
        '125 - 150', '150 - 175', '175 - 200', '200 - 225',
        '225 - 250', '250 - 275', '275 - 300', '0 - 1"', '1 - 2"'
    ],
    'Súbito': ['6 - 10', '10 - 18', '18 - 35', '35 - 50', '50 - 160'],
    'Relógio Comparador': ['Relógio 1', 'Relógio 2', 'Relógio 3'],
    'Paquímetro Digital': ['Modelo Digital']
}
