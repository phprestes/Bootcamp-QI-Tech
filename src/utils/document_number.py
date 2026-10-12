CPF_LENGTH = 11

CHECK_DIGIT_POSITIONS = [9, 10]


def is_valid_cpf(document_number: str) -> bool:
    """Confere os dígitos verificadores; o formato já foi validado pelo schema.

    Formato certo com dígito errado é 422, não 400: o pedido foi entendido, o valor não existe.
    """
    digits = []
    for character in document_number:
        if character.isdigit():
            digits.append(int(character))

    if len(digits) != CPF_LENGTH:
        return False

    # Dígitos repetidos passam na conta, mas não são emitidos pela Receita.
    all_digits_are_equal = True
    for digit in digits:
        if digit != digits[0]:
            all_digits_are_equal = False
            break

    if all_digits_are_equal:
        return False

    for position in CHECK_DIGIT_POSITIONS:
        total = 0
        first_weight = position + 1

        for index in range(position):
            total = total + digits[index] * (first_weight - index)

        remainder = total % 11

        if remainder < 2:
            expected_digit = 0
        else:
            expected_digit = 11 - remainder

        if digits[position] != expected_digit:
            return False

    return True
