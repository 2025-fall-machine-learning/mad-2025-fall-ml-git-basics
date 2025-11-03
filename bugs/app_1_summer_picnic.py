import random
import numpy as np


def pick_the_winners(raffle_tickets):
    randomizer = random.Random(42)
    randomizer.shuffle(raffle_tickets)
    length = len(raffle_tickets)
    bottom_80_percent = int(length * 0.8)
    top_20_percent = length - bottom_80_percent
    eliminated = raffle_tickets[:bottom_80_percent]
    keychain_winners = raffle_tickets[-top_20_percent:]
    top_3_winners = keychain_winners[-3:]
    # print(f"raffle_tickets = {raffle_tickets}, and randomizer = {randomizer}")
    # print(f'Length = {length}, bottom 80% = {bottom_80_percent}, top 20% = {top_20_percent}, eliminated = {eliminated}, keychain winners = {keychain_winners}, top 3 winners = {top_3_winners},')
    print("Keychain winners are:", keychain_winners)
    print(f"Top 3 winners are: {top_3_winners}")
    # print(f"Debugging... {raffle_tickets[0]} should not have won, and {raffle_tickets[-1]} should have won.")


def main():
    raffle_tickets = np.arange(1, 20)
    pick_the_winners(raffle_tickets)


if __name__ == "__main__":
    main()
