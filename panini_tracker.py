#!/usr/bin/env python3
import argparse
import csv
import os
import urllib.request
from typing import List, Dict

# Constants
TOTAL_STICKERS = 720
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collection.csv")
CSV_HEADERS = ["sticker_number", "amount"]

def initialize_csv_if_not_exists() -> None:
    """Initialize the CSV file if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def read_collection() -> Dict[int, int]:
    """Read the collection from the CSV file."""
    initialize_csv_if_not_exists()
    collection = {}
    
    with open(CSV_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sticker_number = int(row["sticker_number"])
                amount = int(row["amount"])
                collection[sticker_number] = amount
            except (ValueError, KeyError):
                continue
    
    return collection

def write_collection(collection: Dict[int, int]) -> None:
    """Write the collection to the CSV file."""
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for sticker_number, amount in sorted(collection.items()):
            writer.writerow([sticker_number, amount])

def add_stickers(stickers: List[int], collection: Dict[int, int]) -> Dict[int, int]:
    """Add stickers to the collection."""
    duplicates = []
    
    for sticker in stickers:
        if sticker in collection:
            duplicates.append(sticker)
        else:
            collection[sticker] = 1
    
    if duplicates:
        print(f"Warning: The following stickers are already in your collection: {', '.join(map(str, duplicates))}")
        confirm = input("Do you want to add these as duplicates? (y/n): ").lower()
        
        if confirm == "y":
            for sticker in duplicates:
                collection[sticker] += 1
    
    return collection

def print_missing(collection: Dict[int, int]) -> None:
    """Print missing sticker numbers."""
    missing = [i for i in range(1, TOTAL_STICKERS + 1) if i not in collection]
    print(f"Missing stickers ({len(missing)}):")
    
    # Print in a more readable format (e.g., 10 per line)
    for i in range(0, len(missing), 10):
        chunk = missing[i:i+10]
        print(", ".join(map(str, chunk)))

def print_owned(collection: Dict[int, int]) -> None:
    """Print owned sticker numbers."""
    owned = sorted(collection.keys())
    print(f"Owned stickers ({len(owned)}):")
    
    # Print in a more readable format (e.g., 10 per line)
    for i in range(0, len(owned), 10):
        chunk = owned[i:i+10]
        print(", ".join(map(str, chunk)))

def print_stats(collection: Dict[int, int]) -> None:
    """Print collection stats."""
    owned = len(collection)
    missing = TOTAL_STICKERS - owned
    duplicates = sum(amount - 1 for amount in collection.values() if amount > 1)
    progress = (owned / TOTAL_STICKERS) * 100
    
    print(f"Collection Stats:")
    print(f"- Owned: {owned} ({progress:.1f}%)")
    print(f"- Missing: {missing}")
    print(f"- Total: {TOTAL_STICKERS}")
    print(f"- Duplicates for exchange: {duplicates}")

def compare_collections(other_url: str, collection: Dict[int, int]) -> None:
    """Compare with another collection for exchanges."""
    # Download the other collection
    try:
        with urllib.request.urlopen(other_url) as response:
            other_csv = response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error downloading the other collection: {e}")
        return
    
    # Parse the other collection
    other_collection = {}
    reader = csv.DictReader(other_csv)
    for row in reader:
        try:
            sticker_number = int(row["sticker_number"])
            amount = int(row["amount"])
            other_collection[sticker_number] = amount
        except (ValueError, KeyError):
            continue
    
    # Find potential exchanges
    my_duplicates = {k: v-1 for k, v in collection.items() if v > 1}
    my_needs = [i for i in range(1, TOTAL_STICKERS + 1) if i not in collection]
    other_duplicates = {k: v-1 for k, v in other_collection.items() if v > 1}
    other_needs = [i for i in range(1, TOTAL_STICKERS + 1) if i not in other_collection]
    
    # What they can give me
    they_give = [num for num in my_needs if num in other_duplicates]
    
    # What I can give them
    i_give = [num for num in other_needs if num in my_duplicates]
    
    print("\nExchange Opportunities:")
    print("\nWhat they can give you:")
    for sticker in they_give:
        print(f"- Sticker #{sticker} (they have {other_duplicates[sticker]} extra)")
    
    print("\nWhat you can give them:")
    for sticker in i_give:
        print(f"- Sticker #{sticker} (you have {my_duplicates[sticker]} extra)")

def compare_local_collections(their_duplicates: List[int], their_missing: List[int], collection: Dict[int, int]) -> None:
    """Compare with another collection using provided duplicates and missing lists."""
    my_duplicates = {k: v-1 for k, v in collection.items() if v > 1}
    my_needs = [i for i in range(1, TOTAL_STICKERS + 1) if i not in collection]
    
    # What they can give me (intersection of my needs and their duplicates)
    they_give = [num for num in my_needs if num in their_duplicates]
    
    # What I can give them (intersection of their needs and my duplicates)
    i_give = [num for num in their_missing if num in my_duplicates]
    
    print("\nExchange Opportunities:")
    print("\nWhat they can give you:")
    if they_give:
        for sticker in sorted(they_give):
            print(f"- Sticker #{sticker}")
    else:
        print("None of their duplicates match your needs.")
    
    print("\nWhat you can give them:")
    if i_give:
        for sticker in sorted(i_give):
            print(f"- Sticker #{sticker} (you have {my_duplicates[sticker]} extra)")
    else:
        print("None of your duplicates match their needs.")
    
    if they_give and i_give:
        print(f"\nPossible trade: {len(min(they_give, i_give, key=len))} stickers")

def print_duplicates(collection: Dict[int, int]) -> None:
    """Print duplicate stickers and their quantities."""
    duplicates = {k: v for k, v in collection.items() if v > 1}
    
    if not duplicates:
        print("You don't have any duplicate stickers.")
        return
    
    print(f"Duplicate stickers ({len(duplicates)}):")
    for sticker, amount in sorted(duplicates.items()):
        print(f"- Sticker #{sticker}: {amount - 1} extra")

def print_exchange_info(collection: Dict[int, int]) -> None:
    """Print both duplicates and missing stickers for exchange purposes."""
    # Print duplicates
    duplicates = {k: v for k, v in collection.items() if v > 1}
    missing = [i for i in range(1, TOTAL_STICKERS + 1) if i not in collection]
    
    print("\n=== EXCHANGE INFO ===")
    print("\nDuplicates available for exchange:")
    if not duplicates:
        print("No duplicate stickers available.")
    else:
        for sticker, amount in sorted(duplicates.items()):
            print(f"{sticker}", end=",")
    
    print("\n\nStickers needed:")
    if not missing:
        print("Collection complete! No stickers needed.")
    else:
        for i in range(0, len(missing), 10):
            chunk = missing[i:i+10]
            print(",".join(f"{n}" for n in chunk))

    print(f"\nCollection progress: {len(collection)}/{TOTAL_STICKERS} ({(len(collection) / TOTAL_STICKERS) * 100:.1f}%)")

def find_stickers(stickers_to_find: List[int], collection: Dict[int, int]) -> None:
    """Check if specific stickers exist in the collection."""
    for sticker in stickers_to_find:
        if sticker in collection:
            print(f"Sticker #{sticker}: Found ({collection[sticker]} copies)")
        else:
            print(f"Sticker #{sticker}: Not found")

def remove_stickers(stickers_to_remove: List[int], collection: Dict[int, int]) -> Dict[int, int]:
    """Remove stickers from the collection."""
    not_found = []
    removed = []
    
    for sticker in stickers_to_remove:
        if sticker in collection:
            if collection[sticker] > 1:
                collection[sticker] -= 1
                removed.append(f"#{sticker} (now have {collection[sticker]} copies)")
            else:
                del collection[sticker]
                removed.append(f"#{sticker} (completely removed)")
        else:
            not_found.append(sticker)
    
    if not_found:
        print(f"Warning: The following stickers were not in your collection: {', '.join(map(str, not_found))}")
    
    if removed:
        print(f"Removed the following stickers from your collection:")
        for item in removed:
            print(f"- {item}")
    
    return collection

def parse_number_list(number_str: str) -> List[int]:
    """Parse a comma-separated list of numbers that may include ranges (e.g., '1,2,3-6,8')."""
    result = []
    for part in number_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start, end + 1))
        else:
            result.append(int(part.strip()))
    return result

def main():
    parser = argparse.ArgumentParser(description="Panini Album Progress Tracker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--add", help="Add stickers to collection (comma-separated list)")
    group.add_argument("-m", "--missing", action="store_true", help="Print missing sticker numbers")
    group.add_argument("-o", "--owned", action="store_true", help="Print owned sticker numbers")
    group.add_argument("-s", "--stats", action="store_true", help="Print collection stats")
    group.add_argument("-c", "--compare", help="URL to another CSV file for exchange comparison")
    group.add_argument("-cl", "--compare-local", nargs=2, 
                      metavar=('DUPLICATES', 'MISSING'),
                      help="Compare with local lists (format: 1,2,3 for both lists)")
    group.add_argument("-d", "--duplicates", action="store_true", help="Print duplicate stickers and their quantities")
    group.add_argument("-e", "--exchange", action="store_true", help="Print exchange info (duplicates and missing)")
    group.add_argument("-f", "--find", help="Check if stickers exist in collection (comma-separated list)")
    group.add_argument("-r", "--remove", help="Remove stickers from collection (comma-separated list)")
    
    args = parser.parse_args()
    collection = read_collection()
    
    if args.add:
        try:
            stickers_to_add = [int(s.strip()) for s in args.add.split(",")]
            # Validate sticker numbers
            invalid_stickers = [s for s in stickers_to_add if s < 1 or s > TOTAL_STICKERS]
            if invalid_stickers:
                print(f"Error: Invalid sticker numbers: {', '.join(map(str, invalid_stickers))}")
                print(f"Sticker numbers must be between 1 and {TOTAL_STICKERS}")
                return
            
            collection = add_stickers(stickers_to_add, collection)
            write_collection(collection)
            print(f"Added stickers to your collection.")
        except ValueError:
            print("Error: Please provide valid sticker numbers.")
    
    elif args.missing:
        print_missing(collection)
    
    elif args.owned:
        print_owned(collection)
    
    elif args.stats:
        print_stats(collection)
    
    elif args.compare:
        compare_collections(args.compare, collection)
        
    elif args.compare_local:
        try:
            their_duplicates = parse_number_list(args.compare_local[0])
            their_missing = parse_number_list(args.compare_local[1])
            
            # Validate sticker numbers
            all_numbers = their_duplicates + their_missing
            invalid_stickers = [s for s in all_numbers if s < 1 or s > TOTAL_STICKERS]
            if invalid_stickers:
                print(f"Error: Invalid sticker numbers: {', '.join(map(str, invalid_stickers))}")
                print(f"Sticker numbers must be between 1 and {TOTAL_STICKERS}")
                return
            
            compare_local_collections(their_duplicates, their_missing, collection)
        except ValueError as e:
            print(f"Error: {str(e)}")
            print("Please provide valid sticker numbers in format: 1,2,3-6,8")
    
    elif args.duplicates:
        print_duplicates(collection)
        
    elif args.exchange:
        print_exchange_info(collection)
    
    elif args.find:
        try:
            stickers_to_find = [int(s.strip()) for s in args.find.split(",")]
            # Validate sticker numbers
            invalid_stickers = [s for s in stickers_to_find if s < 1 or s > TOTAL_STICKERS]
            if invalid_stickers:
                print(f"Error: Invalid sticker numbers: {', '.join(map(str, invalid_stickers))}")
                print(f"Sticker numbers must be between 1 and {TOTAL_STICKERS}")
                return
            
            find_stickers(stickers_to_find, collection)
        except ValueError:
            print("Error: Please provide valid sticker numbers.")
    
    elif args.remove:
        try:
            stickers_to_remove = [int(s.strip()) for s in args.remove.split(",")]
            # Validate sticker numbers
            invalid_stickers = [s for s in stickers_to_remove if s < 1 or s > TOTAL_STICKERS]
            if invalid_stickers:
                print(f"Error: Invalid sticker numbers: {', '.join(map(str, invalid_stickers))}")
                print(f"Sticker numbers must be between 1 and {TOTAL_STICKERS}")
                return
            
            collection = remove_stickers(stickers_to_remove, collection)
            write_collection(collection)
        except ValueError:
            print("Error: Please provide valid sticker numbers.")

if __name__ == "__main__":
    main()
