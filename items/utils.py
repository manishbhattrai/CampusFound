from .models import Item

def match_items(lost_item):

    found_items = Item.objects.filter(status='found')

    results = []

    for found in found_items:

        score = 0

        if lost_item.item_name.lower() in found.item_name.lower():
            score += 20

        if lost_item.category == found.category:
            score += 10

        if lost_item.location.lower() == found.location.lower():
            score += 15


        if lost_item.date_happened and found.date_happened:
            diff = abs((lost_item.date_happened - found.date_happened).days)
            if diff <=2:
                score += 5

            elif diff <=5:
                score += 3


        if score > 30:
            results.append((found,score))

    return sorted(results, key=lambda x: x[1],reverse=True)