import random
import numpy as np


def pick_the_winners(raffle_tickets, raffle_names):
    randomizer = random.Random(42)
    indices = list(range(len(raffle_tickets )))
    # Added code to randomize raffles using indices
    # print(f"indices: {indices}")
    randomizer.shuffle(indices)
    # print(f"randomized indices: {indices}")
    raffle_names = raffle_names[indices]
    # print(f"randomized raffle_names: {raffle_names}")
    raffle_tickets = raffle_tickets[indices]
    # print(f"randomized raffle_tickets: {raffle_tickets}")

    length = len(raffle_tickets)
    bottom_80_percent = int(length * 0.8)
    top_20_percent = length - bottom_80_percent
    # Blanca here: The following will randomize the order of the tickets and names separately.
    # The names should stay coordinated with the ticket numbers. Use indices instead. Please
    # complete. I have to run on a business trip now. Sorry to leave you hanging.
    # randomizer.shuffle(raffle_tickets)
    # print(f"randomized raffle_tickets: {raffle_tickets}")
    # randomizer.shuffle(raffle_names)
    # print(f"randomized raffle_names: {raffle_names}")
    eliminated_tickets = raffle_tickets[:bottom_80_percent]
    eliminated_names = raffle_names[:bottom_80_percent]
    keychain_winner_numbers = raffle_tickets[-top_20_percent:]
    keychain_winner_names = raffle_names[-top_20_percent:]
    top_2_winner_numbers = raffle_tickets[-2:]
    top_2_winner_names = raffle_names[-2:]
    print("Keychain winners are:", ", ".join([f"{name} ({num})" for name, num in zip(keychain_winner_names, keychain_winner_numbers)]))
    print(f"Top 2 winners are: {top_2_winner_numbers} with names {top_2_winner_names}")
    # print(f"Debugging... {top_2_winner_names[-1]} did not start as number {top_2_winner_numbers[-1]}. Bug. Use indices.")


def main():
    raffle_tickets = np.arange(1, 21)
    raffle_names = np.array(["Amara", "Bili", "Chen", "Diego", "Fatima", "Hiroshi", "Ingrid", "Kwame", "Lakshmi", "Mohammed", "Nguyen", "Olga", "Priya", "Rashid", "Sakura", "Tariq", "Uma", "Vladimir", "Yuki", "Zara"])
    print("The raffle ticket holders are:", ", ".join([f"{name} ({num})" for name, num in zip(raffle_names, raffle_tickets)]))
    pick_the_winners(raffle_tickets, raffle_names)


if __name__ == "__main__":
    main()
