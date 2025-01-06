# Seedy - Advanced Ethereum Seed Recovery Tool 🌱

A powerful command-line tool for managing and recovering Ethereum seed phrases with multiple recovery modes.

## Features

- 🔄 Scan positions for address match
- 🎯 Search by address pattern
- 🧩 Find missing words
- ✓ Validate seed phrases
- 📋 Display Ethereum addresses
- 🔀 Descramble seed phrases

## Installation

1. Clone the repository:
git clone https://github.com/D31337m3/Seedy.git



2. Install required dependencies:
pip install mnemonic eth_account

## Usage
Run the tool:

python seedy.py

Select from 6 operating modes:

Position Scanner: Find single-word errors in seed phrases
Address Pattern Search: Search for seeds generating addresses with specific endings
Missing Words Finder: Recover seeds with missing words
Seed Validator: Check if a seed phrase is valid
Address Display: Show Ethereum addresses for a seed
Seed Descrambler: Find valid arrangements of scrambled words
Supported Features
Works with 12, 15, 18, and 24-word seed phrases
BIP39 mnemonic validation
Real-time progress tracking
Results saved to text files
Cross-platform compatibility
Output Files
position_matches.txt: Results from position scanning
pattern_matches.txt: Address pattern search results
missing_words.txt: Missing word recovery results
descrambled.txt: Valid descrambled combinations
Security Note
Always use this tool in a secure, offline environment when working with real seed phrases.

License
MIT License

Author
D31337m3


This README provides a comprehensive overview of the tool's 