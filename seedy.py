
from mnemonic import Mnemonic
import itertools
from datetime import datetime
import time
from eth_account import Account
import os 

"""
Advanced Seed Recovery Tool
This script provides various functionalities to work with Ethereum seed phrases, including:
1. Scanning positions for address match
2. Searching by address pattern
3. Finding missing words
4. Validating seed phrases
5. Displaying addresses
6. Descrambling seed phrases
Classes:
    ProgressTracker: Tracks and displays the progress of long-running operations.
Functions:
    validate_eth_address(seed_phrase: str, target_address: str) -> bool:
        Validates if the Ethereum address generated from the given seed phrase matches the target address.
    validate_seed(words: list) -> bool:
        Validates if the provided list of words forms a valid seed phrase and optionally displays the corresponding Ethereum address.
    display_addresses(seed_phrase: str) -> str:
        Displays the Ethereum address generated from the given seed phrase.
    scan_positions_for_address(seed_words: list, target_address: str, wordlist: set) -> list:
        Scans all positions of the seed words to find a match with the target Ethereum address.
    search_address_pattern(partial_words: list, target_pattern: str, wordlist: set) -> list:
        Searches for seed phrases that generate Ethereum addresses ending with the target pattern.
    find_missing_words(known_words: list, num_missing: int, wordlist: set) -> list:
        Finds valid seed phrases by filling in the missing words from the known words dictionary.
    descramble_seed(scrambled_words: list, wordlist: set) -> list:
        Finds valid seed phrases by testing permutations of the scrambled words.
    main():
        Entry point of the script. Provides a menu for the user to select the desired functionality.
"""

def clear_screen():
    # Cross-platform screen clearing
    os.system('cls' if os.name == 'nt' else 'clear')

class ProgressTracker:
    def __init__(self, mode_name):
        self.start_time = time.time()
        self.last_update = time.time()
        self.processed = 0
        self.mode_name = mode_name
        
    def update(self):
        self.processed += 1
        current_time = time.time()
        if current_time - self.last_update >= 2:
            speed = self.processed/(current_time-self.start_time)
            print(f"\r⚡ [{datetime.now().strftime('%H:%M:%S')}] {self.mode_name} | "
                  f"Tested: {self.processed:,} | "
                  f"Speed: {speed:.0f}/sec | {print_progress_bar(min(1, speed/10000))}", end="")
            self.last_update = current_time

def validate_eth_address(seed_phrase: str, target_address: str) -> bool:
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(seed_phrase)
    return account.address.lower() == target_address.lower()

SUPPORTED_LENGTHS = {12, 15, 18, 24}

def validate_seed(words):
    if len(words) not in SUPPORTED_LENGTHS:
        print(f"\n✗ Invalid: Length must be one of {sorted(SUPPORTED_LENGTHS)} words")
        return False
        
    mnemo = Mnemonic("english")
    is_valid = mnemo.check(" ".join(words))
    
    if is_valid:
        print("\n✓ Valid seed phrase")
        try:
            Account.enable_unaudited_hdwallet_features()
            account = Account.from_mnemonic(" ".join(words))
            print(f"ETH Address: {account.address}")
        except Exception as e:
            print(f"Note: Valid seed but couldn't generate ETH address: {str(e)}")
    else:
        print("\n✗ Invalid seed phrase")
    return is_valid

def display_addresses(seed_phrase):
    try:
        Account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(seed_phrase)
        print("\nAddresses for this seed:")
        print(f"ETH: {account.address}")
        return account.address
    except Exception as e:
        print(f"\nError generating addresses: {str(e)}")
        return None

