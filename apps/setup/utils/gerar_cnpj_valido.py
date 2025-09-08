import random

def gerar_cnpj_valido():
    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(a) * b for a, b in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # Gera os 8 primeiros dígitos da raiz + 4 da filial (geralmente 0001)
    base = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    pesos_d1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = calcular_digito(base, pesos_d1)

    pesos_d2 = [6] + pesos_d1
    d2 = calcular_digito(base + [int(d1)], pesos_d2)

    cnpj = ''.join(map(str, base)) + d1 + d2
    return cnpj
