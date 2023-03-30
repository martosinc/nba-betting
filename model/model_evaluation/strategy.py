def evaluate(prediction, bookmaker):
    parameter = prediction[0] * (1 / bookmaker[0]) - prediction[1] * (1 / bookmaker[1])
    const = prediction[1] * (1 / bookmaker[1]) - 1
    value = max(parameter + const, const)
    return value, parameter + const == value

def bet(bank, prediction, bookmaker, threshold=0.3):
    value, stake = evaluate(prediction, bookmaker)
    if value > 0:
        return [stake * (1 - threshold + value) * bank, (1 - stake) * (1 - threshold + value) * bank]
        # return [stake * bank, (1 - stake) * bank]
    return [0, 0]

    