def scan_positions_for_address(seed_words, target_address, wordlist):
    tracker = ProgressTracker("Position Scanner")
    mnemo = Mnemonic("english")
    matches = []
    
    print(f"\nScanning all positions against target address: {target_address}")
    print("Press Ctrl+C to stop scanning at any time\n")
    
    try:
        # Update to use actual length of seed_words instead of hardcoded 24
        for position in range(len(seed_words)):
            print(f"\nScanning position {position + 1}: {seed_words[position]}")
            test_words = seed_words.copy()
            
            for word in wordlist:
                if word == seed_words[position]:
                    continue
                    
                test_words[position] = word
                phrase = " ".join(test_words)
                
                if mnemo.check(phrase):
                    try:
                        if validate_eth_address(phrase, target_address):
                            match = {
                                'position': position + 1,
                                'original': seed_words[position],
                                'replacement': word,
                                'phrase': phrase
                            }
                            matches.append(match)
                            print(f"\n✓ Found match at position {position + 1}!")
                            print(f"Original: {seed_words[position]} -> New: {word}")
                            print(f"Seed: {phrase}\n")
                    except:
                        continue
                tracker.update()
                
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
        
    return matches
def search_address_pattern(partial_words, target_pattern, wordlist):
    tracker = ProgressTracker("Address Pattern Search")
    valid_phrases = []
    mnemo = Mnemonic("english")
    
    missing_count = 24 - len(partial_words)
    print(f"\nSearching for seeds with address ending in: {target_pattern}")
    print(f"Using {len(partial_words)} known words, searching {missing_count} positions")
    
    try:
        for combo in itertools.combinations(wordlist, missing_count):
            test_words = partial_words + list(combo)
            phrase = " ".join(test_words)
            
            if mnemo.check(phrase):
                try:
                    Account.enable_unaudited_hdwallet_features()
                    account = Account.from_mnemonic(phrase)
                    if account.address.lower().endswith(target_pattern.lower()):
                        match = {
                            'phrase': phrase,
                            'address': account.address
                        }
                        valid_phrases.append(match)
                        print(f"\nMatch found!")
                        print(f"Address: {account.address}")
                        print(f"Seed: {phrase}\n")
                except:
                    continue
            tracker.update()
            
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
        
    return valid_phrases

def find_missing_words(known_words, num_missing, wordlist):
    tracker = ProgressTracker("Missing Words Search")
    valid_phrases = []
    mnemo = Mnemonic("english")
    
    print(f"\nSearching for {num_missing} missing words...")
    
    try:
        for combo in itertools.combinations(wordlist, num_missing):
            test_words = known_words + list(combo)
            phrase = " ".join(test_words)
            if mnemo.check(phrase):
                valid_phrases.append(phrase)
                print(f"\nFound valid phrase: {phrase}")
            tracker.update()
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
        
    return valid_phrases

def descramble_seed(scrambled_words, wordlist):
    if len(scrambled_words) not in SUPPORTED_LENGTHS:
        print(f"\n✗ Invalid: Length must be one of {sorted(SUPPORTED_LENGTHS)} words")
        return []
    
    tracker = ProgressTracker("Descrambling")
    valid_phrases = []
    mnemo = Mnemonic("english")
    
    print(f"Testing permutations of {len(scrambled_words)} words...")
    
    try:
        for perm in itertools.permutations(scrambled_words):
            phrase = " ".join(perm)
            if mnemo.check(phrase):
                valid_phrases.append(phrase)
                print(f"\nFound valid phrase: {phrase}")
            tracker.update()
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
    return valid_phrases

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════╗
    ║     🌱 Advanced Seed Recovery Tool 🌱     ║
    ║         [ Ethereum Seed Manager ]         ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

def print_menu():
    menu = """
    🔍 Available Operations:
    
    [1] 🔄 Scan positions for address match
    [2] 🎯 Search by address pattern
    [3] 🧩 Find missing words
    [4] ✓ Validate seed phrase
    [5] 📋 Display addresses
    [6] 🔀 Descramble seed
    """
    print(menu)

def print_progress_bar(percentage):
    bar_length = 30
    filled = int(bar_length * percentage)
    bar = '█' * filled + '░' * (bar_length - filled)
    return f'[{bar}] {percentage*100:.1f}%'

