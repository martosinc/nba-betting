from random import uniform as rand

class Bet:
    def __init__(self, prob1, prob2):
        self.p1 = prob1
        self.p2 = prob2
        self.c1 = 1 / prob1
        self.c2 = 1 / prob2

def eval_stake(prediction, bookmaker):
    event1_stake = prediction.p1 * bookmaker.c1
    event1_const = -prediction.p1
    event2_stake = -prediction.p2 * bookmaker.c2
    event2_const = -prediction.p2 + prediction.p2 * bookmaker.c2
    stake = event1_stake + event2_stake
    const = event1_const + event2_const
    win = max(const, stake + const)
    return int(win != const), win

bookmaker_precision = 0.075
model_precision = bookmaker_precision

bank = 10 ** 8
win = 0

mean_win = 0

for i in range(bank):
    event_prob = rand(0, 0.5)
    probability = Bet(event_prob, 1 - event_prob)
    bookmaker_error = rand(-1, 1) * bookmaker_precision
    bookmaker_prediction = Bet(probability.p1 + bookmaker_error + 0.025, probability.p2 - bookmaker_error + 0.025)
    model_error = rand(-1, 1) * model_precision
    model_prediction = Bet(probability.p1 + model_error, probability.p2 - model_error)
    stake = eval_stake(model_prediction, bookmaker_prediction)
    if stake[1] > 0.3:
        initial_win = win
        if rand(0, 1) < probability.p1:
            win += stake[0] * bookmaker_prediction.c1 - 1
        else:
            win += (1 - stake[0]) * bookmaker_prediction.c2 - 1
        mean_win += stake[0] * bookmaker_prediction.c1 - 1 + (1 - stake[0]) * bookmaker_prediction.c2 - 1
print(f'{int(win) + bank}/{bank}')