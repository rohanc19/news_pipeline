"""
Analyze the output of the news pipeline.
"""
import json
import sys

def analyze_output(filename):
    """
    Analyze the output of the news pipeline.
    
    Args:
        filename: Path to the output file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        markets = data['eventsData'][0]['markets']
        total_markets = len(markets)
        
        print(f"Total markets: {total_markets}")
        
        # Count markets by category
        categories = {}
        for market in markets:
            category = market['category']
            categories[category] = categories.get(category, 0) + 1
        
        print("\nMarkets by category:")
        for category, count in categories.items():
            print(f"- {category}: {count}")
        
        # Count unique tags
        all_tags = []
        for market in markets:
            all_tags.extend(market['tags'])
        
        unique_tags = set(all_tags)
        tag_counts = {tag: all_tags.count(tag) for tag in unique_tags}
        
        print("\nTop 10 tags:")
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags[:10]:
            print(f"- {tag}: {count}")
        
        # Sample market
        print("\nSample market:")
        sample_market = markets[0]
        print(f"Title: {sample_market['title']}")
        print(f"Category: {sample_market['category']}")
        print(f"Tags: {', '.join(sample_market['tags'])}")
        print(f"End Time: {sample_market['endTime']}")
        print("Description: " + sample_market['description'][:200] + "...")
        
    except Exception as e:
        print(f"Error analyzing output: {str(e)}")
        return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "test_output.json"
    
    analyze_output(filename)
