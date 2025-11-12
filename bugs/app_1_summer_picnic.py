import random
import numpy as np


def pick_the_winners(raffle_tickets):
    randomizer = random.Random(42)
    randomizer.shuffle(raffle_tickets)
    length = len(raffle_tickets)
    # print(f"length: {length}")
    bottom_80_percent = int(length * 0.8)
    print(f"bottom_80_percent: {bottom_80_percent}")
    top_20_percent = length - bottom_80_percent
    # print(f"top_20_percent: {top_20_percent}")
    print(f"raffle_tickets: {raffle_tickets}")
    # eliminated = raffle_tickets[top_20_percent:length]
    # print(f"eliminated: {eliminated}")
    keychain_winners = raffle_tickets[bottom_80_percent:]
    top_3_winners = raffle_tickets[bottom_80_percent + 1:]
    print("Keychain winners are:", keychain_winners)
    print(f"Top 3 winners are: {top_3_winners}")
    print(f"Debugging... {raffle_tickets[0]} should not have won, and {raffle_tickets[-1]} should have won.")


def main():
    raffle_tickets = np.arange(1, 20)
    pick_the_winners(raffle_tickets)


if __name__ == "__main__":
    main()