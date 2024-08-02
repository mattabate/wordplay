import numpy as np


def bernoulli_sample():
    # Generate six Bernoulli random variables with p=0.6
    random_vars = np.random.binomial(1, 0.6, 6)

    # Check if all the first three are 1s or if all the last three are 1s
    first_three = np.all(random_vars[:3] == 1)
    last_three = np.all(random_vars[3:] == 1)

    return first_three or last_three


# Run the function and print the result
num = 1000000
num_true = 0
for _ in range(num):
    if bernoulli_sample():
        num_true += 1
print(num_true / num)
