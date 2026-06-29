# --- DADOS COMUNS COMPARTILHADOS ENTRE FERRAMENTAS.PY E APP_QUALIDADE.PY ---

# --- DADOS DA FÁBRICA (Operadores, Setores e Máquinas) ---
setores_operadores = {
    "Usinagem": ["Pedro Henrique", "Alex", "Vitor", "Rodrigo", "Vinícius", "Márcio", "Gabriel", "Lucas", "Jadson"],
    "Produção": ["Sr. Luis", "Luis", "Daniel", "Felipe", "Jadson"],
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
        'M3 x 0,35', 'M4 x 0,5', 'M5 x 0,5', 'M6 x 0,75', 'M8 x 1',
        'M10 x 1', 'M12 x 1', 'M12 x 1,5', 'M14 x 1', 'M14 x 1,5',
        'M16 x 1', 'M16 x 1,5', 'M18 x 1', 'M18 x 1,5', 'M20 x 1',
        'M20 x 1,5', 'M22 x 1,5', 'M24 x 1,5', 'M27 x 1,5', 'M30 x 1,5'
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
