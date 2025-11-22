filename = 'itf.txt'
target_id = '8o3c9x4'

print(f"Searching for ID: {target_id}...")
with open(filename, 'r') as f:
    for line in f:
        if line.startswith(target_id):
            print("\nFOUND IT:")
            print(line.strip())
            # Extract Date roughly (cols 15-32)
            print(f"Date String: {line[15:32]}")
            break