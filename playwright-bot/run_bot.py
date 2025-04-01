import argparse
from bot.delete_listing import delete_listing_by_item_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--item_id", required=True, help="eBay Item ID to delete")
    args = parser.parse_args()
    delete_listing_by_item_id(args.item_id)
