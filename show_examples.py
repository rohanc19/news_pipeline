"""
Show examples of prediction market questions from each category.
"""
import json
import sys

def show_examples(filename):
    """
    Show examples of prediction market questions from each category.
    
    Args:
        filename: Path to the output file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        markets = data['eventsData'][0]['markets']
        
        # Get unique categories
        categories = set(market['category'] for market in markets)
        
        # Show one example from each category
        for category in sorted(categories):
            for market in markets:
                if market['category'] == category:
                    print(f"\n{category} Example:")
                    print(f"Title: {market['title']}")
                    print(f"Tags: {', '.join(market['tags'])}")
                    print(f"End Time: {market['endTime']}")
                    print(f"Description: {market['description'][:200]}...")
                    break
        
    except Exception as e:
        print(f"Error showing examples: {str(e)}")
        return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "test_run_output.json"
    
    show_examples(filename)