def main():
    clear_screen()
    print_banner()
    print_menu()
    
    mode = input("\n📎 Enter mode number (1-6): ").strip()
    mnemo = Mnemonic("english")
    wordlist = set(mnemo.wordlist)

    if mode == "1":
        print(f"\n🔤 Enter your seed phrase (supported lengths: {sorted(SUPPORTED_LENGTHS)} words):")
        seed_words = input().strip().lower().split()
        if len(seed_words) not in SUPPORTED_LENGTHS:
            print(f"\n⚠️ Input contains {len(seed_words)} words. Please provide {sorted(SUPPORTED_LENGTHS)} words.")
            return
            
        print("🎯 Enter target ETH address:")
        target_address = input().strip()
        
        matches = scan_positions_for_address(seed_words, target_address, wordlist)
        if matches:
            print(f"\nFound {len(matches)} matching combinations!")
            with open('position_matches.txt', 'w') as f:
                for i, match in enumerate(matches, 1):
                    output = (f"\nMatch {i}:"
                            f"\nPosition {match['position']}: {match['original']} -> {match['replacement']}"
                            f"\nSeed phrase:\n{match['phrase']}")
                    print(output)
                    f.write(output + "\n")
            print("\nResults saved to 'position_matches.txt'")
        else:
            print("\nNo matching combinations found")

    elif mode == "2":
        print("\nEnter known words (space-separated):")
        partial_words = input().strip().lower().split()
        print("Enter address pattern to find:")
        target_pattern = input().strip()
        
        matches = search_address_pattern(partial_words, target_pattern, wordlist)
        if matches:
            print(f"\nFound {len(matches)} matching combinations!")
            with open('pattern_matches.txt', 'w') as f:
                for i, match in enumerate(matches, 1):
                    output = f"\nMatch {i}:\nAddress: {match['address']}\nSeed: {match['phrase']}"
                    print(output)
                    f.write(output + "\n")
            print("\nResults saved to 'pattern_matches.txt'")
        else:
            print("\nNo matches found")

    elif mode == "3":
        print("\nEnter known words (space-separated):")
        known_words = input().strip().lower().split()
        print("Enter number of missing words:")
        num_missing = int(input().strip())
        
        valid_phrases = find_missing_words(known_words, num_missing, wordlist)
        if valid_phrases:
            print(f"\nFound {len(valid_phrases)} valid combinations!")
            with open('missing_words.txt', 'w') as f:
                for i, phrase in enumerate(valid_phrases, 1):
                    output = f"\nOption {i}:\n{phrase}"
                    print(output)
                    f.write(output + "\n")
            print("\nResults saved to 'missing_words.txt'")
        else:
            print("\nNo valid combinations found")

    elif mode == "4":
        print(f"\nEnter seed phrase ({sorted(SUPPORTED_LENGTHS)} words supported):")
        words = input().strip().lower().split()
        if len(words) in SUPPORTED_LENGTHS:
            validate_seed(words)
        else:
            print(f"Length must be one of {sorted(SUPPORTED_LENGTHS)} words")

    elif mode == "5":
        print(f"\nEnter seed phrase ({sorted(SUPPORTED_LENGTHS)} words supported):")
        words = input().strip().lower().split()
        if len(words) in SUPPORTED_LENGTHS:
            if validate_seed(words):
                display_addresses(" ".join(words))
        else:
            print(f"Length must be one of {sorted(SUPPORTED_LENGTHS)} words")

    elif mode == "6":
        print(f"\n🔤 Enter your scrambled words (supported lengths: {sorted(SUPPORTED_LENGTHS)} words):")
        scrambled = input().strip().lower().split()
        if len(scrambled) not in SUPPORTED_LENGTHS:
            print(f"\n⚠️ Input contains {len(scrambled)} words. Please provide {sorted(SUPPORTED_LENGTHS)} words.")
            return
        
        valid_phrases = descramble_seed(scrambled, wordlist)
        if valid_phrases:
            print(f"\nFound {len(valid_phrases)} valid combinations!")
            with open('descrambled.txt', 'w') as f:
                for i, phrase in enumerate(valid_phrases, 1):
                    output = f"\nOption {i}:\n{phrase}"
                    print(output)
                    f.write(output + "\n")
            print("\nResults saved to 'descrambled.txt'")
        else:
            print("\nNo valid combinations found")

    else:
        print("Invalid mode number")
        print("Please try one of the listed options or use 'python seedy.py -h' for help")
if __name__ == "__main__":
    main()
