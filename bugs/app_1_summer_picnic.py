import random
import numpy as np


def pick_the_winners(raffle_tickets):
    # print(f"the raffle numbers are: {raffle_tickets}")
    randomizer = random.Random(42)
    randomizer.shuffle(raffle_tickets)
    # print(f"random numbers are: {random_numbers}")
    length = len(raffle_tickets)
    bottom_80_percent = int(length * 0.8)
    top_20_percent = length - bottom_80_percent
    eliminated = raffle_tickets[:bottom_80_percent]
    # print(f"eliminated numbers are: {eliminated}")
    maybe_winners = [length-eliminated]
    # print(f"Maybe winner numbesr are: {maybe_winners}")
    keychain_winners = raffle_tickets[-top_20_percent:]
    top_3_winners = raffle_tickets[-3:]
    print("Keychain winners are:", keychain_winners)
    print(f"Top 3 winners are: {top_3_winners}")
    # print(f"Debugging... {raffle_tickets[0]} should not have won, and {raffle_tickets[-1]} should have won.")


def main():
    raffle_tickets = np.arange(1, 20)
    pick_the_winners(raffle_tickets)


if __name__ == "__main__":
    main()
