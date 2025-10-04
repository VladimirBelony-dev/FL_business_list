import re

text = 'FT. LAUDERDALE FL33304'
print('Text:', repr(text))
print('Text length:', len(text))

# Test basic regex
basic_match = re.search(r'FL', text)
print('Basic FL match:', basic_match)

# Test with different patterns
patterns = [
    r'FL',
    r'FL\s',
    r'FL\s+',
    r'FL\s+\d',
    r'FL\s+\d{5}',
    r'FL\s+(\d{5})',
    r'FL(\d{5})',  # No space between FL and zip
    r'([A-Z]{2})(\d{5})',  # Any state with zip
]

for i, pattern in enumerate(patterns):
    match = re.search(pattern, text)
    print(f'Pattern {i+1}: {pattern} -> {match}')
    if match:
        print(f'  Groups: {match.groups()}')
        print(f'  Start: {match.start()}, End: {match.end()}')
        print(f'  Matched text: {repr(match.group())}')
