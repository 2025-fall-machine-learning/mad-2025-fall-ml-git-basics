import random
import numpy as np


def pick_the_winners(raffle_tickets, raffle_names):
    randomizer = random.Random(42)
    indices = list(range(len(raffle_tickets)))
    #print(f'Initial indices: {indices}')
    randomizer.shuffle(indices)
    #print(f'Shuffled indices: {indices}')
    length = len(raffle_tickets)
    bottom_80_percent = int(length * 0.8)
    top_20_percent = length - bottom_80_percent
    # Blanca here: The following will randomize the order of the tickets and names separately.
    # The names should stay coordinated with the ticket numbers. Use indices instead. Please
    # complete. I have to run on a business trip now. Sorry to leave you hanging.
    # Use the shuffled `indices` to permute both collections identically so
    # each name stays attached to its original ticket number.
    #
    # BUGFIX: Introduced a new variable 'perm' and attached it to shuffled_tickets & shuffled_names to permute both tickets and names identically 
    # so when winners are selected the names stay paired with their ticket numbers.
    perm = np.array(indices)
    shuffled_tickets = np.array(raffle_tickets)[perm]
    shuffled_names = np.array(raffle_names)[perm]
    #print(f'Shuffled tickets: {shuffled_tickets}')
    #print(f'Shuffled names: {shuffled_names}')
    # BUGFIX: Used shuffled_tickets and shuffled_names to select winners so names stay paired with ticket numbers.
    eliminated_tickets = shuffled_tickets[:bottom_80_percent]
    eliminated_names = shuffled_names[:bottom_80_percent]
    keychain_winner_numbers = shuffled_tickets[-top_20_percent:]
    keychain_winner_names = shuffled_names[-top_20_percent:]
    top_2_winner_numbers = shuffled_tickets[-2:]
    top_2_winner_names = shuffled_names[-2:]
    print("Keychain winners are:", ", ".join([f"{name} ({num})" for name, num in zip(keychain_winner_names, keychain_winner_numbers)]))
    print(f"Top 2 winners are: {top_2_winner_numbers} with names {top_2_winner_names}")
    #print(f"Debugging... {top_2_winner_names[-1]} did not start as number {top_2_winner_numbers[-1]}. Bug. Use indices.")


def main():
    raffle_tickets = np.arange(1, 21)
    raffle_names = np.array(["Amara", "Bili", "Chen", "Diego", "Fatima", "Hiroshi", "Ingrid", "Kwame", "Lakshmi", "Mohammed", "Nguyen", "Olga", "Priya", "Rashid", "Sakura", "Tariq", "Uma", "Vladimir", "Yuki", "Zara"])
    print("The raffle ticket holders are:", ", ".join([f"{name} ({num})" for name, num in zip(raffle_names, raffle_tickets)]))
    pick_the_winners(raffle_tickets, raffle_names)


if __name__ == "__main__":
    main()
