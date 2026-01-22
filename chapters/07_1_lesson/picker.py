import random
MIN_NUMBER = 1
MAX_NUMBER = 100

def get_valid_guess():
    # TODO: Implement this function
    guess = int(input("Enter your guess: "))
    return guess
    pass

def play_picker():
    # TODO: Implement this function
    number = random.randint(MIN_NUMBER, MAX_NUMBER)
    print(f"I've picked a number between {MIN_NUMBER} and {MAX_NUMBER}.")
    while True:
        guess = get_valid_guess()
        if guess == number:
            print("Congrats, you got it!")
            break
        elif guess < number:
            print("Too low, try again.")
        elif guess > number:
            print("Too high, try again.")
    pass

def main():
    print('=' * 60)
    print()
    print("Welcome to the Number Guessing Game!")
    print()
    while True:
        guess_count = play_picker()
        answer = input("Do you want to play again? (y/n) ").lower()
        if answer == "n":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()