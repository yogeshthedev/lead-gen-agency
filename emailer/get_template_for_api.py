import sys
import json
from templates import get_template

def main():
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Missing arguments"}))
        return
    
    follow_up_count = int(sys.argv[1])
    business_name = sys.argv[2]
    city = sys.argv[3]
    category = sys.argv[4]

    template = get_template(follow_up_count, business_name, city, category)
    print(json.dumps(template))

if __name__ == "__main__":
    main()
